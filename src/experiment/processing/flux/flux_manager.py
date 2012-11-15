#===============================================================================
# Copyright 2012 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
from traits.api import HasTraits, Property, Str, cached_property, Int, List, \
    Float, Bool, on_trait_change, Button
from traitsui.api import View, Item, EnumEditor, TabularEditor, TableEditor, HGroup
from src.experiment.processing.database_manager import DatabaseManager
from traitsui.tabular_adapter import TabularAdapter
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
#============= standard library imports ========================
import struct
from numpy import average, std, asarray, mgrid, zeros, array
#============= local library imports  ==========================
from src.experiment.processing.argon_calculations import calculate_flux
from src.experiment.processing.flux.position import Position
from src.regression.ols_regressor import MultipleLinearRegressor
from src.database.records.isotope_record import IsotopeRecord
from threading import Thread
from src.helpers.thread_pool import ThreadPool
from src.initializer import MProgressDialog

plusminus = u'\u00b1'
one_sigma = u'1\u03c3'
#class PositionAdapter(TabularAdapter):
#    columns = [
#             ('Labnumber', 'labnumber'),
#             ('Hole', 'hole'),
#             ('X', 'x'), ('Y', 'y'),
#             ('J', 'j'), (plusminus + ' J', 'jerr'),
#             ('Pred. J', 'j'), (plusminus + ' Pred. J', 'pred_jerr'),
#
#             ]


class FluxManager(DatabaseManager):
    irradiation = Str
    irradiations = Property
    irradiation_labels = Property
    level = Str
    levels = Property(depends_on='irradiation')
    level_labels = Property(depends_on='irradiation')

    holder = Property(depends_on='level')
    positions = List

    age = Float
    age_error = Float

    calculate_button = Button
    calculate_j = Button
    plot_button = Button

    def _plot_button_fired(self):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        mx, my, mys, mye = zip(*[(pi.x, pi.y, pi.pred_j, pi.pred_jerr) for pi in self.positions if pi.use_j])
        x, y, ys, ye = zip(*[(pi.x, pi.y, pi.pred_j, pi.pred_jerr) for pi in self.positions if not pi.use_j])

        x = array(x)
        y = array(y)

        ys = array(ys)
        mys = array(mys)

        w = max(x) - min(x)
        w = w * 1.25
        c = len(x)
        r = len(y)
        n = r * 2 - 1

        xx, yy = mgrid[0:n + 1, 0:n + 1]
        xx = xx / float(n) * w - w / 2.
        yy = yy / float(n) * w - w / 2.

#        xx = xx * r / 2. - w
#        yy = yy * r / 2. - w
        z = zeros((r * 2, c * 2))

        reg = self._model_flux(use_pred=True)
        for i in range(r * 2):
            for j in range(c * 2):
                pt = (xx[i, j],
                      yy[i, j])
                v, _ = reg.predict([pt])[0]
                z[i, j] = v

        normalize = True
        if normalize:
            z *= 1 / z.max()# * w - w / 2.
            z *= 100
            z -= z.min() + (z.max() - z.min()) / 2.

            ys *= 1 / ys.max() - ys.min()
            ys *= 100
            ys -= ys.min() + (ys.max() - ys.min()) / 2.

            mys *= 1 / mys.max() - mys.min()
            mys *= 100
            mys -= mys.min() + (mys.max() - mys.min()) / 2.

        ax.plot_surface(xx, yy, z, alpha=0.3,
                        rstride=1, cstride=1,
                        cmap=cm.coolwarm,
                        linewidths=0
                        )
        ax.scatter(x, y, ys, s=10)
        ax.scatter(mx, my, mys, color='g', s=50)
        for xi, yi, zi, ei in zip(x, y, ys, ye):
#        for i in np.arange(0, len(x)):
            ax.plot([xi, xi], [yi, yi], [zi - ei, zi + ei],
                    color='blue',
                    marker='_'
                    )
        for xi, yi, zi, ei in zip(mx, my, mys, mye):
#        for i in np.arange(0, len(x)):
            ax.plot([xi, xi], [yi, yi], [zi - ei, zi + ei],
                    color='green',
                    marker='_'
                    )
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (%change)')
        plt.show()

    def _calculate_button_fired(self):
        self._calculate()

    def _calculate_j_fired(self):
        '''
            instead of using the current j 
            
            load all the analyses for each hole
            plot as ideogram
            
            calculate weighted mean of each group
            
        '''
        aids = []
        for pi in self.positions:
            if pi.use_j:
                ans = [ai.id for ai in pi.labnumber.analyses if ai.status == 0]
                aids.append((pi, ans))

        self._calculate_j(aids)

    def _calculate_j(self, aids, monitor_age=28.02e6):
        def calc_j(ai):
            ar40 = ai.arar_result['rad40']
            ar39 = ai.arar_result['k39']
            return calculate_flux(ar40, ar39, monitor_age)

        def mean_j(ans):
            js, errs = zip(*[calc_j(ai) for ai in ans])
            errs = asarray(errs)
            wts = errs ** -2
            m, ss = average(js, weights=wts, returned=True),
            return m, ss ** -0.5

        def ir_factory(ai):
            a = self.db.clone_record(ai)
            ir = IsotopeRecord(_dbrecord=a)
            return ir

        from src.database.orms.isotope_orm import meas_AnalysisTable
        def calc_mean(pi, aa):
            def factory(ai):
                sess = self.db.new_session()
                q = sess.query(meas_AnalysisTable)
                q = q.filter(meas_AnalysisTable.id == ai)
                dbr = q.one()

                ir = IsotopeRecord(_dbrecord=dbr)
                ir._calculate_age()
                sess.close()
                sess.remove()
                return ir

            ans = [factory(ai) for ai in aa]
            wm, ee = mean_j(ans)
            pi.pred_j = wm
            pi.pred_jerr = ee

        pool = ThreadPool(30)
        pool.map(calc_mean, aids)
        pool.wait_completion()

        reg = self._model_flux(use_pred=True)
        for pi in self.positions:
            if not pi.use_j:
                self._interpolate_flux(reg, pi)

    def _model_flux(self, use_pred=False):
        xy = [(p.x, p.y) for p in self.positions if p.use_j]
        if use_pred:
            zs = [(p.pred_j, p.pred_jerr) for p in self.positions if p.use_j]
        else:
            zs = [(p.j, p.jerr) for p in self.positions if p.use_j]

        reg = MultipleLinearRegressor(xs=xy, ys=zs)
        return reg

    def _calculate(self):

        reg = self._model_flux()

        for p in self.positions:
            if p.use_j:
                self._calculate_flux(p)
            else:
                self._interpolate_flux(reg, p)

    def _interpolate_flux(self, reg, p):
        v, _ = reg.predict([(p.x, p.y)])[0]

        p.pred_j = v
        p.pred_jerr = p.jerr

    def _calculate_flux(self, p):
#        j, jerr = calculate_flux(p.ar40, p.ar39, (self.age * 1e6, self.age_error * 1e6))
        p.pred_j = p.j
        p.pred_jerr = p.jerr

    @cached_property
    def _get_irradiations(self):
        return self.db.get_irradiations()

    def _irradiation_changed(self):
        irradname = self.irradiation
        if irradname == '---':
            return

        self.level = '---'
        self.info('loading irradiation {}'.format(irradname))

    def _level_changed(self):
        irradname = self.irradiation
        ln = self.level
        if ln == '---':
            return
        self.info('loading irradiation={}, level={}'.format(irradname, ln))

        lv = next((l for l in self.levels if l.name == ln))
        hd = lv.holder
        geom = hd.geometry
        hs = [struct.unpack('>ff', geom[i:i + 8]) for i in xrange(0, len(geom), 8)]
        n = len(hs)
        import math
        theta = math.radians(0)
        self.positions = [Position(hole=i + 1,
#                                   x=x, 
#                                   y=y,
                                   x=math.cos(theta) * x - math.sin(theta) * y,
                                   y=math.sin(theta) * x + math.cos(theta) * y,
                                   use_j=not i < n / 2,
                                   save=i < n / 2,
                                   j=0,
                                   jerr=0,
                                   ) for i, (x, y) in enumerate(hs)]

        for dbpos in lv.positions:
            h = dbpos.position
            pos = self.positions[h - 1]
            f = dbpos.labnumber.selected_flux_history.flux
            pos.j, pos.jerr = f.j, f.j_err
            pos.labnumber = dbpos.labnumber
#            pos.dbrecord = dbpos

    def _get_holder(self):
        level = next((l for l in self.levels if l.name == self.level), None)
        return level.holder.name if level else ''


    def _get_irradiation_labels(self):
        return ['---'] + [ir.name for ir in self.irradiations]

    def _get_level_labels(self):
        return ['---'] + [ir.name for ir in self.levels]

    def _get_levels(self):
        n = self.irradiation
        irrad = next((ir for ir in self.irradiations if ir.name == n), None)
        return [l for l in irrad.levels] if irrad else []

    def traits_view(self):
        cols = [

              ObjectColumn(name='hole', width=30, editable=False),
              ObjectColumn(name='x', format='%0.1f', width=40, editable=False),
              ObjectColumn(name='y', format='%0.1f', width=40, editable=False),
              ObjectColumn(name='j', format='%0.4e', width=100),
              ObjectColumn(name='jerr', format='%0.4e', label=plusminus + ' J', width=100),
              CheckboxColumn(name='use_j', label='Use', width=30),
              ObjectColumn(name='pred_j', format='%0.4e', label='Pred. J', width=100),
              ObjectColumn(name='pred_jerr', format='%0.4e', label=plusminus + 'Pred. J', width=100),
              ObjectColumn(name='residual', format='%0.5f', label='Residual', width=100),
              CheckboxColumn(name='save', width=30)
              ]
        v = View(
                 Item('irradiation',
                      editor=EnumEditor(name='irradiation_labels')),
                 Item('level',
                      editor=EnumEditor(name='level_labels')
                      ),
                 Item('holder', style='readonly'),
#                 HGroup(Item('age'), Item('age_error', label=plusminus + one_sigma)),
                HGroup(
                       Item('calculate_button'),
                       Item('calculate_j'),
                       Item('plot_button'),
                       show_labels=False
                       ),

                 Item('positions',
                      show_label=False,
                      editor=TableEditor(columns=cols,
                                         auto_size=False,
                                         row_height=18,
                                         )

#                      editor=TabularEditor(adapter=PositionAdapter())
                      ),
                 width=700,
                 height=500,
                 resizable=True
                 )
        return v

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('fluxman')
    f = FluxManager()
    f.db.connect()
    f.irradiation = 'NM-251'
    f.level = 'H'
    f.configure_traits()
#============= EOF =============================================

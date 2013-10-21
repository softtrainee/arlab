# @PydevCodeAnalysisIgnore
#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item, UItem
#============= standard library imports ========================
from uncertainties import ufloat
from numpy import asarray, average
#============= local library imports  ==========================
from src.irradiation.irradiation_selector import IrradiationSelector
from src.processing.analysis import Analysis
from src.database.records.isotope_record import IsotopeRecord
from src.processing.argon_calculations import calculate_flux
from src.processing.base_analysis_manager import BaseAnalysisManager
from src.processing.flux.level_view import LevelView


class FluxManager(BaseAnalysisManager):
    irradiation_selector = Instance(IrradiationSelector)
    level_view = Instance(LevelView)

    @on_trait_change('irradiation_selector:irradiation')
    def _irradiation_changed(self, new):
        print new

    @on_trait_change('irradiation_selector:level')
    def _level_changed(self, new):
        print new
        irrad = self.irradiation_selector.irradiation
        dblevel = self.db.get_irradiation_level(irrad, new)
        self.level_view.load(dblevel)

    @on_trait_change('level_view:calc_j')
    def _calc_j_fired(self):
        monitor_age = 28.02e6
        # helper funcs
        def calc_j(ai):
            return calculate_flux(ai.rad40, ai.k39, monitor_age)

        def mean_j(ans):
            js, errs = zip(*[calc_j(ai) for ai in ans])
            errs = asarray(errs)
            wts = errs ** -2
            m, ss = average(js, weights=wts, returned=True)
            return m, ss ** -0.5

        for si in self.level_view.positions[:1]:
            dbln = self.db.get_labnumber(si.labnumber)
            ans = dbln.analyses

            def afactory(ai):
                ir = Analysis(isotope_record=IsotopeRecord(_dbrecord=ai))
                return ir
            ans = [afactory(ai) for ai in ans
                    if ai.status == 0 and \
                        ai.step == '']
            self._load_analyses(ans)
            fig = self.ideogram(ans)
            print fig

            si.j = ufloat(*mean_j(ans))

        self.level_view.update = True

    def traits_view(self):
        v = View(
                 UItem('irradiation_selector', style='custom'),
                 UItem('level_view', style='custom'),
                 height=500,
                 width=600,
                 resizable=True
                 )
        return v

    def _irradiation_selector_default(self):
        ir = IrradiationSelector(db=self.db)
        return ir

    def _level_view_default(self):
        ir = LevelView(db=self.db)
        return ir

if __name__ == '__main__':

    fm = FluxManager()
    fm.db.kind = 'mysql'
    fm.db.username = 'root'
    fm.db.host = 'localhost'
    fm.db.password = 'Argon'
    fm.db.name = 'isotopedb_dev'
    fm.db.connect()
#    print fm.db.connect()
    fm.configure_traits()
#============= EOF =============================================

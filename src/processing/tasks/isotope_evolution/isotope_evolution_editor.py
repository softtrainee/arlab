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
from traits.api import Instance, Dict, Bool
from traitsui.api import View, UItem
from enable.component_editor import ComponentEditor
from chaco.plot_containers import GridPlotContainer
#============= standard library imports ========================
from numpy import Inf, polyfit

#============= local library imports  ==========================
from src.processing.tasks.analysis_edit.fits import IsoEvoFitSelector
from src.processing.tasks.analysis_edit.graph_editor import GraphEditor


class IsotopeEvolutionEditor(GraphEditor):
    component = Instance(GridPlotContainer)
    graphs = Dict
    _suppress_update = Bool

    #tool = Instance(IsoEvoFitSelector, ())
    tool = Instance(IsoEvoFitSelector)
    pickle_path = 'iso_fits'
    unpack_peaktime = True
    update_on_unknowns = False

    def _tool_default(self):
        t = IsoEvoFitSelector(auto_update=False)
        return t

    def save(self):
        proc = self.processor
        prog = proc.open_progress(n=len(self.unknowns) * 2)

        db = proc.db
        for unk in self.unknowns:
            prog.change_message('Saving fits for {}'.format(unk.record_id))

            meas_analysis = db.get_analysis_uuid(unk.uuid)
            self._save_fit(unk, meas_analysis)

            prog.change_message('Saving new ArAr age for {}'.format(unk.record_id))

            proc.save_arar(unk, meas_analysis)


    def _save_fit(self, unk, meas_analysis):
        fit_hist = None
        db = self.processor.db

        #ai=self.processor.make_analyses([unk])[0]
        for fi in self.tool.fits:
            if not fi.use:
                continue

            # get database fit
            name = fi.name
            if name.endswith('bs'):
                name = name[:-2]
                dbfit = unk.get_db_fit(name, meas_analysis, 'baseline')
                kind = 'baseline'
                v = unk.isotopes[name].baseline.uvalue
            else:
                dbfit = unk.get_db_fit(name, meas_analysis, 'signal')
                kind = 'signal'
                v = unk.isotopes[name].uvalue

            if dbfit != fi.fit:
                if fit_hist is None:
                    fit_hist = db.add_fit_history(meas_analysis, user=db.save_username)

                dbiso = next((iso for iso in meas_analysis.isotopes
                              if iso.molecular_weight.name == fi.name and
                                 iso.kind == kind), None)

                db.add_fit(fit_hist, dbiso, fit=fi.fit)

                #update isotoperesults
                v, e = float(v.nominal_value), float(v.std_dev)
                db.add_isotope_result(dbiso, fit_hist,
                                      signal_=v, signal_err=e)
                #update arar table

                self.debug('adding fit {} - {}'.format(fi.name, fi.fit))

    def _rebuild_graph(self):

        unk = self.unknowns
        n = len(unk)
        c = 1
        r = 1
        if n == 1:
            r = c = 1
        elif n >= 2:
            r = 2

            while n > r * c:
                c += 1
                if c > 7:
                    r += 1

        display_sniff = True

        self.component = self._container_factory((r, c))

        #fits=[fit for fit in self.tool.fits
        #      if (fit.fit and fit.show)]
        fits = list(self._graph_generator())

        if not fits:
            return

        prog = None
        n = len(self.unknowns)
        if n > 1:
            prog = self.processor.open_progress(n)

        add_tools = bind_index = self.tool.auto_update or n == 1

        for j, unk in enumerate(self.unknowns):
            set_ytitle = j % c == 0
            set_xtitle = j >= (n / r)
            g = self._graph_factory(bind_index=bind_index)
            plot_kw = dict(padding=[50, 1, 1, 1],
                           title=unk.record_id,
                           border_width=2
            )

            with g.no_regression(refresh=False):
                ma = -Inf
                set_x_flag = False
                i = 0
                for fit in fits:
                    #if fit.fit and fit.show:
                    set_x_flag = True
                    isok = fit.name
                    if set_ytitle:
                        plot_kw['ytitle'] = '{} (fA)'.format(isok)

                    if set_xtitle:
                        plot_kw['xtitle'] = 'Time (s)'

                    g.new_plot(**plot_kw)

                    if isok.endswith('bs'):
                        isok = isok[:-2]
                        iso = unk.isotopes[isok]
                        iso.baseline.fit = fit.fit
                        xs, ys = iso.baseline.xs, iso.baseline.ys
                        g.new_series(xs, ys,
                                     fit=fit.fit,
                                     add_tools=add_tools,
                                     plotid=i)
                    else:
                    #                     if isok in unk.isotopes:
                        iso = unk.isotopes[isok]
                        if display_sniff:
                            sniff = iso.sniff
                            if sniff:
                                g.new_series(sniff.xs, sniff.ys,
                                             plotid=i,
                                             type='scatter',
                                             fit=False)
                        iso.fit = fit.fit
                        xs, ys = iso.xs, iso.ys
                        g.new_series(xs, ys,
                                     fit=fit.fit,
                                     add_tools=add_tools,
                                     plotid=i)

                    ma = max(max(xs), ma)
                    i += 1

            if set_x_flag:
                g.set_x_limits(0, ma * 1.1)
                g.refresh()
                #self.graphs[unk.record_id] = g

            self.component.add(g.plotcontainer)
            #self.component.invalidate_draw()
            self.component.request_redraw()
            if prog:
                prog.change_message('Plotting {}'.format(unk.record_id))
                prog.increment()

    #def refresh_unknowns(self):
    #    if not self._suppress_update:
    #        for ui in self.unknowns:
    #        #                 ui.load_age()
    #            ui.analysis_summary.update_needed = True

    def traits_view(self):
        v = View(UItem('component',
                       style='custom',
                       editor=ComponentEditor()))
        return v

    def _component_default(self):
        return self._container_factory((1, 1))

    def _container_factory(self, shape):
        return GridPlotContainer(shape=shape,
                                 spacing=(1, 1,),
                                 backbuffer=True
        )

    #============= deprecated =============================================
    def calculate_optimal_eqtime(self):
        # get x,y data
        self.info('========================================')
        self.info('           Optimal Eq. Results')
        self.info('========================================')

        from src.processing.utils.equilibration_utils import calc_optimal_eqtime

        for unk in self.unknowns:

            for fit in self.tool.fits:
                if fit.fit and fit.use:
                    isok = fit.name
                    iso = unk.isotopes[isok]
                    sniff = iso.sniff
                    if sniff:
                        xs, ys = sniff.xs, sniff.ys
                        _rise_rates, ti, _vi = calc_optimal_eqtime(xs, ys)

                        xs, ys = iso.xs, iso.ys
                        m, b = polyfit(xs[:50], ys[:50], 1)
                        self.info(
                            '{:<12s} {}  t={:0.1f}  initial static pump={:0.2e} (fA/s)'.format(unk.record_id, isok, ti,
                                                                                               m))
                        g = self.graphs[unk.record_id]
                        if ti:
                            for plot in g.plots:
                                g.add_vertical_rule(ti, plot=plot)

        self.info('========================================')
        self.component.invalidate_and_redraw()

        #============= EOF =============================================

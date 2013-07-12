

# from pyface.ui.qt4.tasks.editor import Editor
# from PySide.QtWebKit import QWebView, QWebSettings
# from PySide.QtCore import QUrl
# # class myQWebView(QWebView):
# #    pass
# #
#
# class IsotopeEvolutionEditor(Editor):
#    def create(self, parent):
#        self.control = QWebView(parent)
#    #        self.control.setUrl(QUrl('http://www.google.com'))
#    #        self.control.setUrl(QUrl('file:///Users/ross/Sandbox/publish.pdf'))
# #        self.control.settings().setAttribute(QWebSettings.PluginsEnabled, True)
#    #        self.control.show()
# #        url = QUrl().fromLocalFile('/Users/ross/Sandbox/publish.pdf')
# #        print url
# #        self.control.load(url)
# #        self.control.load(QUrl('http://www.google.com'))
#        html = '''<html>
#    <body>
#    foasdfas
#    <embed src='file:///Users/ross/Sandbox/publish.pdf'></embed>
#    </body>
#    </html>
#    '''
#        self.control.setHtml(html)
# # <object type="application/x-pdf" data="file:///Users/ross/Sandbox/publish.pdf" width="500" height="400"></object>

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
from traits.api import HasTraits, Instance, Dict, on_trait_change, Bool
from traitsui.api import View, Item, UItem
from src.processing.tasks.analysis_edit.graph_editor import GraphEditor
#============= standard library imports ========================
from numpy import Inf, polyfit
from enable.component_editor import ComponentEditor
# from src.graph.regression_graph import StackedRegressionGraph
from chaco.plot_containers import GridPlotContainer
from src.simple_timeit import timethis
from src.processing.tasks.analysis_edit.fits import IsoEvoFitSelector
# from src.processing.equilibration_utils import calc_optimal_eqtime
#============= local library imports  ==========================

class IsotopeEvolutionEditor(GraphEditor):
    component = Instance(GridPlotContainer)
    graphs = Dict
    _suppress_update = Bool
    tool = Instance(IsoEvoFitSelector, ())
    def calculate_optimal_eqtime(self):
        # get x,y data
        self.info('========================================')
        self.info('           Optimal Eq. Results')
        self.info('========================================')

        from src.processing.utils.equilibration_utils import calc_optimal_eqtime
        for unk in self._unknowns:

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
                        self.info('{:<12s} {}  t={:0.1f}  initial static pump={:0.2e} (fA/s)'.format(unk.record_id, isok, ti, m))
                        g = self.graphs[unk.record_id]
                        if ti:
                            for plot in g.plots:
                                g.add_vertical_rule(ti, plot=plot)

        self.info('========================================')
        self.component.invalidate_and_redraw()

    def save(self):
        for unk in self._unknowns:
            self._save_fit(unk)

    def _save_fit(self, unk):
        fit_hist = None

        db = self.processor.db
        for fi in self.tool.fits:
            # get database fit
            dbfit = unk._get_db_fit(fi.name)
            if dbfit != fi.fit:
                if fit_hist is None:
                    fit_hist = db.add_fit_history(self.dbrecord, user=db.save_username)

                dbiso = next((iso for iso in self.dbrecord.isotopes
                              if iso.molecular_weight.name == fi.name), None)

                db.add_fit(fit_hist, dbiso, fit=fi.fit)
#     def _rebuild_graph(self):
#         timethis(self._rebuild_graph2, msg='total')

    def _rebuild_graph(self):
        unk = self._unknowns
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

        for j, unk in enumerate(self._unknowns):
            set_ytitle = j % c == 0
            set_xtitle = j >= (n / r)
            g = self._graph_factory()
            ma = -Inf
            set_x_flag = False
            i = 0
            for fit in self.tool.fits:
                if fit.fit and fit.show:
                    set_x_flag = True
                    isok = fit.name
                    kw = dict(padding=[50, 1, 1, 1],
                              title=unk.record_id
                              )
                    if set_ytitle:
    #                        kw = dict(padding=[50, 1, 1, 1])
                        kw['ytitle'] = '{} (fA)'.format(isok)

                    if set_xtitle:
                        kw['xtitle'] = 'Time (s)'

                    g.new_plot(**kw)

                    if isok.endswith('bs'):
                        isok = isok[:-2]
                        iso = unk.isotopes[isok]
                        iso.baseline.fit = fit.fit
                        xs, ys = iso.baseline.xs, iso.baseline.ys
                        g.new_series(xs, ys,
                                     fit=fit.fit,
#                                      add_tools=False,
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
#                                      add_tools=False,
                                     plotid=i)

                    ma = max(max(xs), ma)
                    i += 1

            if set_x_flag:
                g.set_x_limits(0, ma * 1.1)
                g.refresh()

            self.graphs[unk.record_id] = g
            self.component.add(g.plotcontainer)

    def refresh_unknowns(self):
        if not self._suppress_update:
            for ui in self._unknowns:
                ui.load_age()
                ui.analysis_summary.update_needed = True

    def traits_view(self):
        v = View(UItem('component',
                       style='custom',
                       editor=ComponentEditor()))
        return v

    def _component_default(self):
        return self._container_factory((1, 1))

    def _container_factory(self, shape):
        return GridPlotContainer(shape=shape,
                                 spacing=(1, 1),
#                                 bgcolor='lightgray',
                                 )

#============= EOF =============================================

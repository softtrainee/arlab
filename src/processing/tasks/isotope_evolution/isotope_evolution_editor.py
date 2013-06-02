

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
from traits.api import HasTraits, Instance
from traitsui.api import View, Item, UItem
from src.processing.tasks.analysis_edit.graph_editor import GraphEditor
#============= standard library imports ========================
from numpy import Inf
from enable.component_editor import ComponentEditor
# from src.graph.regression_graph import StackedRegressionGraph
from chaco.plot_containers import GridPlotContainer
#============= local library imports  ==========================

class IsotopeEvolutionEditor(GraphEditor):
    container = Instance(GridPlotContainer)
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

    def _rebuild_graph(self):
        unk = self._unknowns
        n = len(unk)
        c = 1
        r = 1
        if n > 2:
            r = 2

        while n > r * c:
    #            if gpi.fixed == 'cols':
    #                r += 1
    #            else:
            c += 1

        if n == 1:
            r = c = 1

        self.container = self._container_factory((r, c))
        g = self.graph
        for j, unk in enumerate(self._unknowns):
            set_ytitle = j % c == 0
            set_xtitle = j >= (n / r)
            g = self._graph_factory()
            ma = -Inf
            set_x_flag = False
            i = 0
            for fit in self.tool.fits:
                if fit.fit and fit.use:
                    set_x_flag = True
                    isok = fit.name
                    kw = dict(padding=[50, 1, 1, 1])
                    if set_ytitle:
    #                        kw = dict(padding=[50, 1, 1, 1])
                        kw['ytitle'] = '{} (fA)'.format(isok)

                    if set_xtitle:
                        kw['xtitle'] = 'Time (s)'

                    g.new_plot(**kw)

                    if isok in unk.isotopes:
                        iso = unk.isotopes[isok]
                        xs, ys = iso.xs, iso.ys
                        g.new_series(xs, ys,
                                     fit=fit.fit,
                                     plotid=i)

                    ma = max(max(iso.xs), ma)
                    i += 1

            if set_x_flag:
                g.set_x_limits(0, ma * 1.1)
                g.refresh()

    #            self.graphs.append(g)
            self.container.add(g.plotcontainer)

    def traits_view(self):
        v = View(UItem('container',
                       style='custom',
                       editor=ComponentEditor()))
        return v

    def _container_default(self):
        return self._container_factory((1, 1))

    def _container_factory(self, shape):
        return GridPlotContainer(shape=shape,
                                 spacing=(1, 1),
                                 bgcolor='lightgray',

                                 )
#============= EOF =============================================

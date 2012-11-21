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
from traits.api import HasTraits, Instance, Int, Any, Event, \
     on_trait_change, Either, Float, Dict
from traitsui.api import View, Item, ShellEditor
#from pyface.timer.do_later import do_later
#============= standard library imports ========================
from sqlalchemy.sql.expression import and_
#============= local library imports  ==========================
from src.experiment.processing.database_manager import DatabaseManager
from src.graph.graph_container import HGraphContainer
from enable.component_editor import ComponentEditor
from src.helpers.filetools import unique_path
import os
from src.paths import paths
from src.database.records.isotope_record import IsotopeRecord
#from threading import Event as TEvent, Thread
#from src.viewable import ViewableHandler, Viewable

class Window(HasTraits):
    container = Instance(HGraphContainer, ())
    window_width = Either(Int, Float)
    window_height = Either(Int, Float)
    open_event = Any


    def traits_view(self):
        v = View(Item('container',
                         show_label=False, style='custom',
                         editor=ComponentEditor(),
                         ),
                 resizable=True,
                 width=self.window_width,
                 height=self.window_height,
                 )
        return v

class ProcessScript(DatabaseManager):
    _figure = None
    window = Any
    context = Dict
    def _load_context(self):
        ctx = dict(sess=self.db.get_session(),
                   and_=and_,
                   ideogram=self._ideogram,
                   spectrum=self._spectrum,
                   save=self._save,
                   group_by_labnumber=self._group_by_labnumber,
                   group_by_aliquot=self._group_by_aliquot,
                   convert_records=self._convert_records,
                   recall=self._recall,
                   run=self._run,
                   fit=self._fit,
                   analysis=self._analysis,
                   filter_outliers=self._filter_outliers
                   )
        return ctx

    def _filter_outliers(self, analysis, **filter_dict):
        if not analysis.signal_graph:
            analysis.load_graph()

        g = analysis.signal_graph
        n = len(g.fit_selector.fits)
        vis = []
        for k, v in filter_dict.iteritems():
#            print k
#            a = next(((n - i - 1, fi) for i, fi in enumerate(g.fit_selector.fits)
#                                                  if fi.name == k), 0)
            a = next((fi for i, fi in enumerate(g.fit_selector.fits)
                                                  if fi.name == k), 0)
            if a:
#                plotid, fi = a
#                plot = g.plots[plotid]
#                print id(plot)
#                vis.append((plot, plot.visible, fi))
#                plot.visible = True
#                fi.trait_set(filter_outliers=v, trait_change_notify=False)
#                fi._suppress_update = True
                a.filter_outliers = v
#                fi._suppress_update = False

#        return
#        g._update_graph()

        g = analysis.baseline_graph
#        n = len(g.fit_selector.fits)
        for k, v in filter_dict.iteritems():
#            a = next(((n - i - 1, fi) for i, fi in enumerate(g.fit_selector.fits)
#                                                  if fi.name == k[:-2]), 0)
            a = next((fi for i, fi in enumerate(g.fit_selector.fits)
                                                  if fi.name == k[:-2]), 0)

            if a:
#                plotid, fi = a
#                plot = g.plots[plotid]
#                vis.append((plot, plot.visible))
#                plot.visible = True
                a.filter_outliers = v

#        g._update_graph()

#        analysis.age_dirty = True
#        analysis.analysis_summary.refresh()
#        analysis.analysis_summary.refresh()
#        try:
#            for p, v in vis:
#                p.visible = v
#        except ValueError:
#            pass

    def _fit(self, analysis, **fit_dict):
        '''
            e.g. fit(a, Ar40='linear')
        '''
        if not analysis.signal_graph:
            analysis.load_graph()

        g = analysis.signal_graph
        n = len(g.fit_selector.fits)
        for k, v in fit_dict.iteritems():
            a = next(((n - i - 1, fi) for i, fi in enumerate(g.fit_selector.fits)
                                                  if fi.name == k), 0)
            if a:
                plotid, fi = a

                vv = g.plots[plotid].visible
                g.plots[plotid].visible = True
                fi.fit = v
                g._update_graph()
                g.plots[plotid].visible = vv

        analysis.age_dirty = True

    def _analysis(self, labnumber, aliquot, step=''):
        db = self.db
        labn = db.get_labnumber(labnumber)
        if labn:
            ans = next((ai for ai in labn.analyses if ai.aliquot == aliquot and ai.step == step), None)
            if ans:
                return IsotopeRecord(_dbrecord=ans)

    def _run(self, p):
        if not p.endswith('.py'):
            p = '{}.py'.format(p)

        p = os.path.join('/Users/ross/Sandbox/scripts', p)
        txt = open(p, 'r').read()
        code = compile(txt, '<string>', 'exec')

        import ast
        import yaml
        m = ast.parse(txt)
        docstr = ast.get_docstring(m)
        self.parameters_dict = yaml.load(docstr)

        ctx = self.context
#        ctx = self._load_context()
        exec code in ctx
        ctx['main']()

#===============================================================================
# commands
#===============================================================================
    def _ideogram(self, analyses, show=True,
                  aux_plots=None):
        '''
        '''
        from src.experiment.processing.plotters.ideogram import Ideogram

        if aux_plots is None:
            aux_plots = []
#        if use_ages:
#            analyses = [DummyAnalysis(rid=ai[0],
#                                      _age=ai[1],
#                                      _error=ai[2],
#                                      group_id=ai[3]
#                                      ) for ai in analyses]

        wparams = self.parameters_dict['window']
        g = Window(
                   window_width=wparams['width'],
                   window_height=wparams['height'],
                   )
        self.window = g
        p = Ideogram(db=self.db)
        ps = []

        for ap in aux_plots:
            if ap == 'radiogenic':
                d = dict(func='radiogenic_percent',
                          ytitle='40Ar* %',
                          height=100
                          )
            elif ap == 'analysis_number':
                d = dict(func='analysis_number',
                     ytitle='Analysis #',
                     height=100)
            ps.append(d)

        gideo = p.build(analyses, aux_plots=ps)
        if gideo:
            gideo, plots = gideo
            self._figure = gideo
            g.container.add(gideo)
            if show:
                g.edit_traits()

    def _spectrum(self, analyses, show=True):
        from src.experiment.processing.plotters.spectrum import Spectrum

        print len(analyses), 'analyses'
        wparams = self.parameters_dict['window']
        g = Window(
                   window_width=wparams['width'],
                   window_height=wparams['height'],
                   )
        self.window = g
        spec = Spectrum(db=self.db)
        spec_graph = spec.build(analyses)
        if spec_graph:
            self._figure = spec_graph.plotcontainer
            g.container.add(spec_graph.plotcontainer)
            if show:
                g.edit_traits()
            return spec


    def _save(self, p, folder=None, figure=None):
        from chaco.pdf_graphics_context import PdfPlotGraphicsContext

        if folder is None:
            folder = paths.processing_dir

        if not p.endswith('.pdf'):
            p = '{}.pdf'.format(p)

#        root = os.path.dirname(p)
        base = os.path.basename(p)
        base, ext = os.path.splitext(base)
        p, _c = unique_path(folder, base, extension=ext)

        if figure is None:
            figure = self._figure

        if figure:

            gc = PdfPlotGraphicsContext(filename=p,
#                                      pdf_canvas=canvas,
#                                      dest_box=dest_box,
                                      pagesize='letter',
                                      dest_box_units='inch')

            comp = self._figure
            gc.render_component(comp, valign='center')
            gc.save()

    def _recall(self, labnumber, aliquot, step=''):
#        db = self.db
#        labn = db.get_labnumber(labnumber)
#        if labn:
#            ans = next((ai for ai in labn.analyses if ai.aliquot == aliquot and ai.step == step), None)
#            if ans:
#                dbr = IsotopeRecord(_dbrecord=ans)
        dbr = self._analysis(labnumber, aliquot, step)
        if dbr:
            if dbr.age:
                dbr.load_graph()
                dbr.edit_traits()

    def _group_by_aliquot(self, ans):
        groups = dict()
        for ri in ans:
            if ri.aliquot in groups:
                group = groups[ri.aliquot]
                group.append(ri.aliquot)
            else:
                groups[ri.aliquot] = [ri.aliquot]

        keys = sorted(groups.keys())

        for ri in ans:
            ri.group_id = keys.index(ri.aliquot)

    def _group_by_labnumber(self, ans):
        groups = dict()
        for ri in ans:
            if ri.labnumber in groups:
                group = groups[ri.labnumber]
                group.append(ri.labnumber)
            else:
                groups[ri.labnumber] = [ri.labnumber]

        keys = sorted(groups.keys())

        for ri in ans:
            ri.group_id = keys.index(ri.labnumber)

    def _convert_records(self, recs):
        from src.experiment.processing.analysis import Analysis

        return [Analysis(dbrecord=IsotopeRecord(_dbrecord=ri)) for ri in recs]

    def _test_fired(self):
        p = 'a.py'
        self._run(p)

    def traits_view(self):
        shell_grp = Item('context', editor=ShellEditor(share=True),
                         style='custom', show_label=False)
        v = View(Item('test'),
                 shell_grp,
                 resizable=True,
                 width=500,
                 height=500
                 )
        return v

    def _context_default(self):
        return self._load_context()



if __name__ == '__main__':
    c = ProcessScript()
    c.db.connect()
    c.configure_traits()
#============= EOF =============================================

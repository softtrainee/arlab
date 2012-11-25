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
from launchers.helpers import build_version
from src.helpers import alphas
build_version('_experiment')

from src.experiment.processing.analysis import NonDBAnalysis
from src.experiment.processing.plotters.plotter_options import PlotterOptions

#============= enthought library imports =======================
from traits.api import HasTraits, Instance, Int, Any, Event, \
     on_trait_change, Either, Float, Dict, Str
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
    window_x = Either(Int, Float)
    window_y = Either(Int, Float)

    open_event = Any
    title = Str('  ')

    def traits_view(self):
        v = View(Item('container',
                         show_label=False, style='custom',
                         editor=ComponentEditor(),
                         ),
                 resizable=True,
                 width=self.window_width,
                 height=self.window_height,
                 x=self.window_x,
                 y=self.window_y,
                 title=self.title
                 )
        return v

class ProcessScript(DatabaseManager):
    _figure = None
    window = Any
    context = Dict
    parameters_dict = Dict
    def _load_context(self):
        ctx = dict(
                   PlotterOptions=PlotterOptions,
                   and_=and_,
                   os=os,

                   show_plotter_options=self._show_plotter_options,
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
                   filter_outliers=self._filter_outliers,
                   load_text=self._load_text


                   )
        with_db = False
        if with_db:
            ctx['sess'] = self.db.get_session()
        return ctx



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

    def _load_text(self, p, delimiter='\t'):
        '''
            p= path to a text file
            
            parse text file and return list of analyses
        '''
        import csv
        ans = []
        with open(p, 'U') as fp:
            reader = csv.reader(fp, delimiter=delimiter)
            header = map(str.strip, reader.next())
            _info = reader.next()

            def get_value(li, attr, cast=float, offset=0):
#                print li
#                print header.index(attr)
#                print li[header.index(attr) + offset]
                return cast(li[header.index(attr) + offset])


            for li in reader:

                rc = get_value(li, 'Run ID# (pref. XXXX-XX)', cast=str)
#                s = ''
#                al = 1
#                if '-' in ln:
#                    ln, al = ln.split('-')
#                    if al[-1].upper() in alphas:
#                        s = int(al[-1])

                an = NonDBAnalysis(
                                   record_id=rc,
                                   status=get_value(li, '"Status (0=OK, 1=Deleted)"', cast=int),
                                   sample=get_value(li, 'Sample', cast=str),
                                   _age=get_value(li, 'Age (w/o  J;  irr. Param. Opt.)'),
                                   _error=get_value(li, 'Age (w/o  J;  irr. Param. Opt.)', offset=1)
                                   )

                ans.append(an)

        return ans

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
    def _show_plotter_options(self, plots=None):
        po = PlotterOptions(view_id='processing.script.plotter_options')
        if plots:
            po.construct_plots(plots)

        info = po.edit_traits(kind='livemodal')
        if info.result:
            return po

    def _ideogram(self, analyses, show=True,
                  aux_plots=None,
                  title=None,
                  xtick_font=None,
                  xtitle_font=None,
                  ytick_font=None,
                  ytitle_font=None,
                  data_label_font=None,
                  metadata_label_font=None,
                  highlight_omitted=False,
                  display_omitted=False,
                  display_mean_indicator=True,
                  display_mean_text=True
                  ):
        '''
        '''
        from src.experiment.processing.plotters.ideogram import Ideogram

        if aux_plots is None:
            aux_plots = []

        w = self.get_parameter('window', 'width', default=500)
        h = self.get_parameter('window', 'height', default=600)
        x = self.get_parameter('window', 'x', default=20)
        y = self.get_parameter('window', 'y', default=20)
        g = Window(
                   window_width=w,
                   window_height=h,
                   window_x=x, window_y=y
                   )
        self.window = g
        p = Ideogram(db=self.db)
        ps = []

        for ap in aux_plots:
            if isinstance(ap, str):
                name = ap
                scale = 'linear'
                height = 100
            else:
                name = ap.name
                scale = ap.scale
                height = ap.height

            if name == 'radiogenic':
                d = dict(func='radiogenic_percent',
                          ytitle='40Ar* %',
                          )
            elif name == 'analysis_number':
                d = dict(func='analysis_number',
                     ytitle='Analysis #',
                     )
            elif name == 'kca':
                d = dict(func='kca',
                     ytitle='K/Ca',
                     )
            else:
                continue

            d['height'] = height
            d['scale'] = scale
            ps.append(d)

        options = dict(aux_plots=ps,
                       xtitle_font=xtitle_font,
                       xtick_font=xtick_font,
                       ytitle_font=ytitle_font,
                       ytick_font=ytick_font,
                       data_label_font=data_label_font,
                       metadata_label_font=metadata_label_font,
                       title=title,
                       display_mean_text=display_mean_text,
                       display_mean_indicator=display_mean_indicator
                       )

        #filter out omitted results
        if not (display_omitted or highlight_omitted):
            analyses = filter(lambda x: x.status == 0, analyses)

        gideo = p.build(analyses, options=options)
        if gideo:
            gideo, _plots = gideo
            self._figure = gideo
            g.container.add(gideo)

            if highlight_omitted:
                ta = sorted(analyses, key=lambda x:x.age)
                #find omitted ans
                sel = [i for i, ai in enumerate(ta) if ai.status != 0]
                p.set_excluded_points(sel, 0)

            if show:
                g.edit_traits()

            return g, p

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


    def _save(self, p, folder=None, figure=None, unique=True):
        from chaco.pdf_graphics_context import PdfPlotGraphicsContext

        if folder is None:
            folder = paths.processing_dir

        if not p.endswith('.pdf'):
            p = '{}.pdf'.format(p)

#        root = os.path.dirname(p)
        if unique:
            base = os.path.basename(p)
            base, ext = os.path.splitext(base)
            p, _c = unique_path(folder, base, extension=ext)

        if figure is None:
            figure = self._figure

        print p
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

    def get_parameter(self, a, b, default=None):
        r = default
        if a in self.parameters_dict:
            ad = self.parameters_dict[a]
            if b in ad:
                r = ad[b]
        return r

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
#    c.db.connect()
    c.configure_traits()
#============= EOF =============================================

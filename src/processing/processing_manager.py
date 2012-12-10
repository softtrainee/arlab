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
from traits.api import HasTraits, Instance, cached_property, Property, List, Event, \
    Bool, Button
#from traitsui.api import View, Item, TableEditor, EnumEditor, HGroup
#import apptools.sweet_pickle as pickle
#============= standard library imports ========================
#import os
from numpy import array
#============= local library imports  ==========================
from src.processing.database_manager import DatabaseManager
from src.processing.processing_selector import ProcessingSelector
from src.processing.analysis import Analysis
#from src.processing.script import ProcessScript
#from src.constants import NULL_STR
from src.progress_dialog import MProgressDialog
from src.processing.plotter_options_manager import PlotterOptionsManager
from src.processing.window import Window
from src.processing.series_manager import SeriesManager
from src.processing.tabular_analysis_manager import TabularAnalysisManager
from src.processing.plotters.series import Series
from src.processing.corrections.corrections_manager import BlankCorrectionsManager, \
    BackgroundCorrectionsManager



class ProcessingManager(DatabaseManager):
    processing_selector = Instance(ProcessingSelector)
    blank_corrections_manager = Instance(BlankCorrectionsManager)
    background_corrections_manager = Instance(BackgroundCorrectionsManager)
    plotter_options_manager = Instance(PlotterOptionsManager, ())
    only_fusions = Bool(True)
    include_omitted = Bool(True)
    display_omitted = Bool(True)

    _window_count = 0

#===============================================================================
# apply corrections
#===============================================================================
    def apply_blank_correction(self):
        bm = self.blank_corrections_manager
        self._apply_correction(bm)

    def apply_background_correction(self):
        bm = self.background_corrections_manager
        self._apply_correction(bm)

    def _apply_correction(self, bm):
        if self._gather_data():

            bm.analyses = self._get_analyses()

            info = bm.edit_traits(kind='livemodal')
            if info.result:
                bm.apply_correction()

#===============================================================================
# display
#===============================================================================
    def new_series(self):
        self._new_figure('series')

    def new_ideogram(self):
        self._new_figure('ideogram')

    def new_spectrum(self):
        self._new_figure('spectrum')

    def new_isochron(self):
        self._new_figure('isochron')

    def _new_figure(self, name):
        '''
            ask for data and plot options
        '''

        if self._gather_data():
            if name != 'series':
                pom = self.plotter_options_manager
                info = pom.edit_traits(kind='livemodal')
                po = pom.plotter_options
                result = info.result
            else:
                result = True
                po = None

            if result:
                ans = self._get_analyses()
                if ans:
                    progress = self._open_progress(len(ans))
                    for ai in ans:
                        msg = 'loading {}'.format(ai.record_id)
                        progress.change_message(msg)
                        ai.load_age()
                        progress.increment()

                    func = getattr(self, '_display_{}'.format(name))
                    if func(ans, po):
                        self._display_tabular_data()

#===============================================================================
# 
#===============================================================================
    def _gather_data(self):
        '''
            open a data selector view
            
            by default use a db connection
        '''
        d = self.processing_selector
        return True
#        info = d.edit_traits(kind='livemodal')
#        if info.result:
#            return True

    def _display_tabular_data(self):
        tm = TabularAnalysisManager(analyses=self._get_analyses())
        tm.edit_traits()

    def _display_isochron(self, ans, po):
        rr = self._isochron(ans)
        if rr is not None:
            g, _isochron = rr
            self.open_view(g)
            return True

    def _display_spectrum(self, ans, po):
        rr = self._spectrum(ans, aux_plots=po.get_aux_plots())
        if rr is not None:
            g, _spec = rr
            self.open_view(g)
            return True

    def _display_ideogram(self, ans, po):

        rr = self._ideogram(ans, aux_plots=po.get_aux_plots())
#        rr = ps._ideogram(ans, aux_plots=['analysis_number'], show=False)
        if rr is not None:
            g, ideo = rr
            if self.display_omitted:
                #sort ans by age
                ta = sorted(ans, key=lambda x:x.age)
                #find omitted ans
                sel = [i for i, ai in enumerate(ta) if ai.status != 0]
                ideo.set_excluded_points(sel, 0)

            self._set_window_xy(g)
            self.open_view(g)
            return True

    def _display_series(self, ans, po):
        #open a series manager
        sm = SeriesManager(analyses=ans)
        info = sm.edit_traits(kind='livemodal')
        if info.result:
            if sm.use_single_window:
                pass
            else:
                self._build_series(ans, sm.calculated_values)
                self._build_series(ans, sm.measured_values)
                self._build_series(ans, sm.baseline_values)
                self._build_series(ans, sm.blank_values)

            return True

    def _build_series(self, ans, ss):
        for si in ss:
            if not si.show:
                continue
            s = Series(analyses=ans)
            g = s.build(ans, si)
            self._set_window_xy(g)
            self.open_view(g)

    def _get_analyses(self):
        ps = self.processing_selector
        from src.processing.processing_selector import Marker
        ans = [Analysis(dbrecord=ri) for ri in ps.selected_records if not isinstance(ri, Marker)]
        return ans

    def _set_window_xy(self, obj):
        x = 50
        y = 25
        xoff = 25
        yoff = 25
        obj.window_x = x + xoff * self._window_count
        obj.window_y = y + yoff * self._window_count
        self._window_count += 1
#        do_later(g.edit_traits)

    def _open_progress(self, n):
        pd = MProgressDialog(max=n, size=(550, 15))
        pd.open()
        pd.center()
        return pd

    def _sort_analyses(self):
        self.analyses.sort(key=lambda x:x.age)

#===============================================================================
# plotters
#===============================================================================
    def _window_factory(self):
#        w = self.get_parameter('window', 'width', default=500)
#        h = self.get_parameter('window', 'height', default=600)
#        x = self.get_parameter('window', 'x', default=20)
#        y = self.get_parameter('window', 'y', default=20)
        x, y, w, h = 20, 20, 500, 600
        g = Window(
                   window_width=w,
                   window_height=h,
                   window_x=x, window_y=y
                   )
        self.window = g
        return g

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
        from src.processing.plotters.ideogram import Ideogram


        g = self._window_factory()
        p = Ideogram(db=self.db)
        ps = self._build_aux_plots(aux_plots)
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
#            self._figure = gideo
            g.container.add(gideo)

            if highlight_omitted:
                ta = sorted(analyses, key=lambda x:x.age)
                #find omitted ans
                sel = [i for i, ai in enumerate(ta) if ai.status != 0]
                p.set_excluded_points(sel, 0)

#            if show:
#                g.edit_traits()

            return g, p

    def _spectrum(self, analyses, aux_plots=None):
        from src.processing.plotters.spectrum import Spectrum
        g = self._window_factory()
        spec = Spectrum(db=self.db)

        options = dict(aux_plots=self._build_aux_plots(aux_plots))

        spec_graph = spec.build(analyses, options=options)

        if spec_graph:
            spec_graph, _plots = spec_graph
#            self._figure = spec_graph.plotcontainer
            g.container.add(spec_graph)

            return g, spec

    def _isochron(self, analyses, show=False):
        from src.processing.plotters.inverse_isochron import InverseIsochron
        g = self._window_factory()
        isochron = InverseIsochron(db=self.db)
        graph = isochron.build(analyses)
        if graph:
            self._figure = graph.plotcontainer
            g.container.add(graph.plotcontainer)
            if show:
                g.edit_traits()
            return g, isochron

    def _build_aux_plots(self, aux_plots):
        ps = []
        if aux_plots is None:
            aux_plots = []
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
        return ps

#===============================================================================
# defaults
#===============================================================================
    def _processing_selector_default(self):
        d = ProcessingSelector(db=self.db)
        db = self.db
        db.connect()

        d.select_labnumber([22233, 22234])
        return d

    def _blank_corrections_manager_default(self):
        bm = BlankCorrectionsManager(db=self.db)
        return bm

    def _background_corrections_manager_default(self):
        bm = BackgroundCorrectionsManager(db=self.db)
        return bm
#============= EOF =============================================

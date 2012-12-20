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
#from src.processing.processing_selector import ProcessingSelector
from src.processing.analysis import Analysis
#from src.processing.script import ProcessScript
#from src.constants import NULL_STR
from src.progress_dialog import MProgressDialog
from src.processing.plotter_options_manager import PlotterOptionsManager, \
    IdeogramOptionsManager
from src.processing.window import Window
from src.processing.tabular_analysis_manager import TabularAnalysisManager
from src.processing.plotters.series import Series
from src.processing.corrections.corrections_manager import BlankCorrectionsManager, \
    BackgroundCorrectionsManager, DetectorIntercalibrationCorrectionsManager
from src.processing.search.search_manager import SearchManager
from src.processing.search.selector_manager import SelectorManager
from src.processing.search.selected_view import Marker
from src.processing.search.figure_manager import FigureManager
from src.database.records.isotope_record import IsotopeRecord
import csv
from src.processing.publisher.publisher import  CSVWriter, \
    PDFWriter, MassSpecCSVWriter
from src.processing.series_manager import SeriesManager


class ProcessingManager(DatabaseManager):
    selector_manager = Instance(SelectorManager)
    search_manager = Instance(SearchManager)

    blank_corrections_manager = Instance(BlankCorrectionsManager)
    background_corrections_manager = Instance(BackgroundCorrectionsManager)
    detector_intercalibration_corrections_manager = Instance(DetectorIntercalibrationCorrectionsManager)

    ideogram_options_manager = Instance(IdeogramOptionsManager, ())
    spectrum_plotter_options_manager = Instance(PlotterOptionsManager, ())
    isochron_plotter_options_manager = Instance(PlotterOptionsManager, ())

    figure_manager = Instance(FigureManager)
    figures = List

    only_fusions = Bool(True)
    include_omitted = Bool(True)
    display_omitted = Bool(True)

    _window_count = 0

#===============================================================================
# find/display analysis
#===============================================================================
    def open_search(self):
        ps = self.search_manager
#        ps.selector.load_recent()
        ps.selector.load_last()
        ps.edit_traits()

#===============================================================================
# figures
#===============================================================================
    def _get_active_figure(self):
        figure = next((obj for win, obj in self.figures if win.ui.control.IsActive()), None)
        return figure

    def _get_active_window(self):
        window = next((win for win, obj in self.figures if win.ui.control.IsActive()), None)
        return window

    def open_figures(self):
        fm = self.figure_manager
        fm.edit_traits()

    def save_figure(self):
        fm = self.figure_manager
        figure = self._get_active_figure()
        if figure:
            fm.project_name = figure.analyses[0].project
            info = fm.edit_traits(view='save_view')
            if info.result:
                fm.save_figure(figure)

    def open_figure(self, figure_record):

        ans = [Analysis(isotope_record=IsotopeRecord(_dbrecord=ai)) for ai in figure_record.analyses]

        if ans:
            progress = self._open_progress(len(ans))
            for ai in ans:
                msg = 'loading {}'.format(ai.record_id)
                progress.change_message(msg)
                ai.load_age()
                progress.increment()

            func = getattr(self, '_display_{}'.format(figure_record.kind))
            pom = getattr(self, '{}_options_manager'.format(figure_record.kind))
            po = pom.plotter_options
            if func(ans, po):
                self._display_tabular_data()
#===============================================================================
# export
#===============================================================================
    def export_figure(self):
        '''
            save figure as a pdf
        '''
        win = self._get_active_window()
        print win
        if win:
            from chaco.pdf_graphics_context import PdfPlotGraphicsContext
#            p = self.save_file_dialog()
            p = '/Users/ross/Sandbox/figure_export.pdf'
            if p:
                gc = PdfPlotGraphicsContext(filename=p,
                                              pagesize='letter',
                                              dest_box_units='inch')
                gc.render_component(win.container, valign='center')
                gc.save()
                self.info('saving figure to {}'.format(p))


    def export_figure_table(self, kind='csv'):
        '''
            save a figures analyses as a table
        '''
        grouped_analyses = None
        figure = self._get_active_figure()
        if figure is not None:
            grouped_analyses = figure._get_grouped_analyses()
        else:
            if self._gather_data():
                ans = self._get_analyses()
                group_ids = list(set([a.group_id for a in ans]))

                grouped_analyses = [[ai for ai in ans if ai.group_id == gid]
                                  for gid in group_ids
                                  ]

        if grouped_analyses:
#            p = self.save_file_dialog()
            p = '/Users/ross/Sandbox/figure_export.csv'
            if p:
                if kind == 'csv':
                    klass = CSVWriter
                elif kind == 'pdf':
                    p = '/Users/ross/Sandbox/figure_export.pdf'
                    klass = PDFWriter
                elif kind == 'massspec':
                    klass = MassSpecCSVWriter

                self._export(klass, p, grouped_analyses)
                self.info('exported figure to {}'.format(p))

    def _export(self, klass, p, grouped_analyses):
        pub = klass(filename=p)
        n = len(grouped_analyses)
        for i, ans in enumerate(grouped_analyses):
            pub.add_ideogram_table(ans,
                                   title=i == 0,
                                   header=i == 0,
                                   add_group_marker=i < n - 1)

        pub.publish()

#===============================================================================
# apply corrections
#===============================================================================
    def gather_data(self):
        if self._gather_data():
            return self._get_analyses()

    def apply_blank_correction(self):
        bm = self.blank_corrections_manager
        self._apply_correction(bm)

    def apply_background_correction(self):
        bm = self.background_corrections_manager
        self._apply_correction(bm)

    def apply_detector_intercalibration_correction(self):
        bm = self.detector_intercalibration_corrections_manager
        self._apply_correction(bm)

    def _apply_correction(self, bm):
        if self._gather_data():

            ans = self._get_analyses()
            bm.analyses = ans
            bm.edit_traits()
#            self._load_analyses(ans)
#            info = bm.edit_traits(kind='livemodal')
#            if info.result:
#                bm.apply_correction()

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
#                pom = self.plotter_options_manager
                pom = getattr(self, '{}_options_manager'.format(name))
                po = pom.plotter_options
                info = pom.edit_traits(kind='livemodal')
                result = info.result

            else:
                result = True
                po = None

            if result:
                ans = self._get_analyses()
                if ans:
                    self._load_analyses(ans)
                    func = getattr(self, '_display_{}'.format(name))
                    plotter = func(ans, po)
                    if plotter:
                        self._display_tabular_data(plotter.make_title())

    def _open_figure(self, fig, obj=None):
        self._set_window_xy(fig)
        self.figures.append((fig, obj))
        self.open_view(fig)

    def _load_analyses(self, ans):
        progress = self._open_progress(len(ans))
        for ai in ans:
            msg = 'loading {}'.format(ai.record_id)
            progress.change_message(msg)
            ai.load_age()
            progress.increment()
#===============================================================================
# 
#===============================================================================
    def _gather_data(self):
        '''
            open a data selector view
            
            by default use a db connection
        '''
        d = self.selector_manager
        return True
        info = d.edit_traits(kind='livemodal')
        if info.result:
            return True

    def _display_tabular_data(self, title):


        tm = TabularAnalysisManager(analyses=self._get_analyses(),
                                    db=self.db,
                                    title='Table {}'.format(title)

                                    )
        ui = tm.edit_traits()
        self.add_window(ui)

    def _display_isochron(self, ans, po):
        rr = self._isochron(ans)
        if rr is not None:
            g, isochron = rr
            self._open_figure(g, isochron)
#            self.open_view(g)
            return isochron

    def _display_spectrum(self, ans, po):
        rr = self._spectrum(ans, aux_plots=po.get_aux_plots())
        if rr is not None:
            g, spec = rr
            self._open_figure(g, spec)
#            self.open_view(g)
            return spec

    def _display_ideogram(self, ans, po):

        rr = self._ideogram(ans,
                            aux_plots=po.get_aux_plots(),
                            probability_curve_kind=po.probability_curve_kind,
                            mean_calculation_kind=po.mean_calculation_kind
                            )
#        rr = ps._ideogram(ans, aux_plots=['analysis_number'], show=False)
        if rr is not None:
            g, ideo = rr
            if self.display_omitted:
                #sort ans by age
                ta = sorted(ans, key=lambda x:x.age.nominal_value)
                #find omitted ans
                sel = [i for i, ai in enumerate(ta) if ai.status != 0]
                ideo.set_excluded_points(sel, 0)


            self._open_figure(g, ideo)
#            self.open_view(g)
            return ideo

    def _display_series(self, ans, po):
        #open a series manager
        sm = SeriesManager(analyses=ans)
        info = sm.edit_traits(kind='livemodal')
        if info.result:
            if sm.use_single_window:
                pass
            else:
                s = self._build_series(ans, sm.calculated_values)
                sb = self._build_series(ans, sm.measured_values)
                if s is None:
                    s = sb
                sb = self._build_series(ans, sm.baseline_values)
                if s is None:
                    s = sb
                sb = self._build_series(ans, sm.blank_values)
                if s is None:
                    s = sb

                return s
#            return sm

    def _build_series(self, ans, ss):
        s = None
        for si in ss:
            if not si.show:
                continue
            s = Series(analyses=ans)
            g = s.build(ans, si)
            self._open_figure(g, s)
        return s
#            self._set_window_xy(g)
#            self.open_view(g)

    def _get_analyses(self):
        ps = self.selector_manager
        ans = [Analysis(isotope_record=ri) for ri in ps.selected_records if not isinstance(ri, Marker)]
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
                  probability_curve_kind=None,
                  mean_calculation_kind=None,
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
        p = Ideogram(db=self.db,
                     probability_curve_kind=probability_curve_kind,
                     mean_calculation_kind=mean_calculation_kind
                     )

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
                       display_mean_indicator=display_mean_indicator,
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
    def _selector_manager_default(self):
        db = self.db
        d = SelectorManager(db=db)
        if not db.connected:
            db.connect()

        d.select_labnumber([22233])
        return d

    def _search_manager_default(self):
        db = self.db
        d = SearchManager(db=db)
        if not db.connected:
            db.connect()
        return d

    def _figure_manager_default(self):
        db = self.db
        fm = FigureManager(db=db,
                           processing_manager=self
                           )
        if not db.connected:
            db.connect()
        return fm


    def _blank_corrections_manager_default(self):
        bm = BlankCorrectionsManager(db=self.db,
                                     processing_manager=self
                                     )
        return bm

    def _background_corrections_manager_default(self):
        bm = BackgroundCorrectionsManager(db=self.db,
                                          processing_manager=self)
        return bm

    def _detector_intercalibration_corrections_manager_default(self):
        bm = DetectorIntercalibrationCorrectionsManager(db=self.db,
                                                        processing_manager=self
                                                        )
        return bm

#============= EOF =============================================

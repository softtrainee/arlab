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
from traits.api import Instance, List
#from traitsui.api import View, Item, TableEditor, EnumEditor, HGroup
#import apptools.sweet_pickle as pickle
#============= standard library imports ========================
#import os
#from numpy import array
#============= local library imports  ==========================
from src.processing.database_manager import DatabaseManager
#from src.processing.processing_selector import ProcessingSelector
from src.processing.analysis import Analysis, NonDBAnalysis
#from src.processing.script import ProcessScript
#from src.constants import NULL_STR
#from src.progress_dialog import MProgressDialog
from src.processing.plotter_options_manager import PlotterOptionsManager, \
    IdeogramOptionsManager, SpectrumOptionsManager, IsochronOptionsManager
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
#import csv
from src.processing.publisher.publisher import  CSVWriter, \
    PDFWriter, MassSpecCSVWriter
from src.irradiation.flux_manager import FluxManager
from src.processing.base_analysis_manager import BaseAnalysisManager
from src.processing.series_manager import SeriesManager
from src.processing.project_view import ProjectView
from src.graph.graph import Graph
from src.graph.time_series_graph import TimeSeriesGraph
from src.paths import paths
import csv
from src.helpers.filetools import str_to_bool
from src.processing.manual_entry_manager import ManualEntryManager


class ProcessingManager(DatabaseManager, BaseAnalysisManager):
    selector_manager = Instance(SelectorManager)
    search_manager = Instance(SearchManager)
    project_view = Instance(ProjectView)

    blank_corrections_manager = Instance(BlankCorrectionsManager)
    background_corrections_manager = Instance(BackgroundCorrectionsManager)
    detector_intercalibration_corrections_manager = Instance(DetectorIntercalibrationCorrectionsManager)

    ideogram_options_manager = Instance(IdeogramOptionsManager, ())
    spectrum_options_manager = Instance(SpectrumOptionsManager, ())
    isochron_options_manager = Instance(IsochronOptionsManager, ())
#    spectrum_plotter_options_manager = Instance(PlotterOptionsManager, ())
#    isochron_plotter_options_manager = Instance(PlotterOptionsManager, ())

    figure_manager = Instance(FigureManager)
    figures = List

    _window_count = 0

    def open_project_view(self):
        if self.db.connect():
            pv = self.project_view
            self.open_view(pv)
            pv.on_trait_change(self._open_sample_ideogram, 'update_selected_sample')


#===============================================================================
# flux
#===============================================================================
    def calculate_flux(self):
        '''
            1. select tray to calculate flux
                decide which monitor age to use
            2. find flux monitors 
            3. fit plane to flux monitors
            4. apply to unknowns
        '''
        if self.db.connect():
            fm = FluxManager(db=self.db)
            fm.edit_traits()


#===============================================================================
# find/display analysis
#===============================================================================
    def open_search(self):
        if self.db.connect():
            ps = self.search_manager
    #        ps.selector.load_recent()
            ps.selector.load_last(n=20)
            self.open_view(ps)

#===============================================================================
# figures
#===============================================================================
    def open_figures(self):
        fm = self.figure_manager
        fm.edit_traits()

    def save_figure(self):
        fm = self.figure_manager
        figure = self._get_active_plotter()
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
    def export_figure(self, kind='pdf'):
        '''
            save figure as a pdf
        '''
        win = self._get_active_window()
        if win:
            from chaco.pdf_graphics_context import PdfPlotGraphicsContext
            p = self.save_file_dialog()
#            p = '/Users/ross/Sandbox/figure_export.pdf'
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
        figure = self._get_active_plotter()
        if figure is not None:
            grouped_analyses = figure._get_grouped_analyses()
        else:
            if self._gather_data():
                ans = self._get_analyses()
                self._load_analyses(ans)
                group_ids = list(set([a.group_id for a in ans]))

                grouped_analyses = [[ai for ai in ans if ai.group_id == gid]
                                  for gid in group_ids
                                  ]

        if grouped_analyses:
            p = self.save_file_dialog()
#            p = '/Users/ross/Sandbox/figure_export.csv'
            if p:
                if kind == 'csv':
                    klass = CSVWriter
                elif kind == 'pdf':
#                    p = '/Users/ross/Sandbox/figure_export.pdf'
                    klass = PDFWriter
                elif kind == 'massspec':
                    klass = MassSpecCSVWriter

                self._export(klass, p, grouped_analyses)
                self.info('exported figure to {}'.format(p))



#===============================================================================
# tables
#===============================================================================
    def open_table(self):
        if self._gather_data():
            ans = self._get_analyses()
            self._load_analyses(ans)

            tm = TabularAnalysisManager(analyses=ans,
                                        db=self.db)
            self.open_view(tm)

    def gather_data(self):
        if self._gather_data():
            return self._get_analyses()

    def edit_analyses(self):
        sm = self.selector_manager
        info = sm.edit_traits(kind='livemodal')
        if info.result:
            analyses = self._get_analyses()
            title = self._make_title(analyses)

            plotter = self._get_active_plotter()
            if plotter:
                plotter.options['title'] = title
                plotter.build(analyses, new_container=False)

            table = self._get_active_table()
            if table:
                table.set_title(title)
                table.analyses = analyses

#===============================================================================
# apply corrections
#===============================================================================
    def apply_blank_correction(self):
        bm = self.blank_corrections_manager
        self._apply_correction(bm)

    def apply_background_correction(self):
        bm = self.background_corrections_manager
        self._apply_correction(bm)

    def apply_detector_intercalibration_correction(self):
        bm = self.detector_intercalibration_corrections_manager
        self._apply_correction(bm)



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

#===============================================================================
# private
#===============================================================================
    def _apply_correction(self, bm):
        if self._gather_data():

            ans = self._get_analyses()
            bm.analyses = ans
            self.open_view(bm)

#            self._load_analyses(ans)
#            info = bm.edit_traits(kind='livemodal')
#            if info.result:
#                bm.apply_correction()
    def _open_sample_ideogram(self, new):
        pv = self.project_view
        ans = pv.get_filtered_analyses()
        if ans:
            po = pv.plotter_options

            self._load_analyses(ans)
            ideo = self._display_ideogram(ans, po, pv.highlight_omitted)
            self._display_tabular_data(ans, ideo.make_title())

    def _get_active_window(self):
        return self._get_active_item(0)

    def _get_active_plotter(self):
        return self._get_active_item(1)

    def _get_active_table(self):
        return self._get_active_item(2)

    def _get_active_item(self, ind):
        args = next(((win, plotter, table) for win, plotter, table in self.figures
                       if win.ui.control.IsActive()), None)
        if args:
            return args[ind]

    def _export(self, klass, p, grouped_analyses):
        pub = klass(filename=p)
        n = len(grouped_analyses)
        for i, ans in enumerate(grouped_analyses):

            canceled = pub.add_ideogram_table(ans,
                                   configure_table=i == 0,
                                   add_title=i == 0,
                                   add_header=i == 0,
                                   add_group_marker=i < n - 1)
            if canceled:
                break
        else:
            pub.publish()

    def _new_figure(self, name):
        '''
            ask for data and plot option
            ask for plot options first
        '''
        if name != 'series':
#                pom = self.plotter_options_manager
            pom = getattr(self, '{}_options_manager'.format(name))
            po = pom.plotter_options
            info = pom.edit_traits(kind='livemodal')
            result = info.result
            data_type = po.data_type
            if data_type is None:
                data_type = 'database'
        else:
            result = True
            po = None
            data_type = 'database'

        if result:
            if data_type in ['database', 'data_file']:
                use_db_or_path = self._gather_data(data_type)
                if use_db_or_path is not None:
                    ans = self._get_analyses(use_db_or_path)
                    if ans:
                        self._load_analyses(ans)
                        if po and po.title != '' and not po.auto_generate_title:
                            title = po.title
                        else:
                            title = self._make_title(ans)

                        func = getattr(self, '_display_{}'.format(name))
                        func(ans, po, title, data_type=data_type)
            elif name == 'ideogram':
                #open manual entry plotter
                mep = ManualEntryManager(processing_manager=self,
                                         plotter_options_manager=pom
                                         )
                mep.update = True
                self.open_view(mep)


    def _open_figure(self, fig, obj=None, table=None):
        self._set_window_xy(fig)
        self.figures.append((fig, obj, table))
        self.open_view(fig)

#===============================================================================
# 
#===============================================================================
    def _gather_data(self, data_type):
        '''
            open a data selector view
            
            by default use a db connection
            returns database for database entry
                    path for data_file
                    
        '''
#        return True
        if data_type == 'database':
            d = self.selector_manager
            if self.db.connect():
                info = d.edit_traits(kind='livemodal')
                if info.result:
                    return True
        elif data_type == 'data_file':
            if self.confirmation_dialog('''Select a file with the following format. (Include first Line)
            
identifier, age, error
1000,10.0, 0.1
1001,10.0, 0.1
g
2001,10.0, 0.1
2002,10.0, 0.1
Use 'g' to separate groups''', title='Select a DataFile'):
                p = self.open_file_dialog(default_directory=paths.data_dir)
                return p

    def _display_tabular_data(self, ans, title, associated_window=None):


        tm = TabularAnalysisManager(db=self.db)
        tm.set_analyses(ans)
        tm.set_title(title)
        self.open_view(tm)
        return tm

    def _display_isochron(self, ans, po, title, data_type='database'):
        rr = self._isochron(ans)
        if rr is not None:
            g, isochron = rr
            return self._display_figure_and_table(g, isochron, data_type, ans, title)

#            self._display_tabular_data(ans, title)
#            self._open_figure(g, isochron)
#            return isochron

    def _display_spectrum(self, ans, po, title, data_type='database'):
        rr = self._spectrum(ans, po)
        if rr is not None:
            g, spec = rr
            return self._display_figure_and_table(g, spec, data_type, ans, title)

    def _display_ideogram(self, ans, po, title, highlight_omitted=True, data_type='database'):
        rr = self._ideogram(ans,
                            po,
                            title=title,
                            highlight_omitted=highlight_omitted,
#                            aux_plots=po.get_aux_plots(),
                            probability_curve_kind=po.probability_curve_kind,
                            mean_calculation_kind=po.mean_calculation_kind
                            )
        if rr is not None:
            g, ideo = rr
            return self._display_figure_and_table(g, ideo, data_type, ans, title)

    def _display_figure_and_table(self, g, fig, data_type, ans, title):
        table = None
        if data_type == 'database':
            table = self._display_tabular_data(ans, title)

        self._open_figure(g, fig, table=table)
        if table is not None:
            g.associated_windows.append(table)

        return fig

    def _display_series(self, ans, po, title):
        #open a series manager
        sm = SeriesManager(analyses=ans)
        info = sm.edit_traits(kind='livemodal')
        if info.result:
            if sm.use_single_window:
                pass
            else:
                self._display_tabular_data(ans, title)

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

                self._build_peak_center_series(ans, sm.peak_center_option)


#                return s
#            return sm
#    def _calculate_window_xy(self, i, cnt, offsetcnt,
#                             xstep=0.25, ystep=0.2, xstart=0.25, ystart=0.25):
    def _increment_window_xy(self, wx, wy, cnt, xstep=0.025, ystep=0.025, ystart=0.25):
        wx += xstep
        wy += ystep
        if wy > 0.6:
            wy = ystart + cnt * ystep / 4.0
            cnt += 1

        return wx, wy, cnt

    def _build_peak_center_series(self, ans, options):
        if options.plot_centers:
            g = TimeSeriesGraph(container_dict=dict(padding=5))
            g.new_plot(xtitle='Time',
                       ytitle='Peak Center (DAC)')
            xs, ys = zip(*[(ai.timestamp, ai.peak_center_dac) for ai in ans])

            g.new_series(xs, ys, type='scatter', marker='circle', marker_size=2)
            self.open_view(g)
        elif options.plot_scans:
            if options.overlay:
                g = Graph(container_dict=dict(padding=5))
#                import numpy as np
                g.new_plot(xtitle='DAC', ytitle='Intensity')
                for ai in ans:
                    args = ai._get_peakcenter()
                    if args:
                        x, y, c = args[0], args[1], args[2]
                        g.new_series(x, y)
                        g.add_vertical_rule(c)
                self.open_view(g)
            else:
#                import numpy as np
                wx, wy, cnt = 0.25, 0.25, 1
                for i, ai in enumerate(ans):
                    args = ai._get_peakcenter()
#                    x = np.linspace(0, 10, 100)
#                    y = -(x - 5) ** 2
#                    c = np.random.random() * 10
                    args = x, y, c
                    if args:
                        x, y, c = args[0], args[1], args[2]
                        if i > 0:
                            wx, wy, cnt = self._increment_window_xy(wx, wy, cnt, ystart=0.25)

                        g = Graph(container_dict=dict(padding=5),
                                  window_x=wx,
                                  window_y=wy,
                                  window_title=str(i)
                                  )
                        g.new_plot(xtitle='DAC', ytitle='Intensity')
                        g.new_series(x, y)
                        g.add_vertical_rule(c)
                    self.open_view(g)


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

    def _get_analyses(self, use_db_or_path):
        if isinstance(use_db_or_path, bool):
            ps = self.selector_manager
            ans = [Analysis(isotope_record=ri.clone_traits()) for ri in ps.selected_records if not isinstance(ri, Marker)]
        else:
            ans = self._parse_data_file(use_db_or_path)
            if isinstance(ans, str):
                self.warning_dialog('Invalid file. {}'.format(ans))
                return

        return ans

    def _parse_data_file(self, path):

        with open(path, 'U') as fp:
            reader = csv.reader(fp)
            header = reader.next()
            header = map(str.lower, header)
            header = map(str.strip, header)
            try:
                age_index = header.index('age')
                error_index = header.index('error')
                identifier_index = header.index('identifier')
            except ValueError, e:
                return str(e).replace('is not in list', 'is not in header line {}'.format(','.join(header)))

            ans = []
            group_id = 0
            for line in reader:
#                status = str_to_bool(line[status_index])
#                if status:
                if line[0].strip().lower() == 'g':
                    group_id += 1
                    continue

                record_id = line[identifier_index]
                try:
                    age = float(line[age_index])
                except ValueError:
                    return 'Invalid age value {}'.format(line[age_index])
                try:
                    error = float(line[error_index])
                except ValueError:
                    return 'Invalid age value {}'.format(line[age_index])

                ai = NonDBAnalysis(record_id=record_id,
                                   analysis_type='unknown',
                                   age=(age, error),
                                   group_id=group_id
                                   )
                ans.append(ai)
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

    def _sort_analyses(self):
        self.analyses.sort(key=lambda x:x.age)

#===============================================================================
# figures
#===============================================================================
    def _window_factory(self):
#        w = self.get_parameter('window', 'width', default=500)
#        h = self.get_parameter('window', 'height', default=600)
#        x = self.get_parameter('window', 'x', default=20)
#        y = self.get_parameter('window', 'y', default=20)
        x, y, w, h = 20, 20, 500, 600
        g = Window(
                   manager=self,
                   window_width=w,
                   window_height=h,
                   window_x=x, window_y=y
                   )
        self.window = g
        return g

    def _ideogram(self, analyses,
                  plotter_options,
                  probability_curve_kind='cumulative',
                  mean_calculation_kind='weighted_mean',
#                  aux_plots=None,
                  title=None,
#                  xtick_font=None,
#                  xtitle_font=None,
#                  ytick_font=None,
#                  ytitle_font=None,
                  data_label_font=None,
                  metadata_label_font=None,
                  highlight_omitted=True,
                  display_mean_indicator=True,
                  display_mean_text=True
                  ):
        '''
        '''
        from src.processing.plotters.ideogram import Ideogram

        g = self._window_factory()
        p = Ideogram(db=self.db,
                     processing_manager=self,
                     probability_curve_kind=probability_curve_kind,
                     mean_calculation_kind=mean_calculation_kind
                     )

#        ps = self._build_aux_plots(plotter_options.get_aux_plots())
        options = dict(
#                       aux_plots=ps,
#                       use_centered_range=plotter_options.use_centered_range,
#                       centered_range=plotter_options.centered_range,
#                       xmin=plotter_options.xmin,
#                       xmax=plotter_options.xmax,
#                       xtitle_font=xtitle_font,
#                       xtick_font=xtick_font,
#                       ytitle_font=ytitle_font,
#                       ytick_font=ytick_font,
                       data_label_font=data_label_font,
                       metadata_label_font=metadata_label_font,
                       title=title,
                       display_mean_text=display_mean_text,
                       display_mean_indicator=display_mean_indicator,
                       )

        gideo = p.build(analyses, options=options, plotter_options=plotter_options)
        if gideo:
            gideo, _plots = gideo
            g.container.add(gideo)

            if highlight_omitted:
                ta = sorted(analyses, key=lambda x:x.age)
                #find omitted ans
                sel = [i for i, ai in enumerate(ta) if ai.status != 0]
                p.set_excluded_points(sel, 0)

            return g, p

    def _spectrum(self, analyses, plotter_options):
        from src.processing.plotters.spectrum import Spectrum
        g = self._window_factory()
        spec = Spectrum(db=self.db)

#        options = dict(aux_plots=self._build_aux_plots(aux_plots))

        spec_graph = spec.build(analyses, plotter_options=plotter_options)

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


#    def make_title(self, analyses=None):
#        if analyses is None:
#            analyses = self.analyses
#        return self._make_title(analyses)

    def _make_title(self, analyses):
        def make_bounds(gi, sep='-'):
            if len(gi) > 1:
                m = '{}{}{}'.format(gi[0], sep, gi[-1])
            else:
                m = '{}'.format(gi[0])

            return m

        def make_step_bounds(si):
            if not si:
                return
            grps = []
            a = si[0]
            pa = si[1]
            cgrp = [pa]
            for xi in si[2:]:
                if ord(pa) + 1 == ord(xi):
                    cgrp.append(xi)
                else:
                    grps.append(cgrp)
                    cgrp = [xi]
                pa = xi

            grps.append(cgrp)
            return ','.join(['{}{}'.format(a, make_bounds(gi, sep='...')) for gi in grps])

        def _make_group_title(ans):
            lns = dict()
            for ai in ans:
    #            v = '{}{}'.format(ai.aliquot, ai.step)
                v = (ai.aliquot, ai.step)
                if ai.labnumber in lns:
                    lns[ai.labnumber].append(v)
                else:
                    lns[ai.labnumber] = [v]

            skeys = sorted(lns.keys())
            grps = []
            for si in skeys:
                als = lns[si]
                sals = sorted(als, key=lambda x: x[0])
                aliquots, steps = zip(*sals)

                pa = aliquots[0]
                ggrps = []
                cgrp = [pa]
                sgrp = []
                sgrps = []

                for xi, sti in zip(aliquots[1:], steps[1:]):
                    #handle analyses with steps
                    if sti != '':
                        if not sgrp:
                            sgrp.append(xi)
                        elif sgrp[0] != xi:
                            sgrps.append(sgrp)
                            sgrp = [xi]
                        sgrp.append(sti)
                    else:
                        if sgrp:
                            sgrps.append(sgrp)
                            sgrp = []

                        if pa + 1 == xi:
                            cgrp.append(xi)
                        else:
                            ggrps.append(cgrp)
                            cgrp = [xi]

                    pa = xi

                sgrps.append(sgrp)
                ggrps.append(cgrp)
                fs = [make_bounds(gi) for gi in ggrps]

                if sgrps[0]:
                    #handle steps
                    pa = sgrps[0][0]
                    ggrps = []
                    cgrp = [sgrps[0]]
                    for sgi in sgrps[1:]:
                        if pa + 1 == sgi[0]:
                            cgrp.append(sgi)
                        else:
                            grps.append(cgrp)
                            cgrp = [sgi]
                        pa = sgi[0]
                    ggrps.append(cgrp)
                    ss = ['{}-{}'.format(make_step_bounds(gi[0]),
                            make_step_bounds(gi[-1])) for gi in ggrps]
                    fs.extend(ss)

                als = ','.join(fs)

                grps.append('{}-({})'.format(si, als))

            return ', '.join(grps)

        group_ids = list(set([a.group_id for a in analyses]))
        gtitles = []
        for gid in group_ids:
            anss = [ai for ai in analyses if ai.group_id == gid]
            gtitles.append(_make_group_title(anss))

        return ', '.join(gtitles)
#===============================================================================
# defaults
#===============================================================================
    def _selector_manager_default(self):
        db = self.db
        d = SelectorManager(db=db)
#        if not db.connected:
#            db.connect()

#        d.select_labnumber([61541])
#        d.select_labnumber([22233])
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
                                                        processing_manager=self,
                                                        )
        return bm

    def _project_view_default(self):
        pv = ProjectView(db=self.db)
        return pv

#============= EOF =============================================

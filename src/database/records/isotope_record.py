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
from traits.api import HasTraits, Instance, Property, List, Any, cached_property, \
    Event
from traitsui.api import View, Item, HGroup, ListStrEditor
from src.graph.graph import Graph
from src.database.isotope_analysis.fit_selector import FitSelector
from src.graph.regression_graph import StackedRegressionGraph
from src.graph.stacked_graph import StackedGraph
from src.database.records.database_record import DatabaseRecord
from src.database.isotope_analysis.analysis_summary import AnalysisSummary
from src.experiment.identifier import convert_shortname, convert_labnumber
from src.database.isotope_analysis.blanks_summary import BlanksSummary
from pyface.timer.do_later import do_later
from src.database.isotope_analysis.detector_intercalibration_summary import DetectorIntercalibrationSummary
#============= standard library imports ========================
#============= local library imports  ==========================

class EditableGraph(HasTraits):
    graph = Instance(Graph)
    fit_selector = Instance(FitSelector)

    def __getattr__(self, attr):
        try:
            return getattr(self.graph, attr)
        except KeyError:
            pass

    def traits_view(self):
        v = View(Item('graph', show_label=False, style='custom',
                      height=0.6
                      ),

                 Item('fit_selector', show_label=False, style='custom',
                      height=0.4
                      ))

        return v

class IsotopeRecord(DatabaseRecord):
    title_str = 'Analysis'
    window_height = 650
    window_width = 875
    color = 'black'

    sniff_graph = Instance(Graph)
    signal_graph = Instance(EditableGraph)
    baseline_graph = Instance(EditableGraph)
    peak_center_graph = Instance(Graph)
    peak_hop_graphs = List
#    fit_selector = Instance(FitSelector)

    detector_intercalibration_summary = Property
    analysis_summary = Property
#    categories = List(['summary', 'signal', 'sniff', 'baseline', 'peak center' ])
    categories = List(['summary', ])#'signal', 'sniff', 'baseline', 'peak center' ])
    selected = Any('signal')
    display_item = Instance(HasTraits)

#    det_keys = None
#    iso_keys = None
#    signals = None
#    fits = None
    isos = None
#    signals = None
#    baselines = None

    labnumber = Property
    shortname = Property
    analysis_type = Property
    aliquot = Property
    mass_spectrometer = Property

    changed = Event
#    analysis_summary = Instance(AnalysisSummary)



#===============================================================================
# viewable
#===============================================================================
    def opened(self):
        super(IsotopeRecord, self).opened()
        def d():
#            self.selected = None
            self.selected = 'summary'
        do_later(d)

    def closed(self, isok):
        self.selected = None


#    def clear(self):
#        self.baselines = dict()
#        self.categories = ['summary']

#    def get_peakhop_graphs(self):
#        return [getattr(self, tr) for tr in self.traits()
#                    if tr.endswith('_graph') and
#                        not tr in ['signal_graph', 'sniff_graph', 'baseline_graph',
#                              'peak_center_graph'
#                              ]]





#    def _get_peakhop_signals(self, dm):
#        return self._get_table_data(dm, grp)
#        return self._get_peakhop(dm, 'signals')

#    def _get_peakhop_baselines(self, dm):
#        return self._get_peakhop(dm, 'baselines')

#    def _get_peakhop(self, dm, name):
#        grp = dm.get_group('peakhop_{}'.format(name))
#        peakhops = dict()
#        if grp is not None:
#            for di in dm.get_groups(grp):
#                peakhop = dict()
#                for ti in dm.get_tables(di):
#                    data = zip(*[(r['time'], r['value']) for r in ti.iterrows()])
#                    try:
#                        fit = ti.attrs.fit
#                    except AttributeError:
#                        fit = None
#                    peakhop[ti._v_name] = [di._v_name, ti._v_name, fit, data]
#    #                p[ti._v_nam] = [ti._v_name, fit, data]
#                peakhops[di._v_name] = peakhop
#
#        return peakhops

#    def _get_sniffs(self, dm):
#        return self._get_table_data(dm, 'sniffs')
#
#    def _get_baselines(self, dm):
#        return self._get_table_data(dm, 'baselines')
#===============================================================================
# database record
#===============================================================================
    def load_graph(self, graph=None, xoffset=0):

#        self.fits = dict()
#        self.signals = dict()
#        self.baselines = dict()

#        self.clear()

        dm = self.selector.data_manager
        signals = self._get_table_data(dm, 'signals')
        if signals:

            self.categories.append('signal')
            graph = self._load_stacked_graph(signals)

#            for iso, rs in zip(self.isos, graph.regressors):
#                self.signals[iso] = (rs.coefficients[-1], rs.coefficient_errors[-1])

            self.signal_graph = EditableGraph(graph=graph)
            self.signal_graph.fit_selector = FitSelector(analysis=self,
                                                         name='Signal',
                                                         graph=self.signal_graph)
#            self.signal_graph = graph

        sniffs = self._get_table_data(dm, 'sniffs')
        if sniffs:
            self.categories.append('sniff')
            graph = self._load_stacked_graph(sniffs, regress=False)
            self.sniff_graph = EditableGraph(graph=graph)
            self.sniff_graph.fit_selector = FitSelector(analysis=self, graph=self.sniff_graph)

        baselines = self._get_table_data(dm, 'baselines')
        if baselines:
            self.categories.append('baseline')
            graph = self._load_stacked_graph(baselines)
#            for iso, rs in zip(self.isos, graph.regressors):
#                self.baselines[iso] = (rs.coefficients[-1], rs.coefficient_errors[-1])

            self.baseline_graph = EditableGraph(graph=graph)
            self.baseline_graph.fit_selector = FitSelector(analysis=self,
                                                           name='Baseline',
                                                           graph=self.baseline_graph)

        peakcenter = self._get_peakcenter(dm)
        if peakcenter:
            self.categories.append('peak center')
            graph = self._load_peak_center_graph(peakcenter)
            self.peak_center_graph = graph

        blanks = self._get_blanks()
        if blanks:
            self.categories.append('blanks')

        backgrounds = self._get_backgrounds()
        if backgrounds:
            self.categories.append('backgrounds')

        det_intercals = self._get_detector_intercalibrations()
        if det_intercals:
            self.categories.append('Det. Intercal.')

#        self.fit_selector = Analyzer(analysis=self)
#        self.categories.append('Analyzer')

        self.selected = 'summary'
#        self.selected = 'blanks'
#        self.fit_selector.fits = [AnalysisParams(fit='linear', name=k) for k in keys]
#===============================================================================
# private
#===============================================================================
    def __getattr__(self, attr):
        try:
            return getattr(self._dbrecord, attr)
        except AttributeError, e:
            print attr


    def _get_detector_intercalibrations(self):
        ds = self._dbrecord.detector_intercalibration_histories
        return ds

    def _get_blanks(self):
        bhs = self._dbrecord.blanks_histories
        return bhs

    def _get_backgrounds(self):
        bhs = self._dbrecord.backgrounds_histories
        return bhs

    def _get_peakcenter(self, dm):

        ti = dm.get_table('peakcenter', '/')
        if ti is not None:
            try:
                center = ti.attrs.center_dac
            except AttributeError:
                center = 0

            try:
                pcsignals = [ti.attrs.low_signal, ti.attrs.high_signal]
                pcdacs = [ti.attrs.low_dac, ti.attrs.high_dac]
            except AttributeError:
                pcsignals = []
                pcdacs = []

            return ([(r['time'], r['value']) for r in  ti.iterrows()], center, pcdacs, pcsignals)

    def _get_table_data(self, dm, grp):
        ds = dict()
        try:
            isogrps = dm.get_groups(grp)
        except Exception, e:
            print 'get table data', e
            return

        for ig in isogrps:
            for ti in dm.get_tables(ig):
                name = ti.name
                data = zip(*[(r['time'], r['value']) for r in ti.iterrows()])

                iso = ig._v_name
                try:
                    iso = ti.attrs.isotope
                except AttributeError:
                    pass

                fit = None
                try:
                    fit = ti.attrs.fit
                except AttributeError, e:
                    pass
#                print 'nn', name, ig._v_name
                ds[name] = [ti._v_name, iso, fit, data]

        return ds
    def _load_stacked_graph(self, data, det=None, regress=True):
        if regress:
#            klass = StackedTimeSeriesRegressionGraph
#            klass = StackedRegressionTimeSeriesGraph
            klass = StackedRegressionGraph
        else:
            klass = StackedGraph

        graph = self._graph_factory(klass, width=700)
        gkw = dict(padding=[50, 50, 5, 40])

        isos = [vi[1] for vi in data.itervalues()]
        isos = sorted(isos, key=lambda k: int(k[2:]))
        self.isos = isos

        def get_data(k):
            try:
                return data[k]
            except KeyError:
                return next((di for di in data.itervalues() if di[1] == k), None)

        i = 0
#        for i, iso in enumerate(isos):
        for iso in isos:
            try:
                di, _iso, fi, (xs, ys) = get_data(iso)
            except ValueError:
                continue

            gkw['ytitle'] = '{} ({})'.format(di if det is None else det, iso)
            gkw['xtitle'] = 'Time (s)'
            skw = dict()
            if regress:
                skw['fit'] = fi

            graph.new_plot(**gkw)
            graph.new_series(xs, ys, plotid=i,
                             type='scatter', marker='circle',
                             marker_size=1.25,
                             **skw)
#            graph.set_series_label(key, plotid=i)
            ma = max(xs)

            graph.suppress_regression = iso != isos[-1]
            graph.set_x_limits(min=0, max=ma, plotid=i)
            graph.suppress_regression = False

            params = dict(orientation='right' if i % 2 else 'left',
                          axis_line_visible=False
                          )

            graph.set_axis_traits(i, 'y', **params)
            i += 1

        return graph

    def _load_peak_center_graph(self, data):
        xs = []
        ys = []
        if data:
            xsys, center_dac, pcdacs, pcsignals = data
            xs, ys = zip(*xsys)

        graph = self._graph_factory()
        graph.container_dict = dict(padding=[10, 0, 30, 10])
        graph.clear()

        title = ''
        graph.new_plot(title='{}'.format(title),
                       xtitle='DAC (V)',
                       ytitle='Intensity (fA)',
                       )

        graph.new_series(
                         x=xs, y=ys,
                         type='scatter', marker='circle',
                         marker_size=1.25
                         )
        graph.new_series(
                         x=pcdacs,
                         y=pcsignals,
                         type='scatter', marker='circle',
                         marker_size=2
                         )
        graph.add_vertical_rule(center_dac)

#        graph.plots[0].value_range.tight_bounds = False
        if xs:
            graph.set_x_limits(min=min(xs), max=max(xs))
        return graph

#===============================================================================
# handlers
#===============================================================================
    def _selected_changed(self):
        selected = self.selected
        if selected is not None:

            selected = selected.replace(' ', '_')
            selected = selected.lower()

            if selected == 'summary':
                item = self.analysis_summary
                item.refresh()

            elif selected == 'blanks':
                item = BlanksSummary(record=self)
            elif selected == 'det._intercal.':
                item = self.detector_intercalibration_summary
#                item = DetectorIntercalibrationSummary(record=self)
            else:
                item = getattr(self, '{}_graph'.format(selected))

            self.trait_set(display_item=item)
#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_analysis_summary(self):
        fs = FitSelector(analysis=self,
                         graph=self.signal_graph,
                         name='Signal'
                         )

        item = AnalysisSummary(record=self,
                               fit_selector=fs
                               )
        fs.on_trait_change(item.refresh, 'fits:fit, fits:filterstr')
        return item

    def _apply_history_change(self, new):
        self.changed = True

    @cached_property
    def _get_detector_intercalibration_summary(self):
        di = DetectorIntercalibrationSummary(record=self)
        di.on_trait_change(self._apply_history_change, 'history_view.applied_history')

        return di

    @cached_property
    def _get_record_id(self):
        return '{}-{}'.format(self.labnumber, self.aliquot)

    @cached_property
    def _get_labnumber(self):
#        print 'get aasfd', self._dbrecord.labnumber

        ln = self._dbrecord.labnumber.labnumber
        ln = convert_labnumber(ln)
#        ln = '{}-{}'.format(ln, self.aliquot)
        return ln

    @cached_property
    def _get_shortname(self):
#        print 'get aasfd'
        ln = self._dbrecord.labnumber.labnumber
        ln = convert_shortname(ln)

        ln = '{}-{}'.format(ln, self.aliquot)
        return ln

    @cached_property
    def _get_analysis_type(self):
        return self._dbrecord.measurement.analysis_type.name

    @cached_property
    def _get_aliquot(self):
        return self._dbrecord.labnumber.aliquot

    @cached_property
    def _get_mass_spectrometer(self):
        return self._dbrecord.measurement.mass_spectrometer.name.lower()

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        info = self._get_info_grp()
        info.label = 'Info'
        grp = HGroup(
                        Item('categories', editor=ListStrEditor(
                                                                editable=False,
                                                                operations=[],
                                                                selected='selected'
                                                                ),
                             show_label=False,
                             width=0.10
                             ),
                        Item('display_item', show_label=False, style='custom'),
                        )

        return self._view_factory(grp)

#============= EOF =============================================

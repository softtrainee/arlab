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
    Event, Float, Dict
from traitsui.api import View, Item, HGroup, ListStrEditor

#============= standard library imports ========================
from uncertainties import ufloat
import re
import struct
#============= local library imports  ==========================
from src.database.isotope_analysis.blanks_summary import BlanksSummary
from src.graph.graph import Graph
from src.database.isotope_analysis.fit_selector import FitSelector
from src.graph.regression_graph import StackedRegressionGraph
from src.graph.stacked_graph import StackedGraph
from src.database.records.database_record import DatabaseRecord
from src.database.isotope_analysis.analysis_summary import AnalysisSummary
from src.experiment.utilities.identifier import convert_shortname, convert_labnumber, \
    make_runid
from src.database.isotope_analysis.detector_intercalibration_summary import DetectorIntercalibrationSummary
from src.database.isotope_analysis.irradiation_summary import IrradiationSummary
from src.deprecate import deprecated
from src.constants import NULL_STR
from src.database.isotope_analysis.supplemental_summary import SupplementalSummary

import time
from src.database.isotope_analysis.script_summary import MeasurementSummary, \
    ExtractionSummary, ExperimentSummary
from src.database.isotope_analysis.backgrounds_summary import BackgroundsSummary
from src.database.isotope_analysis.notes_summary import NotesSummary
from src.processing.arar_age import ArArAge
from src.processing.isotope import Isotope, Blank, Background, Baseline
from src.database.isotope_analysis.errro_component_summary import ErrorComponentSummary
# from src.database.records.isotope import Isotope, Baseline, Blank, Background

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
                      height=0.75
                      ),

                 Item('fit_selector', show_label=False, style='custom',
                      height=0.25
                      ))

        return v

class IsotopeRecordView(HasTraits):
    group_id = 0
    graph_id = 0
    mass_spectrometer = ''
    analysis_type = ''

    def create(self, dbrecord):
        try:
            self.labnumber = str(dbrecord.labnumber.labnumber)
            self.aliquot = dbrecord.aliquot
            self.step = dbrecord.step
    #        self.aliquot = '{}{}'.format(dbrecord.aliquot, dbrecord.step)
            self.timestamp = dbrecord.analysis_timestamp

            irp = dbrecord.labnumber.irradiation_position
            if irp is not None:
                irl = irp.level
                ir = irl.irradiation
                self.irradiation_info = '{}{} {}'.format(ir.name, irl.name, irp.position)
            else:
                self.irradiation_info = ''
    #        self.mass_spectrometer = ''
    #        self.analysis_type = ''
            meas = dbrecord.measurement
            if meas is not None:
                self.mass_spectrometer = meas.mass_spectrometer.name.lower()
                self.analysis_type = meas.analysis_type.name

            self.uuid = dbrecord.uuid
            self.record_id = make_runid(self.labnumber, self.aliquot, self.step)
            return True
        except Exception, e:
            print e

    def to_string(self):
        return '{} {} {} {}'.format(self.labnumber, self.aliquot, self.timestamp, self.uuid)

class IsotopeRecord(DatabaseRecord, ArArAge):
    title_str = 'Analysis'
    window_height = 800
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
    irradiation_summary = Property
    supplemental_summary = Property
    measurement_summary = Property
    extraction_summary = Property
    experiment_summary = Property
    blanks_summary = Property
    backgrounds_summary = Property
    notes_summary = Property
    error_summary = Property

    categories = List(['summary', 'irradiation',
                       'error',
                       'supplemental', 'measurement', 'extraction', 'experiment',
                       'notes',
                       'signal', 'baseline'
                       ])
    selected = Any
    display_item = Instance(HasTraits)

    sample = Property(depends_on='_dbrecord')
    material = Property(depends_on='_dbrecord')
    labnumber = Property(depends_on='_dbrecord')
    project = Property(depends_on='_dbrecord')
    shortname = Property(depends_on='_dbrecord')
    analysis_type = Property(depends_on='_dbrecord')
    aliquot = Property(depends_on='_dbrecord')
    step = Property(depends_on='_dbrecord')
    mass_spectrometer = Property(depends_on='_dbrecord')

    position = Property(depends_on='_dbrecord')
    extract_device = Property(depends_on='_dbrecord')
    extract_value = Property(depends_on='_dbrecord')
    extract_units = Property(depends_on='_dbrecord')
    extract_duration = Property(depends_on='_dbrecord')
    cleanup_duration = Property(depends_on='_dbrecord')
    experiment = Property(depends_on='_dbrecord')
    extraction = Property(depends_on='_dbrecord')
    measurement = Property(depends_on='_dbrecord')

    changed = Event

    ic_factor = Property(depends_on='_dbrecord')
    irradiation = Property(depends_on='_dbrecord')

    status = Property(depends_on='_dbrecord')
    uuid = Property(depends_on='_dbrecord')

    peak_center_dac = Property(depends_on='_dbrecord')

    item_width = 760

    def initialize(self):
        self.load()
        return True

    def add_note(self, text):
        db = self.selector.db
        note = db.add_note(self.dbrecord, text)
        db.commit()
        return note

    def save(self):
        fit_hist = None
        db = self.selector.db
#        sess = db.get_session()
#        db.sess = db.new_session()

#        sess.expunge_all()
        # save the fits
        for fi in self.signal_graph.fit_selector.fits:
            # get database fit
            dbfit = self._get_db_fit(fi.name)
            if dbfit != fi.fit:
                if fit_hist is None:
#                    fit_hist = proc_FitHistoryTable(analysis=self.dbrecord,
#                                                    user=db.save_username
#                                                    )
#                    self.dbrecord.fit_histories.append(fit_hist)
#                    selhist = self.dbrecord.selected_histories
#                    selhist.selected_fits = fit_hist
                    print db.save_username, 'adsfasfd'
                    fit_hist = db.add_fit_history(self.dbrecord, user=db.save_username)

                dbiso = next((iso for iso in self.dbrecord.isotopes
                              if iso.molecular_weight.name == fi.name), None)

                db.add_fit(fit_hist, dbiso, fit=fi.fit)
#                _f = proc_FitTable(history=fit_hist, fit=fi.fit)

        db.commit()

    def set_status(self, status):
        self.dbrecord.status = status

    def fit_isotope(self, name, fit, kind):
        iso = self.isotopes[name]
        if kind == 'baseline':
            iso = iso.baseline

        iso.fit
#        si = self.signals[name]
#        if len(si.xs) < 1:
#            data = self._get_peak_time_data(kind, names=[name])
#            _det, _iso, _fit, (x, y) = data[name]
#            si.xs = x
#            si.ys = y

#        si.fit = fit

        return float(iso.value), float(iso.error)

    def set_isotope(self, k, v, e):
        if self.isotopes.has_key(k):
            self.isotopes[k].trait_set(value=v, error=e)
        else:
            self.isotopes[k] = Isotope(value=v, error=e)

    def set_blank(self, k, v, e):
        blank = None
        if self.isotopes.has_key(k):
            blank = self.isotopes[k].blank

        if blank is None:
            self.isotopes[k].blank = Blank(value=v, error=e)
        else:
            blank.trait_set(value=v, error=e)

    def set_background(self, k, v, e):
        background = None
        if self.isotopes.has_key(k):
            background = self.isotopes[k].background

        if background is None:
            self.isotopes[k].background = Background(value=v, error=e)
        else:
            background.trait_set(value=v, error=e)

#===============================================================================
# viewable
#===============================================================================
    def opened(self, ui):
#        def d():
# #            self.selected = None
#            self.selected = 'summary'
#        do_later(d)
#        self.selected = 'summary'
#        self.selected = 'notes'
        self.selected = 'error'
        super(IsotopeRecord, self).opened()

    def closed(self, isok):
        self.selected = None
        self.closed_event = True

#===============================================================================
# database record
#===============================================================================
    def load_isotopes(self):
        if self.dbrecord:
            for iso in self.dbrecord.isotopes:
                if iso.kind == 'signal':
                    result = iso.results[-1]
                    name = iso.molecular_weight.name
                    det = iso.detector.name
                    r = Isotope(dbrecord=iso, dbresult=result, name=name, detector=det)
                    fit = self._get_db_fit(name, 'signal')
                    r.set_fit(fit)
                    self.isotopes[name] = r

            for iso in self.dbrecord.isotopes:
                if iso.kind == 'baseline':
                    result = iso.results[-1]
                    name = iso.molecular_weight.name
                    i = self.isotopes[name]
                    r = Baseline(dbrecord=iso, dbresult=result, name=name)
                    fit = self._get_db_fit(name, 'baseline')
                    r.set_fit(fit)
                    i.baseline = r

            blanks = self._get_blanks()
            if blanks:
                for bi in blanks:
                    for ba in bi.blanks:
                        r = Blank(dbrecord=ba, name=ba.isotope)
                        self.isotopes[ba.isotope].blank = r

            return True

    def load(self):
        self.load_isotopes()

        self._make_signal_graph()
        self._make_baseline_graph()

        peakcenter = self._get_peakcenter()
        if peakcenter:
#            self.categories.insert(-1, 'peak center')
            self.categories.append('peak center')
            graph = self._make_peak_center_graph(*peakcenter)
            self.peak_center_graph = graph

#        blanks = self._get_blanks()
#        if blanks:
#            for bi in blanks:
#                for ba in bi.blanks:
#                    r = Blank(dbrecord=ba, name=ba.isotope)
#                    self.isotopes[ba.isotope].blank = r

            if 'blanks' not in self.categories:
#                self.categories.append(-1, 'blanks')
                self.categories.append('blanks')

        backgrounds = self._get_backgrounds()
        if backgrounds:
            if 'backgrounds' not in self.categories:
#                self.categories.insert(-1, 'backgrounds')
                self.categories.append('backgrounds')

        det_intercals = self._get_detector_intercalibrations()
        if det_intercals:
#            self.categories.insert(-1, 'Det. Intercal.')
            self.categories.append('Det. Intercal.')

#    def load_graph(self, graph=None, xoffset=0):
#        graph = self._make_stacked_graph('signal')
#        graph.refresh()
#        self.signal_graph = EditableGraph(graph=graph)
#
#        graph = self._make_stacked_graph('baseline')
#        graph.refresh()
#        self.baseline_graph = EditableGraph(graph=graph)
#        self.baseline_graph.fit_selector = FitSelector(analysis=self,
#                                                        kind='baseline',
#                                                        name='Baseline',
#                                                        graph=self.baseline_graph)

#        sniffs = self._get_table_data(dm, 'sniffs')
#        if sniffs:
#            self.categories.append('sniff')
#            graph = self._make_stacked_graph(sniffs, regress=False)
#            self.sniff_graph = graph

#        peakcenter = self._get_peakcenter()
#        if peakcenter:
#            self.categories.insert(-1, 'peak center')
# #            self.categories.append('peak center')
#            graph = self._make_peak_center_graph(*peakcenter)
#            self.peak_center_graph = graph
#
#        blanks = self._get_blanks()
#        if blanks:
#            if 'blanks' not in self.categories:
# #                self.categories.append(-1, 'blanks')
#                self.categories.append('blanks')
#
#        backgrounds = self._get_backgrounds()
#        if backgrounds:
#            if 'backgrounds' not in self.categories:
# #                self.categories.insert(-1, 'backgrounds')
#                self.categories.append('backgrounds')
#
#        det_intercals = self._get_detector_intercalibrations()
#        if det_intercals:
# #            self.categories.insert(-1, 'Det. Intercal.')
#            self.categories.append('Det. Intercal.')

    def get_baseline_corrected_signal_dict(self):
        d = dict()
        for ki in ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']:
            if self.isotopes.has_key(ki):
                v = self.isotopes[ki].baseline_corrected_value()
            else:
                v = ufloat(0, 0)

            d[ki] = v

        return d

    def get_corrected_value(self, key):
        return self.isotopes[key].get_corrected_value()
#===============================================================================
# handlers
#===============================================================================

    def _selected_changed(self):
        selected = self.selected
        if selected is not None:

            selected = selected.replace(' ', '_')
            selected = selected.lower()

            self.debug('selected= {}'.format(selected))
            if selected in (
                            'blanks',
                            'backgrounds',
                            'det._intercal.',
                            'irradiation',
                            'supplemental',
                            'measurement',
                            'extraction', 'experiment', 'notes',
                            'error',
                            ):
                item = getattr(self, '{}_summary'.format(selected))
            elif selected == 'summary':
                item = self.analysis_summary
#            elif selected == 'blanks':
#                item = self.blanks_summary  # BlanksSummary(record=self)
#            elif selected == 'backgrounds':
#                item = self.backgrounds_summary
#            elif selected == 'det._intercal.':
#                item = self.detector_intercalibration_summary
#            elif selected == 'irradiation':
#                item = self.irradiation_summary
#            elif selected == 'supplemental':
#                item = self.supplemental_summary
#            elif selected == 'measurement':
#                item = self.measurement_summary
#            elif selected == 'extraction':
#                item = self.extraction_summary
#            elif selected == 'experiment':
#                item = self.experiment_summary
#            elif selected == 'notes':
#                item = self.notes_summary
            else:
                name = '{}_graph'.format(selected)
                item = getattr(self, name)

            self.display_item = item
            if hasattr(item, 'refresh'):
                item.refresh()

    def _apply_history_change(self, new):
        self.changed = True

    def _unpack_blob(self, blob, endianness='>'):
        return zip(*[struct.unpack('{}ff'.format(endianness), blob[i:i + 8]) for i in xrange(0, len(blob), 8)])

#    def _load_histories(self):
#
#        #load blanks
#        self._load_from_history('blanks', Blank)
#
#        #load backgrounds
#        self._load_from_history('backgrounds', Background)
#
# #        #load airs for detector intercal
# #        self._load_detector_intercalibration()
# #
# #    def _load_detector_intercalibration(self):
# #        pass
#
#    def _load_from_history(self, name, klass, **kw):
#        kind = name[:-1]
#        item = self._get_history_item(name)
#        if item:
#            for bi in item:
#                isotope = bi.isotope
#                iso = self.isotopes[isotope.name]
#                nitem = klass(bi, None)
#
#                nitem._value = bi.user_value if bi.user_value else 0
#                nitem._error = bi.user_error if bi.user_error else 0
#                nitem.fit = bi.fit
#
#                setattr(iso, kind, nitem)
#                if kind == 'blank':
#                    iso.b = nitem

#                if not bi.fit:
# #                if not bi.use_set:
#                    s = klass(timestamp=self.timestamp, **kw)
#                    s.value = bi.user_value
#                    s.error = bi.user_error
#                else:
#                    xs, ys, es = zip(*[(ba.timestamp,
#                                        ba.signals[isotope].value,
#                                        ba.signals[isotope].error)
#                                   for ba in map(self._record_factory, bi.sets)])
#                    xs = []
#                    ys = []
#                    for ba in bi.sets:
#                        bb = self.__class__(_dbrecord=ba.analysis)
#                        a = bb.timestamp
#                        b = bb.signals[isotope].value
#                        xs.append(a)
#                        ys.append(b)

#                    s = klass(timestamp=self.timestamp,
#                              xs=xs, ys=ys, es=es,
#                              fit=bi.fit.lower(),
#                              **kw)
#                    print 'ssss', s
#                    s.xs = xs
#                    s.ys = ys
#                    s.es = es
#                    s.fit = bi.fit.lower()
#                print isotope, key
#                self._signals['{}{}'.format(isotope, key)] = s

    def _make_signal_graph(self, refresh=True):
        graph = self.signal_graph
        if graph is None:
            g = self._make_stacked_graph('signal')
#            g.refresh()
            fs = self.analysis_summary.fit_selector
            self.signal_graph = EditableGraph(graph=g, fit_selector=self.analysis_summary.fit_selector)
            fs.graph = self.signal_graph
            if refresh:
                fs.refresh()
#
    def _make_baseline_graph(self):
        graph = self.baseline_graph
        if graph is None:
            g = self._make_stacked_graph('baseline')
#            g.refresh()
            self.baseline_graph = EditableGraph(graph=g, fit_selector=self.analysis_summary.fit_selector)
            self.baseline_graph.fit_selector = FitSelector(analysis=self,
                                                        kind='baseline',
                                                        name='Baseline',
                                                        graph=self.baseline_graph)

            self.baseline_graph.fit_selector.refresh()
#

    def _make_stacked_graph(self, kind, regress=True):
        if regress:
            klass = StackedRegressionGraph
        else:
            klass = StackedGraph

        graph = self._graph_factory(klass, width=self.item_width)
        gkw = dict(padding=[50, 50, 5, 50],
                   fill_padding=True
                   )

        isos = reversed(self.isotope_keys)
        i = 0
        for iso in isos:
            dbiso = self.isotopes[iso]
            if kind == 'baseline':
                dbiso = dbiso.baseline

            di = dbiso.detector
            fit = dbiso.fit
            fo = dbiso.filter_outliers
            ite = dbiso.filter_outlier_iterations
            sd = dbiso.filter_outlier_std_devs

            xs = dbiso.xs
            ys = dbiso.ys

            gkw['ytitle'] = '{} ({})'.format(di, iso)
            gkw['xtitle'] = 'Time (s)'

            gkw['detector'] = di
            gkw['isotope'] = iso

            skw = dict()
            if regress:
                skw['fit'] = fit

            graph.new_plot(**gkw)

            fo_dict = dict(filter_outliers=fo,
                             filter_outlier_iterations=ite,
                             filter_outlier_std_devs=sd)

            graph.new_series(xs, ys, plotid=i,
                             type='scatter',
                             marker='circle',
                             filter_outliers_dict=fo_dict,
                             marker_size=1.25,
                             **skw)

            i += 1

        if i:
            graph.set_x_limits(min=0)

        graph.refresh()

        return graph

    def _make_peak_center_graph(self, xs, ys, center_dac, pcdacs, pcsignals):

        graph = self._graph_factory(width=700)
        graph.container_dict = dict(padding=[10, 0, 30, 10])
        graph.clear()

        graph.new_plot(title='Center= {:0.8f}'.format(center_dac),
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
# getters
#===============================================================================
    def _get_history_item(self, name):
        '''
            get the selected history item if available else use the last history
        '''
        dbr = self.dbrecord
        histories = getattr(dbr, '{}_histories'.format(name))
        if histories:
            hist = None
            shists = dbr.selected_histories
            if shists:
                hist = getattr(shists, 'selected_{}'.format(name))

            if hist is None:
                hist = histories[-1]

            return getattr(hist, name)

    def _get_detector_intercalibrations(self):
        ds = self.dbrecord.detector_intercalibration_histories
        return ds

    def _get_blanks(self):
        bhs = self.dbrecord.blanks_histories
        return bhs

    def _get_backgrounds(self):
        bhs = self._dbrecord.backgrounds_histories
        return bhs

    def _get_peakcenter(self):
        pc = self._dbrecord.peak_center
        if pc:
            x, y = self._unpack_blob(pc.points, endianness='<')
            center = pc.center
#            self.peak_center_dac = center
            return x, y, center, [], []

    def _get_db_fit(self, name, kind):
        record = self.dbrecord
        selhist = record.selected_histories
        selfithist = selhist.selected_fits
        fits = selfithist.fits
        return next((fi for fi in fits
                        if fi.isotope.molecular_weight.name == name and
                            fi.isotope.kind == kind), None)
#===============================================================================
# property get/set
#===============================================================================

#    def _get_signal_graph(self):
#        graph = self._make_stacked_graph('signal')
#        graph.refresh()
#        return EditableGraph(graph=graph)
#
#    def _get_baseline_graph(self):
#        graph = self._make_stacked_graph('baseline')
#        graph.refresh()
#        fs = FitSelector(analysis=self, kind='baseline', name='Baseline', graph=graph)
#
#        return EditableGraph(graph=graph, fit_selector=fs)

    @cached_property
    def _get_irradiation(self):
        try:
            lev = self.irradiation_level
            return lev.irradiation
        except AttributeError:
            pass

    @cached_property
    def _get_ic_factor(self):
        ic = (1.0, 0)
        name = 'detector_intercalibration'
        items = self._get_history_item(name)
#        print items
        if items:

            '''
                only get the cdd ic factor for now 
                its the only one with non unity
            '''

            # get Ar36 detector
            det = next((iso.detector for iso in self.dbrecord.isotopes
                      if iso.molecular_weight.name == 'Ar36'), None)
#            for iso in self.dbrecord.isotopes:
#                print iso
            if det:

                # get the intercalibration for this detector
                item = next((item for item in items if item.detector == det), None)
                ic = item.user_value, item.user_error

#                if not item.fit:
#    #                s = Value(value=item.user_value, error=item.user_error)
#                    ic = item.user_value, item.user_error
#                else:
#                    intercal = lambda x:self._intercalibration_factory(x, 'Ar40', 'Ar36', 295.5)
#                    data = map(intercal, item.sets)
#                    xs, ys, es = zip(*data)
#
#                    s = InterpolatedRatio(timestamp=self.timestamp,
#                                          fit=item.fit,
#                                          xs=xs, ys=ys, es=es
#                                          )
#                    ic = s.value, s.error

        return ic

    @cached_property
    def _get_analysis_summary(self):
        fs = FitSelector(analysis=self,
                         name='Signal'
                         )

        item = AnalysisSummary(record=self,
                               fit_selector=fs
                               )
        fs.on_trait_change(item.refresh, 'fits:[fit,filterstr,filter_outliers]')

#        from src.database.isotope_analysis.analysis_display import AnalysisDisplay
#        item = AnalysisDisplay(record=self)
        return item

    @cached_property
    def _get_irradiation_summary(self):
        i = IrradiationSummary(record=self)
        return i

    @cached_property
    def _get_detector_intercalibration_summary(self):
        di = DetectorIntercalibrationSummary(record=self)
        di.on_trait_change(self._apply_history_change, 'history_view.applied_history')
        return di

    @cached_property
    def _get_supplemental_summary(self):
        si = SupplementalSummary(record=self)
        return si

    @cached_property
    def _get_measurement_summary(self):
        si = MeasurementSummary(record=self)
        return si

    @cached_property
    def _get_extraction_summary(self):
        si = ExtractionSummary(record=self)
        return si

    @cached_property
    def _get_experiment_summary(self):
        si = ExperimentSummary(record=self)
        return si

    @cached_property
    def _get_blanks_summary(self):
        bs = BlanksSummary(record=self)
        return bs

    @cached_property
    def _get_backgrounds_summary(self):
        bs = BackgroundsSummary(record=self)
        return bs

    @cached_property
    def _get_notes_summary(self):
        bs = NotesSummary(record=self)
        return bs

    @cached_property
    def _get_error_summary(self):
        bs = ErrorComponentSummary(record=self)
        return bs


    @cached_property
    def _get_record_id(self):
        return make_runid(self.labnumber, self.aliquot, self.step)
#        return '{}-{}{}'.format(self.labnumber, self.aliquot, self.step)

    @cached_property
    def _get_labnumber_record(self):
        return self.dbrecord.labnumber

    @cached_property
    def _get_labnumber(self):
        if self._dbrecord:
            if self._dbrecord.labnumber:
                ln = self._dbrecord.labnumber.labnumber
                ln = convert_labnumber(ln)
                return ln

    @cached_property
    def _get_shortname(self):
        if self._dbrecord:
            ln = self._dbrecord.labnumber.labnumber
            ln = convert_shortname(ln)

            ln = make_runid(ln, self.aliquot, self.step)
#            ln = '{}-{}{}'.format(ln, self.aliquot, self.step)
            return ln

    @cached_property
    def _get_analysis_type(self):
        try:
            return self._dbrecord.measurement.analysis_type.name
        except AttributeError:
            self.debug('no analysis type')

    @cached_property
    def _get_mass_spectrometer(self):
        try:
            return self._dbrecord.measurement.mass_spectrometer.name.lower()
        except AttributeError:
            self.debug('no mass spectrometer')

    @cached_property
    def _get_isotope_keys(self):
        keys = self.isotopes.keys()
        isos = sorted(keys, key=lambda x: re.sub('\D', '', x), reverse=True)
        return isos

#===============================================================================
# dbrecord values
#===============================================================================
    @cached_property
    def _get_timestamp(self):
        analysis = self.dbrecord
        analts = analysis.analysis_timestamp
#        analts = '{} {}'.format(analysis.rundate, analysis.runtime)
#        analts = datetime.datetime.strptime(analts, '%Y-%m-%d %H:%M:%S')
        return time.mktime(analts.timetuple())

    @cached_property
    def _get_rundate(self):
        dbr = self.dbrecord
        if dbr and dbr.analysis_timestamp:
            date = dbr.analysis_timestamp.date()
            return date.strftime('%Y-%m-%d')

    @cached_property
    def _get_runtime(self):
        dbr = self.dbrecord
        if dbr and dbr.analysis_timestamp:
            ti = dbr.analysis_timestamp.time()
            return ti.strftime('%H:%M:%S')

    @cached_property
    def _get_sample(self):
        dbr = self.dbrecord
        if hasattr(dbr, 'sample'):
            return dbr.sample.name
        else:
            return NULL_STR

    @cached_property
    def _get_material(self):
        dbr = self.dbrecord
        if hasattr(dbr, 'sample'):
            return dbr.sample.material.name
        else:
            return NULL_STR

    @cached_property
    def _get_project(self):
        ln = self.dbrecord.labnumber
        sample = ln.sample
        return sample.project.name

    def _get_status(self):
        return self._get_dbrecord_value('status')

    @cached_property
    def _get_uuid(self):
        return self._get_dbrecord_value('uuid')

    @cached_property
    def _get_aliquot(self):
        return self._get_dbrecord_value('aliquot')

    @cached_property
    def _get_step(self):
        return self._get_dbrecord_value('step')

    @cached_property
    def _get_sensitivity(self):
        def func(dbr):
            if dbr.extraction:
                if dbr.extraction.sensitivity:
                    return dbr.extraction.sensitivity.sensitivity

        return self._get_dbrecord_value('sensitivity', func=func, default=1)

    @cached_property
    def _get_sensitivity_multiplier(self):
        def func(dbr):
            if dbr.extraction:
                return dbr.extraction.sensitivity_multiplier
        return self._get_dbrecord_value('sensitivity_multiplier', func=func, default=1)

    def _get_dbrecord_value(self, attr, func=None, default=None):
        v = None
        if self._dbrecord:
            if func is not None:
                v = func(self._dbrecord)
            else:
                v = getattr(self._dbrecord, attr)

        if v is None:
            v = default
        return v

#===============================================================================
# extraction
#===============================================================================
    def _get_extraction_value(self, attr, getter=None):
        '''
            r = NULL_STR
            dbr = self._dbrecord
            if dbr.extraction:
                r = dbr.extraction.position
            return r
        '''
        r = NULL_STR
        dbr = self._dbrecord
        if dbr.extraction:
            if getter is None:
                r = getattr(dbr.extraction, attr)
            else:
                r = getter(dbr.extraction)
        return r

    def _get_position(self):
        r = NULL_STR
        pos = self._get_extraction_value('positions')
        if pos == NULL_STR:
            return NULL_STR

        pp = []
        for pi in pos:
            pii = pi.position

            if pii:
                pp.append(pii)
            else:
                ppp = []
                x, y, z = pi.x, pi.y, pi.z
                if x is not None and y is not None:
                    ppp.append(x)
                    ppp.append(y)
                if z is not None:
                    ppp.append(z)

                if ppp:
                    pp.append('({})'.format(','.join(ppp)))

        if pp:
            r = ','.join(map(str, pp))

        return r

    def _get_extract_device(self):
        def get(ex):
            r = NULL_STR
            if ex.extraction_device:
                r = ex.extraction_device.name
            return r

        return self._get_extraction_value(None, getter=get)

    def _get_extract_value(self):
        return self._get_extraction_value('extract_value')

    def _get_extract_units(self):
        return 'W'

    def _get_extract_duration(self):
        return self._get_extraction_value('extract_duration')

    def _get_cleanup_duration(self):
        return self._get_extraction_value('cleanup_duration')

    def _get_peak_center_dac(self):
        pc = self._get_peakcenter()
        if pc:
            return pc.center
        else:
            return 0

    def _get_experiment(self):
        return self._get_dbrecord_value('experiment')
    def _get_extraction(self):
        return self._get_dbrecord_value('extraction')
    def _get_measurement(self):
        return self._get_dbrecord_value('measurement')
#===============================================================================
# factories
#===============================================================================

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        grp = HGroup(
                        Item('categories', editor=ListStrEditor(
                                                                editable=False,
                                                                operations=[],
                                                                selected='selected'
                                                                ),
                             show_label=False,
                             width=0.05
                             ),
                        Item('display_item', show_label=False, style='custom'),
                        )

        return self._view_factory(grp)

#============= EOF =============================================
#    def _load_regressors(self, data):
#        isos = [vi[1] for vi in data.itervalues()]
#        isos = sorted(isos, key=lambda x:re.sub('\D', '', x))
#        def get_data(k):
#            try:
#                return data[k]
#            except KeyError:
#                return next((di for di in data.itervalues() if di[1] == k), None)
#
#        regs = dict()
#        for iso in isos:
#            try:
#                _di, _iso, ofit, (x, y) = get_data(iso)
#            except ValueError:
#                continue
#
#            fit = self._get_iso_fit(iso, ofit)
#
#            x = array(x)
#            y = array(y)
#
# #            if iso == 'Ar40':
# #                import numpy as np
# #                p = '/Users/ross/Sandbox/61311-36b'
# #                xs, ys = np.loadtxt(p, unpack=True)
# #                for ya, yb in zip(ys, y):
# #                    print ya, yb, ya - yb
#
#
# #            exc = RegressionGraph._apply_filter_outliers(x, y)
# #            x = delete(x[:], exc, 0)
# #            y = delete(y[:], exc, 0)
#
#            low = min(x)
#
#            fit = RegressionGraph._convert_fit(fit)
#            if fit in [1, 2, 3]:
#                if len(y) < fit + 1:
#                    return
#                st = low
#                xn = x - st
# #                print x[0], x[-1]
#                r = PolynomialRegressor(xs=xn, ys=y,
#                                        degree=fit)
#                t_fx, t_fy = x[:], y[:]
#                niterations = 1
#                for ni in range(niterations):
#                    excludes = list(r.calculate_outliers())
#                    t_fx = delete(t_fx, excludes, 0)
#                    t_fy = delete(t_fy, excludes, 0)
#                    r = PolynomialRegressor(xs=t_fx, ys=t_fy,
#                                    degree=fit)
#
#            else:
#                r = MeanRegressor(xs=x, ys=y)
#
#            regs[iso] = r
#
#        return regs

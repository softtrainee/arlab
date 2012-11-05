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
    Event, Dict
from traitsui.api import View, Item, HGroup, ListStrEditor
from pyface.timer.do_later import do_later
#============= standard library imports ========================
from uncertainties import ufloat
import re
import datetime
from numpy import array, delete
#============= local library imports  ==========================
from src.database.isotope_analysis.blanks_summary import BlanksSummary
from src.graph.graph import Graph
from src.database.isotope_analysis.fit_selector import FitSelector
from src.graph.regression_graph import StackedRegressionGraph, RegressionGraph
from src.graph.stacked_graph import StackedGraph
from src.database.records.database_record import DatabaseRecord
from src.database.isotope_analysis.analysis_summary import AnalysisSummary
from src.experiment.identifier import convert_shortname, convert_labnumber
from src.database.isotope_analysis.detector_intercalibration_summary import DetectorIntercalibrationSummary
from src.experiment.processing.argon_calculations import calculate_arar_age
from src.experiment.processing.signal import InterpolatedRatio, Background, \
    Blank, Signal
from src.database.isotope_analysis.irradiation_summary import IrradiationSummary
from src.regression.ols_regressor import PolynomialRegressor
from src.regression.mean_regressor import MeanRegressor
from src.database.orms.isotope_orm import proc_FitHistoryTable, proc_FitTable

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

class IsotopeRecord(DatabaseRecord):
    title_str = 'Analysis'
    window_height = 780
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
    categories = List(['summary', 'irradiation' ])#'signal', 'sniff', 'baseline', 'peak center' ])
    selected = Any('signal')
    display_item = Instance(HasTraits)

    isotope_keys = Property
    signals = Property
    _signals = Dict
#    baselines = None
#    backgrounds = None
#    blanks = None

    labnumber = Property
    shortname = Property
    analysis_type = Property
    aliquot = Property
    step = Property
    mass_spectrometer = Property

    changed = Event

    age = Property(depends_on='age_dirty')
    age_dirty = Event

    ic_factor = Property
    j = Property
    irradiation = Property
    irradiation_info = Property
    irradiation_level = Property
    irradiation_position = Property
    production_ratios = Property

    age_scalar = 1e6

    _no_load = False

    k39 = None
    rad40 = None
    arar_result = None

    def save(self):
        fit_hist = None
        #save the fits
        for fi in self.signal_graph.fit_selector.fits:
            #get database fit
            dbfit = self._get_db_fit(fi.name)
            if dbfit != fi.fit:
                if fit_hist is None:
                    fit_hist = proc_FitHistoryTable(analysis=self.dbrecord,
                                                    user=self.selector.db.save_username
                                                    )
                    self.dbrecord.fit_histories.append(fit_hist)
                    selhist = self.dbrecord.selected_histories
                    selhist.selected_fits = fit_hist

                _f = proc_FitTable(history=fit_hist, fit=fi.fit,
                                                    isotope=fi.name)

        self.selector.db.commit()

#    def _age_dirty_changed(self):
#        print 'asfdasfd'
#===============================================================================
# viewable
#===============================================================================
    def opened(self):
        def d():
#            self.selected = None
            self.selected = 'summary'
        do_later(d)
        super(IsotopeRecord, self).opened()

    def closed(self, isok):
        self.selected = None

#===============================================================================
# database record
#===============================================================================
    def load_graph(self, graph=None, xoffset=0):
        dm = self.selector.data_manager
        signals, baselines = self._load_signals()
        if signals:
            if 'signal' not in self.categories:
                self.categories.append('signal')
            graph = self._load_stacked_graph(signals)
            self.signal_graph = EditableGraph(graph=graph)

        if baselines:
            if 'baseline' not in self.categories:
                self.categories.append('baseline')
            graph = self._load_stacked_graph(baselines)
            self.baseline_graph = EditableGraph(graph=graph)
            self.baseline_graph.fit_selector = FitSelector(analysis=self,
                                                           name='Baseline',
                                                           graph=self.baseline_graph)

        sniffs = self._get_table_data(dm, 'sniffs')
        if sniffs:
            self.categories.append('sniff')
            graph = self._load_stacked_graph(sniffs, regress=False)
            self.sniff_graph = graph

        peakcenter = self._get_peakcenter(dm)
        if peakcenter:
            self.categories.append('peak center')
            graph = self._load_peak_center_graph(peakcenter)
            self.peak_center_graph = graph

        blanks = self._get_blanks()
        if blanks:
            if 'blanks' not in self.categories:
                self.categories.append('blanks')

        backgrounds = self._get_backgrounds()
        if backgrounds:
            if 'backgrounds' not in self.categories:
                self.categories.append('backgrounds')

        det_intercals = self._get_detector_intercalibrations()
        if det_intercals:
            self.categories.append('Det. Intercal.')

    def get_baseline_corrected_signal_dict(self):
#        self._load_signals()
        signals = self.signals
        d = dict()

        for ki in ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']:
            try:
                us = signals[ki].uvalue
            except KeyError:
                us = ufloat((0, 0))
            try:
                ub = signals[ki + 'bs'].uvalue
            except KeyError:
                ub = ufloat((0, 0))

            d[ki] = us - ub

        return d

#===============================================================================
# private
#===============================================================================
#    def __getattr__(self, attr):
#        try:
#            return getattr(self._dbrecord, attr)
#        except AttributeError, e:
#            print 'gettatrr', attr


    def _calculate_age(self):
#        self._load_signals()
        signals = self.signals

        keys = ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']
        for iso in keys:
            for k in ['', 'bs', 'bl', 'bg']:
                isok = iso + k
                if not signals.has_key(isok):
                    signals[isok] = self._signal_factory(isok, None)

        sigs = lambda name: [(signals[iso].value, signals[iso].error)
                                for iso in map('{{}}{}'.format(name).format, keys)]
        fsignals = sigs('')
        bssignals = sigs('bs')
        blsignals = sigs('bl')
        bksignals = sigs('bg')

        ic = self.ic_factor
        j = self.j
        irrad = self.irradiation_info
        result = calculate_arar_age(fsignals, bssignals, blsignals, bksignals, j, irrad, ic)

        if result:
            self.arar_result = result
            self.k39 = result['k39']
            ai = result['age']
            ai = ai / self.age_scalar
            age = ai.nominal_value
            err = ai.std_dev()
            return age, err



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
                item.refresh()
            elif selected == 'det._intercal.':
                item = self.detector_intercalibration_summary
            elif selected == 'irradiation':
                item = self.irradiation_summary
                item.refresh()
#                item = DetectorIntercalibrationSummary(record=self)
            else:
                item = getattr(self, '{}_graph'.format(selected))

            self.trait_set(display_item=item)

    def _apply_history_change(self, new):
        self.changed = True

#===============================================================================
# loaders
#===============================================================================
    def _load_signals(self):
        if self._no_load:
            graph = self.signal_graph
            if graph:
                for iso, rs in zip(self.isotope_keys, graph.regressors):
                    self._signals[iso] = Signal(_value=rs.coefficients[-1],
                                               _error=rs.coefficient_errors[-1])
            graph = self.baseline_graph
            if graph:
                for iso, rs in zip(self.isotope_keys, graph.regressors):
                    self._signals['{}bs'.format(iso)] = Signal(_value=rs.coefficients[-1],
                                                              _error=rs.coefficient_errors[-1])

            return self._signals_table, self._baselines_table

        self._no_load = True
        dm = self.selector.data_manager

        if not dm.open_data(self.path):
            return

        signals = self._get_table_data(dm, 'signals')
        if signals:
            self._signals_table = signals
            regressors = self._load_regressors(signals)
            for iso, rs in regressors.iteritems():
                self._signals[iso] = Signal(_value=rs.coefficients[-1],
                                           _error=rs.coefficient_errors[-1])
        baselines = self._get_table_data(dm, 'baselines')
        if baselines:
            self._baselines_table = baselines
            regressors = self._load_regressors(baselines)
            for iso, rs in regressors.iteritems():
                self._signals['{}bs'.format(iso)] = Signal(_value=rs.coefficients[-1],
                                           _error=rs.coefficient_errors[-1])

        self._load_histories()
        return signals, baselines

    def _load_histories(self):

        #load blanks
        self._load_from_history('blanks', 'bl', Blank)

        #load backgrounds
        self._load_from_history('backgrounds', 'bg', Background)

        #load airs for detector intercal
        self._load_detector_intercalibration()

    def _load_detector_intercalibration(self):
        pass

    def _load_from_history(self, name, key, klass, **kw):
        item = self._get_history_item(name)
        if item:
            for bi in item:
                isotope = bi.isotope
                s = klass(timestamp=self.timestamp, **kw)
                if not bi.fit:
#                if not bi.use_set:
                    s.value = bi.user_value
                    s.error = bi.user_error
                else:
                    s.fit = bi.fit.lower()
                    xs, ys, es = zip(*[(ba.timestamp, ba.signals[isotope].value, ba.signals[isotope].error)
                                   for ba in map(self._analysis_factory, bi.sets)])
                    s.xs = xs
                    s.ys = ys
                    s.es = es

                self.signals['{}{}'.format(isotope, key)] = s



    def _load_regressors(self, data):
        isos = [vi[1] for vi in data.itervalues()]
        isos = sorted(isos, key=lambda x:re.sub('\D', '', x))
        def get_data(k):
            try:
                return data[k]
            except KeyError:
                return next((di for di in data.itervalues() if di[1] == k), None)

        regs = dict()
        for iso in isos:
            try:
                _di, _iso, ofit, (x, y) = get_data(iso)
            except ValueError:
                continue

            fit = self._get_iso_fit(iso, ofit)

            x = array(x)
            y = array(y)

            exc = RegressionGraph._apply_filter_outliers(x, y)
            x = delete(x[:], exc, 0)
            y = delete(y[:], exc, 0)

            low = min(x)
            fit = RegressionGraph._convert_fit(fit)
            if fit in [1, 2, 3]:
                if len(y) < fit + 1:
                    return
                st = low
                xn = x - st
                r = PolynomialRegressor(xs=xn, ys=y,
                                        degree=fit)
            else:
                r = MeanRegressor(xs=x, ys=y)

            regs[iso] = r

        return regs

    def _load_stacked_graph(self, data, det=None, regress=True):
        if regress:
            klass = StackedRegressionGraph
        else:
            klass = StackedGraph

        graph = self._graph_factory(klass, width=700)
#        graph.suppress_regression = True
        gkw = dict(padding=[50, 50, 5, 50],
                   fill_padding=True
                   )

        isos = [vi[1] for vi in data.itervalues()]
        isos = sorted(isos, key=lambda x:re.sub('\D', '', x))

        def get_data(k):
            try:
                return data[k]
            except KeyError:
                return next((di for di in data.itervalues() if di[1] == k), None)

        i = 0
        for iso in isos:
            try:
                di, _iso, ofit, (xs, ys) = get_data(iso)
            except ValueError:
                continue

            fit = self._get_iso_fit(iso, ofit)
            gkw['ytitle'] = '{} ({})'.format(di if det is None else det, iso)
            gkw['xtitle'] = 'Time (s)'
            skw = dict()
            if regress:
                skw['fit'] = fit

            graph.new_plot(
                            **gkw)
            graph.new_series(xs, ys, plotid=i,
                             type='scatter', marker='circle',
                             marker_size=1.25,
                             **skw)
#            graph.set_series_label(key, plotid=i)
            ma = max(xs)

#            graph.suppress_regression = iso != isos[-1]
#            graph.suppress_regression = False

#            params = dict(orientation='right' if i % 2 else 'left',
#                          axis_line_visible=False
#                          )
#
#            graph.set_axis_traits(i, 'y', **params)
            i += 1

        graph.set_x_limits(min=0, max=ma, plotid=0)
#        graph.suppress_regression = False
        graph._update_graph()

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

    def _get_iso_fit(self, iso, ofit):
        fit = ofit
#       get the fit latest fit history or use ofit
        dbfit = self._get_db_fit(iso)
        if dbfit:
            fit = dbfit.fit
        return fit

    def _get_db_fit(self, iso):
        hist = self.dbrecord.fit_histories
        try:
            hist = hist[-1]
            return next((fi for fi in hist.fits if fi.isotope == iso), None)
        except IndexError:
            pass

    def _get_xy(self, tab, x='time', y='value'):
        return zip(*[(r[x], r[y]) for r in tab.iterrows()])

    def _get_detector_intercalibrations(self):
        ds = self.dbrecord.detector_intercalibration_histories
        return ds

    def _get_blanks(self):
        bhs = self.dbrecord.blanks_histories
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
#                print grp
                fit = 'average_SEM' if grp == 'baselines' else 'linear'
                try:
                    fit = ti.attrs.fit
                except AttributeError, e:
#                    fit = 'parabolic'
                    pass

                if grp == 'signals':
                    if iso in ['Ar40', 'Ar39', 'Ar36']:
                        fit = 'parabolic'

#                print 'nn', name, ig._v_name
                ds[ig._v_name] = [ti._v_name, iso, fit, data]

        return ds

#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_j(self):
        s = 1.0
        e = 1e-3
        analysis = self.dbrecord
        labnumber = analysis.labnumber
        try:
            f = labnumber.selected_flux_history.flux
            s = f.j
            e = f.j_err
        except AttributeError:
            pass

        return (s, e)

    @cached_property
    def _get_production_ratios(self):
        try:
            lev = self.irradiation_level
            ir = lev.irradiation
            pr = ir.production
            return pr
        except AttributeError:
            pass

    @cached_property
    def _get_irradiation(self):
        try:
            lev = self.irradiation_level
            return lev.irradiation
        except AttributeError:
            pass

    @cached_property
    def _get_irradiation_level(self):
        try:
            return self.irradiation_position.level
        except AttributeError, e:
            print 'level', e

    @cached_property
    def _get_irradiation_position(self):
        try:
            return self.dbrecord.labnumber.irradiation_position
        except AttributeError, e:
            print 'pos', e
#            print e

    @cached_property
    def _get_irradiation_info(self):
        '''
            return k4039, k3839, ca3937, ca3837, ca3637, cl3638, t
        '''
        prs = (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), 1
        analysis = self.dbrecord
#        labnumber = analysis.labnumber

        irradiation_level = self.irradiation_level
#        if labnumber:
#            try:
#                irradiation = labnumber.irradiation_position.level.irradiation
#            except AttributeError:
#                irradiation = None

        if irradiation_level:
            irradiation = irradiation_level.irradiation
            if irradiation:
                pr = irradiation.production
                if pr:
    #                    prs = self.production_ratios
                    prs = [(getattr(pr, pi), getattr(pr, '{}_err'.format(pi)))
                           for pi in ['K4039', 'K3839', 'Ca3937', 'Ca3837', 'Ca3637', 'Cl3638']]

                chron = irradiation.chronology
                if chron:
                    chronblob = chron.chronology
                    dose = chronblob.split('$')[-1]
                    start, _end = dose.split('%')

#                    end = '2010-01-01 01:01:01'
                    analts = '{} {}'.format(analysis.rundate, analysis.runtime)
                    analts = datetime.datetime.strptime(analts, '%Y-%m-%d %H:%M:%S')
#                    irradts = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                    try:
                        irradts = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                        dt = analts - irradts
                        t = dt.total_seconds()
                        tt = t / (60. * 60 * 24 * 365.25)
                    except ValueError:
                        self.warning('Invalid chronology {} for irradiation {}. Using zero decay time'.format(chronblob, irradiation.name))
                        tt = 0

                    prs.append(tt)

        return prs

    @cached_property
    def _get_ic_factor(self):
        ic = (1.0, 0)
        name = 'detector_intercalibration'
        item = self._get_history_item(name)
        if item:
            if not item.fit:
#                s = Value(value=item.user_value, error=item.user_error)
                self._ic_factor = item.user_value, item.user_error
            else:
                intercal = lambda x:self._intercalibration_factory(x, 'Ar40', 'Ar36', 295.5)
                data = map(intercal, item.sets)
                xs, ys, es = zip(*data)

                s = InterpolatedRatio(timestamp=self.timestamp,
                                      fit=item.fit,
                                      xs=xs, ys=ys, es=es
                                      )

                ic = s.value, s.error

        return ic

    @cached_property
    def _get_analysis_summary(self):
        fs = FitSelector(analysis=self,
                         graph=self.signal_graph,
                         name='Signal'
                         )
        if self.signal_graph:
            self.signal_graph.fit_selector = fs

        item = AnalysisSummary(record=self,
                               fit_selector=fs
                               )
        fs.on_trait_change(item.refresh, 'fits:fit, fits:filterstr')
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
    def _get_record_id(self):
        return '{}-{}{}'.format(self.labnumber, self.aliquot, self.step)

    @cached_property
    def _get_labnumber(self):
        if self._dbrecord:
#            print 'get aasfd', self._dbrecord.labnumber
            if self._dbrecord.labnumber:
                ln = self._dbrecord.labnumber.labnumber
                ln = convert_labnumber(ln)
    #        ln = '{}-{}'.format(ln, self.aliquot)
                return ln

    @cached_property
    def _get_shortname(self):
        if self._dbrecord:
    #        print 'get aasfd'
            ln = self._dbrecord.labnumber.labnumber
            ln = convert_shortname(ln)

            ln = '{}-{}{}'.format(ln, self.aliquot, self.step)
            return ln

    @cached_property
    def _get_analysis_type(self):
        if self._dbrecord:
            if self._dbrecord.measurement:
                return self._dbrecord.measurement.analysis_type.name

    @cached_property
    def _get_aliquot(self):
        if self._dbrecord:
            return self._dbrecord.aliquot

    @cached_property
    def _get_step(self):
        if self._dbrecord:
            return self._dbrecord.step

    @cached_property
    def _get_mass_spectrometer(self):
        if self._dbrecord:
            return self._dbrecord.measurement.mass_spectrometer.name.lower()

    @cached_property
    def _get_age(self):
        r = self._calculate_age()
        return r

    def _get_signals(self):
        self._load_signals()
        return self._signals

    @cached_property
    def _get_isotope_keys(self):
        keys = [k[:4] for k in self._signals.keys()]
        keys = list(set(keys))
        isos = sorted(keys, key=lambda x: re.sub('\D', '', x))
        return isos

#===============================================================================
# factories
#===============================================================================
    def _blank_factory(self, iso, tab):

        return self._signal_factory(iso, tab)

    def _signal_factory(self, iso, tab):
        kw = dict()
        if tab is not None:
            xs, ys = self._get_xy(tab)
            try:
                fit = tab._v_attrs['fit']
            except Exception:
                fit = 1

            kw = dict(xs=xs, ys=ys,
                      fit=fit,
                      detector=tab.name)
        sig = Signal(isotope=iso, **kw)
        return sig
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
                             width=0.10
                             ),
                        Item('display_item', show_label=False, style='custom'),
                        )

        return self._view_factory(grp)

#============= EOF =============================================

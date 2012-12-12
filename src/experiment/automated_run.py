#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import Any, Str, String, Int, CInt, List, Enum, Property, \
     Event, Float, Instance, Bool, cached_property, Dict, on_trait_change, DelegatesTo
from traitsui.api import View, Item, VGroup, EnumEditor, HGroup, Group, spring, Spring
#from pyface.timer.do_later import do_later
#============= standard library imports ========================
import os
import time
import random
import ast
import yaml
import struct
import uuid
from threading import Thread, Event as TEvent
#from threading import Event as TEvent
#============= local library imports  ==========================
from src.loggable import Loggable
#from src.experiment.extract_schedule import ExtractStep
from src.pyscripts.measurement_pyscript import MeasurementPyScript
from src.pyscripts.extraction_line_pyscript import ExtractionLinePyScript
from src.experiment.mass_spec_database_importer import MassSpecDatabaseImporter
from src.helpers.datetime_tools import get_datetime
from src.repo.repository import Repository
from src.experiment.plot_panel import PlotPanel
from src.experiment.identifier import convert_identifier, get_analysis_type
from src.database.adapters.local_lab_adapter import LocalLabAdapter
from src.paths import paths
from src.helpers.alphas import ALPHAS
from src.processing.signal import Signal
from src.managers.data_managers.data_manager import DataManager
from src.database.adapters.isotope_adapter import IsotopeAdapter

from globals import globalv
from src.constants import NULL_STR


class AutomatedRun(Loggable):
    spectrometer_manager = Any
    extraction_line_manager = Any
    experiment_manager = Any
    ion_optics_manager = Any
    data_manager = Instance(DataManager)

    db = Instance(IsotopeAdapter)
    local_lab_db = Instance(LocalLabAdapter)
    massspec_importer = Instance(MassSpecDatabaseImporter)
    repository = Instance(Repository)

    runner = Any
    plot_panel = Any
    peak_plot_panel = Any

    sample = Str

    experiment_name = Str
    labnumber = String(enter_set=True, auto_set=False)

    _labnumber = Int
    labnumbers = Property(depends_on='project')

    project = Any
    projects = Property

    aliquot = CInt
    step = Property(depends_on='_step')
    _step = Int

    state = Property(depends_on='_state')
    _state = Enum('not run', 'extraction',
                 'measurement', 'success', 'fail', 'truncate')
    irrad_level = Str

    duration = Property(depends_on='_duration')
    _duration = Float

    extract_group = CInt
    extract_value = Property(depends_on='_extract_value')
    _extract_value = Float

    extract_units = Property(Enum('---', 'watts', 'temp', 'percent'),
                           depends_on='_extract_units')
    _extract_units = Enum('---', 'watts', 'temp', 'percent')

    extract_device = Str

    position = CInt
    endposition = Int
    multiposition = Bool
    autocenter = Bool
    overlap = CInt
    cleanup = CInt
    ramp_rate = Float

    weight = Float
    comment = Str

    scripts = Dict
    signals = Dict

    mass_spectrometer = Str
    sample_data_record = Any

    measurement_script_dirty = Event
    measurement_script = Property(depends_on='measurement_script_dirty')
    _measurement_script = Any

    post_measurement_script_dirty = Event
    post_measurement_script = Property(depends_on='post_measurement_script_dirty')
    _post_measurement_script = Any

    post_equilibration_script_dirty = Event
    post_equilibration_script = Property(depends_on='post_equilibration_script_dirty')
    _post_equilibration_script = Any

    extraction_script_dirty = Event
    extraction_script = Property(depends_on='extraction_script_dirty')
    _extraction_script = Any

    _active_detectors = List
    _loaded = False
    configuration = None

    _rundate = None
    _runtime = None

    check_executable = Bool(True)
    _executable = Bool(True)
    _alive = False

    regression_results = None
    peak_center = None
#    info_display = DelegatesTo('experiment_manager')
    info_display = None#DelegatesTo('experiment_manager')
    coincidence_scan = None

    username = None
    _save_isotopes = List
    update = Event
    _truncate_signal = Bool
    measuring = Bool(False)

#    def _aliquot_changed(self):
#        print self.labnumber, self.aliquot



    def get_corrected_signals(self):
        d = dict()
        pp = self.plot_panel
        if pp:
            for ki, si in pp.signals.iteritems():
                bi = pp.baselines[ki]
                d[ki] = si - bi
            return d

    def to_string_attrs(self, attr):
        def get_attr(ai):
            aii = getattr(self, ai)
            if ai in ['measurement_script',
                      'extraction_script',
                      'post_measurement_script',
                      'post_equilibration_script']:
                if aii:
                    aii = str(aii).replace(self.mass_spectrometer, '')

            return aii

        return [get_attr(ai) for ai in attr]

    def create_scripts(self):
        _a = self.extraction_script
        _b = self.measurement_script
        _c = self.post_equilibration_script
        _d = self.post_measurement_script

    def truncate(self, style):
        self.info('truncating current run with style= {}'.format(style))
        self.state = 'truncate'
        self._truncate_signal = True

        if style == 'Immediate':
            self._alive = False
            self._measurement_script.truncate()
        elif style == 'Quick':
            self._measurement_script.truncate('quick')

    def finish(self):
#        del self.info_display
        if self.plot_panel:
            self.plot_panel.close_ui()

        if self.peak_plot_panel:
            self.peak_plot_panel.close_ui()

        if self.peak_center:
            self.peak_center.graph.close()

        if self.coincidence_scan:
            self.coincidence_scan.graph.close()

    def info(self, msg, *args, **kw):
        super(AutomatedRun, self).info(msg, *args, **kw)
        if self.info_display:
            self.info_display.add_text(msg)
#            do_later(self.info_display.add_text, msg)

    def get_estimated_duration(self):
        '''
            use the pyscripts to calculate etd
        '''
        s = self.duration

        for si in [self.measurement_script,
                   self.extraction_script,
                   self.post_equilibration_script,
                   self.post_measurement_script]:
            if si is not None:
                s += si.get_estimated_duration()

        return s

    def get_measurement_parameter(self, key, default=None):
        return self._get_yaml_parameter(self.measurement_script, key, default)

    def get_extraction_parameter(self, key, default=None):
        return self._get_yaml_parameter(self.extraction_script, key, default)

    def start(self):
        self.measuring = False
        self.update = True
        self.overlap_evt = TEvent()
        self.info('Start automated run {}'.format(self.name))
        self._alive = True

    def cancel(self):
        self._alive = False
        for s in ['extraction', 'measurement', 'post_equilibration', 'post_measurement']:
            script = getattr(self, '{}_script'.format(s))
            if script is not None:
                script.cancel()
        self.finish()

    def wait_for_overlap(self):
        '''
            by default overlap_evt is set 
            after do_post_equilibration
        '''
        self.info('waiting for overlap signal')
        evt = self.overlap_evt
        evt.wait()

        self.info('starting overlap delay {}'.format(self.overlap))
        starttime = time.time()
        while self._alive:
            if time.time() - starttime > self.overlap:
                break
            time.sleep(0.5)

#===============================================================================
# doers
#===============================================================================
    def do_extraction(self):
        if not self._alive:
            return

        self.info('======== Extraction Started ========')
        self.state = 'extraction'
        self.extraction_script.manager = self.experiment_manager

#        self._pre_extraction_save()
        if self.extraction_script.execute():
            self._post_extraction_save()
            self.info('======== Extraction Finished ========')
            return True
        else:
            self.info('======== Extraction Finished unsuccessfully ========')
            return False

    def do_measurement(self):
        if not self._alive:
            return

        self.measurement_script.manager = self.experiment_manager
        #use a measurement_script to explicitly define 
        #measurement sequence
        self.info('======== Measurement Started ========')
        self._pre_measurement_save()
        self.measuring = True
        if self.measurement_script.execute():
            if self._alive:
                self._post_measurement_save()

            self.info('======== Measurement Finished ========')
            self.measuring = False
            return True
        else:
            self.info('======== Measurement Finished unsuccessfully ========')
            self.measuring = False
            return False

    def do_post_measurement(self):
        if not self._alive and not self._truncate_signal:
            return

        self.info('======== Post Measurement Started ========')
        self.state = 'extraction'
        self.post_measurement_script.manager = self.experiment_manager

        if self.post_measurement_script.execute():
            self.info('======== Post Measurement Finished ========')
            return True
        else:
            self.info('======== Post Measurement Finished unsuccessfully ========')
            return False

    def do_equilibration(self, eqtime=None, inlet=None, outlet=None):
#        if inlet is None:
#            inlet = self.get_measurement_parameter('inlet_valve')

#        if inlet is None:
#            return

        evt = TEvent()
        if not self._alive:
            evt.set()
            return evt

        self.info('====== Equilibration Started ======')

        t = Thread(name='equilibration', target=self._equilibrate, args=(evt,
                                                                         eqtime, inlet, outlet))
        t.start()
        return evt

    def do_post_equilibration(self):
        if not self._alive:
            return
        if self.post_equilibration_script is None:
            return

        self.info('======== Post Equilibration Started ========')
        self.post_equilibration_script.manager = self.experiment_manager
        self.post_equilibration_script.syntax_checked = True
        if self.post_equilibration_script.execute():
            self.info('======== Post Equilibration Finished ========')
        else:
            self.info('======== Post Equilibration Finished unsuccessfully ========')

    def do_data_collection(self, ncounts, starttime, series=0):
        if not self._alive:
            return
        if self.plot_panel:
            self.plot_panel._ncounts = ncounts
            self.plot_panel.isbaseline = False

        gn = 'signal'
        fits = self.fits
        if fits is None:
            fits = ['linear', ] * len(self._active_detectors)

        self._build_tables(gn, fits)

        return self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series, fits)

    def do_sniff(self, ncounts, starttime, series=0):
        if not self._alive:
            return

        if self.plot_panel:
            self.plot_panel._ncounts = ncounts
            self.plot_panel.isbaseline = False

        fits = ['', ] * len(self._active_detectors)
        gn = 'sniff'
        self._build_tables(gn)
        return self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series,
                                fits
                                )

    def do_baselines(self, ncounts, starttime, mass, detector,
                    series=0, nintegrations=5):
        if not self._alive:
            return

        result = None
        ion = self.ion_optics_manager
        if not detector:
            if self.plot_panel:
                self.plot_panel._ncounts = ncounts
                self.plot_panel.isbaseline = True
                self.plot_panel.show()
#            else:
#                p = self._open_plot_panel(self.plot_panel, stack_order='top_to_bottom')
#                self.plot_panel = p


            if mass:
                if ion is not None:
                    ion.position(mass, self._active_detectors[0].name, False)
                    time.sleep(2)

            gn = 'baseline'
            fits = ['average_SEM', ] * len(self._active_detectors)
            self._build_tables(gn, fits=fits)
            result = self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series, fits)
            self.experiment_manager._prev_baselines = self.plot_panel.baselines
        else:
            isotopes = [di.isotope for di in self._active_detectors]
            masses = [ion.get_mass(iso) + mass for iso in isotopes]
            result = self._peak_hop_factory(detector, isotopes, ncounts, nintegrations, starttime, series,
                                   name='baselines',
                                   masses=masses)
        return result

    def do_peak_hop(self, *args):
        if not self._alive:
            return

        self._peak_hop_factory(*args, name='signals')

    def do_peak_center(self, **kw):
        if not self._alive:
            return
        ion = self.ion_optics_manager
        if ion is not None:

            t = ion.do_peak_center(**kw)

            #block until finished
            t.join()

            pc = ion.peak_center
            self.peak_center = pc
            if pc.result:
                dm = self.data_manager
                tab = dm.new_table('/', 'peak_center')

                xs, ys = pc.graph.get_data(), pc.graph.get_data(axis=1)

                for xi, yi in zip(xs, ys):
                    nrow = tab.row
                    nrow['time'] = xi
                    nrow['value'] = yi
                    nrow.append()

                xs, ys, _mx, _my = pc.result
                attrs = tab.attrs
                attrs.low_dac = xs[0]
                attrs.center_dac = xs[1]
                attrs.high_dac = xs[2]

                attrs.low_signal = ys[0]
                attrs.center_signal = ys[1]
                attrs.high_signal = ys[2]
                tab.flush()

    def do_coincidence_scan(self):
        sm = self.spectrometer_manager
        obj, t = sm.do_coincidence_scan()
        self.coincidence_scan = obj
        t.join()

    def set_spectrometer_parameter(self, name, v):
        self.info('setting spectrometer parameter {} {}'.format(name, v))
        if self.spectrometer_manager:
            self.spectrometer_manager.spectrometer.set_parameter(name, v)

    def set_position(self, pos, detector, dac=False):
        if not self._alive:
            return

        ion = self.ion_optics_manager

        if ion is not None:
            ion.position(pos, detector, dac)
            try:
                #update the plot_panel labels
                for det, pi in zip(self._active_detectors, self.plot_panel.graph.plots):
                    pi.y_axis.title = '{} {} (fA)'.format(det.name, det.isotope)
#                self.plot_panel.isotopes = [d.isotope for d in self._active_detectors]
            except Exception, e:
                print 'set_position exception', e

    def activate_detectors(self, dets):
        if not self._alive:
            return

        p = self._open_plot_panel(self.plot_panel, stack_order='top_to_bottom')
        self.plot_panel = p
        self.plot_panel.baselines = self.experiment_manager._prev_baselines
        self.plot_panel.blanks = self.experiment_manager._prev_blanks
        self.plot_panel.correct_for_blank = True if (not self.analysis_type.startswith('blank') and not self.analysis_type.startswith('background')) else False

        if not self.spectrometer_manager:
            self.warning('not spectrometer manager')
            return

        spec = self.spectrometer_manager.spectrometer
        g = p.graph
        g.suppress_regression = True
        for i, l in enumerate(dets):
            det = spec.get_detector(l)
            g.new_plot(ytitle='{} {} (fA)'.format(det.name, det.isotope))
#            g.new_series(type='scatter',
#                         marker='circle',
#                         marker_size=1.25,
#                         fit=None,
#                         label=l, plotid=i)

            g.set_x_limits(min=0, max=400, plotid=i)

        g.suppress_regression = False
        self._active_detectors = [spec.get_detector(n) for n in dets]
        self.plot_panel.detectors = self._active_detectors

    def set_regress_fits(self, fits, series=0):
        n = len(self._active_detectors)
        if isinstance(fits, str):
            fits = [fits, ] * n
        elif isinstance(fits, tuple):
            if len(fits) == 1:
                fits = [fits[0], ] * n
#
        fits = list(fits)
#        if self.plot_panel:
#            self.plot_panel.fits = fits
##            self.plot_panel.regress_id = series
#        if self.peak_plot_panel:
#            self.peak_plot_panel.fits = fits
##            self.peak_plot_panel.regress_id = series
#
        self.fits = fits

    def _open_plot_panel(self, p=None, stack_order='bottom_to_top'):
        if p is not None:
            p.ui.dispose()
            del p

        p = PlotPanel(
                         window_y=0.05 + 0.01 * self.index,
                         window_x=0.6 + 0.01 * self.index,
                         window_title='Plot Panel {}-{}'.format(self.labnumber, self.aliquot),
                         stack_order=stack_order,
                         automated_run=self
                         )
        p.graph.clear()

        self.experiment_manager.open_view(p)
        return p

#    def _regress_graph(self, reg, g, iso, dn, fi, tab, pi):
#        x, y = zip(*[(ri['time'], ri['value']) for ri in tab.iterrows()])
#        reg.xs=x
#        reg.ys=y
#        reg.fit=fi
##        reg.predict()
#
#        i=reg.coefficients[-1]
#        ie=reg.coefficient_errors[-1]
#        self.info('{}-{}-{} intercept {}+/-{}'.format(iso, dn, fi,i,ie))
#        
#        mi,ma=g.get_x_limits()
#        fx=linspace(mi,ma,200)
#        fy=reg.predict(fx)
#        lci,uci=reg.calculate_ci(fx)
#        #plot fit
#        g.new_series(
#                     fx,fy,
#                     plotid=pi, color='black')
#        
#
#        kw = dict(color='red',
#                         line_style='dash',
#                         plotid=pi)
#        #plot upper ci
#        g.new_series(fx,uci
#                     **kw
#                     )
#        g.new_series(fx,lci,
#                     **kw
#                     )
#        g.redraw()
#        return reg
        #plot lower ci

#        rdict = reg._regress_(x, y, fi)
#        try:
##        self.regression_results[dn.name] = rdict
#            self.info('{}-{}-{} intercept {}+/-{}'.format(iso, dn, fi,
#                                                    rdict['coefficients'][-1],
#                                                 rdict['coeff_errors'][-1]
#                                                 ))
#
#            g.new_series(rdict['x'],
#                         rdict['y'],
#                         plotid=pi, color='black')
#            kw = dict(color='red',
#                         line_style='dash',
#                         plotid=pi)
#
#            g.new_series(rdict['upper_x'],
#                         rdict['upper_y'],
#                         **kw
#                         )
#            g.new_series(rdict['lower_x'],
#                         rdict['lower_y'],
#                         **kw
#                         )
#            g.redraw()
#            return rdict
#        except:
#            self.warning('problem regressing')


    def _set_table_attr(self, name, grp, attr, value):
#        print name, attr, value
        dm = self.data_manager
        tab = dm.get_table(name, grp)
        setattr(tab.attrs, attr, value)
        tab.flush()
#        print getattr(tab, attr)

#    def _build_tables(self, gn):
#        dm = self.data_manager
#        #build tables
#        for di in self._active_detectors:
#            tab = dm.new_table('/{}'.format(gn), di.name)
#            tab.attrs.isotope = di.isotope
    def _build_tables(self, gn, fits=None):
        dm = self.data_manager

        dm.new_group(gn)
        for i, d in enumerate(self._active_detectors):
            iso = d.isotope
            name = d.name
            isogrp = dm.new_group(iso, parent='/{}'.format(gn))
            self._save_isotopes.append((iso, name, gn))

            t = dm.new_table(isogrp, name)
            try:
                f = fits[i]
                setattr(t.attrs, 'fit', f)
            except (IndexError, TypeError):
                pass


    def _peak_hop_factory(self, detector, isotopes, ncycles, nintegrations, starttime, series,
                          name='',
                          masses=None
                          ):
        if not self.spectrometer_manager:
            self.warning('not spectrometer manager')
            return
        add_plot = False
        p = self.peak_plot_panel
        if p is None:
#        name = 'peakhop_{}'.format(name)
            p = self._open_plot_panel(stack_order='top_to_bottom')
            self.peak_plot_panel = p
            add_plot = True
            p.series_cnt = 0

        p.detector = detector
#        p.isotopes = isotopes
#        p._ncounts = ncycles

        dm = self.data_manager
#        db = self.db
#        dm.new_group('peakhop', root='/')
#        grp = dm.new_group(detector, parent=grp)

        #get/add the detector to db

        pgrp = dm.new_group(name)
        for iso in isotopes:
            grp = dm.new_group(iso, parent=pgrp)
            dm.new_table(grp, detector)

            #add isotope to db
#            db.add_isotope(iso, det, kind=name)
            self._save_isotopes.append((iso, detector, name))

        data_write_hook = self._get_peakhop_data_writer(name)

        self.info('peak hopping {} on {}'.format(','.join(isotopes), detector))
#        spec = None
        spec = self.spectrometer_manager.spectrometer

        graph = self.peak_plot_panel.graph
        for i, iso in enumerate(isotopes):
            if add_plot:
                graph.new_plot(xtitle='Time (s)',
                           ytitle='{}'.format(iso))

                graph.set_x_limits(0, 400, plotid=i)
                pi = graph.plots[i]
                pi.value_range.margin = 0.5
                pi.value_range.tight_bounds = False

            graph.new_series(type='scatter',
                             marker='circle',
                             marker_size=1.25,
                             plotid=i)

        kw = dict(series=p.series_cnt, do_after=1)

        _debug = globalv.automated_run_debug
        p.series_cnt += 1
        ti = self.integration_time * 0.99 if not _debug else 0.1
        settle_time = ti * 1.1

        for _ in xrange(0, ncycles, 1):
            if not self._alive:
                return False

            for mi, iso in enumerate(isotopes):
                if not self._alive:
                    return False

                if masses:
                    mass = masses[mi]
                else:
                    mass = iso
                #position isotope onto detector
                self.set_position(mass, detector)
                time.sleep(settle_time)
                for _ni in xrange(int(nintegrations)):
                    if not self._alive:
                        return False

                    time.sleep(ti)
                    x = time.time() - starttime

                    if _debug:
                        v = random.random()
                        x *= 3
                    else:
                        v = spec.get_intensity(detector)

                    data_write_hook(x, detector, iso, v)
                    graph.add_datum((x, v), plotid=mi, **kw)

                    if x > graph.get_x_limits()[1]:
                        graph.set_x_limits(0, x + 10)

        return True

    def _equilibrate(self, evt, eqtime=15, inlet=None, outlet=None, delay=3):
#        eqtime = self.get_measurement_parameter('equilibration_time', default=15)
#        inlet = self.get_measurement_parameter('inlet_valve')
#        outlet = self.get_measurement_parameter('outlet_valve')
#        delay = self.get_measurement_parameter('inlet_delay', default=3)

        elm = self.extraction_line_manager
        if elm:
            if outlet:
                #close mass spec ion pump
                elm.close_valve(outlet, mode='script')

            if inlet:
                self.info('waiting {}s before opening inlet value {}'.format(delay, inlet))
                time.sleep(delay)
                #open inlet
                elm.open_valve(inlet, mode='script')

        evt.set()

        #delay for eq time
        self.info('equilibrating for {}sec'.format(eqtime))
        time.sleep(eqtime)
        if self._alive:
            self.info('====== Equilibration Finished ======')
            if elm and inlet:
                elm.close_valve(inlet)

            self.do_post_equilibration()
            self.overlap_evt.set()

    def _measure_iteration(self, grpname, data_write_hook,
                           ncounts, starttime, series, fits):
        self.info('measuring {}. ncounts={}'.format(grpname, ncounts))
        if not self.spectrometer_manager:
            self.warning('not spectrometer manager')
            return True

        spec = self.spectrometer_manager.spectrometer


        graph = self.plot_panel.graph
        for i in xrange(1, ncounts + 1, 1):
            if i > self.plot_panel.ncounts:
                self.info('measurement iteration executed {}/{} counts'.format(i, ncounts))
                break

            if self._truncate_signal:
                self.info('measurement iteration executed {}/{} counts'.format(i, ncounts))
                self._truncate_signal = False
                break

            if not self._alive:
                self.info('measurement iteration executed {}/{} counts'.format(i, ncounts))
                return False

            if i % 50 == 0:
                self.info('collecting point {}'.format(i))

            _debug = globalv.automated_run_debug
            m = self.integration_time * 0.99 if not _debug else 0.1
            time.sleep(m)

            if not _debug:
                data = spec.get_intensities(tagged=True)
                if data is not None:
                    keys, signals = data
#                keys, signals = zip(*data)
            else:
                keys = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']

                if series == 0:
                    signals = [10, 1000, 8, 8, 8, 3]
                elif series == 1:
                    r = random.randint(0, 10)
                    signals = [0.1, (0.015 * (i - 2800 + r)) ** 2,
                               0.1, 1, 0.1, (0.001 * (i - 2000 + r)) ** 2
                               ]
                else:
                    signals = [1, 2, 3, 4, 5, 6]

            if not keys or not signals:
                continue

            #if user forgot to set the time zero in measurement script
            #do it here
            if starttime is None:
                starttime = time.time()

            x = time.time() - starttime# if not self._debug else i + starttime

            self.signals = dict(zip(keys, signals))

            kw = dict(series=series, do_after=1,
                      update_y_limits=True,
                      ypadding='0.5'
                      )
            if len(graph.series[0]) < series + 1:
                kw['marker'] = 'circle'
                kw['type'] = 'scatter'
                kw['marker_size'] = 1.25
                func = lambda x, signal, kw: graph.new_series(x=[x],
                                                                 y=[signal],
                                                                 **kw
                                                                 )
            else:
                func = lambda x, signal, kw: graph.add_datum((x, signal), **kw)

            dets = self._active_detectors

            for pi, (fi, dn) in enumerate(zip(fits, dets)):
                signal = signals[keys.index(dn.name)]
                kw['plotid'] = pi
                kw['fit'] = fi
                func(x, signal, kw)

            mi, ma = graph.get_x_limits()
            dev = (ma - mi) * 0.05
            if (x + dev) > ma:
                graph.suppress_regression = True
                for j, _ in enumerate(graph.plots):
                    graph.set_x_limits(0, x + (ma - mi) * 0.25, plotid=j)
                graph.suppress_regression = False
            graph._update_graph()
            data_write_hook(x, keys, signals)

        return True




#===============================================================================
# save
#===============================================================================
    def pre_extraction_save(self):
        d = get_datetime()
        self._runtime = d.time()
        self._rundate = d.date()
        self.info('Analysis started at {}'.format(self._runtime))

    def _post_extraction_save(self):
        pass

    def _pre_measurement_save(self):
        self.info('pre measurement save')
        dm = self.data_manager
        #make a new frame for saving data


        name = uuid.uuid4()

#        path = os.path.join(self.repository.root, '{}.h5'.format(name))
        path = os.path.join(paths.isotope_dir, '{}.h5'.format(name))
        frame = dm.new_frame(path=path)

        #save some metadata with the file
        attrs = frame.root._v_attrs
        attrs['USER'] = self.username
        attrs['DATA_FORMAT_VERSION'] = '1.0'
        attrs['TIMESTAMP'] = time.time()
        attrs['ANALYSIS_TYPE'] = self.analysis_type

        frame.flush()

    def _post_measurement_save(self):
        self.info('post measurement save')

        cp = self.data_manager.get_current_path()

        uuid, _ext = os.path.splitext(os.path.basename(cp))

        #commit repository
#        self.repository.add_file(cp)

        #close h5 file
        self.data_manager.close()


#        np = self.repository.get_file_path(cp)

        ln = self.labnumber
        ln = convert_identifier(ln)
        aliquot = self.aliquot

        #save to local sqlite database for backup and reference

        ldb = self._local_lab_db_factory()

        ldb.add_analysis(labnumber=ln,
                         aliquot=aliquot,
                         collection_path=cp,
#                         repository_path=np,
                         commit=True)

        #save to a database
        db = self.db
        if db:
            lab = db.get_labnumber(ln)
            experiment = db.get_experiment(self.experiment_name)

            endtime = get_datetime().time()
            self.info('analysis finished at {}'.format(endtime))
            a = db.add_analysis(lab,
                                uuid=uuid,
                                runtime=self._runtime,
                                rundate=self._rundate,
                                endtime=endtime,
                                aliquot=aliquot,
                                step=self.step
                                )

            #added analysis to experiment
            experiment.analyses.append(a)

            #save extraction
            ext = self._save_extraction(a)

            #save measurement
            meas = self._save_measurement(a)

            #save sensitivity info to extraction 
            self._save_sensitivity(ext, meas)

            #use a path relative to the repo repo
#            np = os.path.relpath(np, self.repository.root)
#            db.add_analysis_path(np, analysis=a)

            self._save_spectrometer_info(meas)

            #do preliminary processing of data
            #returns signals dict and peak_center table
            ss, pc = self._preliminary_processing(cp)

            #add selected history
            _sh = db.add_selected_histories(a)
            self._save_isotope_info(a, ss)

            #save blanks
            self._save_blank_info(a)

            #save peak center
            self._save_peak_center(a, pc)

            if globalv.experiment_savedb:
                db.commit()

        #save to massspec
        self._save_to_massspec()

    def _preliminary_processing(self, p):
        dm = self.data_manager
        dm.open_data(p)
        signals = [(iso, detname)
                   for (iso, detname, kind) in self._save_isotopes
                   if kind == 'signal']
        baselines = [(iso, detname)
                   for (iso, detname, kind) in self._save_isotopes
                   if kind == 'baseline']
        sniffs = [(iso, detname)
                   for (iso, detname, kind) in self._save_isotopes
                   if kind == 'baseline']

        rsignals = dict()

        for fit, (iso, detname) in zip(self.fits, signals):
            tab = dm.get_table(detname, '/signal/{}'.format(iso))
            x, y = zip(*[(r['time'], r['value']) for r in tab.iterrows()])
            s = Signal(xs=x, ys=y, fit=fit)
            rsignals['{}signal'.format(iso)] = s

        self.baseline_fits = ['average_SEM', ] * len(baselines)
        for fit, (iso, detname) in zip(self.baseline_fits, baselines):
            tab = dm.get_table(detname, '/baseline/{}'.format(iso))
            x, y = zip(*[(r['time'], r['value']) for r in tab.iterrows()])
            bs = Signal(xs=x, ys=y, fit=fit)

            rsignals['{}baseline'.format(iso)] = bs

        for (iso, detname) in sniffs:
            tab = dm.get_table(detname, '/sniff/{}'.format(iso))
            x, y = zip(*[(r['time'], r['value']) for r in tab.iterrows()])
            sn = Signal(xs=x, ys=y)
            rsignals['{}sniff'.format(iso)] = sn

        peak_center = dm.get_table('peak_center', '/')

        return rsignals, peak_center

    def _save_sensitivity(self, extraction, measurement):
        #get the lastest sensitivity entry for this spectrometr
        spec = measurement.mass_spectrometer
        if spec:
            sens = spec.sensitivities
            if sens:
                extraction.sensitivity = sens[-1]

    def _save_peak_center(self, analysis, tab):
        if tab is not None:
            db = self.db
            packed_xy = [struct.pack('<ff', r['time'], r['value']) for r in tab.iterrows()]
            points = ''.join(packed_xy)
            center = tab.attrs.center_dac
            pc = db.add_peak_center(
                               analysis,
                               center=center, points=points)
            return pc

    def _save_measurement(self, analysis):
        db = self.db
        meas = db.add_measurement(
                              analysis,
                              self.analysis_type,
                              self.mass_spectrometer,
                              self.measurement_script.name,
                              script_blob=self.measurement_script.toblob()
                              )
        return meas

    def _save_extraction(self, analysis):
        db = self.db
        ext = db.add_extraction(analysis,
                          self.extraction_script.name,
                          script_blob=self.measurement_script.toblob(),
                          extract_device=self.extract_device,
                          experiment_blob=self.experiment_manager.experiment_blob(),
                          extract_value=self.extract_value,
                          position=self.position,
                          extract_duration=self.duration,
                          cleanup_duration=self.cleanup,
                          weight=self.weight,
                          sensitivity_multiplier=self.get_extraction_parameter('sensitivity_multiplier', default=1)
                          )
        return ext

    def _save_spectrometer_info(self, meas):
        db = self.db

        if self.spectrometer_manager:
            spec_dict = self.spectrometer_manager.make_parameters_dict()
            db.add_spectrometer_parameters(meas, **spec_dict)
            for det, deflection in self.spectrometer_manager.make_deflections_dict().iteritems():
                det = db.add_detector(det)
                db.add_deflection(meas, det, deflection)

    def _save_blank_info(self, analysis):
        self._save_history_info(analysis, 'blanks')

    def _save_history_info(self, analysis, name):
        db = self.db

        if self.analysis_type != 'unknown':
            return

        pb = getattr(self.experiment_manager, '_prev_{}'.format(name))
        if not pb:
            return

        user = self.username
        user = user if user else '---'

        funchist = getattr(db, 'add_{}_history'.format(name))
        self.info('{} adding {} history for {}-{}'.format(user, name, analysis.labnumber.labnumber, analysis.aliquot))
        history = funchist(analysis, user=user)

        setattr(analysis.selected_histories, 'selected_{}'.format(name), history)

        func = getattr(db, 'add_{}'.format(name))
        for isotope, v in pb.iteritems():
            uv = v.nominal_value
            ue = v.std_dev()
            func(history, user_value=uv, user_error=ue, isotope=isotope)

    def _save_isotope_info(self, analysis, signals):
        db = self.db

        #add fit history
        dbhist = db.add_fit_history(analysis, user=self.username)
        for iso, detname, kind in self._save_isotopes:
            det = db.get_detector(detname)
            if det is None:
                det = db.add_detector(detname)

            #add isotope
            dbiso = db.add_isotope(analysis, iso, det, kind=kind)

            s = signals['{}{}'.format(iso, kind)]

            #add signal data
            data = ''.join([struct.pack('>ff', x, y) for x, y in zip(s.xs, s.ys)])
            db.add_signal(dbiso, data)

            if s.fit:
                #add fit
                db.add_fit(dbhist, dbiso, fit=s.fit)

            if kind in ['signal', 'baseline']:
                #add isotope result
                db.add_isotope_result(dbiso,
                                      dbhist,
                                      signal_=s.value, signal_err=s.error,
                                      )

            db.flush()

#        if globalv.experiment_savedb:
#            db.commit()

    def _save_to_massspec(self):
        h = self.massspec_importer.db.host
        dn = self.massspec_importer.db.name
        self.info('saving to massspec database {}/{}'.format(h, dn))
#        #save to mass spec database
        dm = self.data_manager
        baselines = []
        signals = []
        detectors = []

        for isotope, detname, kind in self._save_isotopes:
            if kind == 'signal':
                detectors.append((detname, isotope))

                table = dm.get_table(detname, '/baseline/{}'.format(isotope))
                if table:
                    bi = [(row['time'], row['value']) for row in table.iterrows()]
                    baselines.append(bi)

                table = dm.get_table(detname, '/signal/{}'.format(isotope))
                if table:
                    si = [(row['time'], row['value']) for row in table.iterrows()]
                    signals.append(si)

        blanks = []
        pb = self.experiment_manager._prev_blanks
        for _di, iso in detectors:
            blanks.append(pb[iso])

        self.massspec_importer.add_analysis(self.labnumber,
                                            self.aliquot,
                                            self.step,
                                            self.labnumber,
                                            baselines,
                                            signals,
                                            blanks,
                                            detectors,
                                            self.regression_results
                                            )

#===============================================================================
# handlers
#===============================================================================
    def __labnumber_changed(self):
        self.labnumber = self._labnumber

    def _runner_changed(self):
        for s in ['measurement', 'extraction', 'post_equilibration', 'post_measurement']:
            sc = getattr(self, '{}_script'.format(s))
            if sc is not None:
                setattr(sc, 'runner', self.runner)

#===============================================================================
# factories
#===============================================================================
    def _load_script(self, name):

        ec = self.configuration
        if not ec:
            return

        fname = os.path.basename(ec['{}_script'.format(name)])
        if not fname:
            return

        if NULL_STR in fname:
            return
        fname = fname if fname.endswith('.py') else fname + '.py'

#        print self.scripts.keys(), fname
        if fname in self.scripts:
#            self.debug('script "{}" already loaded... cloning'.format(fname))
            s = self.scripts[fname]
            if s is not None:
                s = s.clone_traits()
                s.automated_run = self
                hdn = self.extract_device.replace(' ', '_').lower()
                an = self.analysis_type.split('_')[0]
                s.setup_context(position=self.position,
                                extract_value=self.extract_value,
                                extract_units=self.extract_units,
                                duration=self.duration,
                                cleanup=self.cleanup,
                                extract_device=hdn,
                                analysis_type=an
                                )
            return s
        else:

            self.info('loading script "{}"'.format(fname))
            func = getattr(self, '{}_script_factory'.format(name))
            s = func(ec)
            if s and os.path.isfile(s.filename):
                if s.bootstrap():
                    try:
                        s._test()
                        setattr(self, '_{}_script'.format(name), s)
                    except Exception, e:
                        self.warning(e)
                        self.warning_dialog('Invalid Scripta {}'.format(s.filename if s else 'None'))
                        self._executable = False
                        setattr(self, '_{}_script'.format(name), None)

                return s
            else:
                self._executable = False
                self.warning_dialog('Invalid Scriptb {}'.format(s.filename if s else 'None'))
    def measurement_script_factory(self, ec):
        ec = self.configuration
        mname = os.path.basename(ec['measurement_script'])
        mname = self._add_script_extension(mname)

        ms = MeasurementPyScript(root=os.path.dirname(ec['measurement_script']),
            name=mname,
            automated_run=self,
            runner=self.runner
            )
        return ms
#
    def extraction_script_factory(self, ec):
        key = 'extraction_script'
        return self._extraction_script_factory(ec, key)

    def post_measurement_script_factory(self, ec):
        key = 'post_measurement_script'
        return self._extraction_script_factory(ec, key)

    def post_equilibration_script_factory(self, ec):
        key = 'post_equilibration_script'
        return self._extraction_script_factory(ec, key)

    def _extraction_script_factory(self, ec, key):
        #get the klass
        source_dir = os.path.dirname(ec[key])
        file_name = os.path.basename(ec[key])

        file_name = self._add_script_extension(file_name)

        if os.path.isfile(os.path.join(source_dir, file_name)):
#        if file_name.endswith('.py'):
            klass = ExtractionLinePyScript
            hdn = self.extract_device.replace(' ', '_').lower()
            obj = klass(
                    root=source_dir,
                    name=file_name,
                    runner=self.runner
                    )
            an = self.analysis_type.split('_')[0]
#            print self.position, 'positino',an
            obj.setup_context(position=self.position,
                              duration=self.duration,
                              extract_value=self._extract_value,
                              extract_units=self._extract_units,
                              cleanup=self.cleanup,
                              extract_device=hdn,
                              analysis_type=an,
                              ramp_rate=self.ramp_rate
                              )

            return obj

    def _add_script_extension(self, name, ext='.py'):
        return name if name.endswith(ext) else name + ext

    def _local_lab_db_factory(self):
        if self.local_lab_db:
            return self.local_lab_db
        name = os.path.join(paths.hidden_dir, 'local_lab.db')
        #name = '/Users/ross/Sandbox/local.db'
        ldb = LocalLabAdapter(name=name)
        ldb.build_database()
        return ldb
#===============================================================================
# property get/set
#===============================================================================
    def _get_data_writer(self, grpname):
        dm = self.data_manager
        def write_data(x, keys, signals):
#            active = [d.name for d in self._active_detectors]
#            for key, si in zip(keys, signals):
#                if not key in active:
#                    continue
#                t = dm.get_table(key, '/{}'.format(grpname))
#                nrow = t.row
#                nrow['time'] = x
#                nrow['value'] = si
#                nrow.append()
#                t.flush()

            for det in self._active_detectors:
                k = det.name
                try:
                    t = dm.get_table(k,
                                    '/{}/{}'.format(grpname, det.isotope))
                    nrow = t.row
                    nrow['time'] = x
                    nrow['value'] = signals[keys.index(k)]
                    nrow.append()
                    t.flush()
                except AttributeError:
                    pass

        return write_data

    def _get_peakhop_data_writer(self, grpname):
        def write_data(x, det, iso, signal):
            '''
                root.peakhop.iso.det
            '''
            dm = self.data_manager
#            tab = dm.get_table(iso, '/{}/{}'.format(grpname, det))
            tab = dm.get_table(det, '/{}/{}'.format(grpname, iso))
            nrow = tab.row
            nrow['time'] = x
            nrow['value'] = signal
            nrow.append()
            tab.flush()

        return write_data

    def _get_yaml_parameter(self, script, key, default):
        m = ast.parse(script._text)
        docstr = ast.get_docstring(m)
        if docstr is not None:
            params = yaml.load(docstr)
            try:
                return params[key]
            except KeyError:
                pass
            except TypeError:
                self.warning('Invalid yaml docstring in {}. Could not retrieve {}'.format(script.name, key))

        return default

    @cached_property
    def _get_post_measurement_script(self):
        self._post_measurement_script = self._load_script('post_measurement')
        return self._post_measurement_script

    @cached_property
    def _get_post_equilibration_script(self):
        self._post_equilibration_script = self._load_script('post_equilibration')
        return self._post_equilibration_script

    @cached_property
    def _get_measurement_script(self):
        self._measurement_script = self._load_script('measurement')
        return self._measurement_script

    @cached_property
    def _get_extraction_script(self):
        self._extraction_script = self._load_script('extraction')
        return self._extraction_script

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, v):
        self._index = v

    @property
    def runid(self):
        return '{}-{}{}'.format(self.labnumber, self.aliquot, self.step)

    @property
    def analysis_type(self):
        return get_analysis_type(self.labnumber)

    @property
    def executable(self):
        a = True
        if self.check_executable:
            a = self.extraction_script is not None and \
                        self.measurement_script is not None and \
                            self._executable
        return a

    def _get_duration(self):
#        if self.heat_step:
#            d = self.heat_step.duration
#        else:
        d = self._duration
        return d

#    def _get_temp_or_power(self):
#        if self.heat_step:
#
#            t = self.heat_step.temp_or_power
#        else:
#            t = self._temp_or_power
#        return t
#    def _get_temp_or_power(self):
#        if self.heat_step:
#
#            t = self.heat_step.temp_or_power
#        else:
#            t = self._temp_or_power
#        return t
    def _get_extract_units(self):
        return self._extract_units
#        units = dict(t='temp', w='watts', p='percent')
#        if self._extract_units == '---':
#            return 'watts'
#
#        return units[self._extract_units[0]]

    def _set_extract_units(self, v):
        self._extract_units = v

    def _get_extract_value(self):
#        if self.heat_step:
#            v = self.heat_step.extract_value
#            u = self.heat_step.extract_units
#        else:
        v = self._extract_value
        return v
#        u = self._extract_units[0]
#        return (v, u)

#    @property
#    def extract_value_str(self):
#        return '{},{}'.format(*self.extract_value)

    def _validate_duration(self, d):
        return self._validate_float(d)

#    def _validate_temp_or_power(self, d):
#        return self._validate_float(d)
    def _validate_extract_value(self, d):
        return self._validate_float(d)

    def _validate_float(self, d):
        try:
            return float(d)
        except ValueError:
            pass

    def _set_duration(self, d):
        if d is not None:
#            if self.heat_step:
#                self.heat_step.duration = d
#            else:
            self._duration = d

    def _set_extract_value(self, t):
        if t is not None:
#            if self.heat_step:
#                self.heat_step.extract_value = t
#            else:
            self._extract_value = t
            if not t:
                self.extract_units = '---'
            elif self.extract_units == '---':
                self.extract_units = 'watts'

        else:
            self.extract_units = '---'

    def _get_state(self):
        return self._state

    def _set_state(self, s):
        if self._state != 'truncate':
            self._state = s

    def _get_step(self):
        if self._step == 0:
            return ''
        else:
            return ALPHAS[self._step - 1]

    @cached_property
    def _get_projects(self):
        prs = dict([(pi, pi.name) for pi in self.db.get_projects()])
        if prs:
            self.project = pi
        return prs

    def _get_labnumbers(self):
        lns = []
        if self.project:
            lns = [int(ln.labnumber)
                    for s in self.project.samples
                        for ln in s.labnumbers]
        return sorted(lns)
#===============================================================================
# views
#===============================================================================
    def _get_position_group(self):
        grp = VGroup(
                         Item('autocenter'),
                         Item('position'),
                         Item('multiposition', label='Multi. position run'),
                         Item('endposition'),
                         show_border=True,
                         label='Position'
                     )
        return grp

    def simple_view(self):
        ext_grp = VGroup(HGroup(Spring(springy=False, width=33),
                         Item('extract_value', label='Extract'),
                            spring,
                            Item('extract_units',
                                 show_label=False),
                            ),
                         Item('ramp_rate', label='Ramp Rate (C/s)'),
                         Item('duration', label='Duration'),
                         )
        pos_grp = self._get_position_group()
        v = View(VGroup(ext_grp,
                        pos_grp
                        )
                )
        return v

    def traits_view(self):

#        scripts = VGroup(
#                       Item('extraction_line_script_name',
#                        editor=EnumEditor(name='extraction_line_scripts'),
#                        label='Extraction'
#                        ),
#                       Item('measurement_script_name',
#                            editor=EnumEditor(name='measurement_scripts'),
#                            label='Measurement'
#                            ),
#                       label='Scripts',
#                       show_border=True
#                       )
        def readonly(n, **kw):
            return Item(n, style='readonly', **kw)


        sspring = lambda width = 17:Spring(springy=False, width=width)

        pos_grp = self._get_position_group()
        v = View(
                 VGroup(
                     Group(
                           Item('project', editor=EnumEditor(name='projects')),
                           HGroup(Item('labnumber'), Item('_labnumber',
                                                          show_label=False,
                                                          editor=EnumEditor(name='labnumbers'))),
                     readonly('sample'),
                     readonly('irrad_level', label='Irradiation'),

                     HGroup(sspring(width=33), Item('extract_value', label='Heat'),
                            spring,
                            Item('extract_units',
                                 show_label=False),
                            ),
                     Item('ramp_rate', label='Ramp Rate (C/s)'),
                     Item('duration', label='Duration'),
                     Item('weight'),
                     Item('comment'),

                     show_border=True,
                     label='Info'
                     ),
                     pos_grp,
#                     scripts,
                     )
                 )
        return v
#============= EOF =============================================

#    def do_regress(self, fits, series=0):
#        if not self._alive:
#            return
##        time_zero_offset = 0#int(self.experiment_manager.equilibration_time * 2 / 3.)
#        self.regression_results = dict()
#
#        reg = PolynomialRegressor()
#        dm = self.data_manager
#        ppp = self.peak_plot_panel
#        if ppp:
##            print ppp.isotopes
#            n = len(ppp.isotopes)
#            if isinstance(fits, str) or len(fits) < n:
#                fits = [fits[0], ] * n
#            for pi, (iso, fi) in enumerate(zip(ppp.isotopes, fits)):
#                tab = dm.get_table(ppp.detector, '/signals/{}'.format(iso))
#                if tab is None:
#                    continue
#
#                rdict = self._regress_graph(reg,
#                                            ppp.graph,
#                                            iso,
#                                            ppp.detector,
#                                            fi, tab, pi)
#                self.regression_results[ppp.detector + iso] = rdict
#                tab.attrs.fit = fi
#            ppp.series_cnt += 3
#
#        n = len(self._active_detectors)
#        if isinstance(fits, str) or len(fits) < n:
#            fits = [fits[0], ] * n
#
#        if self.plot_panel:
#            for pi, (dn, fi) in enumerate(zip(self._active_detectors, fits)):
#                tab = dm.get_table(dn.name, '/signals/{}'.format(dn.isotope))
#                if tab is None:
#                    continue
#
#                rdict = self._regress_graph(reg,
#                                            self.plot_panel.graph,
#                                            iso,
#                                            dn.name, fi, tab, pi)
#                self.regression_results[dn.name] = rdict
#                tab.attrs.fit = fi

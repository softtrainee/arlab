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
from traits.api import Any, Str, Int, CInt, List, Property, \
     Event, Float, Instance, Bool, cached_property, Dict, HasTraits, \
     String
from pyface.timer.api import do_after
#============= standard library imports ========================
import os
import time
import random
import ast
import yaml
import struct
from threading import Thread, Event as TEvent
from uncertainties import ufloat
#============= local library imports  ==========================
from src.globals import globalv

from src.loggable import Loggable
from src.pyscripts.measurement_pyscript import MeasurementPyScript
from src.pyscripts.extraction_line_pyscript import ExtractionLinePyScript
from src.experiment.utilities.mass_spec_database_importer import MassSpecDatabaseImporter
from src.helpers.datetime_tools import get_datetime
# from src.repo.repository import Repository
# from src.experiment.plot_panel import PlotPanel
from src.experiment.plot_panel_new import PlotPanel
from src.experiment.utilities.identifier import convert_identifier, make_rid, \
    make_runid
from src.database.adapters.local_lab_adapter import LocalLabAdapter
from src.paths import paths
from src.managers.data_managers.data_manager import DataManager
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.constants import NULL_STR, SCRIPT_KEYS, MEASUREMENT_COLOR, \
    EXTRACTION_COLOR
from src.experiment.automated_run.condition import TruncationCondition, \
    ActionCondition, TerminationCondition
from src.processing.arar_age import ArArAge
from src.processing.isotope import IsotopicMeasurement
from src.experiment.export.export_spec import ExportSpec
from src.ui.gui import invoke_in_main_thread


class RunInfo(HasTraits):
    sample = Str
    irrad_level = Str

#
class ScriptInfo(HasTraits):
    measurement_script_name = Str
    extraction_script_name = Str
    post_measurement_script_name = Str
    post_equilibration_script_name = Str


def assemble_script_blob(scripts, kinds=None):
    '''
        make one blob of all the script text
        
        return csv-list of names, blob
    '''
    if kinds is None:
        kinds = ['extraction', 'measurement', 'post_equilibration', 'post_measurement']

    ts = []
    for (name, blob), kind in zip(scripts, kinds):
        ts.append('#' + '=' * 79)
        ts.append('# {} SCRIPT {}'.format(kind.replace('_', ' ').upper(), name))
        ts.append('#' + '=' * 79)
        if blob:
            ts.append(blob)

    return 'Pychron Script', '\n'.join(ts)


class AutomatedRun(Loggable):
    spectrometer_manager = Any
    extraction_line_manager = Any
    experiment_manager = Any
    ion_optics_manager = Any
    data_manager = Instance(DataManager)

    db = Instance(IsotopeAdapter)
    local_lab_db = Instance(LocalLabAdapter)
    massspec_importer = Instance(MassSpecDatabaseImporter)
#    repository = Instance(Repository)

#    run_info = Instance(RunInfo, ())
    script_info = Instance(ScriptInfo, ())

    runner = Any
    monitor = Any
    plot_panel = Any
#    peak_plot_panel = Any
    arar_age = Instance(ArArAge)

    experiment_name = Str
    labnumber = Str
    step = Str
    aliquot = CInt
    user_defined_aliquot = False
    sample = Str
    irradiation = Str

    state = String
    extract_group = CInt
    extract_value = Float
    extract_units = Str(NULL_STR)

    mass_spectrometer = Str
    extract_device = Str
    duration = Float
    tray = Str
    position = Str
    endposition = Int
    multiposition = Bool
    autocenter = Bool
    overlap = CInt
    cleanup = CInt
    ramp_rate = Float

    weight = Float
    comment = Str
    pattern = Str

    ic_factor = Any

    analysis_type = Str
    disable_between_positions = Bool(False)

    scripts = Dict
    signals = Dict

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

    _rundate = None
    _runtime = None
    _timestamp = None

    valid_scripts = Dict
    _alive = False

    peak_center = None
    coincidence_scan = None

    username = None
    _save_isotopes = List
    update = Event
    _truncate_signal = Bool
    truncated = Bool
    measuring = Bool(False)
    dirty = Bool(False)

    uuid = Str

    termination_conditions = List
    truncation_conditions = List
    action_conditions = List

    _total_counts = 0
    _processed_signals_dict = None

    skip = Bool
    fits = List
    runid = Property

    info_color = None
    _equilibration_done = False
#===============================================================================
# pyscript interface
#===============================================================================
    def py_position_magnet(self, pos, detector, dac=False):
        if not self._alive:
            return
        self._set_magnet_position(pos, detector, dac=dac)



    def py_activate_detectors(self, dets):
        if not self._alive:
            return

        if not self.spectrometer_manager:
            self.warning('no spectrometer manager')
            return

        p = self._open_plot_panel(self.plot_panel, stack_order='top_to_bottom')
        self.plot_panel = p

        spec = self.spectrometer_manager.spectrometer
        self._active_detectors = [spec.get_detector(n) for n in dets]
        p.create(self._active_detectors)

        # set plot_panels, baselines, backgrounds
        p.baselines = baselines = self.experiment_manager._prev_baselines
        p.blanks = blanks = self.experiment_manager._prev_blanks
        p.correct_for_blank = True if (not self.analysis_type.startswith('blank') and not self.analysis_type.startswith('background')) else False

        # sync the arar_age object's signals
        if self.use_arar_age():
            if not blanks:
                blanks = dict(Ar40=(0, 0), Ar39=(0, 0), Ar38=(0, 0), Ar37=(0, 0), Ar36=(0, 0))

            for iso, v in blanks.iteritems():
                self.arar_age.set_blank(iso, v)

            if not baselines:
                baselines = dict(Ar40=(0, 0), Ar39=(0, 0), Ar38=(0, 0), Ar37=(0, 0), Ar36=(0, 0))

            for iso, v in baselines.iteritems():
                self.arar_age.set_baseline(iso, v)


#        g = p.graph
#        g.suppress_regression = True
#        # construct plot panels graph
#        for _, l in enumerate(dets):
#            det = spec.get_detector(l)
#            g.new_plot(ytitle='{} {} (fA)'.format(det.name, det.isotope))
#        g.set_x_limits(min=0, max=400)
#
#        g.suppress_regression = False
#        p.detectors = self._active_detectors


    def py_set_regress_fits(self, fits, series=0):
        n = len(self._active_detectors)
        if isinstance(fits, str):
            fits = [fits, ] * n
        elif isinstance(fits, tuple):
            if len(fits) == 1:
                fits = [fits[0], ] * n
#
        fits = list(fits)
        if self.plot_panel:
            self.plot_panel.fits = fits
        self.fits = fits

    def py_set_spectrometer_parameter(self, name, v):
        self.info('setting spectrometer parameter {} {}'.format(name, v))
        if self.spectrometer_manager:
            self.spectrometer_manager.spectrometer.set_parameter(name, v)

    def py_data_collection(self, ncounts, starttime, series=0):
        if not self._alive:
            return

        self.plot_panel._ncounts = ncounts
        self.plot_panel.isbaseline = False

        gn = 'signal'
        fits = self.fits
        if fits is None:
            fits = ['linear', ] * len(self._active_detectors)

        self._build_tables(gn, fits)
        check_conditions = True
        return self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series, fits,
                                check_conditions
                                )

    def py_equilibration(self, eqtime=None, inlet=None, outlet=None,
                         do_post_equilibration=True,
                         delay=None
                         ):

        evt = TEvent()
        if not self._alive:
            evt.set()
            return evt

        self.info('====== Equilibration Started ======')
        t = Thread(name='equilibration', target=self._equilibrate, args=(evt,),
                                                                   kwargs=dict(eqtime=eqtime,
                                                                                inlet=inlet,
                                                                                outlet=outlet,
                                                                                delay=delay,
                                                                                do_post_equilibration=do_post_equilibration)
                 )
        t.start()
        return evt

    def py_sniff(self, ncounts, starttime, series=0):
        if not self._alive:
            return

        if self.plot_panel:
            self.plot_panel._ncounts = ncounts
            self.plot_panel.isbaseline = False

        fits = ['', ] * len(self._active_detectors)
        gn = 'sniff'
        self._build_tables(gn)
        check_conditions = False
        return self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series, fits,
                                check_conditions
                                )

    def py_baselines(self, ncounts, starttime, mass, detector,
                    series=0, nintegrations=5, settling_time=4,
                    fit='average_SEM'
                    ):
        if not self._alive:
            return

        ion = self.ion_optics_manager
        invoke_in_main_thread(self.plot_panel.show)
#        self.plot_panel.show()

        if mass:
            if ion is not None:
                if detector is None:
                    detector = self._active_detectors[0].name
                ion.position(mass, detector, False)
                self.info('Delaying {}s for detectors to settle'.format(settling_time))
                time.sleep(settling_time)

        self.plot_panel._ncounts = ncounts
        self.plot_panel.isbaseline = True

        gn = 'baseline'
        fits = [fit, ] * len(self._active_detectors)
        self._build_tables(gn, fits=fits)
        check_conditions = False
        result = self._measure_iteration(gn,
                            self._get_data_writer(gn),
                            ncounts, starttime, series, fits,
                            check_conditions)

        if self.plot_panel:
            self.experiment_manager._prev_baselines = self.plot_panel.baselines

        return result

    def py_peak_hop(self, cycles, hops, starttime, series=0, group='signal'):
        if not self._alive:
            return

        self._build_peak_hop_tables(group, hops)
        writer = self._get_data_writer(group)

        return self._peak_hop(cycles, hops, writer,
                       starttime, series)


    def py_peak_center(self, **kw):
        if not self._alive:
            return
        ion = self.ion_optics_manager

        if ion is not None:
            self.debug('peak center started')
            ion.do_peak_center(new_thread=False, **kw)

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

    def py_coincidence_scan(self):
        sm = self.spectrometer_manager
        obj, t = sm.do_coincidence_scan()
        self.coincidence_scan = obj
        t.join()

#===============================================================================
# conditions
#===============================================================================
    def py_add_termination(self, attr, comp, value, start_count, frequency):
        '''
            attr must be an attribute of arar_age
        '''
        self.termination_conditions.append(TerminationCondition(attr, comp, value,
                                                                start_count,
                                                                frequency))
    def py_add_truncation(self, attr, comp, value, start_count, frequency):
        '''
            attr must be an attribute of arar_age
        '''
        self.truncation_conditions.append(TruncationCondition(attr, comp, value,
                                                                start_count,
                                                                frequency))
    def py_add_action(self, attr, comp, value, start_count, frequency, action, resume):
        '''
            attr must be an attribute of arar_age
        '''
        self.action_conditions.append(ActionCondition(attr, comp, value,
                                                                start_count,
                                                                frequency,
                                                                action=action,
                                                                resume=resume))
    def py_clear_conditions(self):
        self.clear_terminations()
        self.clear_truncations()
        self.clear_actions()

    def py_clear_terminations(self):
        self.termination_conditions = []

    def py_clear_truncations(self):
        self.truncation_conditions = []

    def py_clear_actions(self):
        self.action_conditions = []

#===============================================================================
#
#===============================================================================
#    def test(self):
#        def _test(script):
#            if script:
#                try:
#                    script.test()
#                except Exception, e:
#                    return
#            return True
#
#        for si in SCRIPT_KEYS:
#            setattr(self, '{}_script_dirty'.format(si), True)
#
#        ok = True
#        if not _test(self.measurement_script):
#            ok = False
#        elif not _test(self.extraction_script):
#            ok = False
#        elif not _test(self.post_measurement_script):
#            ok = False
#            return
#        elif not _test(self.post_equilibration_script):
#            ok = False
#
#        return ok

    def assemble_report(self):
        signal_string = ''
        signals = self.get_baseline_corrected_signals()
        if signals:
            for ai in self._active_detectors:
                det = ai.name
                iso = ai.isotope
                v = signals[iso]
                signal_string += '{} {} {}\n'.format(det, iso, v)

#        signal_string = '\n'.join(['{} {}'.format(k, v) for k, v in self.signals.iteritems()])
        age = ''
        if self.arar_age:
            age = self.arar_age.age
        age_string = 'age={}'.format(age)


        return '''runid={} timestamp={} {}
anaylsis_type={}        
#===============================================================================
# signals
#===============================================================================
{}
{}
'''.format(self.runid, self._rundate, self._runtime, self.analysis_type,
           signal_string, age_string)

    def get_baseline_corrected_signals(self):
        if self._processed_signals_dict is not None:
            d = dict()
            signals = self._processed_signals_dict
            for iso, _, kind in self._save_isotopes:
                if kind == 'signal':
                    si = signals['{}signal'.format(iso)]
                    bi = signals['{}baseline'.format(iso)]
                    d[iso] = si - bi
            return d

    def get_position_list(self):
        return self._make_iterable(self.position)

#===============================================================================
# run termination
#===============================================================================
    def cancel_run(self):
        '''
            terminate the measurement script immediately
            
            do post termination
                post_eq and post_meas
            don't save run
            
        '''
        self._save_enabled = False
        self.do_post_termination()

    def truncate_run(self):
        '''
            truncate the measurement script
        '''
        if self.measuring:
            self.measurement_script.truncate()

#===============================================================================
#
#===============================================================================

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
            self.plot_panel.automated_run = None
            self.plot_panel.on_trait_change(self._plot_panel_closed,
                                            'close_event', remove=True)
            self.plot_panel.close_ui()

#            del self.plot_panel

#        if self.peak_plot_panel:
#            self.peak_plot_panel.close_ui()

#        if self.peak_plot_panel:
#            self.peak_plot_panel.close_ui()

        if self.peak_center:
            self.peak_center.graph.close_ui()
#            del self.peak_center

        if self.coincidence_scan:
            self.coincidence_scan.graph.close_ui()

        if self.monitor:
            self.monitor.stop()

    def info(self, msg, color=None, *args, **kw):
        super(AutomatedRun, self).info(msg, *args, **kw)
        if self.experiment_manager:
            if color is None:
                color = self.info_color

            if color is None:
                color = 'light green'

            self.experiment_manager.info(msg, color=color, log=False)

    def get_measurement_parameter(self, key, default=None):
        return self._get_yaml_parameter(self.measurement_script, key, default)

    def get_extraction_parameter(self, key, default=None):
        return self._get_yaml_parameter(self.extraction_script, key, default)

    def use_arar_age(self):
        ln = self.labnumber
        if '-' in ln:
            ln = ln.split('-')[0]

        return self.analysis_type == 'unknown' or ln in ('c',)

    def start(self):
        def _start():
            if self.use_arar_age():
                # load arar_age object for age calculation
                self.arar_age = ArArAge()
                es = self.extraction_script
                if es is not None:
                    # get senstivity multiplier from extraction script
                    v = self._get_yaml_parameter(es, 'sensitivity_multiplier', default=1)
                    self.arar_age.sensitivity_multiplier = v

                ln = self.labnumber
                ln = convert_identifier(ln)
                ln = self.db.get_labnumber(ln)
                self.arar_age.labnumber_record = ln

            self.measuring = False
            self.update = True
            self.overlap_evt = TEvent()
            self.info('Start automated run {}'.format(self.runid))
            self._alive = True
            self._total_counts = 0

            # setup the scripts
            if self.measurement_script:
                self.measurement_script.reset(self)

            for si in ('extraction', 'post_measurement', 'post_equilibration'):
                script = getattr(self, '{}_script'.format(si))
                if script:
                    self._setup_context(script)

            return True

        if self.monitor is None:
            return _start()
        elif self.monitor.monitor():
            # immediately check the monitor conditions
            if self.monitor.check():
                return _start()

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
            time.sleep(1.0)

#===============================================================================
# doers
#===============================================================================
    def do_extraction(self):
        if not self._alive:
            return

        self.info_color = EXTRACTION_COLOR
        self.info('======== Extraction Started ========')
        self.state = 'extraction'
        self.extraction_script.manager = self.experiment_manager
        self.extraction_script.run_identifier = self.runid

#        self._pre_extraction_save()
        if self.extraction_script.execute():
            self._post_extraction_save()
            self.info('======== Extraction Finished ========')
            self.info_color = None
            return True
        else:
            self.do_post_equilibration()
            self.do_post_measurement()
            self.finish()

            self.info('======== Extraction Finished unsuccessfully ========', color='red')
            self.info_color = None
            return False

    def do_measurement(self):
        if not self._alive:
            return

        self.measurement_script.manager = self.experiment_manager
        # use a measurement_script to explicitly define
        # measurement sequence
        self.info_color = MEASUREMENT_COLOR
        self.info('======== Measurement Started ========')
        self.state = 'measurement'

        self._pre_measurement_save()
        self.measuring = True
        self._save_enabled = True

        if self.measurement_script.execute():
            if self._alive:
                self._post_measurement_save()

            self.info('======== Measurement Finished ========')
            self.measuring = False
            self.info_color = None
            return True
        else:
            self.do_post_equilibration()
            self.do_post_measurement()
            self.finish()

            self.info('======== Measurement Finished unsuccessfully ========', color='red')
            self.measuring = False
            self.info_color = None
            return False

    def do_post_measurement(self):
        if not self.post_measurement_script:
            return

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

    def do_post_equilibration(self):
        if self._equilibration_done:
            return

        self._equilibration_done = True

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

    def do_post_termination(self):
        self.info('========= Post Termination ========')
        self.do_post_equilibration()
        self.do_post_measurement()

    def _plot_panel_closed(self):
        if self.measuring:
            self.truncate('Immediate')

    def _open_plot_panel(self, plot_panel, stack_order='bottom_to_top'):

        if plot_panel is None:
            title = 'Plot Panel {}'.format(self.runid)
            if self.sample:
                title = '{} {}'.format(title, self.sample)
            if self.irradiation:
                title = '{} {}'.format(title, self.irradiation)

            plot_panel = PlotPanel(
                             window_y=0.05,  # + 0.01 * self.index,
                             window_x=0.6,  # + 0.01 * self.index,

                             window_title=title,
                             stack_order=stack_order,
                             arar_age=self.arar_age,
                             sample=self.sample,
                             irradiation=self.irradiation
    #                         signals=dict(),
                             )

            plot_panel.reset()
            plot_panel.on_trait_change(self._plot_panel_closed, 'close_event')
            self.experiment_manager.open_view(plot_panel)

        return plot_panel

    def _set_table_attr(self, name, grp, attr, value):
        dm = self.data_manager
        tab = dm.get_table(name, grp)
        setattr(tab.attrs, attr, value)
        tab.flush()

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

    def _build_peak_hop_tables(self, gn, hops):
        dm = self.data_manager
        dm.new_group(gn)

        for hopstr, _cnt in hops:
            for hi in hopstr.split(','):
                iso, det = map(str.strip, hi.split(':'))
                isogrp = dm.new_group(iso, parent='/{}'.format(gn))
                _t = dm.new_table(isogrp, det)
                self.debug('add group {} table {}'.format(iso, det))

    def _equilibrate(self, evt, eqtime=15, inlet=None, outlet=None,
                     delay=3,
                     do_post_equilibration=True
                     ):

        elm = self.extraction_line_manager
        if elm:
            if outlet:
                # close mass spec ion pump
                elm.close_valve(outlet, mode='script')

            if inlet:
                self.info('waiting {}s before opening inlet value {}'.format(delay, inlet))
                time.sleep(delay)
                # open inlet
                elm.open_valve(inlet, mode='script')

        evt.set()

        # delay for eq time
        self.info('equilibrating for {}sec'.format(eqtime))
        time.sleep(eqtime)
        if self._alive:
            self.info('======== Equilibration Finished ========')
            if elm and inlet:
                elm.close_valve(inlet)

            if do_post_equilibration:
                self.do_post_equilibration()
            self.overlap_evt.set()

    def _set_magnet_position(self, pos, detector, dac=False, update_labels=True):
        ion = self.ion_optics_manager

        if ion is not None:
            ion.position(pos, detector, dac)
            if update_labels:
                try:
                    # update the plot_panel labels
                    for det, pi in zip(self._active_detectors, self.plot_panel.graph.plots):
                        pi.y_axis.title = '{} {} (fA)'.format(det.name, det.isotope)
    #                self.plot_panel.isotopes = [d.isotope for d in self._active_detectors]
                except Exception, e:
                    print 'set_position exception', e

#===============================================================================
# measurement
#===============================================================================
    def _peak_hop(self, ncycles, hops, data_write_hook, starttime, series):
        '''
            ncycles: int
            hops: list of tuples 
            
                hop = 'Isotope:Det[,Isotope:Det,...]', Count
                
                ex. 
                hop = 'Ar40:H1,Ar36:CDD', 10
        '''
        if not self.spectrometer_manager:
            self.warning('not spectrometer manager')
            return

        spec = self.spectrometer_manager.spectrometer

        graph = self.plot_panel.graph

        integration_time = 1 / 2.
        settle_time = 2 / 10.

        ncounts = sum([ci for _h, ci in hops]) * ncycles
        self._total_counts += ncounts
        mi, ma = graph.get_x_limits()
        dev = (ma - mi) * 0.05
        if (self._total_counts + dev) > ma:
            graph.set_x_limits(0, self._total_counts + (ma - mi) * 0.25)

#        _debug = globalv.automated_run_debug
#        p.series_cnt += 1
#        ti = self.integration_time * 0.99 if not _debug else 0.1

        original_idx = [(di.name, di.isotope) for di in self._active_detectors]

        def idx_func(isot):
            '''
            '''
            return next((i for i, (n, ii) in enumerate(original_idx)
                                                    if ii == isot))

        for _ in xrange(0, ncycles, 1):
            if not self._alive:
                return False

            for hopstr , counts in hops:
                if not self._alive:
                    return False

                his = hopstr.split(',')
                isos, dets = zip(*[map(str.strip, hi.split(':')) for hi in  his])
#                dets = [hi.split(':')[1] for hi in  his]
#                dets = detstr.split(',')
                fits = [fi for fi, di in zip(self.fits,
                                             self._active_detectors)
                                      if di.name in dets]

                detector = dets[0]
                isotope = isos[0]

                self._set_magnet_position(isotope, detector, update_labels=False)
                time.sleep(settle_time)
                for _ in xrange(int(counts)):
                    if not self._alive:
                        return False

                    if starttime is None:
                        starttime = time.time()

                    x = time.time() - starttime
                    vs = spec.get_intensity(dets)
                    self.signals = dict(zip(dets, vs))

                    for signal, fi, iso in zip(vs, fits, isos):
                        pi = idx_func(iso)
                        if len(graph.series[pi]) < series + 1:
                            graph_kw = dict(marker='circle', type='scatter', marker_size=1.25)
                            func = lambda xi, yi, kw: graph.new_series(x=[xi],
                                                                             y=[yi],
                                                                             **kw
                                                                             )
                        else:
                            graph_kw = dict(series=series,
#                                             do_after=100,
                                            update_y_limits=True,
                                            ypadding='0.5')
                            func = lambda xi, yi, kw: graph.add_datum((xi, yi), **kw)

#                        print di, isotope, pi
                        graph_kw['plotid'] = pi
                        graph_kw['fit'] = fi
                        func(x, signal, graph_kw)

                    data_write_hook(x, dets, vs)
                    invoke_in_main_thread(graph._update_graph)
#                     do_after(100, graph._update_graph)
                    time.sleep(integration_time)

        return True

    def _measure_iteration(self, grpname, data_write_hook,
                           ncounts, starttime, series, fits, check_conditions):
        self.info('measuring {}. ncounts={}'.format(grpname, ncounts),
                  color=MEASUREMENT_COLOR)

        if not self.spectrometer_manager:
            self.warning('no spectrometer manager')
            return True

        self.truncated = False
        graph = self.plot_panel.graph
        self._total_counts += ncounts
        mi, ma = graph.get_x_limits()
        dev = (ma - mi) * 0.05
        if (self._total_counts + dev) > ma:
            graph.set_x_limits(0, self._total_counts + (ma - mi) * 0.25)

        dets = self._active_detectors
        spec = self.spectrometer_manager.spectrometer
        ncounts = int(ncounts)
        for i in xrange(1, ncounts + 1, 1):
            ck = self._check_iteration(i, ncounts, check_conditions)
            if ck == 'break':
                break
            elif ck == 'cancel':
                return False

            if i % 50 == 0:
                self.info('collecting point {}'.format(i))

            _debug = globalv.automated_run_debug
            m = self.integration_time * 0.99 if not _debug else 0.1
            time.sleep(m)
            data = spec.get_intensities(tagged=True)
            if data is not None:
                keys, signals = data
            else:

                keys, signals = ('H2', 'H1', 'AX', 'L1', 'L2', 'CDD'), (1, 2, 3, 4, 5, 6)
#                continue

            # if user forgot to set the time zero in measurement script
            # do it here
            if starttime is None:
                starttime = time.time()

            x = time.time() - starttime  # if not self._debug else i + starttime

            self.signals = dict(zip(keys, signals))

            if len(graph.series[0]) < series + 1:
                graph_kw = dict(marker='circle', type='scatter', marker_size=1.25)
                func = lambda x, signal, kw: graph.new_series(x=[x],
                                                                 y=[signal],
                                                                 **kw
                                                                 )
            else:
                graph_kw = dict(series=series, do_after=None,
                                update_y_limits=True,
                                ypadding='0.5')
                func = lambda x, signal, kw: graph.add_datum((x, signal), **kw)



            for pi, (fi, dn) in enumerate(zip(fits, dets)):
                signal = signals[keys.index(dn.name)]
                graph_kw['plotid'] = pi
                graph_kw['fit'] = fi
                func(x, signal, graph_kw)

            data_write_hook(x, keys, signals)
            invoke_in_main_thread(graph._update_graph)
#             do_after(100, graph._update_graph)

        return True


    def _check_conditions(self, conditions, cnt):
        for ti in conditions:
            if ti.check(self.arar_age, cnt):
                return ti

    def _check_iteration(self, i, ncounts, check_conditions):
        if self.plot_panel is None:
            return 'break'

        n = i - 1
        if check_conditions:
            termination_condition = self._check_conditions(self.termination_conditions, i)
            if termination_condition:
                self.info('termination condition {}. measurement iteration executed {}/{} counts'.format(termination_condition.message, n, ncounts),
                          color='red'
                          )
                return 'cancel'

            truncation_condition = self._check_conditions(self.truncation_conditions, i)
            if truncation_condition:
                self.info('truncation condition {}. measurement iteration executed {}/{} counts'.format(truncation_condition.message, n, ncounts),
                          color='red'
                          )
                self.truncated = True
                return 'break'

            action_condition = self._check_conditions(self.action_conditions, i)
            if action_condition:
                self.info('action condition {}. measurement iteration executed {}/{} counts'.format(action_condition.message, n, ncounts),
                          color='red'
                          )
                action_condition.perform(self.measurement_script)
                if not action_condition.resume:
                    return 'break'

        if i > self.measurement_script.ncounts:
            self.info('script termination. measurement iteration executed {}/{} counts'.format(i, ncounts))
            return 'break'

        if i > self.plot_panel.ncounts:
            self.info('user termination. measurement iteration executed {}/{} counts'.format(i, ncounts))
            self._total_counts -= (ncounts - i)
            return 'break'

        if self._truncate_signal:
            self.info('measurement iteration executed {}/{} counts'.format(i, ncounts))
            self._truncate_signal = False
            return 'break'

        if not self._alive:
            self.info('measurement iteration executed {}/{} counts'.format(i, ncounts))
            return 'cancel'

#===============================================================================
# save
#===============================================================================
    def pre_extraction_save(self):
        d = get_datetime()
        self._timestamp = d
        self._runtime = d.time()
        self._rundate = d.date()
        self.info('Analysis started at {}'.format(self._runtime))

    def _post_extraction_save(self):
        pass

    def _pre_measurement_save(self):
        self.info('pre measurement save')
        dm = self.data_manager
        # make a new frame for saving data

#        name = uuid.uuid4()
#        self.uuid = str(name)
        name = self.uuid
        path = os.path.join(paths.isotope_dir, '{}.h5'.format(name))
        frame = dm.new_frame(path=path)

        # save some metadata with the file
        attrs = frame.root._v_attrs
        attrs['USER'] = self.username
        attrs['DATA_FORMAT_VERSION'] = '1.0'
        attrs['TIMESTAMP'] = time.time()
        attrs['ANALYSIS_TYPE'] = self.analysis_type

        frame.flush()

    def _post_measurement_save(self):
        self.info('post measurement save')

        if not self._save_enabled:
            self.info('Database saving disabled')
            return

        cp = self.data_manager.get_current_path()
        # close h5 file
        self.data_manager.close_file()

        # do preliminary processing of data
        # returns signals dict and peak_center table
        ss, pc = self._preliminary_processing(cp)
        self._processed_signals_dict = ss

        ln = self.labnumber
#        ln = convert_identifier(ln)
        aliquot = self.aliquot

        # save to local sqlite database for backup and reference

        ldb = self._local_lab_db_factory()

        ldb.add_analysis(labnumber=ln,
                         aliquot=aliquot,
                         collection_path=cp,
                         )
        ldb.commit()

        # save to a database
        db = self.db
        if db and db.connect(force=True):
            pt = time.time()

            lab = db.get_labnumber(ln)
            experiment = db.get_experiment(self.experiment_name)
            if experiment is None:
                experiment = db.add_experiment(self.experiment_name)
            endtime = get_datetime().time()
            self.info('analysis finished at {}'.format(endtime))

            dbuser = db.get_user(self.username)
            if dbuser is None:
                self.debug('user= {} does not existing. adding to database now'.format(self.username))
                dbuser = db.add_user(self.username)

            a = db.add_analysis(lab,
                                user=dbuser,
                                uuid=self.uuid,
                                endtime=endtime,
                                aliquot=aliquot,
                                step=self.step,
                                comment=self.comment
                                )

            # added analysis to experiment
            experiment.analyses.append(a)

            # save extraction
            ext = self._save_extraction(a)

            # save measurement
            meas = self._save_measurement(a)

            # save sensitivity info to extraction
            self._save_sensitivity(ext, meas)

            self._save_spectrometer_info(meas)

            # add selected history

            db.add_selected_histories(a)
            self._save_isotope_info(a, ss)

            # save ic factor
            self._save_detector_intercalibration(a)

            # save blanks
            self._save_blank_info(a)

            # save peak center
            self._save_peak_center(a, pc)

            # save monitor
            self._save_monitor_info(a)

            db.commit()

            # tell the executor to remove this run from backup run recovery
            self.experiment_manager.remove_backup(self.uuid)

            self.debug('pychron save time= {:0.3f} '.format(time.time() - pt))

        # save to massspec
        mt = time.time()
        self._save_to_massspec()
        self.debug('mass spec save time= {:0.3f}'.format(time.time() - mt))

    def _preliminary_processing(self, p):
        self.info('organizing data for database save')
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
                   if kind == 'sniff']

        rsignals = dict()

        for fit, (iso, detname) in zip(self.fits, signals):
            tab = dm.get_table(detname, '/signal/{}'.format(iso))
            x, y = zip(*[(r['time'], r['value']) for r in tab.iterrows()])
#            if iso=='Ar40':
#                print 'prelim signal,',len(x), x[0], x[-1]

            s = IsotopicMeasurement(xs=x, ys=y, fit=fit)
            rsignals['{}signal'.format(iso)] = s

        self.baseline_fits = ['average_SEM', ] * len(baselines)
        for fit, (iso, detname) in zip(self.baseline_fits, baselines):
            tab = dm.get_table(detname, '/baseline/{}'.format(iso))
            x, y = zip(*[(r['time'], r['value']) for r in tab.iterrows()])
            bs = IsotopicMeasurement(xs=x, ys=y, fit=fit)

            rsignals['{}baseline'.format(iso)] = bs

        for (iso, detname) in sniffs:
            tab = dm.get_table(detname, '/sniff/{}'.format(iso))
            x, y = zip(*[(r['time'], r['value']) for r in tab.iterrows()])
            sn = IsotopicMeasurement(xs=x, ys=y)
            rsignals['{}sniff'.format(iso)] = sn

        peak_center = dm.get_table('peak_center', '/')

        return rsignals, peak_center

    def _time_save(self, func, name, *args, **kw):
        st = time.time()
        r = func(*args, **kw)
        self.debug('save {} time= {:0.3f}'.format(name, time.time() - st))
        return r

    def _save_sensitivity(self, extraction, measurement):
        self.info('saving sensitivity')
        def func():
            # get the lastest sensitivity entry for this spectrometr
            spec = measurement.mass_spectrometer
            if spec:
                sens = spec.sensitivities
                if sens:
                    extraction.sensitivity = sens[-1]

        return self._time_save(func, 'sensitivity')



    def _save_peak_center(self, analysis, tab):
        self.info('saving peakcenter')
        def func():
            if tab is not None:
                db = self.db
                packed_xy = [struct.pack('<ff', r['time'], r['value']) for r in tab.iterrows()]
                points = ''.join(packed_xy)
                center = tab.attrs.center_dac
                pc = db.add_peak_center(
                                   analysis,
                                   center=float(center), points=points)
                return pc
        return self._time_save(func, 'peakcenter')

    def _save_measurement(self, analysis):
        self.info('saving measurement')
        def func():
            db = self.db

            meas = db.add_measurement(
                                  analysis,
                                  self.analysis_type,
                                  self.mass_spectrometer,
    #                              self.measurement_script.name,
    #                              script_blob=self.measurement_script.toblob()
                                  )
            script = db.add_script(self.measurement_script.name,
                                self.measurement_script.toblob())
            script.measurements.append(meas)

            return meas
        return self._time_save(func, 'measurement')

    def _save_extraction(self, analysis):
        self.info('saving extraction')
        def func():
            db = self.db
            ext = db.add_extraction(analysis,
    #                          self.extraction_script.name,
    #                          script_blob=self._assemble_extraction_blob(),
                              extract_device=self.extract_device,
    #                          experiment_blob=self.experiment_manager.experiment_blob(),
                              extract_value=self.extract_value,
    #                          position=self.position,
                              extract_duration=self.duration,
                              cleanup_duration=self.cleanup,
                              weight=self.weight,
                              sensitivity_multiplier=self.get_extraction_parameter('sensitivity_multiplier', default=1)
                              )

            exp = db.add_script(self.experiment_manager.experiment_queue.name,
                              self.experiment_manager.experiment_blob()
                              )
            exp.experiments.append(ext)

            if self.extraction_script:
                script = db.add_script(self.extraction_script.name,
                                       self._assemble_extraction_blob())
                script.extractions.append(ext)

            for pi in self.get_position_list():
                if isinstance(pi, tuple):
                    if len(pi) > 1:
                        db.add_analysis_position(ext, x=pi[0], y=pi[1])
                        if len(pi) == 3:
                            db.add_analysis_position(ext, x=pi[0], y=pi[1], z=pi[2])

                else:
                    db.add_analysis_position(ext, pi)

            return ext
        return self._time_save(func, 'extraction')


    def _save_spectrometer_info(self, meas):
        self.info('saving spectrometer info')
        def func():
            db = self.db
            if self.spectrometer_manager:
                spec_dict = self.spectrometer_manager.make_parameters_dict()
                db.add_spectrometer_parameters(meas, spec_dict)
                for det, deflection in self.spectrometer_manager.make_deflections_dict().iteritems():
                    det = db.add_detector(det)
                    db.add_deflection(meas, det, deflection)
        return self._time_save(func, 'spectrometer_info')

    def _save_detector_intercalibration(self, analysis):
        self.info('saving detector intercalibration')

        if self.arar_age:
            self.ic_factor = ic = self.arar_age.ic_factor

        else:
            self.ic_factor = ic = ArArAge(application=self.application).ic_factor

        def func():
            self.info('default ic_factor={}'.format(ic))
            db = self.db
            user = self.username
            user = user if user else NULL_STR

            name = 'detector_intercalibration'
            funchist = getattr(db, 'add_{}_history'.format(name))
            self.info('{} adding {} history for {}'.format(user, name, self.runid))
            history = funchist(analysis, user=user)

            setattr(analysis.selected_histories, 'selected_{}'.format(name), history)

            func = getattr(db, 'add_{}'.format(name))
            uv, ue = ic.nominal_value, ic.std_dev
            func(history, 'CDD', user_value=uv, user_error=float(ue))
        return self._time_save(func, 'detector intercalibration')

    def _save_blank_info(self, analysis):
        self.info('saving blank info')
        return self._time_save(self._save_history_info, 'blank info', analysis, 'blanks')

    def _save_history_info(self, analysis, name):
        db = self.db

        if self.analysis_type.startswith('blank') or \
            self.analysis_type.startswith('background'):
            return

        pb = getattr(self.experiment_manager, '_prev_{}'.format(name))
        if not pb:
            return

        user = self.username
        user = user if user else '---'

        funchist = getattr(db, 'add_{}_history'.format(name))
        self.info('{} adding {} history for {}-{}'.format(user, name, analysis.labnumber.identifier, analysis.aliquot))
        history = funchist(analysis, user=user)

        setattr(analysis.selected_histories, 'selected_{}'.format(name), history)

        func = getattr(db, 'add_{}'.format(name))
        for isotope, v in pb.iteritems():
            uv = v.nominal_value
            ue = float(v.std_dev)
            func(history, user_value=uv, user_error=ue, isotope=isotope)

    def _save_isotope_info(self, analysis, signals):
        self.info('saving isotope info')
        def func():
            db = self.db

            # add fit history
            dbhist = db.add_fit_history(analysis, user=self.username)
            for iso, detname, kind in self._save_isotopes:
                st = time.time()

                det = db.get_detector(detname)
                if det is None:
                    det = db.add_detector(detname)
#                    db.flush()

                # add isotope
                dbiso = db.add_isotope(analysis, iso, det, kind=kind)

                s = signals['{}{}'.format(iso, kind)]

                # add signal data
                data = ''.join([struct.pack('>ff', x, y) for x, y in zip(s.xs, s.ys)])

                db.add_signal(dbiso, data)

                if s.fit:
                    # add fit
                    db.add_fit(dbhist, dbiso, fit=s.fit)

                if kind in ['signal', 'baseline']:
                    # add isotope result
                    db.add_isotope_result(dbiso,
                                          dbhist,
                                          signal_=float(s.value), signal_err=float(s.error),
                                          )

                db.flush()
                self.debug('isotope {}{} save time= {:0.3f}'.format(iso, kind, time.time() - st))

        return self._time_save(func, 'isotope info')

#        if globalv.experiment_savedb:
#            db.commit()
    def _save_monitor_info(self, analysis):
        if self.monitor:
            self.info('saving monitor info')
            def func():
                for ci in self.monitor.checks:
                    data = ''.join([struct.pack('>ff', x, y) for x, y in ci.data])
                    params = dict(name=ci.name,
                                  parameter=ci.parameter, criterion=ci.criterion,
                                  comparator=ci.comparator, tripped=ci.tripped,
                                  data=data)

                    self.db.add_monitor(analysis, **params)
            return self._time_save(func, 'monitor info')

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
            if iso in pb:
                blanks.append(pb[iso])
            else:
                blanks.append(ufloat(0, 0))

#        signals=self._processed_signals_dict
#        sig_ints = dict()
#        base_ints = dict()
        sig_ints = []
        base_ints = []
#        for k,v in self._processed_signals_dict:
        psignals = self._processed_signals_dict
        for iso, _, kind in self._save_isotopes:
            if kind == 'signal':
                si = psignals['{}signal'.format(iso)]
                bi = psignals['{}baseline'.format(iso)]
                sig_ints.append(si.uvalue)
                base_ints.append(bi.uvalue)
#                sig_ints[iso] = si.uvalue
#                base_ints[iso] = bi.uvalue

        baseline_fits = ['Average Y', ] * len(self._active_detectors)

        rs_name, rs_text = self._assemble_script_blob()

        exp = ExportSpec(rid=make_rid(self.labnumber, self.aliquot, self.step),
                         runscript_name=rs_name,
                         runscript_text=rs_text,
                         signal_fits=self.fits,
                         baseline_fits=baseline_fits,
                         signal_intercepts=sig_ints,
                         baseline_intercepts=base_ints,
                         spectrometer='Pychron {}'.format(self.mass_spectrometer.capitalize()),
                         baselines=baselines,
                         signals=signals,
                         blanks=blanks,
                         detectors=detectors,
                         )

        exp.load_record(self)

#        self.massspec_importer.add_analysis(exp)
#        self.info('analysis added to mass spec database')
        try:
            self.massspec_importer.add_analysis(exp)
            self.info('analysis added to mass spec database')
        except Exception:
            import traceback
            tb = traceback.format_exc()
            self.message('Could not save to Mass Spec database.\n {}'.format(tb))
            self.cancel()
            self.experiment_manager.cancel()

    def _assemble_extraction_blob(self):
        _names, txt = self._assemble_script_blob(kinds=('extraction', 'post_equilibration', 'post_measurement'))
        return txt

    def _assemble_script_blob(self, kinds=None):
        if kinds is None:
            kinds = 'extraction', 'measurement', 'post_equilibration', 'post_measurement'
        okinds = []
        bs = []
        for s in kinds:  # ('extraction', 'post_equilibration', 'post_measurement'):
            sc = getattr(self, '{}_script'.format(s))
            if sc is not None:
                bs.append((sc.name, sc.toblob()))
                okinds.append(s)

        return assemble_script_blob(bs, kinds=okinds)

#===============================================================================
# handlers
#===============================================================================
    def _runner_changed(self):
        for s in ['measurement', 'extraction', 'post_equilibration', 'post_measurement']:
            sc = getattr(self, '{}_script'.format(s))
            if sc is not None:
                setattr(sc, 'runner', self.runner)

#===============================================================================
# factories
#===============================================================================
    def _load_script(self, name):
        script = None
        sname = getattr(self.script_info, '{}_script_name'.format(name))

        if sname and sname != NULL_STR:
            sname = self._make_script_name(sname)
            if sname in self.scripts:
                script = self.scripts[sname]
                if script.check_for_modifications():
                    self.debug('script {} modified reloading'.format(sname))
                    script = self._bootstrap_script(sname, name)
            else:
                script = self._bootstrap_script(sname, name)

        return script

    def _bootstrap_script(self, fname, name):
        self.info('loading script "{}"'.format(fname))
        func = getattr(self, '{}_script_factory'.format(name))
        s = func()
        valid = True
        if s and os.path.isfile(s.filename):
            if s.bootstrap():
                s.set_default_context()
                try:
                    s.test()
#                    s.test()
# #                    setattr(self, '_{}_script'.format(name), s)
#
                except Exception, e:
                    self.warning(e)
                    self.warning_dialog('Invalid Scripta {}'.format(e))
                    valid = False
#                    setattr(self, '_{}_script'.format(name), None)
        else:
            valid = False
            self.warning_dialog('Invalid Scriptb {}'.format(s.filename if s else fname))

        self.valid_scripts[name] = valid
        return s

    def measurement_script_factory(self):

        sname = self.script_info.measurement_script_name
        root = paths.measurement_dir
        sname = self._make_script_name(sname)

        ms = MeasurementPyScript(root=root,
            name=sname,
#            automated_run=self,
            runner=self.runner
            )
        return ms
#
    def extraction_script_factory(self):
        root = paths.extraction_dir
        return self._extraction_script_factory(root, self.script_info.extraction_script_name)

    def post_measurement_script_factory(self):
        root = paths.post_measurement_dir
        return self._extraction_script_factory(root, self.script_info.post_measurement_script_name)

    def post_equilibration_script_factory(self):
        root = paths.post_equilibration_dir
        return self._extraction_script_factory(root, self.script_info.post_equilibration_script_name)

    def _make_iterable(self, pos):
        if '(' in pos and ')' in pos and ',' in pos:
            # interpret as (x,y)
            pos = pos.strip()[1:-1]
            ps = [map(float, pos.split(','))]

        elif ',' in pos:
            # interpert as list of holenumbers
#            ps = map(int, pos.split(','))
            ps = list(pos.split(','))
        else:
#            if pos:
#                pos = int(pos)

            ps = [pos]

        return ps

    def _make_script_name(self, name):
        name = '{}_{}'.format(self.mass_spectrometer.lower(), name)
        name = self._add_script_extension(name)
        return name

    def _extraction_script_factory(self, root, file_name):
        file_name = self._make_script_name(file_name)
        if os.path.isfile(os.path.join(root, file_name)):
            klass = ExtractionLinePyScript
            obj = klass(
                    root=root,
                    name=file_name,
                    runner=self.runner
                    )



            return obj

    def _setup_context(self, script):
        '''
            setup_context to expose variables to the pyscript
        '''
        hdn = self.extract_device.replace(' ', '_').lower()
        an = self.analysis_type.split('_')[0]
        script.setup_context(tray=self.tray,
                          position=self.get_position_list(),
                          disable_between_positions=self.disable_between_positions,
                          duration=self.duration,
                          extract_value=self.extract_value,
                          extract_units=self.extract_units,
                          cleanup=self.cleanup,
                          extract_device=hdn,
                          analysis_type=an,
                          ramp_rate=self.ramp_rate,
                          pattern=self.pattern
                          )

    def _add_script_extension(self, name, ext='.py'):
        return name if name.endswith(ext) else name + ext

    def _local_lab_db_factory(self):
        if self.local_lab_db:
            return self.local_lab_db
        name = os.path.join(paths.hidden_dir, 'local_lab.db')
        # name = '/Users/ross/Sandbox/local.db'
        ldb = LocalLabAdapter(name=name)
        ldb.build_database()
        return ldb
#===============================================================================
# property get/set
#===============================================================================
    def _get_data_writer(self, grpname, dets=None):
        dm = self.data_manager
        if dets is None:
            dets = self._active_detectors

        def write_data(x, keys, signals):
            for det in dets:
                k = det.name
                try:
                    if k in keys:
                        t = dm.get_table(k,
                                        '/{}/{}'.format(grpname, det.isotope))

                        nrow = t.row
                        nrow['time'] = x
                        nrow['value'] = signals[keys.index(k)]
                        nrow.append()
                        t.flush()
                except AttributeError, e:
                    self.debug('{} {} {}'.format(e, grpname, det.isotope))

        return write_data

#    def _get_peakhop_data_writer(self, grpname):
#        def write_data(x, det, iso, signal):
#            '''
#                root.peakhop.iso.det
#            '''
#            dm = self.data_manager
# #            tab = dm.get_table(iso, '/{}/{}'.format(grpname, det))
#            tab = dm.get_table(det, '/{}/{}'.format(grpname, iso))
#            nrow = tab.row
#            nrow['time'] = x
#            nrow['value'] = signal
#            nrow.append()
#            tab.flush()
#
#        return write_data

    def _get_yaml_parameter(self, script, key, default):
        if not script:
            return default

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

    def _get_runid(self):
        return make_runid(self.labnumber, self.aliquot, self.step)



#============= EOF =============================================

# def _peak_hop_factory(self, detector, isotopes, ncycles, nintegrations, starttime, series,
#                          name='',
#                          masses=None
#                          ):
#        if not self.spectrometer_manager:
#            self.warning('not spectrometer manager')
#            return
#        add_plot = False
#        p = self.peak_plot_panel
#        if p is None:
# #        name = 'peakhop_{}'.format(name)
#            p = self._open_plot_panel(stack_order='top_to_bottom')
#            self.peak_plot_panel = p
#            add_plot = True
#            p.series_cnt = 0
#
#        p.detector = detector
# #        p.isotopes = isotopes
# #        p._ncounts = ncycles
#
#        dm = self.data_manager
# #        db = self.db
# #        dm.new_group('peakhop', root='/')
# #        grp = dm.new_group(detector, parent=grp)
#
#        # get/add the detector to db
#
#        pgrp = dm.new_group(name)
#        for iso in isotopes:
#            grp = dm.new_group(iso, parent=pgrp)
#            dm.new_table(grp, detector)
#
#            # add isotope to db
# #            db.add_isotope(iso, det, kind=name)
#            self._save_isotopes.append((iso, detector, name))
#
#        data_write_hook = self._get_peakhop_data_writer(name)
#
#        self.info('peak hopping {} on {}'.format(','.join(isotopes), detector))
# #        spec = None
#        spec = self.spectrometer_manager.spectrometer
#
#        graph = self.peak_plot_panel.graph
#        for i, iso in enumerate(isotopes):
#            if add_plot:
#                graph.new_plot(xtitle='Time (s)',
#                           ytitle='{}'.format(iso))
#
#                graph.set_x_limits(0, 400, plotid=i)
#                pi = graph.plots[i]
#                pi.value_range.margin = 0.5
#                pi.value_range.tight_bounds = False
#
#            graph.new_series(type='scatter',
#                             marker='circle',
#                             marker_size=1.25,
#                             plotid=i)
#
#        kw = dict(series=p.series_cnt, do_after=1)
#
#        _debug = globalv.automated_run_debug
#        p.series_cnt += 1
#        ti = self.integration_time * 0.99 if not _debug else 0.1
#        settle_time = ti * 1.1
#
#        for _ in xrange(0, ncycles, 1):
#            if not self._alive:
#                return False
#
#            for mi, iso in enumerate(isotopes):
#                if not self._alive:
#                    return False
#
#                if masses:
#                    mass = masses[mi]
#                else:
#                    mass = iso
#                # position isotope onto detector
#                self.set_position(mass, detector)
#                time.sleep(settle_time)
#                for _ni in xrange(int(nintegrations)):
#                    if not self._alive:
#                        return False
#
#                    time.sleep(ti)
#                    x = time.time() - starttime
#
#                    if _debug:
#                        v = random.random()
#                        x *= 3
#                    else:
#                        v = spec.get_intensity(detector)
#
#                    data_write_hook(x, detector, iso, v)
#                    graph.add_datum((x, v), plotid=mi, **kw)
#
#                    if x > graph.get_x_limits()[1]:
#                        graph.set_x_limits(0, x + 10)
#
#        return True
#===============================================================================
# views
#===============================================================================
#    def _get_position_group(self):
#        grp = VGroup(
# #                         Item('autocenter',
# #                              tooltip='Should the extract device try to autocenter on the sample'
# #                              ),
#                         HGroup(Item('position',
#                                     tooltip='Set the position for this analysis. Examples include 1, P1, L2, etc...'
#                                     ),
#                                Item('endposition', label='End')
#                                ),
# #                         Item('multiposition', label='Multi. position run'),
#                         show_border=True,
#                         label='Position'
#                     )
#        return grp

#    def _get_supplemental_extract_group(self):
#        pass
#
#    def simple_view(self):
#        ext_grp = VGroup(
# #                         HGroup(Spring(springy=False, width=33),
#                         HGroup(Item('labnumber', style='readonly'),
#                                Item('aliquot'),
#                                Item('step')
#                                ),
#                         HGroup(
#                                Item('extract_value', label='Extract'),
#                                spring,
#                                Item('extract_units', editor=EnumEditor(name='extract_units_names'),
#                                     show_label=False)
#                                ),
#                         Item('ramp_rate', label='Ramp Rate (C/s)'),
#                         Item('duration', label='Duration'),
#                         label='Extract'
#                         )
#
#        pos_grp = self._get_position_group()
#        grp = Group(ext_grp,
#                     pos_grp,
#                     layout='tabbed',
#                     enabled_when='not skip'
#                     )
#        extra_grp = self._get_supplemental_extract_group()
#        if extra_grp:
#            grp.content.append(extra_grp)
#
#        v = View(Item('skip'), grp)
#        return v
#
#    def traits_view(self):
#
# #        scripts = VGroup(
# #                       Item('extraction_line_script_name',
# #                        editor=EnumEditor(name='extraction_line_scripts'),
# #                        label='Extraction'
# #                        ),
# #                       Item('measurement_script_name',
# #                            editor=EnumEditor(name='measurement_scripts'),
# #                            label='Measurement'
# #                            ),
# #                       label='Scripts',
# #                       show_border=True
# #                       )
#        def readonly(n, **kw):
#            return Item(n, style='readonly', **kw)
#
#        sspring = lambda width = 17:Spring(springy=False, width=width)
#
#        extract_grp = VGroup(
#                             HGroup(sspring(width=33),
#                                    Item('extract_value', label='Extract',
#                                         tooltip='Set the extract value in extract units'
#                                         ),
#                                    spring,
#                                    Item('extract_units', editor=EnumEditor(name='extract_units_names'),
#                                    show_label=False),
#                                    ),
#                             Item('duration', label='Duration (s)',
#                                  tooltip='Set the number of seconds to run the extraction device.'
#                                  ),
#                             Item('cleanup', label='Cleanup (s)',
#                                  tooltip='Set the number of seconds to getter the sample gas'
#                                  ),
#                             # Item('ramp_rate', label='Ramp Rate (C/s)'),
#                             Item('pattern', editor=EnumEditor(name='patterns')),
#                             label='Extract'
#                             )
#        pos_grp = self._get_position_group()
# #        extract_grp = Group(extract_grp, pos_grp, layout='tabbed')
#        sup = self._get_supplemental_extract_group()
#        if sup:
#            extract_grp = Group(extract_grp, sup, layout='tabbed')
#        else:
#            extract_grp.show_border = True
#
#        extract_grp = VGroup(extract_grp, pos_grp)
#
#        v = View(
#                 Group(
#                       Item('project', editor=EnumEditor(name='projects'),
#                           tooltip='Select a project to constrain the labnumbers'
#                           ),
#                       Item('special_labnumber', editor=EnumEditor(values=SPECIAL_NAMES),
#                           tooltip='Select a special Labnumber for special runs, e.g Blank, Air, etc...'
#                           ),
#                       HGroup(Item('labnumber',
#                                  tooltip='Enter a Labnumber'
#                                  ),
#                              Item('_labnumber', show_label=False,
#                                  editor=EnumEditor(name='labnumbers'),
#                                  tooltip='Select a Labnumber from the selected Project'
#                                  )
#                             ),
#                       readonly('object.run_info.sample',
#                              tooltip='Sample info retreived from Database'
#                              ),
#                       readonly('object.run_info.irrad_level',
#                              tooltip='Irradiation info retreived from Database',
#                              label='Irradiation'),
#                       Item('weight',
#                            label='Weight (mg)',
#                            tooltip='(Optional) Enter the weight of the sample in mg. Will be saved in Database with analysis'
#                            ),
#                       Item('comment',
#                            tooltip='(Optional) Enter a comment for this sample. Will be saved in Database with analysis'
#                            ),
#                       extract_grp,
#                       show_border=True,
#                       label='Info'
#                       )
#                 )
#        return v
#    def _get_spectrometer_signals(self, series):
#        keys, signals = None, None
#        spec = self.spectrometer_manager.spectrometer
#        if not _debug:
#            data = spec.get_intensities(tagged=True)
#            if data is not None:
#                keys, signals = data
# #                keys, signals = zip(*data)
#        else:
#            keys = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']
#
#            if series == 0:
#                signals = [10, 1000, 8, 8, 8, 3]
#            elif series == 1:
#                r = random.randint(0, 10)
#                signals = [0.1, (0.015 * (i - 2800 + r)) ** 2,
#                           0.1, 1, 0.1, (0.001 * (i - 2000 + r)) ** 2
#                           ]
#            else:
#                signals = [1, 2, 3, 4, 5, 6]
#        return keys, signals

#    def _regress_graph(self, reg, g, iso, dn, fi, tab, pi):
#        x, y = zip(*[(ri['time'], ri['value']) for ri in tab.iterrows()])
#        reg.xs=x
#        reg.ys=y
#        reg.fit=fi
# #        reg.predict()
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
        # plot lower ci

#        rdict = reg._regress_(x, y, fi)
#        try:
# #        self.regression_results[dn.name] = rdict
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
#    def get_estimated_duration(self):
#        '''
#            use the pyscripts to calculate etd
#        '''
#        s = self.duration
#
#        for si in [self.measurement_script,
#                   self.extraction_script,
#                   self.post_equilibration_script,
#                   self.post_measurement_script]:
#            if si is not None:
#                s += si.get_estimated_duration()
#
#        return s

#    def to_string_attrs(self, attr):
#        def get_attr(attrname):
#            if attrname in ['measurement_script',
#                            'extraction_script',
#                            'post_measurement_script',
#                            'post_equilibration_script']:
#                v = getattr(self.script_info, '{}_name'.format(attrname))
#                if v:
#                    v = str(v).replace(self.mass_spectrometer, '')
#            elif attrname == 'labnumber':
#                if self.user_defined_aliquot:
#                    v = '{}-{}'.format(self.labnumber, self.aliquot)
#                else:
#                    v = self.labnumber
#            else:
#                v = getattr(self, attrname)
#
#
#            return v
#
#        return [get_attr(ai) for ai in attr]

#    def do_regress(self, fits, series=0):
#        if not self._alive:
#            return
# #        time_zero_offset = 0#int(self.experiment_manager.equilibration_time * 2 / 3.)
#        self.regression_results = dict()
#
#        reg = PolynomialRegressor()
#        dm = self.data_manager
#        ppp = self.peak_plot_panel
#        if ppp:
# #            print ppp.isotopes
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

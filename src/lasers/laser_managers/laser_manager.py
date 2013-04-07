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
from traits.api import Event, Property, Instance, Bool, Str, Float, \
    on_trait_change, Interface, implements
from traitsui.api import View, Item, VGroup, HGroup, spring, VSplit
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.lasers.stage_managers.stage_manager import StageManager
#
from src.monitors.laser_monitor import LaserMonitor
# from src.managers.graph_manager import GraphManager
from src.lasers.laser_managers.pulse import Pulse
from src.paths import paths
# from src.hardware.meter_calibration import MeterCalibration
from src.lasers.pattern.pattern_maker_view import PatternMakerView
from src.lasers.pattern.pattern_executor import PatternExecutor
from src.lasers.power.power_calibration_manager import PowerCalibrationManager
# from src.lasers.laser_managers.extraction_device import IExtractionDevice
from src.lasers.laser_managers.laser_script_executor import LaserScriptExecutor
from src.database.adapters.power_map_adapter import PowerMapAdapter
from src.traits_editors.led_editor import LED, LEDEditor
from src.lasers.laser_managers.extraction_device import IExtractionDevice

class ILaserManager(IExtractionDevice):
    def trace_path(self, *args, **kw):
        pass
    def drill_point(self, *args, **kw):
        pass
    def take_snapshot(self, *args, **kw):
        pass
#    def extract(self, *args, **kw):
#        pass
#    def end_extract(self, *args, **kw):
#        pass
#    def move_to_position(self, *args, **kw):
#        pass

class BaseLaserManager(Manager):
    implements(ILaserManager)
    pattern_executor = Instance(PatternExecutor)
    use_video = Bool(False)

    enable = Event
    enable_label = Property(depends_on='enabled')
    enabled_led = Instance(LED, ())
    enabled = Bool(False)

    def is_ready(self):
        return True

    def take_snapshot(self, *args, **kw):
        pass

    def prepare(self):
        pass

    def set_motor_lock(self, name, value):
        pass

    def set_motor(self, *args, **kw):
        pass

    def get_motor(self, name):
        pass

    def enable_device(self):
        self.enable_laser()

    def disable_device(self):
        self.disable_laser()

    def enable_laser(self):
        pass

    def disable_laser(self):
        pass

    def new_pattern_maker(self):
        pm = PatternMakerView()
        self.open_view(pm)

    def open_pattern_maker(self):
        pm = PatternMakerView()
        pm.load_pattern()
        self.open_view(pm)

    def execute_pattern(self, name=None, block=False):
        pm = self.pattern_executor
        if pm.load_pattern(name):
            pm.execute(block)

    def stop_pattern(self):
        if self.pattern_executor:
            self.pattern_executor.stop()

    def isPatterning(self):
        if self.pattern_executor:
            return self.pattern_executor.isPatterning()

    def _pattern_executor_default(self):
        controller = None
        if self.stage_manager:
            controller = self.stage_manager.stage_controller

        pm = PatternExecutor(application=self.application, controller=controller)
        return pm

    def move_to_position(self, pos, *args, **kw):
        if not isinstance(pos, list):
            pos = [pos]

        for pi in pos:
            self._move_to_position(pi)

        return True

    def trace_path(self, *args, **kw):
        pass

    def drill_point(self, *args, **kw):
        pass

    def set_motors_for_point(self, pt):
        pass

    def get_control_button_group(self):
        grp = HGroup(spring, Item('enabled_led', show_label=False, style='custom', editor=LEDEditor()),
                        self._button_group_factory(self.get_control_buttons(), orientation='h'),
#                                  springy=True
                    )
        return grp

    def get_control_buttons(self):
        return [('enable', 'enable_label', None)]

    def _get_enable_label(self):
        '''
        '''
        return 'DISABLE' if self.enabled else 'ENABLE'

    def _enabled_changed(self):
        if self.enabled:
            self.enabled_led.state = 'green'
        else:
            self.enabled_led.state = 'red'

class LaserManager(BaseLaserManager):
    '''
        Base class for a GUI representation of a laser device
    '''

#    enable = Event
#    enable_label = Property(depends_on='enabled')
#    enabled_led = Instance(LED, ())
#    enabled = Bool(False)

#    graph_manager = Instance(GraphManager, ())
    stage_manager = Instance(StageManager)
#    pattern_executor = Instance(PatternExecutor)
    power_calibration_manager = Instance(PowerCalibrationManager)
    laser_script_executor = Instance(LaserScriptExecutor)

#    use_video = Bool(False)
    record_lasing_video = Bool(False)
    record_lasing_power = Bool(False)

    monitor = Instance(LaserMonitor)
    monitor_name = 'laser_monitor'
    monitor_klass = LaserMonitor

    plugin_id = Str
    # simulation_led = Instance(LED, ())

    status_text = Str
    pulse = Instance(Pulse)

    requested_power = Property(Float, depends_on='_requested_power')
    units = Property(depends_on='use_calibrated_power')
    _requested_power = Float
    _calibrated_power = None
    use_calibrated_power = Bool(True)

#    internal_meter_response = DelegatesTo('laser_controller')

    _power_calibration = None

#    dbname = ''

#===============================================================================
# public interface
#===============================================================================
    def bind_preferences(self, pref_id):

        from apptools.preferences.preference_binding import bind_preference
        bind_preference(self, 'use_video', '{}.use_video'.format(pref_id))
        bind_preference(self, 'close_after_minutes', '{}.close_after'.format(pref_id))
        bind_preference(self, 'record_lasing_video', '{}.record_lasing_video'.format(pref_id))
        bind_preference(self, 'record_lasing_power', '{}.record_lasing_power'.format(pref_id))
        bind_preference(self, 'window_height', '{}.height'.format(pref_id))
        bind_preference(self, 'window_x', '{}.x'.format(pref_id))
        bind_preference(self, 'window_y', '{}.y'.format(pref_id))
        bind_preference(self, 'use_calibrated_power', '{}.use_calibrated_power'.format(pref_id))
        self.stage_manager.bind_preferences(pref_id)

    def set_xy(self, xy, velocity=None):
        self.stage_manager.set_xy(*xy)

#===============================================================================
# patterning
#===============================================================================
#    def _pattern_executor_factory(self):
#        pm = self.pattern_executor
#        pm.controller = self.stage_manager.stage_controller
#        return pm

    def get_pattern_names(self):
        return self.get_file_list(paths.pattern_dir, extension='.lp')

    def enable_laser(self):
        self.info('enable laser')
        enabled = self._enable_hook()

        if self.simulation:
            self.enabled = True
#            self.enabled_led.state = 'green'
            return True

        if isinstance(enabled, bool) and enabled:
            if self.clear_flag('enable_error_flag'):
                self.debug('clearing enable error flag')

            self.enabled = True
            self.monitor = self.monitor_factory()
            if not self.monitor.monitor():
#                self.enabled_led.state = 'green'
#                self.enabled_led.state = 'green'
#            else:
                self.disable_laser()
                self.warning_dialog('Monitor could not be started. Laser disabled', sound='alarm1')
        else:
            self.warning('Could not enable laser')

            if self.set_flag('enable_error_flag'):
                self.debug('setting enable_error_flag')

            self.disable_laser()


        return enabled

    def disable_laser(self):
        self.info('disable laser')
        # stop the laser monitor
        # if the laser is not firing is there any reason to be running the monitor?
        if self.monitor is not None:
            self.monitor.stop()

        enabled = self._disable_hook()

        self.enabled = False

#        self.enabled_led.state = 'red'
        self._requested_power = 0

        return enabled

    def set_laser_output(self, *args, **kw):
        '''
            by default set_laser_output simply uses set_laser_power
            but subclasses can override for different units
        '''
        self.set_laser_power(*args, **kw)


    def set_laser_power(self, power,
                        verbose=True,
                         *args, **kw):
        '''
        '''
        p = self._get_calibrated_power(power, verbose=verbose, **kw)
        if p is None:
            self.emergency_shutoff('Invalid power calibration')
            self.warning_dialog('Invalid Power Calibration')
            return False

        if verbose:
            self.info('request power {:0.3f}, calibrated power {:0.3f}'.format(power, p))

        self._requested_power = power
        self._calibrated_power = p
        self._set_laser_power_hook(p, verbose=verbose)

    def close(self, ok):
        self.pulse.dump_pulse()
        return super(LaserManager, self).close(self)

    def set_laser_monitor_duration(self, d):
        '''
            duration in minutes
        '''
        self.monitor.max_duration = d
        self.monitor.reset_start_time()

    def reset_laser_monitor(self):
        '''
        '''
        self.monitor.reset_start_time()

    def emergency_shutoff(self, reason):
        ''' 
        '''
        self.disable_laser()

        if reason is not None:
            self.warning('EMERGENCY SHUTOFF reason: {}'.format(reason))
            self.warning_dialog(reason, sound='alarm1', title='AUTOMATIC LASER SHUTOFF')
            from src.remote_hardware.errors.laser_errors import LaserMonitorErrorCode
            self.error_code = LaserMonitorErrorCode(reason)

    def start_power_recording(self, *args, **kw):
        pass

    def stop_power_recording(self, *args, **kw):
        pass

#===============================================================================
# manager interface
#===============================================================================
    def finish_loading(self):
        self.enabled_led.state = 'red' if not self.enabled else 'green'

    def dispose_optional_windows(self):
#        if self.use_video:
#            self.stage_manager.machine_vision_manager.close_images()
#
        self._dispose_optional_windows_hook()
#===============================================================================
# public getters
#===============================================================================
    def get_pulse_manager(self):
        return self.pulse

    def get_power_map_manager(self):
        from src.lasers.power.power_map_manager import PowerMapManager
        pm = PowerMapManager(laser_manager=self, database=self.get_power_map_database())
        return pm

    def get_power_map_database(self):
        db = PowerMapAdapter(
                             name=paths.powermap_db,
#                            name=self.dbname,
                            kind='sqlite',
                            application=self.application
                            )
        db.manage_database()
        db.connect()

        return db
#===============================================================================
# views
#===============================================================================
    def get_stage_group(self):
        return Item('stage_manager', height=0.70, style='custom', show_label=False)

    def get_control_group(self):
        return VGroup()

    def get_unique_view_id(self):
        return 'pychron.{}'.format(self.__class__.__name__.lower())

    def get_control_buttons(self):
        '''
        '''
        return [('enable', 'enable_label', None)
                ]

    def get_control_items(self):
        pass

    def get_additional_controls(self, *args):
        pass

    def get_power_slider(self):
        '''
        '''
        return self._slider_group_factory([('request_power', 'request_power', dict(enabled_when='enabled'))])

    def traits_view(self):
        '''
        '''

        vg = VSplit(self.get_control_group(),
                    self.get_stage_group()
                    )

#        hooks = [h for h in dir(self) if '__group__' in h]
#        for h in hooks:
#            vg.content.append(getattr(self, h)())

        return View(
                    vg,
                    id=self.get_unique_view_id(),
                    resizable=True,
                    title=self.__class__.__name__ if self.title == '' else self.title,
                    handler=self.handler_klass,
                    height=self.window_height,
                    x=self.window_x,
                    y=self.window_y,
                    statusbar='status_text',
                    )

#===============================================================================
# ##handlers
#===============================================================================
    @on_trait_change('stage_manager:canvas:current_position')
    def update_status_bar(self, obj, name, old, new):
        if isinstance(new, tuple):
            self.status_text = 'x = {:n} ({:0.4f} mm), y = {:n} ({:0.4f} mm)'.format(*new)

    def _enable_fired(self):
        '''
        '''
        if not self.enabled:
            self.enable_laser()
        else:

            self.disable_laser()

    def _use_video_changed(self):
        if not self.use_video:
            try:
                self.stage_manager.video.shutdown()
            except AttributeError, e:
                print e

        try:
            sm = self._stage_manager_factory(self.stage_args)

            sm.stage_controller = self.stage_manager.stage_controller
            sm.stage_controller.parent = sm
            if self.plugin_id:
                sm.bind_preferences(self.plugin_id)
            sm.visualizer = self.stage_manager.visualizer

            sm.load()

            self.stage_manager = sm
        except AttributeError, e:
            print e
##===============================================================================
# # persistence
##===============================================================================
#    def dump_power_calibration(self, coefficients, bounds=None, calibration_path=None):
#
#        calibration_path = self._get_calibration_path(calibration_path)
#        self.info('dumping power calibration {}'.format(calibration_path))
#
#        coeffstr = lambda c:'calibration coefficients= {}'.format(', '.join(map('{:0.3f}'.format, c)))
#        if bounds:
#            for coeffs, bi in zip(coefficients, bounds):
#                self.info('calibration coefficient')
#            self.info('{} min={:0.2f}, max={:0.2f}'.format(coeffstr(coeffs, *bi)))
#        else:
#            self.info(coeffstr(coefficients))
#
#        pc = MeterCalibration(coefficients)
#        pc.bounds = bounds
#        try:
#            with open(calibration_path, 'wb') as f:
#                pickle.dump(pc, f)
#        except  (pickle.PickleError, EOFError, OSError), e:
#            self.warning('pickling error {}'.format(e))
#
#    def load_power_calibration(self, calibration_path=None, verbose=True):
#        calibration_path = self._get_calibration_path(calibration_path)
#        if os.path.isfile(calibration_path):
#            if verbose:
#                self.info('loading power calibration {}'.format(calibration_path))
#
#            with open(calibration_path, 'rb') as f:
#                try:
#                    pc = pickle.load(f)
#                except (pickle.PickleError, EOFError, OSError), e:
#                    self.warning('unpickling error {}'.format(e))
#                    pc = MeterCalibration([1, 0])
#
#        else:
#            pc = MeterCalibration([1, 0])
#
#        return pc
#===============================================================================
# hooks
#===============================================================================
    def _dispose_optional_windows_hook(self):
        pass

    def _kill_hook(self):
        self.disable_laser()

    def _enable_hook(self):
        return True

    def _disable_hook(self):
        pass

    def _set_laser_power_hook(self, *args, **kw):
        pass

#===============================================================================
# getter/setters
#===============================================================================
    def _get_calibrated_power(self, power, use_calibration=True, verbose=True):

        if self.use_calibrated_power and use_calibration:
            pc = self.power_calibration_manager.load_power_calibration(verbose=verbose, warn=False)
            if pc is None:
                return

            if power < 0.1:
                power = 0
            else:
                power = pc.get_input(power)
                if verbose:
                    self.info('using power coefficients  (e.g. ax2+bx+c) {}'.format(pc.print_string()))
#                if coeffs is not None:
#                    sc = ','.join(['{}={:0.3e}'.format(*c) for c in zip('abcdefg', coeffs)])
#                    if verbose:
#                        self.info('using power coefficients (e.g. ax2+bx+c) {}'.format(sc))
        return power

    def _get_requested_power(self):
        return self._requested_power



#===============================================================================
# factories
#===============================================================================
    def monitor_factory(self):
        lm = self.monitor
        if lm is None:
            lm = self.monitor_klass(manager=self,
#                            configuration_dir_name=paths.monitors_dir,
                            name=self.monitor_name)
        if hasattr(lm, 'update_imb'):
            self.on_trait_change(lm.update_imb, 'laser_controller:internal_meter_response')
        return lm

    def _stage_manager_factory(self, args):
        self.stage_args = args
        if self.use_video:
            from src.lasers.stage_managers.video_stage_manager import VideoStageManager
            klass = VideoStageManager
        else:
            klass = StageManager

        args['parent'] = self
        sm = klass(**args)
        return sm
#===============================================================================
# defaults
#===============================================================================
    def _pulse_default(self):
        p = os.path.join(paths.hidden_dir, 'pulse')
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                try:
                    pul = pickle.load(f)
                    pul.manager = self
                except pickle.PickleError:
                    pul = Pulse(manager=self)
        else:
            pul = Pulse(manager=self)

        return pul

    def _power_calibration_manager_default(self):
        return PowerCalibrationManager(
                                       parent=self,
                                       db=self.get_power_calibration_database(),
                                       application=self.application
                                       )

    def _laser_script_executor_default(self):
        return LaserScriptExecutor(laser_manager=self,
                                   name=self.name)
if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('calib')
    lm = LaserManager(name='FusionsDiode')
    lm.set_laser_power(10)
#    from src.lasers.power.power_calibration_manager import PowerCalibrationManager, PowerCalibrationObject
#
#    pc=PowerCalibrationObject()
#    pc.coefficients=[0.84,-13.76]
#
#    pm=PowerCalibrationManager(parent=lm)
#    pm._dump_calibration(pc)

#    lm.set_laser_power(10)
#============= EOF ====================================
#        import wx
#        ls = self._get_optional_window_labels()
#        if ls:
#            for li in ls:
#                w = wx.FindWindowByLabel(li)
#                if w is not None:
#                    w.Destroy()
#
#    def _get_optional_window_labels(self):
#        labels = []
#
#        hl = self._get_optional_window_labels_hook()
#        if hl:
#            labels += hl
#
#        return labels
#
#    def _get_optional_window_labels_hook(self):
#        pass

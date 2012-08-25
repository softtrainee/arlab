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
    on_trait_change, DelegatesTo
from traitsui.api import View, Item, VGroup
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.led.led import LED
from src.lasers.stage_managers.stage_manager import StageManager
from src.lasers.stage_managers.video_stage_manager import VideoStageManager
from src.monitors.laser_monitor import LaserMonitor
from src.managers.graph_manager import GraphManager
from src.lasers.laser_managers.pulse import Pulse
from src.paths import paths
from src.hardware.meter_calibration import MeterCalibration


class LaserManager(Manager):
    '''
        Base class for a GUI representation of a laser device
    '''
    enable = Event
    enable_label = Property(depends_on='enabled')
    enabled_led = Instance(LED, ())
    enabled = Bool(False)

    graph_manager = Instance(GraphManager, ())
    stage_manager = Instance(StageManager)
    use_video = Bool(False)
    record_lasing_video = Bool(False)
    record_lasing_power = Bool(False)

    monitor = Instance(LaserMonitor)
    monitor_name = 'laser_monitor'
    monitor_klass = LaserMonitor
    failure_reason = None

    #simulation_led = Instance(LED, ())

    status_text = Str
    pulse = Instance(Pulse)

    requested_power = Property(Float, depends_on='_requested_power')
    _requested_power = Float
    _calibrated_power = None
    use_calibrated_power = Bool(True)
    internal_meter_response = DelegatesTo('logic_board')

    _power_calibration = None
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

    def enable_laser(self):

        self.info('enable laser')
        enabled = self._enable_hook()

        if self.simulation or (isinstance(enabled, bool) and enabled):
            if self.clear_flag('enable_error_flag'):
                self.debug('clearing enable error flag')

            self.enabled = True
            self.monitor = self.monitor_factory()
            self.monitor.monitor()
            self.enabled_led.state = 'green'
        else:
#            self.failure_reason = 'Could not enable laser'
            self.warning('Could not enable laser')

            if self.set_flag('enable_error_flag'):
                self.debug('setting enable_error_flag')

            self.disable_laser()

        return enabled

    def disable_laser(self):
        self.info('disable laser')

        enabled = self._disable_hook()

        self.enabled = False
        #stop the laser monitor 
        #if the laser is not firing is there any reason to be running the monitor?
        if self.monitor is not None:
            self.monitor.stop()

        self.enabled_led.state = 'red'
        self._requested_power = 0

        return enabled

    def set_laser_power(self, power, use_calibration=True,
                        memoize_calibration=False,
                        verbose=True,
                         *args, **kw):
        '''
        '''
        p = self._get_calibrated_power(power,
                                       use_calibration,
                                       memoize_calibration,
                                       verbose=verbose)

        if verbose:
            self.info('request power {:0.2f}, calibrated power {:0.2f}'.format(power, p))

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

    def emergency_shutoff(self, reason=None):
        ''' 
        '''
        if reason is not None:
            self.warning('EMERGENCY SHUTDOWN reason: {}'.format(reason))
            self.failure_reason = reason

            from src.remote_hardware.errors.laser_errors import LaserMonitorErrorCode
            self.error_code = LaserMonitorErrorCode(reason)

        self.disable_laser()

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

        pm = PowerMapManager(laser_manager=self)
        return pm


#===============================================================================
# views
#===============================================================================
    def __stage__group__(self):
        return Item('stage_manager', height=0.70, style='custom', show_label=False)

    def get_unique_view_id(self):
        return 'pychron.{}'.format(self.__class__.__name__.lower())

    def get_control_buttons(self):
        '''
        '''
        return [('enable', 'enable_label', None)
                ]
    def get_control_sliders(self):
        pass

    def get_additional_controls(self):
        pass

    def get_power_slider(self):
        '''
        '''
        return self._slider_group_factory([('request_power', 'request_power', dict(enabled_when='enabled'))])

    def traits_view(self):
        '''
        '''
        vg = VGroup()

        hooks = [h for h in dir(self) if '__group__' in h]
        for h in hooks:
            vg.content.append(getattr(self, h)())

        return View(
                    vg,
                    id=self.get_unique_view_id(),
                    resizable=True,
                    title=self.__class__.__name__ if self.title == '' else self.title,
                    handler=self.handler_klass,
                    height=self.window_height,
                    x=self.window_x,
                    y=self.window_y,
                    statusbar='status_text'
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
            except AttributeError:
                pass

        try:
            sm = self._stage_manager_factory(self.stage_args)

            sm.stage_controller = self.stage_manager.stage_controller
            sm.stage_controller.parent = sm
            sm.bind_preferences(self.id)
            sm.visualizer = self.stage_manager.visualizer

            sm.load()

            self.stage_manager = sm
        except AttributeError:
            pass
#===============================================================================
# persistence
#===============================================================================
    def dump_power_calibration(self, coefficients, bounds=None, calibration_path=None):

        calibration_path = self._get_calibration_path(calibration_path)
        self.info('dumping power calibration {}'.format(calibration_path))

        coeffstr = lambda c:'calibration coefficients= {}'.format(', '.join(map('{:0.3f}'.format, c)))
        if bounds:
            for coeffs, bi in zip(coefficients, bounds):
                self.info('calibration coefficient')
            self.info('{} min={:0.2f}, max={:0.2f}'.format(coeffstr(coeffs, *bi)))
        else:
            self.info(coeffstr(coefficients))

        pc = MeterCalibration(coefficients)
        pc.bounds = bounds
        try:
            with open(calibration_path, 'wb') as f:
                pickle.dump(pc, f)
        except  (pickle.PickleError, EOFError, OSError), e:
            self.warning('pickling error {}'.format(e))

    def load_power_calibration(self, calibration_path=None, verbose=True):
        ospath = os.path
        calibration_path = self._get_calibration_path(calibration_path)
        if ospath.isfile(calibration_path):
            if verbose:
                self.info('loading power calibration {}'.format(calibration_path))

            with open(calibration_path, 'rb') as f:
                try:
                    pc = pickle.load(f)
                except (pickle.PickleError, EOFError, OSError), e:
                    self.warning('unpickling error {}'.format(e))
                    pc = MeterCalibration([1, 0])

        else:
            pc = MeterCalibration([1, 0])

        self._power_calibration = pc
        return pc
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

    def _get_calibrated_power(self, power, calibration,
                              memoize_calibration=False,
                              verbose=True):

        if self.use_calibrated_power and calibration:
            path = None
            if isinstance(calibration, str):
                path = calibration
            elif isinstance(calibration, tuple):
                pass

            if memoize_calibration:
                pc = self._power_calibration
                if pc is None:
                    pc = self.load_power_calibration(calibration_path=path, verbose=verbose)

            else:
                pc = self.load_power_calibration(calibration_path=path, verbose=verbose)

            if power < 0.1:
                power = 0
            else:
                power, coeffs = pc.get_input(power)
                if coeffs is not None:
                    sc = ','.join(['{}={:0.2f}'.format(*c) for c in zip('abcdefg', coeffs)])
                    if verbose:
                        self.info('using power coefficients (e.g. ax2+bx+c) {}'.format(sc))
        return power

    def _get_calibration_path(self, cp):
        if cp is None:
            cp = os.path.join(paths.hidden_dir, '{}_power_calibration'.format(self.name))
        return cp

    def _get_requested_power(self):
        return self._requested_power

    def _get_enable_label(self):
        '''
        '''
        return 'DISABLE' if self.enabled else 'ENABLE'

#===============================================================================
# factories
#===============================================================================
    def monitor_factory(self):
        lm = self.monitor
        if lm is None:
            lm = self.monitor_klass(manager=self,
                            configuration_dir_name=paths.monitors_dir,
                            name=self.monitor_name)

        self.on_trait_change(lm.update_imb, 'logic_board:internal_meter_response')
        return lm

    def _stage_manager_factory(self, args):
        self.stage_args = args
        if self.use_video:
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

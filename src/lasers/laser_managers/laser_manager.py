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
from traits.api import Event, Property, Instance, Bool, Str, on_trait_change, Enum
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
from pulse import Pulse
from src.paths import paths
from src.lasers.power.power_calibration_manager import PowerCalibrationObject


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
    record_lasing = Bool(False)

    monitor = Instance(LaserMonitor)
    monitor_name = 'laser_monitor'
    monitor_klass = LaserMonitor
    failure_reason = None

    #simulation_led = Instance(LED, ())

    status_text = Str
    pulse = Instance(Pulse)

    _requested_power = None
    _calibrated_power = None
    use_calibrated_power = Bool(True)

    def bind_preferences(self, pref_id):
        from apptools.preferences.preference_binding import bind_preference

        bind_preference(self, 'use_video', '{}.use_video'.format(pref_id))
        bind_preference(self, 'close_after_minutes', '{}.close_after'.format(pref_id))
        bind_preference(self, 'record_lasing', '{}.record_lasing'.format(pref_id))

        bind_preference(self, 'window_height', '{}.height'.format(pref_id))
        bind_preference(self, 'window_x', '{}.x'.format(pref_id))
        bind_preference(self, 'window_y', '{}.y'.format(pref_id))
        bind_preference(self, 'use_calibrated_power', '{}.use_calibrated_power'.format(pref_id))

    def dispose_optional_windows(self):
        if self.use_video:
            self.stage_manager.machine_vision_manager.close_images()

        self._dispose_optional_windows_hook()

    def _dispose_optional_windows_hook(self):
        pass

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

#    @on_trait_change('stage_manager:canvas:current_position')
#    def update_status_bar(self, obj, name, old, new):
#        if isinstance(new, tuple):
#            self.status_text = 'x = {:n} ({:0.4f} mm), y = {:n} ({:0.4f} mm)'.format(*new)

    def get_pulse_manager(self):
        return self.pulse

    def get_power_map_manager(self):
        from src.lasers.power.power_map_manager import PowerMapManager

        pm = PowerMapManager(laser_manager=self)
        return pm


#        path = self.open_file_dialog(default_directory = os.path.join(scripts_dir,
#                                                                      'laserscripts',
#                                                                      'power_maps'
#                                                                      )
#                                     )
#        path = '/Users/Ross/Pychrondata_beta/scripts/laserscripts/power_maps/s.rs'
#        if path:
#            pm = PowerMapManager()
#            pm.parent = self
#            pm.file_name = path
#            pm.new_script()
#            return pm


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

    def finish_loading(self):
        self.enabled_led.state = 'red' if not self.enabled else 'green'

    def _enable_fired(self):
        '''
        '''
        if not self.enabled:
            self.enable_laser()
        else:

            self.disable_laser()

    def start_power_recording(self, *args, **kw):
        pass

    def stop_power_recording(self, *args, **kw):
        pass

    def enable_laser(self):

#    def enable_laser(self, is_ok=True):
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
        self._requested_power = None

        return enabled

    def _enable_hook(self):
        return True

    def _disable_hook(self):
        pass

    def set_laser_power(self, power, use_calibration=True, *args, **kw):
        '''
        '''
        p = self._get_calibrated_power(power, use_calibration)

        self.info('request power {:0.2f}, calibrated power {:0.2f}'.format(power, p))
        self._requested_power = power
        self._calibrated_power = p
        self._set_laser_power_hook(p)

    def _set_laser_power_hook(self, p):
        pass

    def _get_calibrated_power(self, power, calibration):

        if self.use_calibrated_power and calibration:
            path = None
            if isinstance(calibration, str):
                path = calibration
            elif isinstance(calibration, tuple):
                pass

            pc = self.load_power_calibration(calibration_path=path)
            if power < 0.1:
                power = 0
            else:
#                c = pc.coefficients
                power, coeffs = pc.get_calibrated_power(power)

                sc = ','.join(['{}={:0.2f}'.format(*c) for c in zip('abcdefg', coeffs)])
                self.info('using power coefficients (e.g. ax2+bx+c) {}'.format(sc))
        return power

    def _get_calibration_path(self, cp):
        if cp is None:
            cp = os.path.join(paths.hidden_dir, '{}_power_calibration'.format(self.name))
        return cp

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

        pc = PowerCalibrationObject()
        pc.coefficients = coefficients
        pc.bounds = bounds
        try:
            with open(calibration_path, 'wb') as f:
                pickle.dump(pc, f)
        except  (pickle.PickleError, EOFError, OSError), e:
            self.warning('pickling error {}'.format(e))

    def load_power_calibration(self, calibration_path=None):
        ospath = os.path
        calibration_path = self._get_calibration_path(calibration_path)
        if ospath.isfile(calibration_path):
            self.info('loading power calibration {}'.format(calibration_path))
            with open(calibration_path, 'rb') as f:
                try:
                    pc = pickle.load(f)
                except (pickle.PickleError, EOFError, OSError), e:
                    self.warning('unpickling error {}'.format(e))
                    pc = PowerCalibrationObject()
                    pc.coefficients = [1, 1]
        else:
            pc = PowerCalibrationObject()
            pc.coefficients = [1, -1]

        return pc

#    def kill(self, **kw):
#        '''
#           
#        '''
#        if super(LaserManager, self).kill(**kw):
#
##            self.emergency_shutoff()
#            self.disable_laser()
##            self.stage_manager.kill()
    def _kill_hook(self):
        self.disable_laser()

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

        self.disable_laser()



    def _get_enable_label(self):
        '''
        '''
        return 'DISABLE' if self.enabled else 'ENABLE'

    def _use_video_changed(self):
        if not self.use_video:
            try:
                self.stage_manager.video.shutdown()
            except AttributeError:
                pass
#            self.stage_manager.video_manager.shutdown()

        try:
            sm = self._stage_manager_factory(self.stage_args)

            sm.stage_controller = self.stage_manager.stage_controller
            sm.stage_controller.parent = sm
            sm.bind_preferences(self.id)
            sm.visualizer = self.stage_manager.visualizer

        #        sm.canvas.crosshairs_offset = self.stage_manager.canvas.crosshairs_offset
#        bind_preference(sm.canvas, 'show_grids', '{}.show_grids'.format(self.id))
#
#        sm .canvas.change_grid_visibility()
#
#        bind_preference(sm.canvas, 'show_laser_position', '{}.show_laser_position'.format(self.id))
#        bind_preference(sm.canvas, 'show_desired_position', '{}.show_laser_position'.format(self.id))
#        bind_preference(sm.canvas, 'show_map', '{}.show_map'.format(self.id))
#
#        bind_preference(sm.canvas, 'crosshairs_kind', '{}.crosshairs_kind'.format(self.id))
#        bind_preference(sm.canvas, 'crosshairs_color', '{}.crosshairs_color'.format(self.id))
#
#        sm.canvas.change_indicator_visibility()

            sm.load()

            self.stage_manager = sm
        except AttributeError:
            pass

    #========================= views =========================
    def __stage__group__(self):
        return Item('stage_manager', height=0.70, style='custom', show_label=False)

    def get_unique_view_id(self):
        return 'pychron.{}'.format(self.__class__.__name__.lower())

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
#                    statusbar='status_text'
                    )
#===============================================================================
# factories
#===============================================================================
    def monitor_factory(self):
        lm = self.monitor
        if lm is None:
            lm = self.monitor_klass(manager=self,
                            configuration_dir_name=paths.monitors_dir,
                            name=self.monitor_name)
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

'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import Event, Property, Instance, Bool, Str, on_trait_change
from traitsui.api import View, Item, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from src.managers.manager import Manager
from src.led.led import LED
from src.managers.stage_managers.stage_manager import StageManager
from src.managers.stage_managers.video_stage_manager import VideoStageManager
from src.monitors.laser_monitor import LaserMonitor
from src.helpers import paths
from src.managers.step_heat_manager import StepHeatManager
from src.managers.graph_manager import GraphManager
from src.managers.laser_managers.laser_pulse_manager import Pulse


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

    @on_trait_change('stage_manager:canvas:current_position')
    def update_status_bar(self, obj, name, old, new):
        if isinstance(new, tuple):
            self.status_text = 'x = {:n} ({:0.4f} mm), y = {:n} ({:0.4f} mm)'.format(*new)

    def get_pulse_manager(self):
        return self.pulse

    def _pulse_default(self):
        return Pulse(manager=self)

    def get_power_map_manager(self):
        from power_map_manager import PowerMapManager

#        path = self.open_file_dialog(default_directory = os.path.join(scripts_dir,
#                                                                      'laserscripts',
#                                                                      'power_maps'
#                                                                      )
#                                     )

        path = '/Users/Ross/Pychrondata_beta/scripts/laserscripts/power_maps/s.rs'
        if path:
            pm = PowerMapManager()
            pm.parent = self
            pm.file_name = path
            pm.new_script()
            return pm


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
        if self._enable_hook():
            self.enabled = True
            self.monitor = self.monitor_factory()
            self.monitor.monitor()
            self.enabled_led.state = 'green'
        else:
            self.failure_reason = 'Could not enable laser'
            self.disable_laser()


    def disable_laser(self):
        self.info('disable laser')

        self._disable_hook()

        self.enabled = False
        #stop the laser monitor 
        #if the laser is not firing is there any reason to be running the monitor?
        if self.monitor is not None:
            self.monitor.stop()

        self.enabled_led.state = 'red'

    def _enable_hook(self):
        return True

    def _disable_hook(self):
        pass

    def show_step_heater(self):

        shm = StepHeatManager(laser_manager=self,
                              video_manager=self.stage_manager.video_manager
                              )
        self.step_heat_manager = shm
        shm.edit_traits()

    def set_laser_power(self, *args, **kw):
        '''
        '''

        pass

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

        sm = klass(**args)
        return sm

    def _get_enable_label(self):
        '''
        '''
        return 'STOP' if self.enabled else 'ENABLE'

    def _use_video_changed(self):
        if not self.use_video:
            self.stage_manager.video_manager.shutdown()

        sm = self._stage_manager_factory(self.stage_args)

        sm.stage_controller = self.stage_manager.stage_controller
        sm.stage_controller.parent = sm
        sm.bind_preferences(self.id)

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

    #========================= views =========================
    def __stage__group__(self):
        return Item('stage_manager', height=0.70, style='custom', show_label=False)

    def traits_view(self):
        '''
        '''
        vg = VGroup()

        hooks = [h for h in dir(self) if '__group__' in h]
        for h in hooks:
            vg.content.append(getattr(self, h)())

        return View(vg,
                    resizable=True,
                    title=self.__class__.__name__ if self.title == '' else self.title,
                    handler=self.handler_klass,
                    height=0.67,
                    x=300,
                    y=25,
                    statusbar='status_text'
                    )
#============= EOF ====================================

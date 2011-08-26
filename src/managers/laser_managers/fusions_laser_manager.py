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
'''
'''
#=============enthought library imports=======================
from traits.api import DelegatesTo, Property, Instance, on_trait_change, Event, Bool
from traitsui.api import VGroup, Item, HGroup
from pyface.timer.do_later import do_later
#from apptools.preferences.preference_binding import bind_preference
#=============standard library imports ========================
import time
#=============local library imports  ==========================
#from src.managers.stage_managers.stage_manager import StageManager
#from src.managers.stage_managers.video_stage_manager import VideoStageManager

from src.hardware.fusions.fusions_logic_board import FusionsLogicBoard
from src.hardware.fiber_light import FiberLight
from src.hardware.subsystems.arduino_subsystem import ArduinoSubsystem
#from src.managers.step_heat_manager import StepHeatManager
from src.led.led_editor import LEDEditor

from laser_manager import LaserManager

class FusionsLaserManager(LaserManager):
    '''
    '''

    logic_board = Instance(FusionsLogicBoard)

    subsystem = Instance(ArduinoSubsystem)
    fiber_light = Instance(FiberLight)

    light = DelegatesTo('fiber_light', prefix = 'power')
    light_label = DelegatesTo('fiber_light', prefix = 'power_label')
    light_intensity = DelegatesTo('fiber_light', prefix = 'intensity')

    beam = DelegatesTo('logic_board')
    beammin = DelegatesTo('logic_board')
    beammax = DelegatesTo('logic_board')
    update_beam = DelegatesTo('logic_board')

    zoom = DelegatesTo('logic_board')
    zoommin = DelegatesTo('logic_board')
    zoommax = DelegatesTo('logic_board')
    update_zoom = DelegatesTo('logic_board')

    pointer = Event
    pointer_state = Bool(False)
    pointer_label = Property(depends_on = 'pointer_state')

    step_heat_manager = None
    def set_light(self, state):
        if state:
            self.fiber_light.power_off()
        else:
            self.fiber_light.power_on()

    def set_light_intensity(self, v):
        self.fiber_light.intensity = v

    def kill(self, **kw):
        if self.step_heat_manager is not None:
            self.step_heat_manager.kill(**kw)

        super(FusionsLaserManager, self).kill(**kw)

    def finish_loading(self):
        '''
        '''
        if self.fiber_light._cdevice is None:
            self.fiber_light._cdevice = self.subsystem.get_module('FiberLightModule')

        super(FusionsLaserManager, self).finish_loading()

    @on_trait_change('pointer')
    def pointer_ononff(self):
        '''
        '''
        self.pointer_state = not self.pointer_state

        self.logic_board.set_pointer_onoff(self.pointer_state)

    def get_laser_watts(self):
        pass

    def get_laser_internal_temperature(self):
        '''
        '''
        return 0

    def get_coolant_temperature(self, **kw):
        '''
        '''
        chiller = self.get_device('thermo_rack')
        if chiller is not None:
            return chiller.get_coolant_out_temperature(**kw)

    def get_coolant_status(self, **kw):
        chiller = self.get_device('thermo_rack')
        if chiller is not None:
            return chiller.get_faults(**kw)

#    @on_trait_change('beam')
#    def beam_change(self):
#        self.stage_manager.canvas.set_beam_radius(self.beam / 2.0)


    def set_beam_diameter(self, bd, **kw):
        '''
        '''
        self.logic_board.set_beam_diameter(bd, **kw)


    def set_zoom(self, z, **kw):
        '''
        '''
        self.logic_board.set_zoom(z, **kw)

    def move_to_hole(self, holenumber):
        if self.stage_manager is not None:
            #if not self.stage_manager.opened:
                #do_later opens the stage manager from the main thread
            do_later(self.show_stage_manager)

            #give the stage manager some time to open
            time.sleep(1)

            self.stage_manager.move_to_hole(holenumber)

    def enable_laser(self, mode = 'normal'):
        '''
        '''
        if mode == 'remote':
            '''
                do a final adjustment of the last position
                
                method 1
                1. find the center of the hole
                2. move to the center
                method 2
                1. find the centroid of the grain
                    a. zoom or crop image to a single hole
                    b. use a TargetImage
                2. move to the centroid x,y  
            '''
            #use the video manager to do calculations
            #method 1
            self.stage_manager.video_manager.locate_center()

            #method 2
            self.stage_manager.video_manager.locate_centroid()

        is_ok = self.logic_board._enable_laser_()
        super(FusionsLaserManager, self).enable_laser(is_ok = is_ok)
        return is_ok

    def disable_laser(self):
        '''
        '''
        super(FusionsLaserManager, self).disable_laser()
        return self.logic_board._disable_laser_()

#    def show_step_heater(self):
#
#        shm = StepHeatManager(laser_manager = self,
#                              video_manager = self.stage_manager.video_manager
#                              )
#        self.step_heat_manager = shm
#        shm.edit_traits()

    def show_motion_controller_manager(self):
        '''
        '''
        stage_controller = self.stage_manager.stage_controller
        package = 'src.managers.motion_controller_managers'
        if 'Aerotech' in stage_controller.__class__.__name__:
            _class_ = 'AerotechMotionControllerManager'
            package += '.aerotech_motion_controller_manager'
        else:
            _class_ = 'NewportMotionControllerManager'
            package += '.newport_motion_controller_manager'

        module = __import__(package, globals(), locals(), [_class_], -1)
        factory = getattr(module, _class_)
        m = factory(motion_controller = stage_controller)
        m.edit_traits()

#========================= views =========================
    def get_control_buttons(self):
        '''
        '''
        return [('enable', 'enable_label', None),
                ('pointer', 'pointer_label', None),
                ('light', 'light_label', None)
                ]

    def get_control_sliders(self):
        '''
        '''
        s = [('zoom', 'zoom', {}),
            ('beam', 'beam', {})
            ]
        return s
#
#    def get_power_slider(self):
#        '''
#        '''
#        return None



    def __control__group__(self):
        '''
        '''

        vg = VGroup(HGroup(
                                 Item('enabled_led', show_label = False, style = 'custom', editor = LEDEditor()),
                                 self._button_group_factory(self.get_control_buttons(), orientation = 'h'),
                                    ),
                                    springy = True
                          )

        ps = self.get_power_slider()
        if ps:
            vg.content.append(ps)

        vg.content.append(Item('light_intensity',
                                 enabled_when = 'fiber_light.state'))

        csliders = self.get_control_sliders()
        vg.content.append(self._update_slider_group_factory(csliders))
        ac = self.get_additional_controls()
        if ac is not None:
            vg = HGroup(vg, ac)

        return vg

    def _get_pointer_label(self):
        '''
        '''
        return 'Pointer ON' if not self.pointer_state else 'Pointer OFF'

#========================= defaults =======================
    def _subsystem_default(self):
        '''
        '''
        return ArduinoSubsystem(name = 'arduino_subsystem_2')

    def _fiber_light_default(self):
        '''
        '''
        return FiberLight(name = 'FiberLight')

#========================== EOF ====================================
#    def show_video_controls(self):
#        '''
#        '''
#        self.video_manager.edit_traits(view = 'controls_view')

#    def launch_laser_pulse(self):
#        '''
#        '''
#        p = os.path.join(paths.scripts_dir, 'laserscripts', 'laser_pulse.txt')
#        pulse = LaserPulseScript(manager = self)
#        pulse._load_script(p)
#        pulse.edit_traits()

#    def show_power_scan(self):
#        '''
#        '''
#
#        pp = os.path.join(paths.scripts_dir, 'laserscripts', 'power_scans')
#        pscan = PowerScanScript(manager = self, source_dir = pp)

        #pscan.start()
        #pscan.open()
#    def traits_view(self):
#        '''
#        '''
#        title = self.__class__.__name__ if self.title == '' else self.title
#        vg = VSplit()
#
#        hooks = [h for h in dir(self) if '__group__' in h]
#        for h in hooks:
#            vg.content.append(getattr(self, h)())
#
#        return View(#HSplit(
#                           #Item('stream_manager', show_label = False, style = 'custom'),
#                           vg,
#                       #    ),
#                    resizable = True,
#                   # menubar = self._menubar_factory(),
#                    title = title,
#                    handler = self.handler_klass)
#    def _stage_manager_factory(self, args):
#        if self.use_video:
#            klass = VideoStageManager
#        else:
#            klass = StageManager
#
#        sm = klass(**args)
#        return sm
#
#    def show_stage_manager(self, **kw):
#        #self.stage_manager.controllable = True
#        self.stage_manager.edit_traits(**kw)
#
#    def close_stage_manager(self):
#        self.stage_manager.close_ui()
#    def _show_streams_(self, available_streams):
#        sm = self.stream_manager
#        dm = sm.data_manager
#
#        available_streams.append(self.logic_board)
#
#        streams = sm.open_stream_loader(available_streams)
#
#        if streams:
#
#            self.streaming = True
#            self.dirty = True
#            if streams != 'running':
#                for s in streams:
#                    p = s['parent']
#                    name = p.name
#
#                    dm.add_group(name)
#                    table = 'stream'
#                    dm.add_table(table, parent = 'root.%s' % name)
#                    sm.set_stream_tableid(name, 'root.%s.%s' % (name, table))
#                self.stream_manager.edit_traits()

#    def show_laser_control(self):
#        self.edit_traits()
#    
#    def show_stage_manager(self):
#        '''
#        '''
#        self.stage_manager.edit_traits()

#    def show_motor_configurer(self):
#        self.logic_board.configure_motors()

#    def show_video(self):
#        self.video_manager = VideoManager()
#        self.video_manager.edit_traits()

#    def stop_streams(self):
#        '''
#        '''
#        self.streaming = False
#        self.stream_manager.stop_streams()

#    def show_preferences(self):
#        preferences.edit_traits()
#def get_menus(self):
#        '''
#        '''
#        return [('File', [dict(name = 'Preferences', action = 'show_preferences',),
#                         #dict(name = 'Open Graph', action = 'open_graph'),
#                         #dict(name = 'Video Controls', action = 'show_video_controls')
#                         ]),
#
#                ('Devices', [
#                             #dict(name = 'Laser Controller', action = 'show_laser_controller'),
#                             #dict(name = 'Laser Stats', action = 'show_laser_stats'),
#                             dict(name = 'Stage Manager', action = 'show_stage_manager'),
#                             dict(name = 'Configure Motion Controller', action = 'show_motion_controller_manager',
#                                #enabled_when='not stage_simulation'
#                                ),
#                             dict(name = 'Configure Motors', action = 'show_motor_configurer'),
#                          # dict(name = 'Video', action = 'show_video')
#                           ]),
# #               ('Streams', [dict(name = 'Streams...', action = 'show_streams'),
##                            dict(name = 'Stop', action = 'stop_streams', enabled_when = 'streaming'),
##                            #dict(name = 'Save Graph ...', action = '_save_graph', enabled_when = 'dirty')
##                            ]),
#
#
#                self.get_calibration_menu()
#
#                ]
##    def get_calibration_menu(self):
##        '''
##        '''
##        return ('Calibration', [
##                               dict(name = 'Power Map', action = 'launch_power_map'),
##                               dict(name = 'Beam Scan', action = 'launch_beam_scan')
###                               dict(name = 'Power Scan', action = 'launch_power_scan'),
###                               dict(name = 'Laser Pulse', action = 'launch_laser_pulse')
##                                  ]
##                                )

#    def control_group(self):
#        cg = VGroup(
#                    HGroup(
#                          # Item('simulation_led', show_label = False, style = 'custom', editor = LEDEditor()),
#                           Item('enabled_led', show_label = False, style = 'custom', editor = LEDEditor()),
#                           self._button_factory('enable', 'enable_label', None),
#                           ),
#
#                    self._slider_group_factory([('request_power', 'request_power',
#                                                 {'enabled_when':'object.parent._enabled',
#                                                  'defined_when':'object.parent.use_power_slider'
#                                                  }
#                                                 #{'defined_when':'"Diode" not in object.parent.__class__.__name__'}
#                                                 )]),
#                    self._update_slider_group_factory([('zoom', 'zoom', {})]),
#                    self._update_slider_group_factory([('beam', 'beam', {})]),
#
#                    defined_when = 'object.controllable'
#                    )
#        return cg
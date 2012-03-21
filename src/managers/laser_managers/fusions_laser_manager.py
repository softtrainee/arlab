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
from src.graph.stream_graph import StreamGraph
'''
'''
#=============enthought library imports=======================
from traits.api import DelegatesTo, Property, Instance, Str, List, Dict, \
    on_trait_change, Event, Bool
from traitsui.api import VGroup, Item, HGroup, spring, EnumEditor
from pyface.timer.do_later import do_later
#=============standard library imports ========================
from threading import Thread, Timer as DoLaterTimer
import time
#=============local library imports  ==========================

from src.helpers.timer import Timer
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.hardware.fusions.fusions_logic_board import FusionsLogicBoard
from src.hardware.fiber_light import FiberLight
from src.led.led_editor import LEDEditor

from laser_manager import LaserManager


class FusionsLaserManager(LaserManager):
    '''
    '''

    logic_board = Instance(FusionsLogicBoard)

    #subsystem = Instance(ArduinoSubsystem)
    fiber_light = Instance(FiberLight)

#    light = DelegatesTo('fiber_light', prefix='power')
#    light_label = DelegatesTo('fiber_light', prefix='power_label')
#    light_intensity = DelegatesTo('fiber_light', prefix='intensity')

    beam = DelegatesTo('logic_board')
    beammin = DelegatesTo('logic_board')
    beammax = DelegatesTo('logic_board')
    update_beam = DelegatesTo('logic_board')
    beam_enabled = Bool(True)

    zoom = DelegatesTo('logic_board')
    zoommin = DelegatesTo('logic_board')
    zoommax = DelegatesTo('logic_board')
    update_zoom = DelegatesTo('logic_board')

    pointer = Event
    pointer_state = Bool(False)
    pointer_label = Property(depends_on='pointer_state')

    step_heat_manager = None

    lens_configuration = Str('gaussian')
    lens_configuration_dict = Dict
    lens_configuration_names = List

    power_timer = None
    power_graph = None

    def _record_power(self):
        p = self.get_laser_watts()
        if p is not None:
            self.data_manager.add_time_stamped_value(p, rawtime=True)

            try:
                self.power_graph.record(p)
            except Exception, e:
                self.info(e)
                print 'record power ', e

    def open_power_graph(self, rid):
        if self.power_graph is None:
            g = StreamGraph(window_title='Power Readback - {}'.format(rid),
                            window_x=0.01,
                            window_y=0.4,
                            container_dict=dict(padding=5)
                            )
            g.new_plot(data_limit=60,
                       scan_delay=1,
                       xtitle='time (s)',
                       ytitle='8bit power',

                       )
            g.new_series()
            self.power_graph = g
#        else:
#            g = self.power_graph
#            g.close()
#            g.clear()
#            g.new_plot(data_limit=60,
#                       scan_delay=1,
#                       xtitle='time (s)',
#                       ytitle='8bit power')
#            g.new_series()

#        self.power_graph.edit_traits()
        do_later(self.power_graph.edit_traits)

    def _dispose_optional_windows_hook(self):
        if self.power_graph is not None:
            self.power_graph.close()

    def start_power_recording(self, rid):
        if self.power_graph is not None:
            self.power_graph.close()
            
        self.open_power_graph(rid)

        self.data_manager = CSVDataManager()
        self.data_manager.new_frame(directory='co2power',
                                    base_frame_name=rid)
        self.power_timer = Timer(1000, self._record_power)

    def stop_power_recording(self):

        def _stop():
            self.power_timer.Stop()
            self.info('Power recording stopped')
            self.power_timer = None
            '''
                analyze the power graph
                if requested power greater than 1.5 
                average power should be greater than 2 
            '''
            if self._requested_power > 1.5:
                ps = self.power_graph.get_data(axis=1)
                a = sum(ps) / len(ps)
                if a < 2:
                    self.warning('Does not appear laser fired. Average power reading ={}'.format(a))

        if self.power_timer is not None:
            n = 5
            self.info('Stopping power recording in {} seconds'.format(n))
            t = DoLaterTimer(n, _stop)
            t.start()
#            self.power_timer.Stop()

    def _lens_configuration_changed(self):

        t = Thread(target=self.set_lens_configuration)
        t.start()

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

    def load_lens_configurations(self):
        for config_name in ['gaussian', 'homogenizer']:
            self.config_path = None
            config = self.get_configuration(name=config_name)
            if config:
                self.info('loading lens configuration {}'.format(config_name))
                self.lens_configuration_names.append(config_name)

                offset = tuple(map(int, self.config_get(config, 'General', 'offset', default='0,0').split(',')))

                bd = self.config_get(config, 'General', 'beam', cast='float')
                user_enabled = self.config_get(config, 'General', 'user_enabled', cast='boolean', default=True)
                self.lens_configuration_dict[config_name] = (bd, offset, user_enabled)

        self.set_lens_configuration('gaussian')

    def set_lens_configuration(self, name=None):
        if name is None:
            name = self.lens_configuration

        try:
            bd, offset, enabled = self.lens_configuration_dict[name]
        except KeyError:
            return

        self.stage_manager.canvas.crosshairs_offset = offset

        self.set_beam_diameter(bd, force=True)
        self.beam_enabled = enabled

    def finish_loading(self):
        '''
        '''
#        if self.fiber_light._cdevice is None:
#            self.fiber_light._cdevice = self.subsystem.get_module('FiberLightModule')

        super(FusionsLaserManager, self).finish_loading()

        self.load_lens_configurations()

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

    def set_beam_diameter(self, bd, force=False, **kw):
        '''
        '''
        result = False
        if self.beam_enabled or force:
            self.logic_board.set_beam_diameter(bd, **kw)
            result = True
        else:
            self.info('beam disabled by lens configuration {}'.format(self.lens_configuration))
        return result

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

    def _enable_hook(self):

        return self.logic_board._enable_laser_()
#        if self.logic_board._enable_laser_():
#            if self.record_lasing:
#                self.stage_manager.start_recording()
#            return True

    def _disable_hook(self):
        return self.logic_board._disable_laser_()

#        if self.record_lasing:
#            self.stage_manager.stop_recording()
#        return
#    def enable_laser(self, mode='normal'):
#        '''
#        '''
#
#        is_ok = self.logic_board._enable_laser_()
#        super(FusionsLaserManager, self).enable_laser(is_ok=is_ok)
#        return is_ok
#
#    def disable_laser(self):
#        '''
#        '''
#        super(FusionsLaserManager, self).disable_laser()
#        return self.logic_board._disable_laser_()

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
        m = factory(motion_controller=stage_controller)
        m.edit_traits()

#========================= views =========================
    def get_control_buttons(self):
        '''
        '''
        return [('enable', 'enable_label', None),
                #('pointer', 'pointer_label', None),
                #('light', 'light_label', None)
                ]

    def get_control_sliders(self):
        '''
        '''
        s = [('zoom', 'zoom', {}),
            ('beam', 'beam', {'enabled_when':'object.beam_enabled'})
            ]
        return s

    def get_lens_configuration_group(self):
        return Item('lens_configuration',
                           editor=EnumEditor(values=self.lens_configuration_names)
                           )

    def get_optics_group(self):
        csliders = self.get_control_sliders()
        vg = VGroup(
                      self._update_slider_group_factory(csliders),
                      show_border=True,
                      label='Optics'
                      )

        lens_config = self.get_lens_configuration_group()
        if lens_config:
            vg.content.insert(0, lens_config)

        return vg

    def __control__group__(self):
        '''
        '''
        power_grp = VGroup(
                           HGroup(spring,
                                  Item('enabled_led', show_label=False, style='custom', editor=LEDEditor()),
                                  self._button_group_factory(self.get_control_buttons(), orientation='h'),

                                  springy=True
                                  ),

                           show_border=True,
                           springy=True,
                           label='Power'
                           )

        ps = self.get_power_slider()
        if ps:
            ps.springy = True
            power_grp.content.append(ps)

        pulse_grp = HGroup(
                           #spring,
                           Item('pulse', show_label=False, style='custom'),
                           show_border=True,
                           springy=False,
                           label='Pulse'
                           )

        vg = VGroup()


        optics_grp = self.get_optics_group()
        hg = HGroup(#spring,
                   optics_grp,
                  #VGroup(
                      pulse_grp,
                      power_grp,
                   #   springy=True,
                      #show_border=True
                    #  ),
                  springy=True
                  )
#        vg.content.append(self._update_slider_group_factory(csliders))
        vg.content.append(hg)

        ac = self.get_additional_controls()
        if ac is not None:
            vg = HGroup(vg, ac)

        return vg

    def _get_pointer_label(self):
        '''
        '''
        return 'Pointer ON' if not self.pointer_state else 'Pointer OFF'
    def _get_lock_stage_label(self):
        return 'Lock' if not self.lock_stage_state else 'Unlock'
#========================= defaults =======================
#    def _subsystem_default(self):
#        '''
#        '''
#        return ArduinoSubsystem(name='arduino_subsystem_2')

    def _fiber_light_default(self):
        '''
        '''
        return FiberLight(name='fiber_light')
if __name__ == '__main__':

    d = FusionsLaserManager()
    d.open_power_graph('1')
#    d.configure_traits()
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

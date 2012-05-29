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

#=============enthought library imports=======================
from traits.api import DelegatesTo, Property, Instance, Str, List, Dict, \
    on_trait_change, Event, Bool, Float
from traitsui.api import VGroup, Item, HGroup, spring, EnumEditor
from pyface.timer.do_later import do_later
from apptools.preferences.preference_binding import bind_preference
#=============standard library imports ========================
from threading import Thread, Timer as DoLaterTimer, Lock
import time
#=============local library imports  ==========================
from src.graph.stream_graph import StreamGraph
from src.database.adapters.power_adapter import PowerAdapter
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.data_warehouse import DataWarehouse
from src.helpers.timer import Timer
from src.hardware.fusions.fusions_logic_board import FusionsLogicBoard
from src.hardware.fiber_light import FiberLight
from src.led.led_editor import LEDEditor
from laser_manager import LaserManager
from src.helpers.paths import co2laser_db_root, co2laser_db
import os
from src.initializer import MProgressDialog


class FusionsLaserManager(LaserManager):
    '''
    '''

    logic_board = Instance(FusionsLogicBoard)
    fiber_light = Instance(FiberLight)

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
    brightness_timer = None

    power_graph = None
    _prev_power = 0
    record_brightness = Bool
    recording_zoom = Float

    record = Event
    record_label = Property(depends_on='_recording_power_state')
    _recording_power_state = Bool(False)

    simulation = DelegatesTo('logic_board')

    data_manager = None
    _data_manager_lock = None

    _current_rid = None

    def _record_fired(self):
        if self._recording_power_state:
            save = self.db_save_dialog()
            self.stop_power_recording(delay=0, save=save)
        else:
            t = Thread(name='fusions.power_record',
                       target=self.start_power_recording, args=('Manual',))
            t.start()

        self._recording_power_state = not self._recording_power_state

    def bind_preferences(self, pref_id):
        super(FusionsLaserManager, self).bind_preferences(pref_id)
        bind_preference(self, 'recording_zoom',
                        '{}.recording_zoom'.format(pref_id)
                        )
        bind_preference(self, 'record_brightness',
                        '{}.record_brightness'.format(pref_id)
                        )

    def _write_h5(self, table, v, x):
        dm = self.data_manager
        table = dm.get_table(table, 'Power')
        if table is not None:
            row = table.row
            row['time'] = x
            row['value'] = v
            row.append()
            table.flush()

    def _record_brightness(self):
        cp = self.get_laser_intensity(verbose=False)
        if cp is None:
            cp = 0

        xi = self.power_graph.record(cp, series=1)
        self._write_h5('brightness', cp, xi)

    def _record_power(self):
        p = self.get_laser_watts()

        if p is not None:
            self._prev_power = p
        else:
            p = self._prev_power

        if p is not None:
            try:
                x = self.power_graph.record(p)
                self._write_h5('internal', p, x)
            except Exception, e:
                self.info(e)
                print 'record power ', e

    def open_power_graph(self, rid, path=None):
        if self.power_graph is not None:
            self.power_graph.close()
            del(self.power_graph)

        g = StreamGraph(
                    window_x=0.01,
                    window_y=0.4,
                    container_dict=dict(padding=5),
#                        view_identifier='pychron.fusions.power_graph'
                    )
        self.power_graph = g

        g.window_title = 'Power Readback - {}'.format(rid)
        g.new_plot(data_limit=60,
                   scan_delay=1,
                   xtitle='time (s)',
                   ytitle='power (%)',

                   )
        g.new_series()

        if self.record_brightness:
            g.new_series()

        do_later(self._open_power_graph, g)

    def _open_power_graph(self, graph):
        ui = graph.edit_traits()
        self.add_window(ui)

    def _dispose_optional_windows_hook(self):
        if self.power_graph is not None:
            self.power_graph.close()

    def _get_record_brightness(self):
        return self.record_brightness and self._get_machine_vision() is not None

    def start_power_recording(self, rid):

        m = 'power and brightness' if self.record_brightness else 'power'
        self.info('start {} recording for {}'.format(m, rid))
        self._current_rid = rid

        #zoom in for recording
        self._previous_zoom = self.zoom
        self.set_zoom(self.recording_zoom, block=True)

        self.open_power_graph(rid)

        self.data_manager = dm = H5DataManager()
        self._data_manager_lock = Lock()

        dw = DataWarehouse(root=os.path.join(co2laser_db_root, 'power'))
        dw.build_warehouse()

        dm.new_frame(directory=dw.get_current_dir(),
                                    base_frame_name=rid)
        pg = dm.new_group('Power')
        dm.new_table(pg, 'internal')

        if self._get_record_brightness():
            dm.new_table(pg, 'brightness')

        if self.power_timer is not None:
            self.power_timer.Stop()

        self.power_timer = Timer(1000, self._record_power)

        if self.brightness_timer is not None:
            self.brightness_timer.Stop()

        #before starting the timer collect quick baseline
        #default is 5 counts @ 25 ms per count
        if self._get_record_brightness():
            self.collect_baseline_intensity()

        if self._get_record_brightness():
            self.brightness_timer = Timer(175, self._record_brightness)

    def get_power_database(self):
#        db = PowerAdapter(dbname='co2laserdb',
#                                   password='Argon')
        db = PowerAdapter(dbname=co2laser_db,
                          kind='sqlite')

        return db

    def stop_power_recording(self, delay=5, save=True):

        def _stop():
            if self.power_timer is not None:
                self.power_timer.Stop()
            if self.brightness_timer is not None:
                self.brightness_timer.Stop()

            self.info('Power recording stopped')
            self.power_timer = None
            self.brightness_timer = None
            if save:
                db = self.get_power_database()
                if db.connect():
                    dbp = db.add_power_record(rid=str(self._current_rid))
                    self._current_rid = None
                    db.add_path(dbp, self.data_manager.get_current_path())
                    db.commit()

            else:
                self.data_manager.delete_frame()

            self.data_manager.close()

            self.set_zoom(self._previous_zoom)
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

        delay = 0
        if self.power_timer is not None:
            if delay == 0:
                _stop()
            else:
                self.info('Stopping power recording in {} seconds'.format(delay))
                t = DoLaterTimer(delay, _stop)
                t.start()

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

    def collect_baseline_intensity(self, **kw):
        mv = self._get_machine_vision()
        if mv:
            mv.collect_baseline_intensity(**kw)

    def _get_machine_vision(self):
        sm = self.stage_manager
        m = 'machine_vision_manager'
        mv = None
        if hasattr(sm, m):
            mv = getattr(sm, m)
        return mv

    def get_laser_intensity(self, **kw):
        sm = self.stage_manager
        m = 'machine_vision_manager'
        if hasattr(sm, m):
            mv = getattr(sm, m)
            return mv.get_intensity(**kw)

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

    def do_motor_initialization(self, name):
        if self.logic_board:
            motor = getattr(self.logic_board, '{}_motor'.format(name))
            if motor is not None:
                n = 4
                pd = MProgressDialog(max=n, size=(550, 15))
                pd.open()
                motor.initialize(progress=pd)
                pd.close()

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
                ('record', 'record_label', None),
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

    def _get_record_label(self):
        return 'Record' if not self._recording_power_state else 'Stop'
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
#    d.open_power_graph('1')
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

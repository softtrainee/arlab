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
from traits.api import Instance, Button, Bool, Float
from traitsui.api import VGroup, Group, Item, InstanceEditor
from apptools.preferences.preference_binding import bind_preference
#=============standard library imports ========================
from functools import partial
import os
from threading import Timer
#=============local library imports  ==========================

from src.hardware.fusions.fusions_diode_logic_board import FusionsDiodeLogicBoard
# from src.hardware.fusions.vue_diode_control_module import VueDiodeControlModule
from src.hardware.mikron_pyrometer import MikronGA140Pyrometer
from src.hardware.watlow_ezzone import WatlowEZZone
from src.hardware.temperature_monitor import DPi32TemperatureMonitor
from src.hardware.pyrometer_temperature_monitor import PyrometerTemperatureMonitor


from src.lasers.laser_managers.vue_metrix_manager import VueMetrixManager
from src.paths import paths
from src.monitors.fusions_diode_laser_monitor import FusionsDiodeLaserMonitor

from fusions_laser_manager import FusionsLaserManager


class FusionsDiodeManager(FusionsLaserManager):
    '''
    '''
    id = 'pychron.fusions.diode'
    name = 'fusions_diode'
    configuration_dir_name = 'diode'

    pyrometer = Instance(MikronGA140Pyrometer)
    temperature_controller = Instance(WatlowEZZone)
    # temperature_monitor = Instance(DPi32TemperatureMonitor)

    control_module_manager = Instance(VueMetrixManager)

    pyrometer_temperature_monitor = Instance(PyrometerTemperatureMonitor)

    tune = Button
    configure = Button
    tuning = Bool

    # laser_measured_power = Float
#    thermocouple_temp = Float

#    update_timers = List
    monitor_name = 'diode_laser_monitor'
    monitor_klass = FusionsDiodeLaserMonitor

    use_power_slider = Bool(True)

    request_power = Float
    request_powermin = Float(0)
    request_powermax = Float(1500)


    dbname = paths.diodelaser_db
    db_root = paths.diodelaser_db_root

    use_calibrated_temperature = Bool(False)
    #    def finish_loading(self):
#        super(FusionsDiodeManager, self).finish_loading()
#
#        self.pyrometer.start_scan()
# #        self.control_module_manager.start_scan()

    def open_scanner(self):
        from src.lasers.scanner import ScannerController, PIDScanner
        p = '/Users/ross/Sandbox/foo.yaml'
        p = os.path.join(paths.scripts_dir, 'scanner.yaml')

        s = PIDScanner(control_path=p,
                       )

        tc = self.temperature_controller
        tm = self.get_device('temperature_monitor')
        def tc_gen():
            while 1:
                pr = tc.get_temp_and_power(verbose=False)
                for pi in pr.data:
                    yield pi

        # populate scanner with functions
        gen = tc_gen()
        s.new_function(gen, name='Temp. Pyrometer (C)', directory='diode_reflector_scans')
        s.new_function(gen, name='Power (%)')

        func = partial(tm.read_temperature, verbose=False)
        s.new_function(func, name='Reflector Temp (C)')

        # bind to request_power change. set Setpoint static value
        s.new_static_value('Setpoint')
        self.on_trait_change(lambda v:s.set_static_value('Setpoint', v), self._requested_power)

        # bind to Scanner's stop_event. Set laser power to 0.
        s.on_trait_change(lambda: self.set_laser_temperature(0), 'stop_event')

        # bind to Scanners setpoint
        s.on_trait_change(lambda v: self.set_laser_temperature(v), 'setpoint')

        sc = ScannerController(model=s,
                               application=self.application)
        self.open_view(sc)


    def bind_preferences(self, pref_id):
        super(FusionsDiodeManager, self).bind_preferences(pref_id)
        bind_preference(self, 'use_calibrated_temperature', '{}.use_calibrated_temperature'.format(pref_id))

#    def get_process_temperature(self):
#        '''
#        '''
#        return self.temperature_controller.get_temperature()



    def map_temperature(self, v):
        if self.use_calibrated_temperature:
            v = self.temperature_controller.map_temperature(v)
        return v

    def get_pyrometer_temperature(self, **kw):
        '''
        '''
        return self._try('pyrometer',
                         'read_temperature', kw)


    def get_laser_internal_temperature(self, **kw):
        '''
        '''
        return self._try('control_module_manager',
                         'get_internal_temperature', kw)

    def get_power_slider(self):
        return None

    def get_lens_configuration_group(self):
        return None

    def load_lens_configurations(self):
        pass

    def emergency_shutoff(self, *args, **kw):
        '''
 
        '''

        super(FusionsDiodeManager, self).emergency_shutoff(*args, **kw)
        self.control_module_manager.disable()

        self.temperature_controller.set_control_mode('open')
        self.temperature_controller.set_open_loop_setpoint(0.0)

    def set_laser_output(self, value, units):
        if units == 'temp':
            self.set_laser_temperature(value)
        else:
            self.set_laser_power(value)

    def set_laser_temperature(self, temp):
        return self._set_laser_power_hook(temp, mode='closed', use_calibration=self.use_calibrated_temperature)



#    def enable_laser(self):
#        '''
#        '''
#        if self.fiber_light.auto_onoff and self.fiber_light.state:
#            self.fiber_light.power_off()
#
#        #simple calls logicboard.enable_laser
#        if super(FusionsDiodeManager, self).enable_laser():
#            return self.control_module_manager.enable()
#===============================================================================
# private
#===============================================================================
    def _set_laser_power_hook(self, power, mode='open', use_calibration=False, **kw):
        ''' 
        '''
        tc = self.temperature_controller
        if tc._control_mode != mode:

            tc.set_control_mode(mode)

        func = getattr(tc, 'set_{}_loop_setpoint'.format(mode))
        func(float(power), use_calibration=use_calibration)

    def _enable_hook(self):
        if super(FusionsDiodeManager, self)._enable_hook():  # logic board sucessfully enabled
            if self.fiber_light.auto_onoff and self.fiber_light.state:
                self.fiber_light.power_off()

            return self.control_module_manager.enable()

    def _disable_hook(self):
        if self.fiber_light.auto_onoff and not self.fiber_light.state:

            fl_on = lambda:self.fiber_light.power_on()
            if self._recording_power_state:
                t = Timer(7, fl_on)
                t.start()
            else:
                fl_on()


        self.temperature_controller.disable()
        self.control_module_manager.disable()
        return super(FusionsDiodeManager, self)._disable_hook()

    def _try(self, obj, func, kw):
        try:

            obj = getattr(self, obj)
            func = getattr(obj, func)
            return func(**kw)

        except AttributeError:
            pass
#===============================================================================
# views
#===============================================================================
    def get_additional_controls(self):
#        v = Group(
        gs = [
                  VGroup(Item('temperature_controller', style='custom',
                               editor=InstanceEditor(view='control_view'),
                               show_label=False,
                               ),
                      label='Watlow',
#                      show_border = True,
                      ),
                 VGroup(Item('pyrometer', show_label=False, style='custom',
                              ),
#                      show_border = True,
                      label='Pyrometer',

                      ),
                 VGroup(Item('control_module_manager', show_label=False, style='custom',
                             ),
#                      show_border = True,
                      label='ControlModule',

                      ),
                  VGroup(Item('fiber_light', style='custom', show_label=False),
                         label='FiberLight'
                         ),
#                  layout = 'tabbed',
                ]
        return gs

#===============================================================================
# defaults
#===============================================================================
#    def _monitor_factory(self):
#        '''
#        '''
#        return DiodeLaserMonitor

#    def monitor_factory(self):
#        lm = self.monitor
#        if lm is None:
#            lm = self._monitor_factory()(manager = self,
#                            configuration_dir_name = paths.monitors_dir,
#                            name = 'diode_laser_monitor')
#        return lm

    def _temperature_monitor_default(self):
        '''
        '''
        tm = DPi32TemperatureMonitor(name='temperature_monitor',
                                     configuration_dir_name='diode')
        return tm

    def _pyrometer_default(self):
        '''
        '''
        p = MikronGA140Pyrometer(name='pyrometer',
                                 configuration_dir_name='diode')
        return p

    def _laser_controller_default(self):
        '''
        '''
        b = FusionsDiodeLogicBoard(name='laser_controller',
                                   configuration_name='laser_controller',
                                   configuration_dir_name='diode')
        return b

#    def _control_module_default(self):
#        '''
#        '''
#        b = VueDiodeControlModule(name = 'diodecontrolmodule',
#                                      configuration_dir_name = 'diode'
#                                      )
#        return b

    def _stage_manager_default(self):
        '''
        '''
        args = dict(name='stage',
                    configuration_name='stage',
                            configuration_dir_name='diode',
                             parent=self,
                             )
        return self._stage_manager_factory(args)

    def _temperature_controller_default(self):
        '''
        '''
        w = WatlowEZZone(name='temperature_controller',
                        configuration_dir_name=self.configuration_dir_name)
        return w
    def _pyrometer_temperature_monitor_default(self):
        '''
        '''
        py = PyrometerTemperatureMonitor(name='pyrometer_tm',
                                       configuration_dir_name=self.configuration_dir_name)
        return py
    def _title_default(self):
        '''
        '''
        return 'Diode Manager'

    def _control_module_manager_default(self):
        v = VueMetrixManager()  # control = self.control_module)
        return v

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    from src.initializer import Initializer


    logging_setup('fusions diode')
    f = FusionsDiodeManager()
    f.use_video = True
    f.record_brightness = True
    ini = Initializer()

    a = dict(manager=f, name='FusionsDiode')
    ini.add_initialization(a)
    ini.run()
#    f.bootstrap()
    f.configure_traits()

#======================= EOF ============================
#    def get_laser_amps(self):
#        '''
#        '''
#        return self.control_module.read_laser_amps()
#
#    def get_laser_current(self):
#        '''
#        '''
#        return self.control_module.read_laser_current_adc()

#    def get_laser_power(self):
#        '''
#        '''
#        return self.control_module.read_laser_power_adc()
#
#    def get_measured_power(self):
#        '''
#        '''
#        return self.control_module.read_measured_power()
#    def disable_laser(self):
#        '''
#        '''
#        if self.fiber_light.auto_onoff and not self.fiber_light.state:
#            self.fiber_light.power_on()
#
#        self.temperature_controller.disable()
#        self.control_module_manager.disable()
#
#        super(FusionsDiodeManager, self).disable_laser()
#
#        return True

#    def get_degas_manager(self):
#        from degas_manager import DegasManager
#
# #        path = self.open_file_dialog(default_directory = os.path.join(scripts_dir,
# #                                                                      'laserscripts',
# #                                                                      'degas'
# #                                                                      )
# #                                     )
#
#        path = '/Users/pychron/Pychrondata_beta/scripts/laserscripts/degas/puck1.rs'
#        if path:
#            dm = DegasManager()
#            dm.parent = self
#            dm.file_name = path
#            dm.new_script()
#            return dm


#    def launch_camera_scan(self):
#        '''
#        '''
#        p = os.path.join(paths.scripts_dir, 'laserscripts', 'camera_scans')
#        cs = CameraScanScript(manager = self, parent_path = p)
#        cs.open()
#
#    def launch_power_scan(self):
#        '''
#        overriding super
#        '''
#        p = os.path.join(paths.scripts_dir, 'laserscripts', 'diode_power_scans')
#        ps = DiodePowerScanScript(manager = self, parent_path = p)
#        ps.open()

#    def show_image_process(self):
#        '''
#        '''
#
#        vm = self.video_manager
#        p = os.path.join(paths.data_dir, 'video', 'testframe.png')
#        vm.process_frame(path=p)
#        vm.edit_traits(view='image_view')

#    def show_step_heater(self):
#
#        shm = StepHeatManager(laser_manager = self,
#                              video_manager = self.stage_manager.video_manager
#                              )
#        shm.edit_traits()

#    def show_pyrometer_calibration_manager(self):
#        '''
#        '''
#        c = CalibrationManager(diode_manager = self,
#                             style = 'pyrometer')
#        c.open()
#
#    def show_calibration_manager(self):
#        '''
#        '''
#
#        c = CalibrationManager(diode_manager = self)
#        c.open()

#    @on_trait_change('configure')
#    def _show_temperature_controller_configuration(self):
#        '''
#        '''
#        self.temperature_controller.edit_traits(view='configure_view')


#    def __watlow__group__(self):
#        '''
#        '''
#        return VGroup(Item('temperature_controller', style = 'custom', show_label = False),
#                      label = 'Watlow',
#                      show_border = True)
#
#    def __pyrometer__group__(self):
#        '''
#        '''
#        return VGroup(Item('pyrometer', show_label = False, style = 'custom'),
#                      show_border = True,
#                      label = 'Pyrometer')
#    def show_streams(self):
#        '''
#        '''
#
#        tc = self.temperature_controller
#        pyro = self.pyrometer
#        tm = self.pyrometer_temperature_monitor
#        apm = self.analog_power_meter
#        ipm = self.control_module
#
#
#        avaliable_streams = [apm, pyro, tc, tm, ipm]
#    @on_trait_change('tune')
#    def _tune_temperature_controller(self):
#        '''
#        '''
#        if not self.tuning:
#            tune = TuneThread(self)
#            tune.setDaemon(1)
#            tune.start()
#
#        self.tuning = not self.tuning

#    @on_trait_change('calibrate')
#    def _calibrate_power(self):
#        '''
#        '''
#
#        cm = CalibrationManager(parent = self)
#        cm._calibrate_()
#        cm.edit_traits(kind = 'livemodal')


#    def _devices_default(self):
#        '''
#        '''
#        return [self.pyrometer,
#                self.temperature_controller,
#                self.temperature_monitor,
#                self.analog_power_meter,
#                self.logic_board,
#                self.control_module,
#                self.stage_controller]

#    def launch_power_profile(self):
#        '''
#        '''
#        self.logger.info('launching power profile')
#
#        sm = self.stream_manager
#        tc = self.temperature_controller
#        pyro = self.pyrometer
#        stm = self.stage_manager
#        apm = self.analog_power_meter
#
#        self.raster_manager = rm = RasterManager(stream_manager = sm)
#
#        if not stm.centered:
#            self.warning('Please set a center position')
#
#            return
#        p=os.path.join(preferences.root,'laserscripts','beamprofile.txt')
#        pt = BeamProfileThread(self,p)
#        rm.set_canvas_parameters(pt.steps, pt.steps)
#
#        if sm.open_stream_loader([pyro, tc, apm]):
#            self.dirty = True
#
#            #setup the data frame
#            dm = sm.data_manager
#            if not self.streaming:
#                self.streaming = True
#
#                dm.add_group('molectron')
#            for i in range(10):
#                dm.add_group('row%i' % i, parent = 'root.molectron')
#                for j in range(10):
#                    dm.add_group('cell%i%i' % (i, j), parent = 'root.molectron.row%i' % i)
#                    dm.add_table('power', parent = 'root.molectron.row%i.cell%i%i' % (i, i, j))
#
#            #stm.edit_traits(kind = 'livemodal')
#            pt.center_x = stm.center_x
#            pt.center_y = stm.center_y
#
#            pt.start()
#            rm.edit_traits()
#    def get_calibration_menu(self):
#        d = super(FusionsDiodeManager, self).get_calibration_menu()
#        dn = d[1] + [#dict(name='Calibrate',action='show_calibration_manager'),
#                 dict(name = 'Calibrate Pyrometer', action = 'show_pyrometer_calibration_manager'),
#                 dict(name = 'Camera Scan', action = 'launch_camera_scan'),
#                 dict(name = 'Image Process', action = 'show_image_process')
#                 ]
#        return (d[0], dn)
#    def get_control_buttons(self):
#        '''
#        '''
#        v = super(FusionsDiodeManager, self).get_control_buttons()
#        return v + [('pointer', None, None),
#                  #('enable', None, None),
#                  #('interlock', None, None)
#                  ]

#    def get_menus(self):
#        '''
#        '''
#        m = super(FusionsDiodeManager, self).get_menus()
#
#
#
#        m += [('Calibration', [
#                                  dict(name = 'Tune', action = '_tune_temperature_controller'),
#                                  dict(name = 'Calibrate', action = '_calibrate_power'),
#                                  #dict(name='Open Graph',action='_open_graph'),
#                                  dict(name = 'Power Profile', action = 'launch_power_profile'),
#                                  ]
#                                ),
#
# #            ('Streams', [dict(name = 'Stop', action = 'stop_streams', enabled_when = 'streaming'),
# #                        dict(name = 'Stream ...', action = '_launch_stream'),
# #                        dict(name='Save Graph ...', action ='_save_graph', enabled_when='dirty')
# #                        ])
#                ]
#        return m

#    def show_stats_view(self):
#        '''
#        '''
#
#        self.timer = t = Timer(1000, self._update_stats)
#        self.update_timers.append(t)
#        self.outputfile = open(os.path.join(paths.data_dir, 'laser_stats.txt'), 'w')
#        self.outputfile.write('time\tlaser power\tmeasured power\tlaser_current\tlaser amps\n')
#
#        self.edit_traits(view = 'stats_view')
#
#    def _update_stats(self):
#        '''
#        '''
#        self.laser_power = lp = self.get_laser_power()
#        self.laser_measured_power = lm = self.get_measured_power()
#        self.laser_current = lc = self.get_laser_current()
#        self.laser_amps = la = self.get_laser_amps()
#        self.outputfile.write('%s\n' % '\t'.join(('%0.3f' % time.time(), '%s' % lp, '%s' % lm, '%s' % lc, '%s' % la)))
#
#    def _request_amps_changed(self):
#        '''
#        '''
#        self.control_module.set_request_amps(self.request_amps)
#
#    def stats_view(self):
#        '''
#        '''
#        v = View(VGroup(Item('request_amps'),
#                      Item('laser_power'),
#                      Item('laser_measured_power'),
#                      Item('laser_current'),
#                      Item('laser_amps'),
#                    ),
#                    resizable = True,
#                    handler = UpdateHandler
#                )
#        return v

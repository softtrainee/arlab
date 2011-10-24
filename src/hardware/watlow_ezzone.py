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

#=============enthought library imports========================
from traits.api import Enum, Float, Event, Property, Int, String, Button, Bool, Str
from traitsui.api import View, HGroup, Item, Group, VGroup, EnumEditor, RangeEditor, ButtonEditor
from pyface.timer.api import Timer
#=============standard library imports ========================
import sys, os
#=============local library imports  ==========================
sys.path.insert(0, os.path.join(os.path.expanduser('~'),
                               'Programming', 'mercurial', 'pychron_beta'))

from core.core_device import CoreDevice
from src.helpers.logger_setup import setup
from src.graph.time_series_graph import TimeSeriesStreamGraph
from pyface.timer.do_later import do_later
sensor_map = {'62':'off',
                    '95':'thermocouple',
                    '104':'volts dc',
                    '112':'milliamps',
                    '113':'rtd 100 ohm',
                    '114':'rtd 1000 ohm',
                    '155':'potentiometer',
                    '229':'thermistor'
                    }
isensor_map = {'off':62,
                'thermocouple':95,
                'volts dc':104,
                 'milliamps':112,
                 'rtd 100 ohm':113,
                  'rtd 1000 ohm':114,
                'potentiometer':155,
                    'thermistor':229
                    }
itc_map = {'B':11, 'K':48,
                'C':15, 'N':58,
                'D':23, 'R':80,
                'E':26, 'S':84,
                'F':30, 'T':93,
                'J':46,
                }
tc_map = {'11':'B', '48':'K',
         '15':'C', '58':'N',
         '23':'D', '80':'R',
         '26':'E', '84':'S',
         '30':'F', '93':'T',
         '46':'J'}
autotune_aggressive_map = {'under damp':99,
                         'critical damp':21,
                         'over damp':69
                         }
yesno_map = {'59':'NO', '106':'YES'}
heat_alogrithm_map = {'62':'off', '71':'PID', '64':'on-off'}
class WatlowEZZone(CoreDevice):
    '''
    WatlowEZZone represents a WatlowEZZone PM PID controller.
    this class provides human readable methods for setting the modbus registers 
    '''
    Ph = Property(Float(enter_set=True,
                        auto_set=False), depends_on='_Ph_')
    _Ph_ = Float(50)
    Pc = Property(Float(enter_set=True,
                        auto_set=False), depends_on='_Pc_')
    _Pc_ = Float(4)
    I = Property(Float(enter_set=True,
                        auto_set=False), depends_on='_I_')
    _I_ = Float(32)
    D = Property(Float(enter_set=True,
                        auto_set=False), depends_on='_D_')
    _D_ = Float(33)

#    pmin = Float(0.0)
#    pmax = Float(100.0)
#    imin = Float(0.0)
#    imax = Float(6000.0)
#    dmin = Float(0.0)
#    dmax = Float(6000.0)

    stablization_time = Float(3.0)
    sample_time = Float(0.25)
    nsamples = Int(5)
    tune_setpoint = Float(500.0)
    delay = Int(1)

#    power=Property
#    _power=Float(0.0)
#    powermin=Float(300.0)
#    powermax=Float(1500.0)
#    
    closed_loop_setpoint = Property(Float(0,
                                          auto_set=False,
                                          enter_set=True),
                                    depends_on='_clsetpoint')
    _clsetpoint = Float(0.0)
    setpointmin = Float(0.0)
    setpointmax = Float(100.0)

    open_loop_setpoint = Property(Float(0, auto_set=False,
                                        enter_set=True),
                                 depends_on='_olsetpoint')
    _olsetpoint = Float(0.0)
    olsmin = Float(0.0)
    olsmax = Float(100.0)

#    calibration_offset = Property
#    _calibration_offset = Float
#    comin = Float(-500.0)
#    comax = Float(500.0)

    output_scale_low = Property(Float(auto_set=False, enter_set=True),
                               depends_on='_output_scale_low') 
    _output_scale_low = Float(0)
    
    output_scale_high = Property(Float(auto_set=False, enter_set=True),
                               depends_on='_output_scale_high') 
    _output_scale_high = Float(1)
    
    control_mode = Property(depends_on='_control_mode')
    _control_mode = String('closed')

    autotune = Event
    autotune_label = Property(depends_on='autotuning')
    autotuning = Bool
    configure = Button
    
    autotune_setpoint = Property(Float(auto_set=False, enter_set=True),
                                 depends_on='_autotune_setpoint')
    _autotune_setpoint = Float(0)
    
    enable_tru_tune = Property(Bool,
                                depends_on='_enable_tru_tune')
    _enable_tru_tune = Bool
    
    
    tru_tune_band = Property(Int(auto_set=False, enter_set=True),
                                 depends_on='_tru_tune_band')
    _tru_tune_band = Int(0)
    
    tru_tune_gain = Property(Enum(('1', '2', '3', '4', '5', '6')),
                                 depends_on='_tru_tune_gain')
    _tru_tune_gain = Str
    
    heat_alogrithm = Property(Enum('PID', 'On-Off', 'Off'),
                            depends_on='_heat_alogrithm')
    _heat_alogrithm = Str
    
    sensor1_type = Property(Enum('off', 'thermocouple', 'volts dc',
                 'milliamps', 'rtd 100 ohm', 'rtd 1000 ohm', 'potentiometer', 'thermistor'),
                            depends_on='_sensor1_type')
    
    thermocouple1_type = Property(Enum('B', 'K',
                                       'C', 'N',
                                       'D', 'R',
                                       'E', 'S',
                                       'F', 'T',
                                       'J'),
                                        depends_on='_thermocouple1_type')

    _sensor1_type = Int#(112)
    _thermocouple1_type = Int#(11)

    process_value = Float
    process_value_flag = Event
 
    heat_power_flag = Event
    heat_power_value = Float
        

    def initialize(self, *args, **kw):
        '''
        '''
        #set open loop and closed loop to zero
        self.disable()
        
        s = self.read_analog_input_sensor_type(1)
        if s is not None:
            self._sensor1_type = s
        
        print s
        if self._sensor1_type == 95:
            t = self.read_thermocouple_type(1)
            print t
            if t is not None:
                self._thermocouple1_type = t
                #print self.sensor1_type
                #print self.thermocouple1_type
        print self.sensor1_type, self._sensor1_type
        print self.thermocouple1_type, self._thermocouple1_type
        
        #read pid parameters
        ph = self.read_heat_proportional_band()
        if ph is not None:
            self._Ph_ = ph
        
        pc = self.read_cool_proportional_band()
        if pc is not None:
            self._Pc_ = pc
        
        i = self.read_time_integral()
        if i is not None:
            self._I_ = i
            
        d = self.read_time_derivative()
        if d is not None:
            self._D_ = d
            
        #read autotune parameters
        asp = self.read_autotune_setpoint()
        if asp is not None:
            self._autotune_setpoint = asp
        ttb = self.read_tru_tune_band()
        if ttb is not None:
            self._tru_tune_band = ttb
            
        ttg = self.read_tru_tune_gain()
        if ttg is not None: 
            self._tru_tune_gain = str(ttg)
        
        osl = self.read_output_scale_low()
        if osl is not None:
            self._output_scale_low = osl
            
        osh = self.read_output_scale_low()
        if osh is not None:
            self._output_scale_high = osh
        return True

    def get_temperature(self, **kw):
        '''
        '''
        if 'verbose' in kw and kw['verbose']:
            self.info('Read temperature')

        if self.simulation:
#            t = 4 + self.closed_loop_setpoint
            t = self.get_random_value() + self.closed_loop_setpoint
        else:
            t = self.read_process_value(1, **kw)
        
        if t is not None:
            try:

                t = float(t)
                self.process_value = t
                self.process_value_flag = True
                return t
            except ValueError, TypeError:
                pass
            
    def complex_query(self, **kw):
        if 'verbose' in kw and kw['verbose']:
            self.info('Do complex query')

        if self.simulation:
#            t = 4 + self.closed_loop_setpoint
            t = self.get_random_value() + self.closed_loop_setpoint
            hp = self.get_random_value()
            
        else:
            t = self.read_process_value(1, **kw)
            hp = self.read_heat_power(**kw)
        
        if t is not None and hp is not None:
            try:
                hp = float(hp)
                self.heat_power = hp
                #self.heat_power_flag = True
                
                t = float(t)
                self.process_value = t
                self.process_value_flag = True
                
                return t, hp
            except ValueError, TypeError:
                pass
            
        
#    def kill(self):
#        '''
#        '''
#        self.info('kill')
#        self.set_control_mode('open')
#        self.set_open_loop_setpoint(0)
#
#        self.set_control_mode('closed')
#        self.set_closed_loop_setpoint(0)

    def disable(self):
        self.info('disable')

        func = getattr(self, 'set_%s_loop_setpoint' % self.control_mode)
        func(0)

#        self.set_control_mode('open')
#        self.set_open_loop_setpoint(0)

    def load_additional_args(self, config):
        '''
        '''
        self.set_attribute(config, 'setpointmin', 'Setpoint', 'min', cast='float')
        self.set_attribute(config, 'setpointmax', 'Setpoint', 'max', cast='float')
        return True

    def set_closed_loop_setpoint(self, setpoint, **kw):
        '''
        '''

        self.info('setting closed loop setpoint = {:0.3f}'.format(setpoint))
        self._clsetpoint = setpoint

        self.write(2160, setpoint, nregisters=2, **kw)

    def set_open_loop_setpoint(self, setpoint, **kw):
        '''
    
        '''
        self.info('setting open loop setpoint = {:0.3f}'.format(setpoint))
        self._olsetpoint = setpoint

        self.write(2162, setpoint, nregisters=2, **kw)

    def set_temperature_units(self, comms, units, **kw):
        '''
   
            
        '''
        register = 2490 if comms == 1 else 2510
        value = 15 if units == 'C' else 30
        self.write(register, value)

    def set_calibration_offset(self, input, value, **kw):
        '''
        '''
        self.info('set calibration offset {}'.format(value))
        register = 382 if input == 1 else 462
        self.write(register, value, nregisters=2, **kw)

    def set_control_mode(self, mode, **kw):
        '''
        10=closed
        54=open
        '''
        self.info('setting control mode = %s' % mode)
        self._control_mode = mode
        value = 10 if mode == 'closed' else 54
        self.write(1880, value, **kw)
#===============================================================================
# Autotune
#===============================================================================
    def start_autotune(self, **kw):
        '''
        '''
        self.info('start autotune')
        self.write(1920, 106, **kw)
        
        
        g = TimeSeriesStreamGraph()
        sp = 1
        g.new_plot(data_limit=3600,
                   scan_delay=sp
                   )
        g.new_series()
        do_later(g.edit_traits)
        
        #start a query thread
        self.autotune_timer = Timer(sp * 1000, self._autotune_update, g)
        self.autotune_timer.Start()
        
        
    def _autotune_update(self, graph):
        if self.simulation:
            d = self.get_random_value(0, 100)
        else:
            d = self.get_temperature()
        graph.record(d)
        
    
    def stop_autotune(self, **kw):
        '''
        '''
        self.info('stop autotune')
        self.write(1920, 59, **kw)
        self.autotune_timer.Stop()
        
    def set_autotune_setpoint(self, value, **kw):
        '''
        '''
        self.info('setting autotune setpoint {:0.3f}'.format(value))
        self.write(1998, value, **kw)
        
    def set_autotune_aggressiveness(self, key, **kw):
        '''
            under damp - reach setpoint quickly
            critical damp - balance a rapid response with minimal overshoot
            over damp - reach setpoint with minimal overshoot
        '''
        if key in autotune_aggressive_map:
            value = autotune_aggressive_map[key]
        
            self.info('setting auto aggressiveness {} ({})'.format(key, value))
            
            self.write(1916, value, **kw)
        
    def set_tru_tune(self, onoff, **kw):
        if onoff:
            msg = 'enable TRU-TUNE+'
            value = 106
        else:
            msg = 'disable TRU-TUNE+'
            value = 59
        self.info(msg)  
        self.write(1910, value, **kw)
        
    def set_tru_tune_band(self, value, **kw):
        '''
            0 -100 int
            
            only adjust this parameter is controller is unable to stabilize.
            only the case for processes with fast responses
            
        '''
        self.info('setting TRU-TUNE+ band {}'.format(value))
        self.write(1912, int(value), **kw)
        
    def set_tru_tune_gain(self, value, **kw):
        '''
            1-6 int
            1= most aggressive response and potential for overshoot
            6=least "                                      "
        '''
        self.info('setting TRU-TUNE+ gain {}'.format(value))
        self.write(1914, int(value), **kw)
        
#===============================================================================
#  PID
#===============================================================================
    def set_heat_alogrithm(self, value, **kw):
        '''
        '''
        self.info('setting heat alogrithm {}'.format(value))
        self.write(1890)
        
    def set_heat_proportional_band(self, value, **kw):
        '''
        '''
        self.info('setting heat proportional band ={:0.3f}'.format(value))
        self.write(1890, value, nregisters=2, **kw)

    def set_cool_proportional_band(self, value, **kw):
        '''
        '''
        self.info('setting cool proportional band = {:0.3f}'.format(value))
        self.write(1892, value, nregisters=2, **kw)

    def set_time_integral(self, value, **kw):
        '''
        '''
        self.info('setting time integral = {:0.3f}'.format(value))
        self.write(1894, value, nregisters=2, **kw)

    def set_time_derivative(self, value, **kw):
        '''

        '''
        self.info('setting time derivative = {:0.3f}'.format(value))
        self.write(1896, value, nregisters=2, **kw)
#===============================================================================
# Output
#===============================================================================
    def set_output_function(self, value, **kw):
        '''
        '''
        
        inmap = {'heat':36,
               'off':62
               }

        if value in inmap:
            self.info('set output function {}'.format(value))
            value = inmap[value]
            self.write(722, value, **kw)

    def set_output_scale_low(self, value, **kw):
        '''
        '''
        self.info('set output scale low {}'.format(value))
        self.write(736, value, nregisters=2, **kw)

    def set_output_scale_high(self, value, **kw):
        '''
        '''
        self.info('set output scale high {}'.format(value))
        self.write(738, value, nregisters=2, **kw)

    def set_analog_input_sensor_type(self, input, value, **kw):
        '''
        '''
        self.info('set input sensor type {}'.format(value))
        register = 368 if input == 1 else 448
        v = value if isinstance(value, int) else isensor_map[value]
        self.write(register, v, **kw)
        if v == 95:
            tc = self.read_thermocouple_type(1)
            self._thermocouple1_type = tc
        

    def set_thermocouple_type(self, input, value, **kw):
        '''
        '''
        self.info('set input thermocouple type {}'.format(value))
        register = 370 if input == 1 else 450
        v = value if isinstance(value, int) else itc_map[value.upper()]

        self.write(register, v, **kw)
        
#    def duty_cycle_increment(self):
#        '''
#        simple keep track off the number of times an output state is true and 
#        the number of times queried
#        '''
#        self.n_queries += 1
#        outputstate = self.read_output_state()
#        if outputstate == 'On':
#            self.n_ons += 1
#        if self.simulation:
#            self.duty_cycle = self.get_random_value(0, 100)
#        else:
#            self.duty_cycle = self.n_ons / float(self.n_queries) * 100.
#        self.info('on = %i n = %i  dc = %0.2f' % (self.n_ons, self.n_queries, self.duty_cycle))

    def read_output_state(self, **kw):
        '''
        '''
        rid = str(self.read(1012, response_type='int', **kw))
        units_map = {'63':'On', '62':'Off'}
        return units_map[rid] if rid in units_map else None

    def read_heat_proportional_band(self, **kw):
        '''
        '''
        return self.read(1890, nregisters=2, **kw)

    def read_cool_proportional_band(self, **kw):
        '''
        '''
        return self.read(1892, nregisters=2, **kw)

    def read_time_integral(self, **kw):
        '''
        '''
        return self.read(1894, nregisters=2, **kw)

    def read_time_derivative(self, **kw):
        '''
        '''
        return self.read(1896, nregisters=2, **kw)

    def read_calibration_offset(self, input, **kw):
        '''
        '''
        register = 382 if input == 1 else 462

        return self.read(register, nregisters=2, **kw)

    def read_closed_loop_setpoint(self, **kw):
        '''
        '''
        return self.read(2160, nregisters=2, **kw)

    def read_open_loop_setpoint(self, **kw):
        '''
        '''
        return self.read(2162, nregisters=2, **kw)

    def read_analog_input_sensor_type(self, input, **kw):
        '''
        '''
        if input == 1:
            register = 368
        else:
            register = 448

        return self.read(register, response_type='int', **kw)

    def read_thermocouple_type(self, input, **kw):
        '''

        '''
        if input == 1:
            register = 370
        else:
            register = 450
        rid = self.read(register, response_type='int', **kw)
        return rid

    def read_filtered_process_value(self, input, **kw):
        '''
        '''
        return self.read(402, nregisters=2, **kw)

    def read_process_value(self, input, **kw):
        '''
            unfiltered process value
        '''
        register = 360 if input == 1 else 440

        return self.read(register, nregisters=2, **kw)

    def read_error_status(self, input, **kw):
        '''
        '''
        register = 362 if input == 1 else 442
        return self.read(register, response_type='int', **kw)

    def read_temperature_units(self, comms):
        '''
        '''
        register = 2490 if comms == 1 else 2510
        rid = str(self.read(register, response_type='int'))
        units_map = {'15':'C', '30':'F'}
        return units_map[rid] if rid in units_map else None

    def read_control_mode(self):
        '''
        '''
        return self.read(1880, response_type='int')

    def read_heat_algorithm(self, **kw):
        '''
             
        '''
        rid = str(self.read(1884, response_type='int', **kw))
        return heat_alogrithm_map[rid] if rid in heat_alogrithm_map else None

    def read_open_loop_detect_enable(self, **kw):
        '''
 
        '''
        rid = str(self.read(1922, response_type='int'))
        return yesno_map[id] if rid in yesno_map else None
    
    def read_output_scale_low(self, **kw):
        return self.read(736, **kw)
    
    def read_output_scale_high(self, **kw):
        return self.read(738, **kw)
    
    def read_output_type(self, **kw):
        '''

        '''
        r_map = {'104':'volts', '112':'milliamps'}
        rid = str(self.read(720, response_type='int', **kw))
        return r_map[rid] if rid in r_map else None

    def read_output_function(self, **kw):
        '''
       
        '''
        rid = str(self.read(722, response_type='int', **kw))
        r_map = {'36':'heat', '62':'off'}

        return r_map[rid] if rid in r_map else None
    
    def read_heat_power(self, **kw):
        '''
        '''
        return self.read(1904, **kw)

    def read_autotune_setpoint(self, **kw):
        return self.read(1998, **kw)

    def read_tru_tune_enabled(self, **kw):
        r = self.read(1919, response_type='int', **kw)
        return yesno_map[r] if r in yesno_map else None

    def read_tru_tune_band(self, **kw):
        return self.read(1912, response_type='int', **kw)
    
    def read_tru_tune_gain(self, **kw):
        return self.read(1914, response_type='int', **kw)

        
#    def read_cool_power(self,**kw):
#        register=1906
#        return self.read(register,**kw)


        
#    def _scan_(self, *args, **kw):
#        '''
#
#        '''
#        p = self.get_temperature()
#        record_id = self.name
#        self.stream_manager.record(p, record_id)


    def _get_sensor1_type(self):
        '''
        '''
        try:
            return sensor_map[str(self._sensor1_type)]
        except KeyError:
            pass
        
    def _set_sensor1_type(self, v):
        '''

        '''
        self._sensor1_type = isensor_map[v]
        self.set_analog_input_sensor_type(1, self._sensor1_type)

    def _get_thermocouple1_type(self):
        '''
        '''
        try:
            return tc_map[str(self._thermocouple1_type)]
        except KeyError:
            pass
        
    def _set_thermocouple1_type(self, v):
        '''

        '''
        self._thermocouple1_type = itc_map[v]
        self.set_thermocouple_type(1, self._thermocouple1_type)

    def _get_closed_loop_setpoint(self):
        '''
        '''
        return self._clsetpoint

    def _set_closed_loop_setpoint(self, v):
        '''

        '''
        self.set_closed_loop_setpoint(v)
        
    def _get_open_loop_setpoint(self):
        '''
        '''
        return self._olsetpoint

    def _set_open_loop_setpoint(self, v):
        '''
        '''
        self.set_open_loop_setpoint(v)

    def _get_control_mode(self):
        '''
        '''
        return self._control_mode

    def _set_control_mode(self, mode):
        '''
        '''

        self.set_control_mode(mode)

    def _get_Ph(self):
        '''
        '''
        return self._Ph_

    def _set_Ph(self, v):
        '''
        '''
        if self._validate_number(v) is not None:
            if self._validate_new(v, self._Ph_):
                self._Ph_ = v
#                self.set_control_mode('open')
                self.set_heat_proportional_band(v)
#                self.set_control_mode('closed')

    def _get_Pc(self):
        '''
        '''
        return self._Pc_

    def _set_Pc(self, v):
        '''
        '''
        if self._validate_number(v) is not None:
            if self._validate_new(v, self._Pc_):
                self._Pc_ = v
#                self.set_control_mode('open')
                self.set_cool_proportional_band(v)
#                self.set_control_mode('closed')

    def _get_I(self):
        '''
        '''
        return self._I_

    def _set_I(self, v):
        '''

        '''
        if self._validate_number(v) is not None:
            if self._validate_new(v, self._I_):
                self._I_ = v
#                self.set_control_mode('open')
                self.set_time_integral(v)
#                self.set_control_mode('closed')
    
    def _get_D(self):
        '''
        '''
        return self._D_

    def _set_D(self, v):
        '''
        '''
        if self._validate_number(v) is not None:
            if self._validate_new(v, self._D_):
                self._D_ = v
#                self.set_control_mode('open')
                self.set_time_derivative(v)
#                self.set_control_mode('closed')
    
        
    def _get_calibration_offset(self):
        '''
        '''
        return self._calibration_offset

    def _set_calibration_offset(self, v):
        '''

        '''
        self._calibration_offset = v
        self.set_calibration_offset(1, v)

    def _get_output_scale_low(self):
        return self._output_scale_low
    
    def _set_output_scale_low(self, v):
        '''
        '''
        if self._validate_number(v) is not None:
            if self._validate_new(v, self._output_scale_low):
                self._output_scale_low = v
                self.set_output_scale_low(v)
    
    def _get_output_scale_high(self):
        return self._output_scale_high
    
    def _set_output_scale_high(self, v):
        '''
        '''
        if self._validate_number(v) is not None:
            if self._validate_new(v, self._output_scale_high):
                self._output_scale_high = v
                self.set_output_scale_high(v)
        
    def _get_enable_tru_tune(self):
        return self._enable_tru_tune
    
    def _set_enable_tru_tune(self, v):
        
        self._enable_tru_tune = v
        self.set_tru_tune(v)
        
    def _get_tru_tune_band(self):
        return self._tru_tune_band
    
    def _set_tru_tune_band(self, v):
        if self._validate_number(v) is not None:
            if self._validate_new(v, self._tru_tune_band):
                self._tru_tune_band = v
                self.set_tru_tune_band(v)
            
    def _get_tru_tune_gain(self):
        return self._tru_tune_gain
    
    def _set_tru_tune_gain(self, v):
        self._tru_tune_gain = v        
        self.set_tru_tune_gain(v)
            
    def _get_autotune_setpoint(self):
        return self._autotune_setpoint
    
    def _set_autotune_setpoint(self, v):
        if self._validate_number(v) is not None:
            if self._validate_new(v, self._autotune_setpoint):
                self._autotune_setpoint = v
                self.set_autotune_setpoint(v) 
    
    def _get_heat_alogrithm(self):
        return self._heat_alogrithm
    
    def _set_heat_alogrithm(self, v):
        self._heat_alogrithm = v
        self.set_heat_alogrithm(v)
           
    def _validate_number(self, v):
        try:
            v = float(v)        
            return v
            
        except ValueError:
            pass
        
    def _validate_new(self, new, old, tol=0.001):
        if abs(new - old) > tol:
            return True
    
    def _get_autotune_label(self):
        return 'Autotune' if not self.autotuning else 'Stop'
    
    def _autotune_fired(self):
        if self.autotuning:
            self.stop_autotune()
        else:
            self.start_autotune()
            
        self.autotuning = not self.autotuning
        
    def _configure_fired(self):
        self.edit_traits(view='autotune_configure_view')
        
#========================= views ===========================
    
    def get_control_group(self):
        closed_grp = VGroup(Item('closed_loop_setpoint',
                                 label='setpoint',
                                 editor=RangeEditor(mode='slider',
                                               low_name='setpointmin', high_name='setpointmax'),
                                 visible_when='control_mode=="closed"'))

        open_grp = VGroup(Item('open_loop_setpoint',
                               label='setpoint',
                               editor=RangeEditor(mode='slider',
                                                  low_name='olsmin', high_name='olsmax'),
                               visible_when='control_mode=="open"'))
        cg = VGroup(Item('control_mode', editor=EnumEditor(values=['closed', 'open'])),
                    closed_grp, open_grp)
        return cg

    def get_configure_group(self):
        '''
        '''

        output_grp = VGroup('output_scale_low',
                              'output_scale_high',
                              label='Output',
                              show_border=True
                              )
        autotune_grp = HGroup(Item('autotune', show_label=False, editor=ButtonEditor(label_value='autotune_label')),
                              Item('configure', show_label=False, enabled_when='not autotuning'),
                            label='Autotune',
                            show_border=True
                            )
        
        input_grp = Group(VGroup(Item('sensor1_type',
                                      #editor=EnumEditor(values=sensor_map),
                                      show_label=False),
                                Item('thermocouple1_type',
                                     #editor=EnumEditor(values=tc_map),
                                     show_label=False,
                                     visible_when='_sensor1_type==95')),
                         label='Input',
                         show_border=True
                         )
        
        pid_grp = VGroup(HGroup('Ph',
                                'Pc'),
                         'I',
                         'D',
                         show_border=True,
                         label='PID')
        return Group(
                    autotune_grp,
                    HGroup(output_grp,
                           input_grp),
                    pid_grp,
                    #autotune_grp,
                    
                    )
    def autotune_configure_view(self):
        v = View('autotune_setpoint',
                 VGroup(
                        'enable_tru_tune',
                         Group(
                               Item('tru_tune_band', label='Band'),
                               Item('tru_tune_gain', label='Gain', tooltip='1:Most overshot, 6:Least overshoot'),
                               enabled_when='enable_tru_tune'),
                        show_border=True,
                        label='TRU-TUNE+'
                        ),
                 title='Autotune Configuration',
                 kind='livemodal'
                 )
        return v
    
    def traits_view(self):
        return View(self.get_configure_group())
        
if __name__ == '__main__':
    setup('foo')
    w = WatlowEZZone(name='temperature_controller',
                     configuration_dir_name='diode')
    w.bootstrap()
    w.configure_traits()
#============================== EOF ==========================

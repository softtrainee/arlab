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
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports========================
from traits.api import Float, Event, Property, Int, String, Button
from traitsui.api import View, Item, Group, VGroup, EnumEditor, RangeEditor
#=============standard library imports ========================

#=============local library imports  ==========================
from core.core_device import CoreDevice

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

class WatlowEZZone(CoreDevice):
    '''
    WatlowEZZone represents a WatlowEZZone PM PID controller.
    this class provides human readable methods for setting the modbus registers 
    '''
    Ph = Property
    _Ph_ = Float(50)
    Pc = Property
    _Pc_ = Float(4)
    I = Property
    _I_ = Float(032)
    D = Property
    _D_ = Float(33)

    pmin = Float(0.0)
    pmax = Float(100.0)
    imin = Float(0.0)
    imax = Float(6000.0)
    dmin = Float(0.0)
    dmax = Float(6000.0)

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

    scale_low = Float(0, auto_set=False, enter_set=True)
    scale_high = Float(3.8, auto_set=False, enter_set=True)

    control_mode = Property(depends_on='_control_mode')
    _control_mode = String('closed')

    autotune = Button
    configure = Button

    sensor1_type = Property(String, depends_on='_sensor1_type')
    thermocouple1_type = Property(String, depends_on='_thermocouple1_type')

    _sensor1_type = Int(95)
    _thermocouple1_type = Int(11)

    process_value = Float

    n_ons = Int
    n_queries = Int
    duty_cycle = Float
    process_value_flag = Event
    def load_configuration_values_from_device(self):
        '''
        '''
        if not self.simulation:
            self._sensor1_type = s1 = self.read_analog_input_sensor_type(1)
            #self._sensor2_type=self.read_analog_input_sensor_type(2)
            self._thermocouple1_type = t1 = self.read_thermocouple_type(1)
            #self._thermocouple2_type=self.read_thermocouple_type(2)
            print s1, t1

    def initialize(self, *args, **kw):
        '''
        '''
        #set open loop and closed loop to zero
        self.disable()
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
            @type config: C{str}
            @param config:
        '''
        self.set_attribute(config, 'setpointmin', 'Setpoint', 'min', cast='float')
        self.set_attribute(config, 'setpointmax', 'Setpoint', 'max', cast='float')
        return True

    def set_pid_parameter(self, **kw):
        '''
        '''
        self.set_control_mode('open')
        for k in kw:
            v = kw[k]
            self.trait_set(**{k:v})
            self.trait_property_changed(k, v)

        self.set_control_mode('closed')

    def set_closed_loop_setpoint(self, setpoint, **kw):
        '''
        '''

        self.info('setting closed loop setpoint = {:0.3f}'.format(setpoint))
        self._clsetpoint = setpoint

        register = 2160
        self.write(register, setpoint, nregisters=2, **kw)

    def set_open_loop_setpoint(self, setpoint, **kw):
        '''
    
        '''
        self.info('setting open loop setpoint = {:0.3f}'.format(setpoint))
        self._olsetpoint = setpoint

        register = 2162
        self.write(register, setpoint, nregisters=2, **kw)

    def set_temperature_units(self, comms, units, **kw):
        '''
            @type comms: C{str}
            @param comms:

            @type units: C{str}
            @param units:
            
        '''
        register = 2490 if comms == 1 else 2510
        value = 15 if units == 'C' else 30
        self.write(register, value)

    def set_calibration_offset(self, input, value, **kw):
        '''
            @type input: C{str}
            @param input:

            @type value: C{str}
            @param value:
    
        '''
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
        register = 1880

        self.write(register, value, **kw)

    def start_autotune(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        self.info('starting autotune')
        register = 1920
        value = 106
        self.write(register, value, **kw)

    def set_autotune_setpoint(self):
        '''
        '''
        pass
    def set_heat_proportional_band(self, value, **kw):
        '''
            @type value: C{str}
            @param value:

        '''
        self.info.logger('setting heat proportional band = %0.3f' % value)
        register = 1890
        self.write(register, value, nregisters=2, **kw)

    def set_cool_proportional_band(self, value, **kw):
        '''
            @type value: C{str}
            @param value:

        '''
        self.info.logger('setting cool proportional band = %0.3f' % value)

        register = 1892
        self.write(register, value, nregisters=2, **kw)

    def set_time_integral(self, value, **kw):
        '''
            @type value: C{str}
            @param value:
 
        '''
        self.info.logger('setting time integral = %0.3f' % value)

        register = 1894
        self.write(register, value, nregisters=2, **kw)

    def set_time_derivative(self, value, **kw):
        '''
            @type value: C{str}
            @param value:

        '''
        self.info.logger('setting time derivative = %0.3f' % value)
        register = 1896
        self.write(register, value, nregisters=2, **kw)

    def set_output_function(self, value, **kw):
        '''
            

        '''
        register = 722
        inmap = {'heat':36,
               'off':62
               }

        if value in inmap:
            value = inmap[value]
            self.write(register, value, **kw)

    def set_output_scale_low(self, value, **kw):
        '''
          
        '''
        register = 736
        self.write(register, value, nregisters=2, **kw)

    def set_output_scale_high(self, value, **kw):
        '''
           
    
        '''
        register = 738
        self.write(register, value, nregisters=2, **kw)

    def set_analog_input_sensor_type(self, input, value, **kw):
        '''
            @type input: C{str}
            @param input:

            @type value: C{str}
            @param value:

            @type **kw: C{str}
            @param **kw:
        '''

        register = 368 if input == 1 else 448
        v = value if isinstance(value, int) else isensor_map[value]

        self.write(register, v, **kw)

    def set_thermocouple_type(self, input, value, **kw):
        '''
            @type input: C{str}
            @param input:

            @type value: C{str}
            @param value:

            @type **kw: C{str}
            @param **kw:
        '''

        register = 370 if input == 1 else 450
        v = value if isinstance(value, int) else itc_map[value.upper()]

        self.write(register, v, **kw)
    def duty_cycle_increment(self):

        #simple keep track off the number of times an output state is true and 
        #the number of times queried

        self.n_queries += 1
        outputstate = self.read_output_state()
        if outputstate == 'On':
            self.n_ons += 1
        if self.simulation:
            self.duty_cycle = self.get_random_value(0, 100)
        else:
            self.duty_cycle = self.n_ons / float(self.n_queries) * 100.
        self.info('on = %i n = %i  dc = %0.2f' % (self.n_ons, self.n_queries, self.duty_cycle))

    def read_output_state(self, **kw):
        register = 1012
        rid = str(self.read(register, response_type='int', **kw))
        units_map = {'63':'On', '62':'Off'}
        return units_map[rid] if rid in units_map else None

    def read_heat_proportional_band(self, **kw):
        '''
 
        '''
        register = 1890
        return self.read(register, nregisters=2, **kw)

    def read_cool_proportional_band(self, **kw):
        '''
     
        '''
        register = 1892
        return self.read(register, nregisters=2, **kw)

    def read_time_integral(self, **kw):
        '''
 
        '''
        register = 1894
        return self.read(register, nregisters=2, **kw)

    def read_time_derivative(self, **kw):
        '''

        '''
        register = 1896
        return self.read(register, nregisters=2, **kw)

    def read_calibration_offset(self, input, **kw):
        '''
            @type input: C{str}
            @param input:

        '''
        register = 382 if input == 1 else 462

        return self.read(register, nregisters=2, **kw)

    def read_closed_loop_setpoint(self, **kw):
        '''

        '''
        register = 2160
        return self.read(register, nregisters=2, **kw)

    def read_open_loop_setpoint(self, **kw):
        '''

        '''
        register = 2162
        return self.read(register, nregisters=2, **kw)

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
        register = 402

        return self.read(register, nregisters=2, **kw)

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
        register = 1880
        return self.read(register, response_type='int')

    def read_heat_algorithm(self, **kw):
        '''
             
        '''
        register = 1884
        rid = str(self.read(register, response_type='int', **kw))

        hal_map = {'62':'off', '71':'PID', '64':'on-off'}
        return hal_map[rid] if rid in hal_map else None

    def read_open_loop_detect_enable(self, **kw):
        '''
 
        '''
        register = 1922
        r_map = {'59':'NO', '106':'YES'}
        rid = str(self.read(register, response_type='int'))
        return r_map[id] if rid in r_map else None

    def read_output_type(self, **kw):
        '''

        '''
        register = 720
        r_map = {'104':'volts', '112':'milliamps'}
        rid = str(self.read(register, response_type='int', **kw))
        return r_map[rid] if rid in r_map else None

    def read_output_function(self, **kw):
        '''
       
        '''
        register = 722
        rid = str(self.read(register, response_type='int', **kw))
        r_map = {'36':'heat', '62':'off'}

        return r_map[rid] if rid in r_map else None
#    def read_heat_power(self,**kw):
#        register=1904
#        return self.read(register,**kw)
#    
#    def read_cool_power(self,**kw):
#        register=1906
#        return self.read(register,**kw)

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
#    def traits_view(self):
#        '''
#        '''
#
#
#        return View(
#                    self.get_control_group()
#                    #HGroup(Item('configure', show_label = False), spring),
#
##                    Item('control_mode', editor = EnumEditor(values = ['closed', 'open'])),
##                    closed_grp, open_grp
#                    )

    def configure_view(self):
        '''
        '''

        output_process = VGroup('scale_low',
                              'scale_high',
                              label='Output Process',
                              show_border=True)
        autotune_grp = VGroup(Item('autotune', show_label=False),
                            #'autotune_setpoint'
                            )
        sensor_grp = Group(VGroup(Item('sensor1_type', editor=EnumEditor(values=sensor_map)),
                                Item('thermocouple1_type',
                                     editor=EnumEditor(values=tc_map),
                                     show_label=False,
                                     visible_when='_sensor1_type==95')),

                         )
        return View(
                    autotune_grp,
                    output_process,
                    sensor_grp,
                    #tune_grp,
                    buttons=['OK', 'Cancel'],
                    kind='livemodal')
    def _scan_(self, *args, **kw):
        '''

        '''
        p = self.get_temperature()
        record_id = self.name
        self.stream_manager.record(p, record_id)

    def _configure_fired(self):
        '''
        '''
        self.load_configuration_values_from_device()
        self.edit_traits(view='configure_view')

    def _autotune_fired(self):
        '''
        '''
        self.info('starting autotune')
        self.start_autotune()

    def _get_sensor1_type(self):
        '''
        '''
        return sensor_map['%i' % self._sensor1_type]

    def _set_sensor1_type(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self._sensor1_type = int(v)
        self.set_analog_input_sensor_type(1, int(v))

    def _get_thermocouple1_type(self):
        '''
        '''
        return tc_map['%i' % self._thermocouple1_type]

    def _set_thermocouple1_type(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self._thermocouple1_type = int(v)
        self.set_thermocouple_type(1, int(v))

    def _get_closed_loop_setpoint(self):
        '''
        '''
        return self._clsetpoint

    def _set_closed_loop_setpoint(self, v):
        '''
            @type v: C{str}
            @param v:
        '''

        #self.set_control_mode('open')
        self.set_closed_loop_setpoint(v)
        #self.set_control_mode('closed')

    def _get_open_loop_setpoint(self):
        '''
        '''
        return self._olsetpoint

    def _set_open_loop_setpoint(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self.set_open_loop_setpoint(v)

    def _get_control_mode(self):
        '''
        '''
        return self._control_mode

    def _set_control_mode(self, mode):
        '''
            @type mode: C{str}
            @param mode:
        '''

        self.set_control_mode(mode)

    def _get_Ph(self):
        '''
        '''
        return self._Ph_

    def _set_Ph(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self._Ph_ = v
        self.set_heat_proportional_band(v)

    def _get_Pc(self):
        '''
        '''
        return self._Pc_

    def _set_Pc(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self._Pc_ = v
        self.set_cool_proportional_band(v)

    def _get_I(self):
        '''
        '''
        return self._I_

    def _set_I(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self._I_ = v
        self.set_time_integral(v)
    def _get_D(self):
        '''
        '''
        return self._D_

    def _set_D(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self._D_ = v
        self.set_time_derivative(v)


    def _get_calibration_offset(self):
        '''
        '''
        return self._calibration_offset

    def _set_calibration_offset(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self._calibration_offset = v
        self.set_calibration_offset(1, v)

    def _scale_low_changed(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self.set_output_scale_low(v)

    def _scale_high_changed(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self.set_output_scale_high(v)

#============================== EOF ==========================

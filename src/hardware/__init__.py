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
HW_PACKAGE_MAP = {'CommandProcessor': 'src.messaging.command_processor',
               'RemoteCommandServer': 'src.messaging.remote_command_server',
             'ArduinoSubsystem': 'src.hardware.subsystems.arduino_subsystem',
             'DPi32TemperatureMonitor': 'src.hardware.temperature_monitor',
             'ValveController': 'src.hardware.actuators.valve_controller',
             'AnalogPowerMeter': 'src.hardware.analog_power_meter',
             'ADC': 'src.hardware.adc.adc_device',
             'AgilentADC': 'src.hardware.adc.analog_digital_converter',
             'Eurotherm': 'src.hardware.eurotherm',
             'ThermoRack': 'src.hardware.thermorack',
             'MicroIonController': 'src.hardware.gauges.granville_phillips.micro_ion_controller',
             'ArgusController': 'src.hardware.argus_controller',
             'FerrupsUPS': 'src.hardware.FerrupsUPS'
             #'ControlModule': 'src.hardware.fusions.vue_diode_control_module'
             }

'''
Hardware Package contains

G{packagetree }

'''
HW_PACKAGE_MAP = {'CommandProcessor':'src.messaging.command_processor',
               'RemoteCommandServer':'src.messaging.remote_command_server',
             'ArduinoSubsystem':'src.hardware.subsystems.arduino_subsystem',
             'DPi32TemperatureMonitor':'src.hardware.temperature_monitor',
             'ValveController':'src.hardware.actuators.valve_controller',
             'AnalogPowerMeter':'src.hardware.analog_power_meter',
             'ADC':'src.hardware.adc.adc_device',
             'AgilentADC':'src.hardware.adc.analog_digital_converter',
             'Eurotherm':'src.hardware.eurotherm',
             'ThermoRack':'src.hardware.thermorack',
             'MicroIonController':'src.hardware.gauges.granville_phillips.micro_ion_controller',
             'ArgusController':'src.hardware.argus_controller'
             #'ControlModule':'src.hardware.fusions.vue_diode_control_module'
             }

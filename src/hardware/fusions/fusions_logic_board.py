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
Fusions Control board 
a combination of the logic board and the kerr microcontroller 
see Photon Machines Logic Board Command Set for additional information
'''
#=============enthought library imports=======================
from traits.api import  Instance, DelegatesTo, Str, Button
from traitsui.api import Item, VGroup, RangeEditor
#=============standard library imports ========================

import os
#=============local library imports  ==========================
from fusions_motor_configurer import FusionsMotorConfigurer
from src.hardware.core.core_device import CoreDevice

from src.hardware.kerr.kerr_snap_motor import KerrSnapMotor
from src.hardware.kerr.kerr_microcontroller import KerrMicrocontroller
from src.hardware.kerr.kerr_motor import KerrMotor

class FusionsLogicBoard(CoreDevice):
    '''
    '''

    motor_microcontroller = Instance(KerrMicrocontroller)

    beam_motor = Instance(KerrMotor)
    beam = DelegatesTo('beam_motor', prefix='data_position')
    beammin = DelegatesTo('beam_motor', prefix='min')
    beammax = DelegatesTo('beam_motor', prefix='max')
    beam_enabled = DelegatesTo('beam_motor', prefix='enabled')
    update_beam = DelegatesTo('beam_motor', prefix='update_position')

    zoom_motor = Instance(KerrMotor)
    zoom = DelegatesTo('zoom_motor', prefix='data_position')
    zoommin = DelegatesTo('zoom_motor', prefix='min')
    zoommax = DelegatesTo('zoom_motor', prefix='max')
    zoom_enabled = DelegatesTo('zoom_motor', prefix='enabled')
    update_zoom = DelegatesTo('zoom_motor', prefix='update_position')


    initialize_beam = True
    initialize_zoom = True
    configure = Button


    prefix = Str

    def initialize(self, *args, **kw):
        '''
        '''
        progress = kw['progress'] if 'progress' in kw else None
        print self._communicator.handle
        print self.ask(';LB.VER')
        #disable laser 
        if progress is not None:
            progress.change_message('Disabling Laser')
        self._disable_laser_()

        #turn off pointer
        if progress is not None:
            progress.change_message('Turning off pointer laserr')
        self.set_pointer_onoff(False)

        #initialize Kerr devices
        self.motor_microcontroller.initialize(*args, **kw)

        if self.initialize_zoom:
            zm = self.zoom_motor
            zm.initialize(*args, **kw)
            self.set_zoom(zm.nominal_position)

        if self.initialize_beam:
            bm = self.beam_motor
            bm.initialize(*args, **kw)
            self.set_beam_diameter(bm.nominal_position)

        return True

    def _build_command(self, cmd):
        '''
           
        '''
        if self.prefix is not None:
            return ''.join((self.prefix, cmd))
        else:
            self.warning('Prefix not set')

    def load_additional_args(self, config):
        '''
           
        '''

        self.prefix = self.config_get(config, 'General', 'prefix')
        if self.prefix is None:
            return False

        z = self.config_get(config, 'Motors', 'zoom')
        b = self.config_get(config, 'Motors', 'beam', optional=True)

        if z is not None:
            self.zoom_motor.load(os.path.join(self.configuration_dir_path, z))

        if b is not None:
            self.beam_motor.load(os.path.join(self.configuration_dir_path, b))

        return True

    def read_power_meter(self):
        '''
        '''
        cmd = self._build_command('ADC1')
        r = self._parse_response(self.ask(cmd))

#        if cmd is not None:
#            r = self._parse_response(self.ask(cmd))
#        else:
#            return self.current_value

        if r is not None:
            try:
                r = float(r)
            except:
                self.warning('*Bad response from ADC ==> %s' % r)

        return r

    def _scan_(self, *args):
        '''

        '''

        r = self.read_power_meter()

        if r is not None:
            self.stream_manager.record(r, self.name)


    def _configure_fired(self):
        '''
        '''
        self.configure_motors()

    def configure_motors(self):
        '''
        '''
        fc = FusionsMotorConfigurer(motors=[self.zoom_motor, self.beam_motor])
        fc.edit_traits()

#==============================================================================
#laser methods
#==============================================================================

    def check_interlocks(self):
        '''
        '''
        lock_bits = []

        if not self.simulation:
            cmd = self._build_command('INTLK')
            if cmd is not None:
                resp = None
                i = 0
                ntries = 3
                while resp is None and i < ntries:
                    resp = self._parse_response(self.ask(cmd, verbose=True, delay=100))
                    try:
                        resp = int(resp)
                    except:
                        resp = None
                    i += 1

                if resp is None:
                    return ['Failed Response']

                if resp != 0:
                    LOCK_MAP = ['External', 'E-stop', 'Coolant Flow']
                    rbits = []
                    for i in range(16):
                        if (resp >> i) & 1 == 1:
                            rbits.append(i)

                    lock_bits = [LOCK_MAP[cb] for cb in rbits]


        return lock_bits

    def _enable_laser_(self):
        '''
        '''
        interlocks = self.check_interlocks()
        if not interlocks:
            cmd = self._build_command('ENBL 1')
            if cmd is not None:
                resp = self._parse_response(self.ask(cmd, delay=100))

                if resp == 'OK' or self.simulation:
                    return True

        else:
            self._disable_laser_()
            self.warning('Cannot fire. Interlocks enabled')
            for i in interlocks:
                self.warning(i)

    def _disable_laser_(self):
        '''
        '''
        cmd = self._build_command('ENBL 0')
        if cmd is not None:
            
            resp = self._parse_response(self.ask(cmd))
#            resp = self._parse_response(self.ask(cmd, delay=100))

            if resp == 'OK' or self.simulation:
                return True


    def _set_laser_power_(self, *args, **kw):
        '''
           
        '''
        pass

    def set_pointer_onoff(self, onoff):
        '''
           
        '''
        if onoff:
            cmd = 'DRV1 1'
        else:
            cmd = 'DRV1 0'

        cmd = self._build_command(cmd)
        self.ask(cmd)

    def _parse_response(self, resp):
        '''
            remove the CR at EOL
        '''
        if resp is not None:
            return resp.rstrip()

    def _motor_microcontroller_default(self):
        '''
        '''
        return KerrMicrocontroller(name='microcontroller',
                                   parent=self)

    def _zoom_motor_default(self):
        '''
        '''
        return KerrMotor(name='zoom', parent=self)

    def _beam_motor_default(self):
        '''
        '''
        return KerrSnapMotor(name='beam', parent=self)
#==============================================================================
#motor methods
#==============================================================================
    def _block_(self, motor):
        '''

        '''
        self.info('waiting for move to complete')
        if not self.simulation:
            motor.block()
        self.info('move complete')

    def _enable_motor_(self, motor, pos):
        '''
        '''
        if motor.data_position != pos:
            motor.enabled = False

    def set_zoom(self, zoom, block=False, relative=False):
        '''

        '''
        motor = self.zoom_motor

        if relative:
            zoom = motor.data_position + zoom
            if not 0 <= zoom <= 100:
                return

        self._enable_motor_(motor, zoom)

        self.info('setting zoom to {:0.1f}'.format(zoom))

        motor.data_position = zoom

        if block:
            self._block_(motor)

    def set_beam_diameter(self, pos, block=True):
        '''

        '''
        motor = self.beam_motor

        self._enable_motor_(motor, pos)

        self.info('setting beam position {:0.3f}'.format(pos))

        motor.data_position = pos

        if block == True:
            self._block_(motor)

    def get_control_group(self):
        be = RangeEditor(low_name='beammin',
                       high_name='beammax'
                       )
        ube = RangeEditor(low_name='beammin',
                        high_name='beammax',
                        enabled=False
                        )
        zo = RangeEditor(low_name='zoommin',
                        high_name='zoommax'
                        )
        uzo = RangeEditor(low_name='zoommin',
                        high_name='zoommax',
                        enabled=False
                        )
        return VGroup(
                      Item('zoom', editor=zo),
                      Item('update_zoom', editor=uzo, show_label=False),
                      Item('beam', editor=be),
                      Item('update_beam', editor=ube, show_label=False),
                      )

#================== EOF ================================================



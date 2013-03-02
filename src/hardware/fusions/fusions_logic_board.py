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
from src.hardware.kerr.kerr_manager import KerrManager
'''
Fusions Control board
a combination of the logic board and the kerr microcontroller
see Photon Machines Logic Board Command Set for additional information
'''
#=============enthought library imports=======================
from traits.api import  Instance, DelegatesTo, Str, Float, List
#from traitsui.api import Item, VGroup, RangeEditor
from traitsui.api import Item, ListEditor, InstanceEditor, Group, View
#=============standard library imports ========================
import os
#=============local library imports  ==========================
from globals import globalv
#from fusions_motor_configurer import FusionsMotorConfigurer
from src.hardware.core.core_device import CoreDevice
from src.hardware.kerr.kerr_microcontroller import KerrMicrocontroller
from src.hardware.kerr.kerr_motor import KerrMotor


class FusionsLogicBoard(CoreDevice):
    '''
    '''

    motor_microcontroller = Instance(KerrMicrocontroller)

#    beam_motor = Instance(KerrMotor, ())
#    beam = DelegatesTo('beam_motor', prefix='data_position')
#    beammin = DelegatesTo('beam_motor', prefix='min')
#    beammax = DelegatesTo('beam_motor', prefix='max')
#    beam_enabled = DelegatesTo('beam_motor', prefix='enabled')
#    update_beam = DelegatesTo('beam_motor', prefix='update_position')
#
#    zoom_motor = Instance(KerrMotor, ())
#    zoom = DelegatesTo('zoom_motor', prefix='data_position')
#    zoommin = DelegatesTo('zoom_motor', prefix='min')
#    zoommax = DelegatesTo('zoom_motor', prefix='max')
#    zoom_enabled = DelegatesTo('zoom_motor', prefix='enabled')
#    update_zoom = DelegatesTo('zoom_motor', prefix='update_position')

#    configure = Button

    prefix = Str
    scan_func = 'read_power_meter'

    internal_meter_response = Float

    motors = List
    _test_comms = True

    def initialize(self, *args, **kw):
        '''
        '''

        #disable laser

        #test communciations with board issue warning if 
        #no handle or response is none
        resp = True
        if self._test_comms:
            resp = True if self.ask(';LB.VER') else False

#        resp = self._disable_laser_()
        if self._communicator.handle is None or resp is not True:
            if not globalv.ignore_initialization_warnings:
#                    warning(None, 'Laser not connected. Power cycle USB hub.')
                result = self.confirmation_dialog('Laser not connected. Power cycle USB hub.', title='Quit Pychron')
                if result:
                    os._exit(0)

        #turn off pointer
        self.set_pointer_onoff(False)

        #initialize Kerr devices
        self.motor_microcontroller.initialize(*args, **kw)

        for m in self.motors:
            if m.use_initialize:
                m.initialize(*args, **kw)

        return True

    def _build_command(self, *args):
        '''
        '''
        if self.prefix is not None:
            cmd = ' '.join(map(str, args))
            return ''.join((self.prefix, cmd))
        else:
            self.warning('Prefix not set')

    def load_additional_args(self, config):
        '''
        '''

        prefix = self.config_get(config, 'General', 'prefix')
        if prefix is not None:
            self.prefix = prefix

        for option in config.options('Motors'):
            v = config.get('Motors', option)
            self.add_motor(option, v)

#        z = self.config_get(config, 'Motors', 'zoom')
#        b = self.config_get(config, 'Motors', 'beam', optional=True)
#
#        if z is not None:
#            self.zoom_motor.load(os.path.join(self.configuration_dir_path, z))
#
#        if b is not None:
#            self.beam_motor.load(os.path.join(self.configuration_dir_path, b))


        return True

    def open_motor_configure(self):
        mc = KerrManager(motor=self.get_motor('attenuator'))

        mc.edit_traits()

    def add_motor(self, name, path):
        p = os.path.join(self.configuration_dir_path, path)
        config = self.get_configuration(path=p)
        klassname = self.config_get(config, 'General', 'kind', default='', optional=True)
        m = self._motor_factory(name, klassname)
        m.load(p)
#        self.info('adding motor {} klass={}'.format(name, klassname if klassname else 'KerrMotor'))
        self.info('adding motor {} klass={}'.format(name, m.__class__.__name__))
        self.motors.append(m)
        setattr(self, '{}_motor'.format(name), m)
#        if name == 'beam':
#            self.beam_motor = m
#        elif name == 'zoom':
#            self.zoom_motor = m

#    def __getattr__(self, attr):
#        if attr.endswith('_motor'):
#            return self.get_motor(attr.replace('_motor', ''))

#    def _motor_attr(self, attr, cb):
#        if 'min' in attr:
#            vattr = 'min'
#            mname = attr.replace(vattr, '')
#        elif 'max' in attr:
#            vattr = 'max'
#            mname = attr.replace(vattr, '')
#        elif 'update' in attr:
#            vattr = 'update_position'
#            mname = attr.replace('update_', '')
#        elif 'enabled' in attr:
#            vattr = 'enabled'
#            mname = attr.replace('_enabled', '')
#        else:
#            mname = attr
#            vattr = 'data_position'
#
#        motor = self.get_motor(mname)
#        if motor:
#            return cb(motor, vattr)
#
##    def __setattr__(self, attr, v):
##        print attr, v
##        cb = lambda m, va:setattr(m, va, v)
##        r = self._motor_attr(attr, cb)
##        if not r:
##            super(FusionsLogicBoard, self).__setattr__(attr, v)
#
#    def __getattr__(self, attr):
#        cb = lambda m, va:getattr(m, va)
#        return self._motor_attr(attr, cb)

#
#        if 'min' in attr:
#            vattr = 'min'
#            mname = attr.replace(vattr, '')
#        elif 'max' in attr:
#            vattr = 'max'
#            mname = attr.replace(vattr, '')
#        elif 'update' in attr:
#            vattr = 'update_position'
#            mname = attr.replace('update_', '')
#        elif 'enabled' in attr:
#            vattr = 'enabled'
#            mname = attr.replace('_enabled', '')
#        else:
#            mname = attr
#            vattr = 'data_position'
#
#        motor = self.get_motor(mname)
#        if motor:
#            return getattr(motor, vattr)
#        try:
#            motor = self.get_motor(mname)
#            if motor:
#                print mname, motor
#                return getattr(motor, vattr)
#        except Exception, e:
#            pass
#            pass

    def get_motor(self, name):
        return next((m for m in self.motors if m.name == name), None)

    def _motor_factory(self, name, klassname):
        if klassname:
            n = '{}_motor'.format(klassname.lower())
        else:
            n = 'motor'

        pkg = 'src.hardware.kerr.kerr_{}'.format(n)
        klass = 'Kerr{}Motor'.format(klassname)
        m = __import__(pkg, fromlist=[klass])
        m = getattr(m, klass)
        return m(parent=self, name=name)


#    def _configure_fired(self):
#        '''
#        '''
#        self.configure_motors()
#
#    def configure_motors(self):
#        '''
#        '''
#        fc = FusionsMotorConfigurer(motors=[self.zoom_motor, self.beam_motor])
#        fc.edit_traits()

#==============================================================================
#laser methods
#==============================================================================
    def check_interlocks(self, verbose=True):
        '''
        '''
        lock_bits = []
        if verbose:
            self.info('checking interlocks')

        if not self.simulation:
            resp = self.repeat_command('INTLK', check_type=int, verbose=verbose)

            try:
                resp = int(resp)
            except (ValueError, TypeError):
                resp = None

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

    def _enable_laser(self):
        '''
        '''
        interlocks = self.check_interlocks()
        if not interlocks:

            resp = self.repeat_command('ENBL 1', check_val='OK')
            if resp == 'OK' or self.simulation:
                return True

        else:
            self._disable_laser()
            msg = 'Cannot fire. Interlocks enabled '
            self.warning(msg)
            for i in interlocks:
                self.warning(i)

            return msg + ','.join(interlocks)

    def _disable_laser(self):
        '''
        '''
        ntries = 3
        for i in range(ntries):
            resp = self.repeat_command('ENBL 0', check_val='OK')
            if resp is None:
                self.warning('LASER NOT DISABLED {}'.format(i + 1))
            else:
                break

            if self.simulation:
                break
        else:
            return 'laser was not disabled'

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

#    def _zoom_motor_default(self):
#        '''
#        '''
#        return KerrMotor(name='zoomrrrr', parent=self)
#
#    def _beam_motor_default(self):
#        '''
#        '''
#        return KerrMotor(name='beameere', parent=self)

#==============================================================================
#motor methods
#==============================================================================
    def set_motor(self, name, value, block=False,
                  relative=False):
        motor = next((m for m in self.motors if m.name == name), None)
        if motor is None:
            return

        if relative:
            value = motor.data_position + value
            if not 0 <= value <= 100:
                return

        self._enable_motor_(motor, value)

        self.info('setting {} to {:0.1f}'.format(name, value))

        motor.data_position = value

        if block:
            self._block_(motor)

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

#    def set_zoom(self, zoom, block=False, relative=False):
#        '''
#
#        '''
#        motor = self.zoom_motor
#
#        if relative:
#            zoom = motor.data_position + zoom
#            if not 0 <= zoom <= 100:
#                return
#
#        self._enable_motor_(motor, zoom)
#
#        self.info('setting zoom to {:0.1f}'.format(zoom))
#
#        motor.data_position = zoom
#
#        if block:
#            self._block_(motor)
#
#    def set_beam_diameter(self, pos, block=True):
#        '''
#
#        '''
#        motor = self.beam_motor
#
#        self._enable_motor_(motor, pos)
#
#        self.info('setting beam position {:0.3f}'.format(pos))
#
#        motor.data_position = pos
#
#        if block == True:
#            self._block_(motor)

    def get_control_group(self):
        return Group(Item('motors', style='custom',
                          height= -100,
                          editor=ListEditor(mutable=False,
                                      columns=max(1, len(self.motors) / 2),
                                      style='custom',
                                      editor=InstanceEditor(view='control_view')),

                                      show_label=False),
                     )



#        be = RangeEditor(low_name='beammin',
#                       high_name='beammax'
#                       )
#        ube = RangeEditor(low_name='beammin',
#                        high_name='beammax',
#                        enabled=False
#                        )
#        zo = RangeEditor(low_name='zoommin',
#                        high_name='zoommax'
#                        )
#        uzo = RangeEditor(low_name='zoommin',
#                        high_name='zoommax',
#                        enabled=False
#                        )
#        return VGroup(
#                      Item('zoom', editor=zo),
#                      Item('update_zoom', editor=uzo, show_label=False),
#                      Item('beam', editor=be),
#                      Item('update_beam', editor=ube, show_label=False),
#                      )

#================== EOF ================================================

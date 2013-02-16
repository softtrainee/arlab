#===============================================================================
# Copyright 2012 Jake Ross
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

#============= enthought library imports =======================
from traits.api import CInt, Str, on_trait_change, Button, Float
from traitsui.api import View, Item, VGroup, HGroup, spring, RangeEditor
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import time
from threading import Thread
#============= local library imports  ==========================
from src.hardware.core.communicators.ethernet_communicator import EthernetCommunicator
from src.lasers.laser_managers.laser_manager import BaseLaserManager
from src.helpers.filetools import str_to_bool


class PychronLaserManager(BaseLaserManager):
    '''
    A PychronLaserManager is used to control an instance of 
    pychron remotely. 
    
    Common laser functions such as enable_laser are converted to 
    the RemoteHardwareServer equivalent and sent by the _communicator
    
    e.g enable_laser ==> self._communicator.ask('Enable')
    
    The communicators connection arguments are set in initialization.xml
    
    use a communicator block
    <plugin enabled="true" mode="client">FusionsDiode
        ...
        <communications>
          <host>129.138.12.153</host>
          <port>1069</port>
          <kind>UDP</kind>
        </communications>
    </plugin>
    '''

    port = CInt
    host = Str

    _cancel_blocking = False

    position = Str(enter_set=True, auto_set=False)
    x = Float
    y = Float
    z = Float

    def bind_preferences(self, pref_id):
        pass

    def open(self):
        host = self.host
        port = self.port

        self._communicator = ec = EthernetCommunicator(host=host,
                                                       port=port)
        return ec.open()

#===============================================================================
# patterning
#===============================================================================
    def execute_pattern(self, name=None, block=False):
        '''
            name is either a name of a file 
            of a pickled pattern obj
        '''

        pm = self.pattern_executor
        pattern = pm.load_pattern(name)
        if pattern:
            t = Thread(target=self._execute_pattern,
                       args=(pattern,))
            t.start()
            if block:
                t.join()

            return True

    def _execute_pattern(self, pattern):
        '''
        '''
        name = pattern.name
        self.info('executing pattern {}'.format(name))
        pm = self.pattern_executor

        pm.start()

        #set the current position
        xyz = self.get_position()
        if xyz:
            pm.set_current_position(*xyz)

        '''
            look for pattern name in local pattern dir
            if exists send the pickled pattern string instead of
            the name
        '''
        if pm.is_local_pattern(name):
            txt = pickle.dumps(pattern)
            msg = 'DoPattern <local pickle> {}'.format(name)
        else:
            msg = 'Do Pattern {}'.format(name)

        cmd = 'DoPattern {}'.format(txt)

        '''
            display an alternate message
            if is local pattern then txt is a binary str
            log msg instead of cmd
        '''
        self._ask(cmd, verbose=False)
        self._communicator.info(msg)

        time.sleep(0.5)

        if not self._block('IsPatterning',
                           position_callback=pm.set_current_position):
            cmd = 'AbortPattern'
            self._ask(cmd)

        pm.finish()

    @on_trait_change('pattern_executor:pattern:canceled')
    def pattern_canceled(self):
        '''
            this patterning window was closed so cancel the blocking loop
        '''
        self._cancel_blocking = True

#===============================================================================
# 
#===============================================================================


    def _move_to_position(self, pos):
        cmd = 'GoToHole {}'.format(pos)
        if isinstance(pos, tuple):
            cmd = 'SetXY {}'.format(pos[:2])
#            if len(pos) == 3:
#                cmd = 'SetZ {}'.format(pos[2])

        self.info('sending {}'.format(cmd))
        self._ask(cmd)

        time.sleep(0.5)
        return self._block()

    def enable_laser(self, *args, **kw):
        self.info('enabling laser')
        return self._ask('Enable') == 'OK'

    def disable_laser(self, *args, **kw):
        self.info('disabling laser')
        return self._ask('Disable') == 'OK'

    def set_laser_power(self, v, *args, **kw):
        self.info('set laser power {}'.format(v))
        return self._ask('SetLaserPower {}'.format(v)) == 'OK'

    def get_position(self):
        xyz = self._ask('GetPosition')
        if xyz:
            try:
                x, y, z = map(float, xyz.split(','))
                return x, y, z
            except Exception, e:
                print 'pychron laser manager get_position', e

        if self._communicator.simulation:
            return 0, 0, 0

    def _block(self, cmd='GetDriveMoving', position_callback=None):

        ask = self._ask

        cnt = 0
        tries = 0
        maxtries = 200 #timeout after 50 s
        nsuccess = 4
        self._cancel_blocking = False
        period = 0.25
        while tries < maxtries and cnt < nsuccess:
            if self._cancel_blocking:
                break

            time.sleep(period)
            resp = ask(cmd)

            if self._communicator.simulation:
                resp = 'False'

            if resp is not None:
                try:
                    if not str_to_bool(resp):
                        cnt += 1
                except:
                    cnt = 0

                if position_callback:

                    if self._communicator.simulation:
                        x, y, z = cnt / 3., cnt / 3., 0
                        position_callback(x, y, z)
                    else:
                        xyz = self.get_position()
                        if xyz:
                            position_callback(*xyz)

            else:
                cnt = 0
            tries += 1

        state = cnt >= nsuccess
        if state:
            self.info('Move completed')
        else:
            if self._cancel_blocking:
                self.info('Move failed. canceled by user')
            else:
                self.info('Move failed. timeout after {}s'.format(maxtries * period))

        return state

    def _ask(self, cmd, **kw):
        return self._communicator.ask(cmd, **kw)

    def _enable_fired(self):
        if self.enabled:
            resp = self._ask('Enable')
            self.enabled = False
        else:
            resp = self._ask('Disable')
            self.enabled = True

    def traits_view(self):
        v = View(self.get_control_button_group(),
                 Item('position'),
                 Item('x', editor=RangeEditor(low= -25.0, high=25.0)),
                 Item('y', editor=RangeEditor(low= -25.0, high=25.0)),
                 Item('z', editor=RangeEditor(low= -25.0, high=25.0)),
                 title='Laser Manager'
                 )
        return v

class PychronUVLaserManager(PychronLaserManager):
#===============================================================================
#    hy
#===============================================================================
    def _position_changed(self):
        if self.position is not None:
            self._move_to_position(self.position)
#===============================================================================
# 
#===============================================================================
    def trace_path(self, value, name):
        cmd = 'TracePath {} {}'.format(value, name)
        self.info('sending {}'.format(cmd))
        self._ask(cmd)
        return self._block(cmd='IsTracing')

    def drill_point(self, value, name):
        pass

    def _move_to_position(self, pos):
        cmd = 'GoToPoint'
        if isinstance(pos, (str, unicode)):
            if pos[0] in ['p', 'l', 'd']:
                cmd = 'GoToNamedPosition'

        if cmd:
            cmd = '{} {}'.format(cmd, pos)
            self.info('sending {}'.format(cmd))
            self._ask(cmd)
            time.sleep(0.5)
            return self._block()

#        else:
#
#            return super(PychronUVLaserManager, self)._move_to_position(pos)

#============= EOF =============================================

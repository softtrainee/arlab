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
from traits.api import CInt, Str, implements, on_trait_change
from traitsui.api import View, Item, TableEditor
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

    def bind_preferences(self, pref_id):
        pass

    def open(self):
        host = self.host
        port = self.port

        self._communicator = ec = EthernetCommunicator(host=host,
                                                       port=port)
        return ec.open()

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
        pm.show_pattern()

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
        self._ask(cmd, verbose=False)

        self._communicator.info(msg)

        time.sleep(0.5)
        self._block('IsPatterning')
        self.pattern_executor.close_pattern()

    @on_trait_change('pattern_executor:pattern:canceled')
    def pattern_canceled(self):
        self._cancel_blocking = True

    def move_to_position(self, pos, *args, **kw):
        cmd = 'GoToHole {}'.format(pos)
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

    def _block(self, cmd='GetDriveMoving'):

        ask = self._ask

        cnt = 0
        tries = 0
        maxtries = 200 #timeout after 200 s
        nsuccess = 4
        self._cancel_blocking = False
        while tries < maxtries and cnt < nsuccess:
            if self._cancel_blocking:
                break

            time.sleep(0.25)
            resp = ask(cmd)

            if self._communicator.simulation:
                cnt = nsuccess + 1
                continue

            if resp is not None:
                try:
                    if not str_to_bool(resp):
                        cnt += 1
                except:
                    cnt = 0
            else:
                cnt = 0
            tries += 1

        state = cnt > nsuccess
        if state:
            self.info('Move completed')
        else:
            if self._cancel_blocking:
                self.info('Move failed. canceled by user')
            else:
                self.info('Move failed. timeout after {}s'.format(maxtries / 4))

        return state

    def _ask(self, cmd, **kw):
        return self._communicator.ask(cmd, **kw)

#============= EOF =============================================

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
from traits.api import CInt, Str, implements
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.hardware.core.communicators.ethernet_communicator import EthernetCommunicator
from src.managers.manager import Manager
import time
from src.lasers.laser_managers.laser_manager import ILaserManager
from src.helpers.filetools import str_to_bool

class PychronLaserManager(Manager):
    implements(ILaserManager)

    port = CInt
    host = Str
    def bind_preferences(self, pref_id):
        pass

    def open(self):
        host = self.host
        port = self.port

        self._communicator = ec = EthernetCommunicator(host=host,
                                                       port=port)
        return ec.open()
    
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

    def _block(self):
        cmd = 'GetDriveMoving'
        ask = self._ask
        
        cnt=0
        tries=0
        maxtries=200 #timeout after 200 s
        nsuccess=4
        while tries<maxtries and cnt<nsuccess:
            time.sleep(0.25)
            resp = ask(cmd)
#            print 'getmoviing repos', resp
            if resp is not None:
                try:
                    if not str_to_bool(resp):
                        cnt+=1
                except:
                    cnt=0
            else:
                cnt=0
            tries+=1
            
        state=cnt>nsuccess
        if state:
            self.info('Move completed')
        else:
            self.info('Move failed. timeout after {}s'.format(maxtries/4))
        
        return state
                

    def _ask(self, cmd, **kw):
        return self._communicator.ask(cmd, **kw)



#============= EOF =============================================

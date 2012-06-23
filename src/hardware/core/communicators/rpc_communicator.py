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
#============= standard library imports ========================
#import xmlrpclib
#import hmac
#import Pyro4 as pyro
#pyro.configuration.HMAC_KEY = bytes(hmac.new('pychronjjj.rpc.hmac').digest())

#============= local library imports  ==========================
from src.hardware.core.communicators.communicator import Communicator

#return to xml-rpc ?

class RpcCommunicator(Communicator):
    '''
    '''

    def load(self, config, path):
        '''
        '''
        self._backend_load_hook(config)
        return True

    def _backend_load_hook(self, config):
        backend = self.config_get(config, 'Communications', 'backend')
        if backend == 'pyro':
            from src.rpc.backends import PyroBackend
            bk = PyroBackend()
            bk.name = self.config_get(config, 'Communications', 'name')
        else:
            from src.rpc.backends import XMLBackend
            bk = XMLBackend()
            bk.port = self.config_get(config, 'Communications', 'port')

        self._rpc_backend = bk

    def _get_handle(self):
        return self._rpc_backend.handle

    handle = property(fget=_get_handle)
#============= EOF =============================================

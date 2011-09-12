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
#============= enthought library imports =======================

#============= standard library imports ========================
import socket
from threading import Thread
import os
#============= local library imports  ==========================
from src.config_loadable import ConfigLoadable
from src.helpers import paths

from globals import use_shared_memory
import threading
from src.remote_hardware.error_handler import ErrorCode
if use_shared_memory:
    from src.messaging.shm_server import SHMServer
else:
    SHMServer = object

class CommandProcessor(ConfigLoadable):
    '''
    listens to a specified port for incoming requests.
    request will come from the repeater
    '''
    #port = None
    path = None

    _listen = True
    simulation = False
    manager = None
    _sock = None
    def load(self, *args, **kw):
        '''
        '''
        #grab the port from the repeater config file
        config = self.get_configuration(path = os.path.join(paths.device_dir,
                                                            'servers', 'repeater.cfg'))
        if config:
#            self.port = self.config_get(config, 'General', 'port', cast = 'int')
            self.path = self.config_get(config, 'General', 'path')
            return True

    def close(self):
        '''
        '''
        self.info('Stop listening to {}'.format(self.path))
        self._listen = False
        if self._sock:
            self._sock.close()

    def open(self, *args, **kw):
        '''

        '''
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            os.remove(self.path)
        except:
            pass
        self._sock.bind(self.path)

        self._sock.listen(2)
        self.info('listening to {}'.format(self.path))

        t = Thread(target = self._listener)
        t.start()
        return True

    def _listener(self, *args, **kw):
        '''
        '''

        while self._listen:

            sock, _addr = self._sock.accept()
            self._handler(sock)

    def _handler(self, rsock):
        '''
        '''
        data = rsock.recv(1024)
        #self.debug('Received %s' % data)
        if self.manager is not None:
            ptype, payload = data.split('|')

            t = Thread(target = self.manager.process_server_request, args = (ptype, payload))
            t.start()
            t.join()

            response = self.manager.get_server_response()
#            response = self.manager.process_server_request(ptype, payload)
            rsock.send(str(response))
        else:
            self.warning('No manager reference')
        rsock.close()
#============= views ===================================
#if __name__ == '__main__':
#    setup('command server')
#    e = CommandProcessor(name = 'command_server',
#                                  configuration_dir_name = 'servers')
#    e.bootstrap()
#============= EOF ====================================


#===============================================================================
# SHMCommandProcessor
#===============================================================================


class SHMCommandProcessor(SHMServer):
    '''
    listens to a specified port for incoming requests.
    request will come from the repeater
    '''
    #port = None
    path = None

    _listen = True
    simulation = False
    manager = None
    def load(self, *args, **kw):
        '''
        '''
        #grab the port from the repeater config file
        config = self.get_configuration(path = os.path.join(paths.device_dir,
                                                            'servers', 'repeater.cfg'))
        if config:
#            self.port = self.config_get(config, 'General', 'port', cast = 'int')
            self.path = self.config_get(config, 'General', 'path')
            return True

    def close(self):
        '''
        '''
        self._listen = False


    def _handle(self, data):
        '''
  
        '''
        self.debug('Received %s' % data)
        response = None
        if self.manager is not None:
            type = None
            if '|' in data:
                type, data = data.split('|')

            response = self.manager.process_server_request(type, data)

            if isinstance(response, ErrorCode):
                response = repr(response)
                
            self.debug('Response %s' % response)
        else:
            self.warning('No manager reference')

        return response

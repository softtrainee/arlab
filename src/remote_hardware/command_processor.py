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
from traits.api import Bool, Str
#============= standard library imports ========================
import socket
from threading import Thread
import os
#============= local library imports  ==========================
from src.config_loadable import ConfigLoadable
from src.helpers import paths

#from globals import use_shared_memory
from src.remote_hardware.errors.error import ErrorCode
from src.remote_hardware.context import ContextFilter
from src.remote_hardware.errors.system_errors import SystemLockErrorCode
import select

#class Processor(ThreadingUDPServer):
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
    
    system_lock_name = Str
    system_lock = Bool(False)
    system_lock_address = Str
    
    def __init__(self, *args, **kw):
        super(CommandProcessor, self).__init__(*args, **kw)
        self.context_filter = ContextFilter()

    def load(self, *args, **kw):
        '''
        '''
        #grab the port from the repeater config file
        config = self.get_configuration(path=os.path.join(paths.device_dir,
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
        self._sock.setblocking(False)
        try:
            os.remove(self.path)
        except OSError:
            pass
        
        self._sock.bind(self.path)

        self._sock.listen(10)
        self.info('listening to {}'.format(self.path))
        t = Thread(target=self._listener)
        t.start()
        
        return True
    
    
    def _check_system_lock(self, addr):    
        '''
            return true if addr is not equal to the system lock address
            ie this isnt who locked us so we deny access
        '''
#        print self.system_lock, self.system_lock_name, self.system_lock_address
        if self.system_lock:
            if not addr in [None, 'None']:
                return self.system_lock_address != addr
        
    def _listener(self, *args, **kw):
        '''
        '''

        input = [self._sock]
        while self._listen:
            
            try:
                inputready, _outputready, _exceptready = select.select(input, [], [], timeout=5)
               
                for s in inputready:
                    if s == self._sock:
                        client, _addr = self._sock.accept()
                        input.append(client)
                    else:
                        client = s
                        data = client.recv(4096)
                        if data:
                            sender_addr, ptype, payload = data.split('|')                    
                            t = Thread(target=self._process_request, args=(client, sender_addr, ptype, payload))
                            t.start()
                        else:
                            client.close()
                            input.remove(client)
                        
            except Exception, err:
                self.debug('Listener Exception {}'.format(err))
            
                    
    def _end_request(self, sock, data):
        self.debug('Result: {}'.format(data))
        try:
            sock.send(data)
            #sock.close()
        except Exception, err:
            self.debug('End Request Exception: {}'.format(err))
             
    def _process_request(self, sock, sender_addr, request_type, data):
        
        self.debug('Request: {}, {}'.format(request_type, data.strip()))
        try:
            if self._check_system_lock(sender_addr):
                result = repr(SystemLockErrorCode(self.system_lock_name,
                                             self.system_lock_address,
                                             sender_addr, logger=self.logger))
            else:
                
                result = 'error handling'
                if not request_type in ['System', 'Diode', 'Synrad', 'CO2', 'test']:
                    self.warning('Invalid request type ' + request_type)
                elif request_type == 'test':
                    result = data
                else:
        
                    klass = '{}Handler'.format(request_type.capitalize())
                    pkg = 'src.remote_hardware.handlers.{}_handler'.format(request_type.lower())
                    try:
                        
                            
                        module = __import__(pkg, globals(), locals(), [klass])
        
                        factory = getattr(module, klass)
        
                        handler = factory(application=self.application)
                        '''
                            the context filter uses the handler object to 
                            get the kind and request
                            if the min period has elapse since last request or the message is triggered
                            get and return the state from pychron
                            
                
                            pure frequency filtering could be accomplished earlier in the stream in the 
                            Remote Hardware Server (CommandRepeater.get_response) 
                        '''
        
                        result = handler.handle(data, sender_addr)
        #                result = self.context_filter.get_response(handler, data)
        
                    except ImportError, e:
                        result = 'ImportError klass={} pkg={} error={}'.format(klass, pkg, e)
        
                
                if isinstance(result, ErrorCode):
                    result = repr(result)

            self._end_request(sock, result)
        
        except Exception, err:
            self.debug('Process request Exception {}'.format(err))
        

#if __name__ == '__main__':
#    setup('command server')
#    e = CommandProcessor(name='command_server',
#                                  configuration_dir_name='servers')
#    e.bootstrap()
#============= EOF ====================================
#            
#    def _handler(self, rsock):
#        '''
#        '''
#        data = rsock.recv(1024)
#        #self.debug('Received %s' % data)
##        if self.manager is not None:
#        ptype, payload = data.split('|')
#
##            t = Thread(target=self.manager.process_server_request, args=(ptype, payload))
##            t.start()
##            t.join()
#
#            #response = self.manager.get_server_response()
#
#        response = self._process_server_request(ptype, payload)
#            #rsock.send(str(response))
##        else:
##            self.warning('No manager reference')
##        
#        return response

#===============================================================================
# SHMCommandProcessor
#===============================================================================


#class SHMCommandProcessor(SHMServer):
#    '''
#    listens to a specified port for incoming requests.
#    request will come from the repeater
#    '''
#    #port = None
#    path = None
#
#    _listen = True
#    simulation = False
#    manager = None
#    def load(self, *args, **kw):
#        '''
#        '''
#        #grab the port from the repeater config file
#        config = self.get_configuration(path=os.path.join(paths.device_dir,
#                                                            'servers', 'repeater.cfg'))
#        if config:
##            self.port = self.config_get(config, 'General', 'port', cast = 'int')
#            self.path = self.config_get(config, 'General', 'path')
#            return True
#
#    def close(self):
#        '''
#        '''
#        self._listen = False
#
#
#    def _handle(self, data):
#        '''
#  
#        '''
#        self.debug('Received %s' % data)
#        response = None
#        if self.manager is not None:
#            type = None
#            if '|' in data:
#                type, data = data.split('|')
#
#            response = self.manager.process_server_request(type, data)
#
#            if isinstance(response, ErrorCode):
#                response = repr(response)
#                
#            self.debug('Response %s' % response)
#        else:
#            self.warning('No manager reference')
#
#        return response

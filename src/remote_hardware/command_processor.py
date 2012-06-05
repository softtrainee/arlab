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



#============= enthought library imports =======================
from traits.api import Bool, Str
#============= standard library imports ========================
import socket
from threading import Thread, Lock
import os
#============= local library imports  ==========================
from src.config_loadable import ConfigLoadable

#from globals import use_shared_memory
from src.remote_hardware.errors.error import ErrorCode
from src.remote_hardware.context import ContextFilter
from src.remote_hardware.errors.system_errors import SystemLockErrorCode, \
    SecurityErrorCode
import select
from globals import ipc_dgram, use_ipc
BUFSIZE = 2048


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

    _handlers = None
    _manager_lock = None

    use_security = None
    _hosts = None

    def __init__(self, *args, **kw):
        super(CommandProcessor, self).__init__(*args, **kw)
        self.context_filter = ContextFilter()
        self._handlers = dict()
        self._manager_lock = Lock()
        self._hosts = []

#    def load(self, *args, **kw):
#        '''
#        '''
#        #grab the port from the repeater config file
#        config = self.get_configuration(path=os.path.join(paths.device_dir,
#                                                        'servers',
#                                                        'repeater.cfg'
#                                                        ))
#        if config:
#            self.path = self.config_get(config, 'General', 'path')
#
#            return True

    def close(self):
        '''
        '''
        if not use_ipc:
            return

        self.info('Stop listening to {}'.format(self.path))
        self._listen = False
        if self._sock:
            self._sock.close()

    def open(self, *args, **kw):
        '''

        '''
        if not use_ipc:
            return True


        kind = socket.SOCK_STREAM
        if ipc_dgram:
            kind = socket.SOCK_DGRAM

        self._sock = socket.socket(socket.AF_UNIX, kind)
        #self._sock.settimeout(1)
        if not ipc_dgram:
            self._sock.setblocking(False)

        try:
            os.unlink(self.path)
        except OSError:
            pass

        self._sock.bind(self.path)

        if not ipc_dgram:
            self._sock.listen(10)

        self.info('listening to {} using {}'.format(self.path,
                        'DATAGRAM' if ipc_dgram else 'STREAM'))

        t = Thread(name='processor.listener',
                   target=self._listener)
        t.start()

        return True

    def _check_system_lock(self, addr):
        '''
            return true if addr is not equal to the system lock address
            ie this isnt who locked us so we deny access
        '''
        if self.system_lock:
            if not addr in [None, 'None']:
                return self.system_lock_address != addr

    def _stream_listener(self, _input):
        try:
            ins, _, _ = select.select(_input, [], [], 5)

            for s in ins:
                if s == self._sock:
                    client, _addr = self._sock.accept()
                    _input.append(client)
                else:
                    data = s.recv(BUFSIZE)
                    if data:
    #                            sender_addr, ptype, payload = data.split('|')
                        self._process_data(s, data)
                    else:
                        s.close()
                        _input.remove(s)
        except Exception:
            pass

    def _process_data(self, sock, data):
        args = [sock] + data.split('|')
#                            args = client, sender_addr, ptype, payload
        if len(args) == 4:
#                        process request should be blocking
#                        dont spawn a new thread
            self._process_request(*args)
        else:
            self.debug('data = {}'.format(data))
            self.debug('too many args {}, {}'.format(len(args), args))
        return args

    def _dgram_listener(self):
        print 'daga'
        try:
            data, address = self._sock.recv(BUFSIZE)
            print data, address, 'f'
            if data is not None:
                self._process_data(self._sock, data)
        except socket.error:
            pass
#            args = [self._sock] + data.split('|')
#            if len(args) == 4:
##            if self._threaded:
##                t = Thread(target=self._process_request, args=args)
##                t.start()
##            else:
#                self._process_request(*args)


    def _listener(self, *args, **kw):
        '''
        '''

        _input = [self._sock]
        while self._listen:
            try:
                if ipc_dgram:
                    self._dgram_listener()
                else:
                    self._stream_listener(_input)

            except Exception, err:
                self.debug('Listener Exception {}'.format(err))
                import traceback
                tb = traceback.format_exc()
                self.debug(tb)

    def _end_request(self, sock, data):

        if use_ipc:
            #self.debug('Result: {}'.format(data))
            if isinstance(data, ErrorCode):
                data = repr(data)
            try:
                if ipc_dgram:
                    sock.sendto(data, self.path)
                else:
                    sock.send(data)
                #sock.close()
            except Exception, err:
                self.debug('End Request Exception: {}'.format(err))
        else:
            if not isinstance(data, ErrorCode):

                data = data.split('|')[-1]
#            else:
#                print data
            return data

    def get_response(self, cmd_type, data, addr):
        return self._process_request(None, addr, cmd_type, data)

    def _process_request(self, sock, sender_addr, request_type, data):
        #self.debug('Request: {}, {}'.format(request_type, data.strip()))
        try:
            if self.use_security:
                if self._hosts:
                    if not sender_addr in self._hosts:
                        return repr(SecurityErrorCode(sender_addr))
                else:
                    self.warning('hosts not configured, security not enabled')

            if self._check_system_lock(sender_addr):
                result = repr(SystemLockErrorCode(self.system_lock_name,
                                             self.system_lock_address,
                                             sender_addr, logger=self.logger))
            else:

                result = 'error handling'
                if not request_type in ['System',
                                        'Diode',
                                        'Synrad',
                                        'CO2',
                                        'test']:
                    self.warning('Invalid request type ' + request_type)
                elif request_type == 'test':
                    result = data
                else:

                    handler = None
                    klass = '{}Handler'.format(request_type.capitalize())
                    if klass not in self._handlers:
                        pkg = 'src.remote_hardware.handlers.{}_handler'.format(request_type.lower())
                        try:
                            module = __import__(pkg, globals(), locals(), [klass])
                            factory = getattr(module, klass)
                            handler = factory(application=self.application)
                            self._handlers[klass] = handler
                            '''
                                the context filter uses the handler object to
                                get the kind and request
                                if the min period has elapse since last request or the message is triggered
                                get and return the state from pychron

                                pure frequency filtering could be accomplished earlier in the stream in the 
                                Remote Hardware Server (CommandRepeater.get_response) 
                            '''
                        except ImportError, e:
                            result = 'ImportError klass={} pkg={} error={}'.format(klass, pkg, e)
                    else:
                        handler = self._handlers[klass]
                    if handler is not None:
#                    result = self.context_filter.get_response(handler, data)
                        result = handler.handle(data, sender_addr, self._manager_lock)

            r_args = self._end_request(sock, result)
            if not use_ipc:
                return r_args

        except Exception, err:
            import traceback

            tb = traceback.format_exc()
            self.debug(tb)

            self.debug('Process request Exception {}'.format(err))
            traceback.print_exc()



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

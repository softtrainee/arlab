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
from traits.api import Button, Instance, String
from traitsui.api import View, HGroup, Item, Handler
#============= standard library imports ========================
import socket
#============= local library imports  ==========================
from src.config_loadable import ConfigLoadable
from src.led.led import LED
from src.led.led_editor import LEDEditor
import random
from src.helpers.paths import pychron_src_dir
from src.remote_hardware.errors.system_errors import SystemLockErrorCode, \
    PychronCommunicationErrorCode


class CRHandler(Handler):
    def init(self, info):
        '''
  
        '''
        info.object.test_connection()


class CommandRepeater(ConfigLoadable):
    '''
    '''
    path = String(enter_set=True, auto_set=False)

    test = Button
    led = Instance(LED, ())
    
    system_lock = False
    system_lock_address = None

    def _test_fired(self):
        '''
        '''
        self.test_connection()

    def test_connection(self):
        '''
        '''
        ra = '{:0.3f}'.format(random.random())

        r = self.get_response('test', ra, None)
        connected = False
        if r is None:
            self.led.state = 0
        elif r == ra:
            self.led.state = 2
            connected = True
        
        return connected
    
    def _path_changed(self, old, new):
        '''
        '''
        if old:
            self.info('reconfigured for {}'.format(self.path))

    def traits_view(self):
        '''
        '''
        v = View(
                 'path',
                    HGroup(
                           Item('led', editor=LEDEditor(), show_label=False),
                           Item('test', show_label=False),

                           ),
                    handler=CRHandler,
                    )
        return v

    def load(self, *args, **kw):
        '''

        '''

        config = self.get_configuration()

        if config:
            self.path = self.config_get(config, 'General', 'path')
            self.info('configured for {}'.format(self.path))
            return True
        
    def remote_launch(self, name):
        import subprocess, os
        #launch pychron
        p = os.path.join(pychron_src_dir, '{}.app'.format(name))
        result = 'OK'
        try:
            subprocess.Popen(['open', p])
        except OSError:
            result = 'ERROR: failed to launch Pychron'

        return result
    
    def _check_system_lock(self, addr):    
        '''
            return true if addr is not equal to the system lock address
            ie this isnt who locked us so we deny access
        '''
        
        if self.system_lock:
            if addr is not None:
                return self.system_lock_address != addr
        
    def get_response(self, rid, data, sender_address):
        '''

        '''
        #intercept the pychron ready command
        #sent a test query 
        
        ready_flag = False
        if data == 'PychronReady':
            ready_flag = True
            data = '{:0.3f}'.format(random.random())
            rid = 'test'
        
        elif data == 'RemoteLaunch':
            return self.remote_launch('pychron')
        
        elif data in ['SystemLock On', 'SystemLock Off']:
            _cmd, onoff = data.split(' ')
            self.system_lock = onoff == 'On'
            self.system_lock_address = sender_address
            return 'OK'
        
        
        if self._check_system_lock(sender_address):
            return repr(SystemLockErrorCode(self.system_lock_address, sender_address, logger=self.logger))
        
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(self.path)
            sock.send('{}|{}'.format(rid, data))
            result = sock.recv(4096)
            sock.close()
        except socket.error, e:
            return repr(PychronCommunicationErrorCode(self.path, e))
            
        if ready_flag and data == result:
            result = 'OK'
        
        return result
#============= EOF ====================================

#===============================================================================
# SHMCommandRepeater
#===============================================================================

#class SHMCommandRepeater(SHMClient):
#    '''
#    '''
#    path = String(enter_set=True, auto_set=False)
#
#    test = Button
#    led = Instance(LED, ())
#    def _test_fired(self):
#        '''
#        '''
#        self.test_connection()
#
#    def test_connection(self):
#        '''
#        '''
#        ra = '%0.3f' % random.random()
#        r = self.get_response('test', ra)
#
#        if r is None:
#            self.led.state = 0
#        elif r == ra:
#            self.led.state = 2
#
#    def _path_changed(self, old, new):
#        '''
#        '''
#        if old:
#            self.info('reconfigured for %s' % self.path)
#
#    def traits_view(self):
#        '''
#        '''
#        v = View(
#                 'path',
#                    HGroup(
#                           Item('led', editor=LEDEditor(), show_label=False),
#                           Item('test', show_label=False),
#
#                           ),
#                    handler=CRHandler,
#                    )
#        return v
#
#    def load(self, *args, **kw):
#        '''
#  
#        '''
#
#        config = self.get_configuration()
#
#        if config:
#            self.path = self.config_get(config, 'General', 'path')
#            self.info('configured for %s' % self.path)
#            return True
#
#    def get_response(self, _type, data):
#        '''
#
#        '''
#
#        return self.send_command('|'.join((_type, data)))

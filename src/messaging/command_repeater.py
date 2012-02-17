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
from src.remote_hardware.errors.system_errors import PychronCommunicationErrorCode
from threading import Lock

from globals import ipc_dgram
from src.helpers.logger_setup import setup

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



    def load(self, *args, **kw):
        '''
        '''
        config = self.get_configuration()

        if config:
            self.path = self.config_get(config, 'General', 'path')
            self.info('configured for {}'.format(self.path))
            return True

    def open(self, *args, **kw):

        kind = socket.SOCK_STREAM
        if ipc_dgram:
            kind = socket.SOCK_DGRAM

        sock = socket.socket(socket.AF_UNIX, kind)

        sock.settimeout(3)
        self._sock = sock

        #create a sync lock
        self._lock = Lock()
        return True

    def get_response(self, rid, data, sender_address):
        '''
        '''
        #intercept the pychron ready command
        #sent a test query
        with self._lock:
            ready_flag = False
            ready_data = ''
            if data == 'PychronReady':
                ready_flag = True
                ready_data = '{:0.3f}'.format(random.random())
                rid = 'test'

            elif data == 'RemoteLaunch':
                return self.remote_launch('pychron')

            try:
                self._sock.connect(self.path)
            except socket.error:
                #_sock is already connected
                pass

            s = '{}|{}|{}'.format(sender_address, rid, data)
            send_success, rd = self._send_(s)
            if send_success:
                read_success, rd = self._read_()
                if read_success:
                    self.led.state = 'green'

            if send_success and read_success:
                if ready_flag and ready_data == rd:
                    rd = 'OK'
                result = rd
            else:
                self.led.state = 'red'
                result = repr(PychronCommunicationErrorCode(self.path, rd))

            return result
#            try:
#
#                self._sock.send()
#                self.led.state = 'green'
#            except socket.error, e:
#            result = self._sock.recv(2048)
#            if not is_ok:
#            #pychron is not running
#            self.led.state = 'red'
#            self.open()
#            return repr(PychronCommunicationErrorCode(self.path, e))
#        else:
#            return result
#            if ready_flag and data == result:
#                result = 'OK'
#
#            return result

#===============================================================================
# commands
#===============================================================================
    def test_connection(self):
        '''
        '''
        ra = '{:0.3f}'.format(random.random())

        r = self.get_response('test', ra, None)
        connected = False
        if 'ERROR 6' in r:
            self.led.state = 'red'
        elif r == ra:
            self.led.state = 'green'
            connected = True

        self.debug('Connection State - {}'.format(connected))
        return connected

    def remote_launch(self, name):
        import subprocess
        import os
        #launch pychron
        p = os.path.join(pychron_src_dir, '{}.app'.format(name))
        result = 'OK'
        try:
            subprocess.Popen(['open', p])
        except OSError:
            result = 'ERROR: failed to launch Pychron'

        return result

#===============================================================================
# response helpers
#===============================================================================
    def _send_(self, s):
        success = True
        e = None
        try:
            self._sock.send(s)
        except socket.error, e:
            success = self._handle_socket_send_error(e, s)

        return success, e

    def _read_(self):
        rd = None
        try:
            rd = self._sock.recv(2048)
            success = True
        except socket.error, e:
            success, rd = self._handle_socket_read_error(e)

        return success, rd

    def _handle_socket_send_error(self, e, s):
        retries = 0
        for ei in ['Errno 32', 'Errno 9', 'Errno 11']:
            if ei in str(e):
                retries = 3
                break

        self.info('send failed - {} - retrying n={}'.format(e, retries))

        #use a retry loop only if error is a broken pipe
        for i in range(retries):
            try:
                self.open()
                try:
                    self._sock.connect(self.path)
                except socket.error, e:
                    self.debug('connecting to {} failed. {}'.
                               format(self.path, e))

                self._sock.send(s)
                self.debug('send success on retry {}'.format(i + 1))
                return True

            except socket.error, e:
                self.debug('send retry {} failed. {}'.format(i + 1, e))

        self.info('send failed after {} retries. {}'.format(retries, e))

    def _handle_socket_read_error(self, e):
        return False, e

#==============================================================================
# View
#==============================================================================
    def _path_changed(self, old, new):
        '''
        '''
        if old:
            self.info('reconfigured for {}'.format(self.path))

    def _test_fired(self):
        '''
        '''
        self.test_connection()

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


def profiling():
    import profile

    repeator = CommandRepeater(configuration_dir_name='servers',
                               name='repeater')
#    repeator.load()
    repeator.bootstrap()
#    repeator.test_connection()

    profile.runctx('repeator.get_response(*args)', globals(), {'repeator':repeator, 'args':(1, 2, 3) })

if __name__ == '__main__':
    setup('profile_repeator')
    profiling()
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

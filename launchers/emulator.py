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

import sys
import os
version_id='_test'
p = os.path.join(os.path.expanduser('~'),
                 'Programming', 'mercurial','pychron{}'.format(version_id))

sys.path.insert(0,p)

from src.paths import paths
paths.build(version_id)

#============= enthought library imports =======================
from traits.api import Int, Bool, Event, Property
from traitsui.api import View, Item, ButtonEditor
#============= standard library imports ========================
import SocketServer
import shlex
import socket
from threading import Thread
#============= local library imports  ==========================


from src.loggable import Loggable

class VerboseServer(SocketServer.UDPServer):
    logger = None

#    def info(self, *args, **kw):
#        if self.logger:
#            self.logger.info(*args, **kw)

class Server(Loggable):
    port = Int(8000)
    host = None
    state_button = Event
    state_label = Property(depends_on='_alive')
    _alive = Bool(False)
    def _get_state_label(self):
        return 'Stop' if self._alive else 'Start'

    def _state_button_fired(self):
        if self._alive:
            self.server.shutdown()

        else:
            self.start_server()
            
        self._alive = not self._alive
            
    def start_server(self):
        host = self.host
        if host is None:
            host = socket.gethostbyname(socket.gethostname())

        port = self.port
        self.info('Starting server {} {}'.format(host, port))
        t = Thread(name='serve', target=self._serve, args=(host, port))
        t.start()

    def _serve(self, host, port):
#        self.server = server = SocketServer.UDPServer((host, port), EmulatorHandler)
        server = VerboseServer((host, port), EmulatorHandler)
        server.info = self.info
        server.allow_reuse_address = True
        self.server = server
        server.serve_forever()

    def traits_view(self):
        v = View(Item('state_button', show_label=False,
                    editor=ButtonEditor(label_value='state_label')
                    ),

                 Item('port'),

                 title='Emulator'
                 )

        return v

def verbose(func):
    def _verbose(obj, *args, **kw):
        result = func(obj, *args, **kw)
        obj.server.info('Func={} args={}'.format(func.__name__,
                                  ','.join(map(str, args))
                                  ))
        return result

    return _verbose

class QtegraEmulator(Loggable):
    #===========================================================================
    # Qtegra Protocol    
    #===========================================================================
    @verbose
    def SetMass(self, mass):
        mass = float(mass)
#        print 'setting mass %f' % mass
        return 'OK'

    @verbose
    def GetData(self, *args):
        d = [
            [36, 0.01, 1.5],
            [37, 0.1, 1.5],
            [38, 1, 1.5],
            [39, 10, 1.5],
            [40, 100, 1.5],
            ]
        return '\n'.join([','.join(map('{:0.3f}'.format, r)) for r in d])

#    @verbose
#    def GetDataNow(self, *args):
##        print 'get data now'
#        return self.GetData(*args)

    @verbose
    def GetCupConfigurations(self, *args):
#        print 'get cup configurations'
        return ','.join(['Argon'])

    @verbose
    def GetSubCupConfigurations(self, cup_name):
#        print 'get sub cup configurations for %s' % cup_name
        return ','.join(['A', 'B', 'C', 'X'])

    @verbose
    def ActivateCupConfiguration(self, names):
        cup_name, sub_cup_name = names.split(',')
        return 'OK'

    @verbose
    def SetIntegrationTime(self, itime):
        return 'OK'

    @verbose
    def GetTuneSettings(self, *args):
        return ','.join(['TuneA', 'TuneB', 'TuneC', 'TuneD'])

    @verbose
    def SetTuning(self, name):
        return 'OK'

    @verbose
    def GetHighVoltage(self,*args):
        return '4500'
    
class EmulatorHandler(SocketServer.BaseRequestHandler, QtegraEmulator):

    #===========================================================================
    # BaseRequestHandler protocol
    #===========================================================================
#    def __init__(self, *args, **kw):
#        super(EmulatorHandler, self).__init__(*args, **kw)
#        QtegraEmulator.__init__(self, **kw)


    def handle(self):
        data = self.request[0].strip()
        if ':' in data:
            datargs = data.split(':')
        else:
            datargs = shlex.split(data)

        try:
            cmd = datargs[0]
            args = tuple(datargs[1:])
            try:
                func = getattr(self, cmd)
                try:
                    result = str(func(*args))
                except TypeError:
                    result = 'Error: Invalid parameters %s passed to %s' % (args, cmd)
            except AttributeError:
                result = 'Error: Command %s not available' % cmd
        except IndexError:
            result = 'Error: poorly formatted command %s' % data

        self.server.info('received ({}) - {}, {}'.format(len(data), data, result))
        self.request[1].sendto(result + '\n', self.client_address)

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup

    logging_setup('emulator')

    s = Server(port=1099)

    s.start_server()
    s.configure_traits()
#    portn = 8000
#    s = Server()

#    ls = LinkServer()    
#    ls.start_server('129.138.12.138', 1070)

#    s.start_server('localhost', portn)
#============= EOF =============================================

#===============================================================================
# link
#===============================================================================
#class LinkServer(Loggable):
#    def start_server(self, host, port):
#        self.info('Link Starting server {} {}'.format(host, port))
#        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        server.bind((host, port))
#        server.listen(5)
#        input = [server, sys.stdin]
#        running = 1
#        c = LinkEmulator()
#        while running:
#            inputready, _outputready, _exceptready = select.select(input, [], [])
#            for s in inputready:
#
#                if s == server:
#                    # handle the server socket
#                    client, _address = server.accept()
#                    input.append(client)
#
#                elif s == sys.stdin:
#                    # handle standard input
#                    _junk = sys.stdin.readline()
#                    running = 0
#
#                else:
#                    # handle all other sockets
#
#                    c.request = s
#                    data = c.handle()
#                    if data:
#                        try:
#                            s.send(data)
#                        except socket.error:
#                            pass
#                    else:
#                        s.close()
#                        input.remove(s)
#        server.close()
#class LinkEmulator(Emulator):
#    def handle(self):
#        try:
#            data = self.request.recv(1024).strip()
#        except socket.error:
#            return
#
#        if not data:
#            return
#
#        print 'recieved (%i) - %s' % (len(data), data)
#        if ':' in data:
#            datargs = data.split(':')
#        else:
#            datargs = shlex.split(data)
#
#        try:
#            cmd = datargs[0]
#            args = tuple(datargs[1:])
#            try:
#                func = getattr(self, cmd)
#                try:
#                    result = str(func(*args))
#                except TypeError:
#                    result = 'Error: Invalid parameters %s passed to %s' % (args, cmd)
#            except AttributeError:
#                result = 'Error: Command %s not available' % cmd
#        except IndexError:
#            result = 'Error: poorly formatted command %s' % data
#
#        return result

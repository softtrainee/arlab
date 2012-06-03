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

#============= standard library imports ========================
import SocketServer
import shlex
import socket
from src.remote_hardware.handlers.system_handler import SystemHandler
from src.remote_hardware.handlers.diode_handler import DiodeHandler
from src.remote_hardware.handlers.co2_handler import Co2Handler
#============= local library imports  ==========================

class Emulator(object):
    def build_namespace(self):
        sh = SystemHandler
        dh = DiodeHandler
        ch = Co2Handler

        for h, ao in [(sh, 1), (dh, 2), (ch, 2)]:
            self._build_handler_namespace(h, args_offset=ao)

    def _build_handler_namespace(self, h, args_offset=1):
        for d in dir(h):
            if d == 'add_class_trait':
                break
            if not d.startswith('_'):
                if not hasattr(self, d):

                    if (d.startswith('Get') and not d.endswith('Moving')) or d.startswith('Read'):
                        setattr(self, d, self.get)
                    elif d.endswith('Moving'):
                        setattr(self, d, self.get_boolean)
                    else:
                        nargs = getattr(h, d).func_code.co_argcount
                        setattr(self, d, getattr(self, 'default{}'.format(nargs - args_offset)))

    def GetValveState(self, a):
        return 'True'

    def GetValveStates(self):
        return 'A1B1C0D0E1F1'

    def GetPosition(self):
        return '1,1,1'

    def GetManualState(self, a):
        return 'False'

    def default0(self):
        return 'OK'

    def default1(self, a):
        return 'OK'

    def default2(self, a, b):
        return 'OK'

    def get(self, a):
        return '10.0'

    def get_boolean(self):
        return 'True'
    #===========================================================================
    # Qtegra Protocol    
    #===========================================================================
    def SetMass(self, mass):
        mass = float(mass)
        return 'OK'

    def GetData(self, *args):
        d = [
            [36, 0.01, 1.5],
            [37, 0.1, 1.5],
            [38, 1, 1.5],
            [39, 10, 1.5],
            [40, 100, 1.5],
            ]
        return '\n'.join([','.join(['%f' % ri for ri in r]) for r in d])

    def GetDataNow(self, *args):
        return self.GetData(*args)

    def GetCupConfigurations(self, *args):
        return ','.join(['Argon'])

    def GetSubCupConfigurations(self, cup_name):
        return ','.join(['A', 'B', 'C', 'X'])

    def ActivateCupConfiguration(self, names):
        try:
            _cup_name, _sub_cup_name = names.split(',')
        except ValueError:
            return 'Error: Invalid cup and sub cup'

        return 'OK'

    def SetIntegrationTime(self, itime):
        return 'OK'

    def GetTuneSettings(self, *args):
        return ','.join(['TuneA', 'TuneB', 'TuneC', 'TuneD'])

    def SetTuning(self, name):
        return 'OK'

class BaseHandler(SocketServer.BaseRequestHandler, Emulator):
    def handle(self):
        self.build_namespace()

        data = self.request.recv(1024).strip()

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

        print 'recieved (%i) - %s, %s' % (len(data), data, result)
        self.request.send(result + '\n')

class LinkHandler(Emulator):
    def handle(self):
        self.build_namespace()
        try:
            data = self.request.recv(1024).strip()
        except socket.error:
            return

        if not data:
            return

        print 'recieved (%i) - %s' % (len(data), data)
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

        return result


if __name__ == '__main__':
    e = Emulator()
    e.build_namespace()
#============= EOF =============================================

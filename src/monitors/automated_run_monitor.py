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
from traits.api import HasTraits, List, Str, Property, Any, Array, Bool
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import vstack, hstack, array
#============= local library imports  ==========================
from src.monitors.monitor import Monitor
from src.hardware.core.communicators.ethernet_communicator import EthernetCommunicator
import time

class Check(HasTraits):
    name = Str
    parameter = Str
    action = Str
    criterion = Str
    comparator = Property
    _comparator = Str
    data = Array
    tripped = Bool
    message = Str

    def _set_comparator(self, c):
        self._comparator = c

    def _get_comparator(self):
        comp = '__eq__'
        c = self._comparator
        if c == '<':
            comp = '__gt__'
        elif c == '>':
            comp = '__lt__'
        elif c == '>=':
            comp = '__ge__'
        elif c == '<=':
            comp = '__le__'

        return comp

    def check_condition(self, v):
        '''
        '''

        vs = (time.time(), v)
        if not len(self.data):
            self.data = array([vs])
        else:
            self.data = vstack((self.data, vs))
        compf = getattr(v, self.comparator)
        cr = float(self.criterion)
        r = compf(cr)
        if r:
            self.message = 'Automated Run Check tripped. {} {} {} {}'.format(self.parameter, v, self.comparator, self.criterion)
            self.tripped = True

        return r


class AutomatedRunMonitor(Monitor):
    checks = List
    automated_run = Any
    def _load_hook(self, config):
        self.checks = []
        for section in config.sections():
            if section.startswith('Check'):
                pa = self.config_get(config, section, 'parameter')

                if 'Pressure' in pa and not ',' in pa:
                    self.warning_dialog('Invalid Pressure Parameter in AutomatedRunMonitor, need to specify name, e.g. Pressure, <gauge_name>')
                    return
                else:
                    cr = self.config_get(config, section, 'criterion')
                    co = self.config_get(config, section, 'comparator')
                    ch = Check(name=section,
                               parameter=pa,
                               criterion=cr,
                               comparator=co,

                               )
                    self.checks.append(ch)

        return True

    def _fcheck_conditions(self):
        ok = True
        for ci in self.checks:
            v = 0
            pa = ci.parameter
            if pa.startswith('Pressure'):
                pa, controller, name = pa.split(',')
                v = self.get_pressure(controller, name)

            if ci.check_condition(v):
                if self.automated_run:
                    if self.automated_run.isAlive():
                        self.automated_run.cancel()
                        self.warning_dialog(ci.message)

                ok = False
                break

        return ok

    def get_pressure(self, controller, name):
        elm = self.automated_run.extraction_line_manager
        p = elm.get_pressure(controller, name)
        return p

class RemoteAutomatedRunMonitor(AutomatedRunMonitor):
    handle = None
    def __init__(self, host, port, kind, *args, **kw):
        super(RemoteAutomatedRunMonitor, self).__init__(*args, **kw)
        self.handle = EthernetCommunicator()
        self.handle.host = host
        self.handle.port = port
        self.handle.kind = kind

    def get_pressure(self, controller, name):
        cmd = 'GetPressure {}, {}'.format(controller, name)
        p = self.handle.ask(cmd)
        try:
            p = float(p)
        except (ValueError, TypeError):
            p = 1.0
        return p

#============= EOF =============================================

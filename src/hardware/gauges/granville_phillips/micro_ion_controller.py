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



#=============enthought library imports=======================
from traits.api import List, Str, HasTraits, Float
from traitsui.api import View, HGroup, Item, ListEditor, InstanceEditor, Group
#=============standard library imports ========================
from numpy import random, char

#=============local library imports  ==========================
from src.hardware.core.core_device import CoreDevice

class Gauge(HasTraits):
    name = Str
    pressure = Float
    def traits_view(self):
        v = View(HGroup(Item('name', show_label=False, style='readonly',
                             width= -50,
                             ),
                         Item('pressure', format_str='%0.2e', show_label=False, style='readonly')))
        return v

class MicroIonController(CoreDevice):
    scan_func = 'get_pressures'
    address = '01'
    gauges = List
    display_name = Str
    def gauge_view(self):
        v = View(
                 Group(
                     Item('gauges', style='custom',
                          show_label=False,
                          editor=ListEditor(mutable=False,
                                            style='custom',
                                        editor=InstanceEditor())),
                       show_border=True,
                       label=self.display_name
                       ),
#                 height= -100
                 )
        return v

    def load_additional_args(self, config, *args, **kw):
        self.address = self.config_get(config, 'General', 'address', optional=False)
        self.display_name = self.config_get(config, 'General', 'name', default=self.name)

        ns = self.config_get(config, 'Gauges', 'names')
        if ns:
            for ni in ns.split(','):
                print ni
                self.gauges.append(Gauge(name=ni.strip()))

        return True

    def graph_builder(self, g):
        CoreDevice.graph_builder(self, g, **{'show_legend':True})
        g.new_series()
        g.set_series_label('IG')

        g.new_series()
        g.set_series_label('CG1', series=1)

        g.new_series()
        g.set_series_label('CG2', series=2)

    def get_gauge(self, name):
        return next((gi for gi in self.gauges if gi.name == name), None)

    def _set_gauge_pressure(self, name, v):
        g = self.get_gauge(name)
        if g is not None:
            try:
                g.pressure = float(v)
            except (TypeError, ValueError):
                pass

    def get_pressures(self, verbose=False):
        b = self.get_convectron_b_pressure(verbose=verbose)
        self._set_gauge_pressure('CG2', b)

        a = self.get_convectron_a_pressure(verbose=verbose)
        self._set_gauge_pressure('CG1', a)

        ig = self.get_ion_pressure(verbose=verbose)
        self._set_gauge_pressure('IG', ig)

        return ig, a, b
        # return self.get_convectron_a_pressure()

    def set_degas(self, state):
        key = 'DG'
        value = 'ON' if state else 'OFF'
        cmd = self._build_command(key, value)
        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def get_degas(self):
        key = 'DGS'
        cmd = self._build_command(key)
        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def get_ion_pressure(self, **kw):
        name = 'IG'
        return self._get_pressure(name, **kw)

    def get_convectron_a_pressure(self, **kw):
        name = 'CG1'
        return self._get_pressure(name, **kw)

    def get_convectron_b_pressure(self, **kw):
        name = 'CG2'
        return self._get_pressure(name, **kw)

    def set_ion_gauge_state(self, state):
        key = 'IG1'
        value = 'ON' if state else 'OFF'
        cmd = self._build_command(key, value)
        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def get_process_control_status(self, channel=None):
        key = 'PCS'

        cmd = self._build_command(key, channel)

        r = self.ask(cmd)
        r = self._parse_response(r)

        if channel is None:
            if r is None:
                # from numpy import random,char
                r = random.randint(0, 2, 6)
                r = ','.join(char.array(r))

            r = r.split(',')
        return r

    def _get_pressure(self, name, verbose=False):
        key = 'DS'
        cmd = self._build_command(key, name)

        r = self.ask(cmd, verbose=False)
        r = self._parse_response(r)
        return r

    def _build_command(self, key, value=None):

        # prepend key with our address
        # example of new string formating
        # see http://docs.python.org/library/string.html#formatspec
        key = '#{}{}'.format(self.address, key)
        if value is not None:
#            args = (key, value, CRLF)
            args = (key, value)
        else:
#            args = (key, CRLF)
            args = (key,)
        c = ' '.join(args)

        return  c

    def _parse_response(self, r):
        if self.simulation or r is None:
            r = self.get_random_value(0, 10000) / 10000.0

        return r


#============= EOF ====================================

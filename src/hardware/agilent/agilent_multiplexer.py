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
from traits.api import HasTraits, Str, List, Float, Property, Tuple
from traitsui.api import View, Item, HGroup, ListEditor, InstanceEditor, Group
#=============standard library imports ========================
from numpy import polyval
from src.hardware.agilent.agilent_unit import AgilentUnit
#=============local library imports  ==========================
# from src.hardware.adc.analog_digital_converter import AnalogDigitalConverter

'''
Agilent requires chr(10) as its communicator terminator

'''
class Channel(HasTraits):
    address = Str
    name = Str
    value = Float
    process_value = Property(depends_on='value')
    coefficients = Tuple
    kind = Str('DC')
    def traits_view(self):
        v = View(HGroup(Item('name', show_label=False, style='readonly', width=200),
                      Item('address', show_label=False, style='readonly', width=75),
                      Item('value', show_label=False, style='readonly', width=100),
                      Item('process_value', show_label=False, style='readonly', width=100)))
        return v

    def _get_process_value(self):
        value = self.value
        if self.coefficients:
            value = polyval(self.coefficients, value)
        return value

class AgilentMultiplexer(AgilentUnit):
    channels = List

    scan_func = 'channel_scan'
    def load_additional_args(self, config):
        super(AgilentMultiplexer, self).load_additional_args(config)
        # load channels
        self.channels = []
        for section in config.sections():
            if section.startswith('Channel'):
                kind = self.config_get(config, section, 'kind', default='DC')
                name = self.config_get(config, section, 'name', default='')

                cs = self.config_get(config, section, 'coefficients', default='1,0')
                try:
                    cs = map(float, cs.split(','))
                except ValueError:
                    self.warning('invalid coefficients for {}. {}'.format(section, cs))
                    cs = 1, 0

                ch = Channel(address='{}{:02n}'.format(self.slot, int(section[7:])),
                           kind=kind,
                           name=name,
                           coefficients=cs
                           )
                self.channels.append(ch)

#        self._update_channels = True
        return True

    def initialize(self, *args, **kw):
        '''
        '''

        self._communicator.write_terminator = chr(10)
        cmds = (
              '*CLS',
              'FORM:READING:ALARM OFF',
              'FORM:READING:CHANNEL ON',
              'FORM:READING:TIME OFF',
              'FORM:READING:UNIT OFF',
              # 'ROUT:CHAN:DELAY {} {}'.format(0.05, self._make_scan_list()),
              'ROUT:SCAN {}'.format(self._make_scan_list()),
              'TRIG:COUNT {}'.format(self.trigger_count),
              'TRIG:SOURCE TIMER',
              'TRIG:TIMER 0',
             )

        for c in cmds:
            self.tell(c)

        # configure channels
        # configure volt changes
        chs = self._get_dc_channels()
        c = 'CONF:VOLT:DC {}'.format(self._make_scan_list(chs))
        self.tell(c)

        return True

    def _get_dc_channels(self):
        return [ci for ci in self.channels if ci.kind == 'DC']

    def _make_scan_list(self, channels=None):
        if channels is None:
            channels = self.channels

        return '(@{})'.format(','.join([ci.address for ci in channels]))

    def channel_scan(self, **kw):
        verbose = False
        self._trigger(verbose=verbose)
        if self._wait(verbose=verbose):
            rs = []
            n = len(self.channels)
            for i, ci in enumerate(self.channels):
                v = self.ask('DATA:REMOVE? 1', verbose=verbose)
                if v is None:
                    v = str(self.get_random_value())

                try:
                    ci.value = float(v)
                    rs.append(v)
                except ValueError:
                    rs = []
                    break

                if i == n - 1 or not self._wait(n=5, verbose=verbose):
                    break

            return ','.join(rs)

    def read_channel(self, name):
        # if device is not scanning force a channel scan
        # otherwise use the last scan value
        if not self._scanning:
            self.channel_scan()

        channel = self._get_channel(name)
        if channel is not None:
            return channel.value

    def _get_channel(self, name):
        return next((chan for chan in self.channels
                            if chan.name == name or \
                                 chan.address[1:] == name), None)

#    def _get_channels(self):
# #        print 'asdfasdfasdfsadfsda', len(self._channels)
#        return self._channels

    def traits_view(self):
        v = View(
                 Group(
                       Item('channels', show_label=False,
                            height=400,
                            editor=ListEditor(mutable=False,
                                              editor=InstanceEditor(), style='custom')),
                       show_border=True
                       )
                 )
        return v

class AgilentSingleADC(AgilentUnit):
    '''
    '''
#    def __init__(self, *args, **kw):
#        super(AgilentADC, self).__init__(*args, **kw)
#    address = None

    def load_additional_args(self, config):
        '''

        '''
        super(AgilentSingleADC, self).load_additional_args(config)
        channel = self.config_get(config, 'General', 'channel', cast='int')

        if self.slot is not None and channel is not None:
            self.address = '{}{:02n}'.format(self.slot, channel)
            return True

    def initialize(self, *args, **kw):
        '''
        '''

        self._communicator.write_terminator = chr(10)
        if self.address is not None:
            cmds = [
                  '*CLS',
                  'CONF:VOLT:DC (@{})'.format(self.address),
                  'FORM:READING:ALARM OFF',
                  'FORM:READING:CHANNEL ON',
                  'FORM:READING:TIME OFF',
                  'FORM:READING:UNIT OFF',
                  'TRIG:SOURCE TIMER',
                  'TRIG:TIMER 0',
                  'TRIG:COUNT {}'.format(self.trigger_count),
                  'ROUT:SCAN (@{})'.format(self.address)
                 ]

            for c in cmds:
                self.tell(c)

            return True

    def read_device(self, **kw):
        '''
        '''
        self._trigger()
        pts = self._wait()
        if pts:
            resp = self.ask('DATA:REMOVE? {}'.format(pts))
            resp = self._parse_response(resp)
            return resp

#        resp = self.ask('DATA:POINTS?')
#        if resp is not None:
#            n = float(resp)
#            resp = 0
#            if n > 0:
#                resp = self.ask('DATA:REMOVE? {}'.format(float(n)))
#                resp = self._parse_response_(resp)

            # self.current_value = resp
#            self.read_voltage = resp
#        return resp

    def _parse_response_(self, r):
        '''
            
        '''
        if r is None:
            return r

        return float(r)
#        args = r.split(',')
#        data = args[:-1]

#        return sum([float(d) for d in data]) / self.trigger_count



#============= EOF =====================================

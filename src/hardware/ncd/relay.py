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
'''
    National Control Devices
    
   http://www.controlanything.com/ 
   
   The Complete ProXR Command Set:
   http://www.controlanything.com/Relay/Device/A0010
   http://assets.controlanything.com/manuals/ProXR.pdf
'''

#============= enthought library imports =======================
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.hardware.ncd import ON_MAP, OFF_MAP, STATE_MAP
from src.hardware.ncd.ncd_device import NCDDevice


class ProXR(NCDDevice):
    '''
        implement the actuator interface
        open_channel
        close_channel
        get_channel_state
    '''
    def open_channel(self, channel, *args, **kw):
        '''
            idx=1-255
            32 banks of 8
            
            bank = idx/8
            
        '''
        name = self._set_bank(channel)
        if name:
            local_idx = ON_MAP[name]
            cmdstr = self._make_cmdstr(254, local_idx)
            resp = self.ask(cmdstr, nbytes=1)
            return resp == '55'  # hex(85)

    def close_channel(self, channel, *args, **kw):
        name = self._set_bank(channel)
        if name:
            local_idx = OFF_MAP[name]
            cmdstr = self._make_cmdstr(254, local_idx)
            resp = self.ask(cmdstr, nbytes=1)
            return resp == '55'  # hex(85)

    def get_channel_state(self, channel, *args, **kw):

        name = self._set_bank(channel)
        if name:
            local_idx = STATE_MAP[name]
            cmdstr = self._make_cmdstr(254, local_idx)
            resp = self.ask(cmdstr, nbytes=1)  # returns 1 or 0
            return bool(int(resp))


    def get_channel_states(self, *args, **kw):
        cmdstr = self._make_cmdstr(254, 24)
        resp = self.ask(cmdstr)

#===============================================================================
# configuration
#===============================================================================


#===============================================================================
# private
#===============================================================================
    def _set_bank(self, channel):
        idx = channel.name
        bank = idx / 8
        cmdstr = self._make_cmdstr(254, 49, bank)
        if self.ask(cmdstr, nbytes=1) == '55':
            return idx % 8




#============= EOF =============================================

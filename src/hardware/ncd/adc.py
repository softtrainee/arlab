'''
    National Control Devices
    
   http://www.controlanything.com/ 
   
   The Complete ProXR Command Set:
   http://www.controlanything.com/Relay/Device/A0010
   http://assets.controlanything.com/manuals/ProXR.pdf
'''
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
from src.paths import paths
from src.helpers.logger_setup import logging_setup
import struct
logging_setup('prox')
paths.build('_prox')


#============= enthought library imports =======================
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.hardware.ncd.ncd_device import NCDDevice

class ProXADCExpansion(NCDDevice):
    def read_channel(self, channel, nbits=8):
        if nbits == 10:
            start = 157
            nbytes = 2
        else:
            start = 149
            nbytes = 1
        idx = int(channel) + start
        cmdstr = self._make_cmdstr(254, idx)
        resp = self.ask(cmdstr, nbytes=nbytes)
        return int(resp, 16)


EIGHT_BIT_BANKS = [195, 203, 208]
TWELVE_BIT_BANKS = [199, 207, 209]

class MultiBankADCExpansion(NCDDevice):
    def read_channel(self, channel, nbits=8):
        channel = int(channel)
        if nbits == 12:
#            self._read_ten_bit(channel)
            bank = TWELVE_BIT_BANKS
            nchars = 2
        else:
#            self._read_eight_bit(channel)
            bank = EIGHT_BIT_BANKS
            nchars = 1

        bank_idx = bank[channel / 16]
        channel_idx = channel % 16

        cmdstr = self._make_cmdstr(254, bank_idx, channel_idx)

#        band_idx = 192
#        cmdstr = self._make_cmdstr(254, bank_idx)
        resp = self.ask(cmdstr, nchars=nchars, remove_eol=False)

        if nbits == 12:
            '''
                resp is lsb msb
                switch to msb lsb
            '''
#            resp = resp[1:] + resp[:1]
            fmt = '<h'
#            return struct.unpack('@H', resp)[0]
        else:

            fmt = '>B'
        return struct.unpack(fmt, resp)[0]


#        print resp
#        return int(resp, 2)

    def read_all(self):
        pass

if __name__ == '__main__':
    a = MultiBankADCExpansion(name='proxr_adc')
    a.bootstrap()
    print a.read_channel(0, nbits=8)
    print a.read_channel(0, nbits=12)
#============= EOF =============================================

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
import socket

#============= standard library imports ========================

#============= local library imports  ==========================
from data_transfer_object import DataTransferObject

class DataTransferClient(DataTransferObject):
    '''
        G{classtree}
    '''

    def connect(self):
        '''
        '''
        if self.address is not None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.address)
            return sock

    def send_file(self, p):
        '''
            @type p: C{str}
            @param p:
        '''
        sock = self.connect()
        if sock is not None:
            data, fmt = self.encode_file(p)
            sock.send('%s\n%s' % (fmt, data))
            sock.close()

if __name__ == '__main__':
    c = DataTransferClient('localhost', 5990)
    c.connect()
    p = '/Users/Ross/Pychrondata_beta/data/argusVI/data.csv'
    c.send_file(p)
#============= EOF ====================================

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
#import socket
#from threading import Thread
import csv
import struct
#============= local library imports  ==========================

#============= views ===================================
class DataTransferObject(object):
    def __init__(self, host, port):
        '''
           
        '''
        self.address = (host, port)
    def encode(self, header, data):
        '''
        '''
        fmt = '!'
        for i, di in enumerate(data):
            #print i, di
            #loop thru the data to determine float or str
            try:
                data[i] = float(di)
                fmt = ''.join((fmt, 'f'))
            except ValueError:
                fmt = ''.join((fmt, '10s'))

        args = (fmt,) + tuple(data)
        r = struct.pack(*args)
        return r, fmt


    def decode(self, data, fmt):
        '''
            
        '''

        size = struct.calcsize(fmt)
        lines = []
        for i in range(0, len(data), size):
            lines.append(struct.unpack(fmt, data[i:i + size]))
        return lines

    def encode_file(self, path):
        '''
            
        '''
        edata = ''
        with open(path, 'U') as f:
            reader = csv.reader(f)
            header = reader.next()
            for line in reader:
                ed, fmt = self.encode(header, line)
                edata += ed
        return edata, fmt

if __name__ == '__main__':
    d = DataTransferObject('l', 9)
    p = '/Users/Ross/Pychrondata_beta/data/argusVI/data.csv'
    ed, fmt = d.encode_file(p)
    lines = d.decode(ed, fmt)
    rp = '/Users/Ross/Pychrondata_beta/data/argusVI/data_r.csv'
    with open(rp, 'w') as f:
        writer = csv.writer(f)
        for l in lines:
            writer.writerow(l)
#============= EOF ====================================

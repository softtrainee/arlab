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
import socket
from threading import Thread

#============= local library imports  ==========================
from data_transfer_object import DataTransferObject

class DataTransferServer(DataTransferObject):
    '''
        G{classtree}
    '''
    bufsize = 1024
    kill = False
    def connect(self):
        '''
        '''
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(self.address)
        self._sock.listen(5)

    def serve_forever(self):
        '''
        '''
        t = Thread(target=self.serve)
        t.start()
    def serve(self):
        '''
        '''
        while not self.kill:
            sock, _addr = self._sock.accept()
            self.handle(sock)

    def handle(self, sock):
        '''
            @type sock: C{str}
            @param sock:
        '''
        data = sock.recv(self.bufsize)
        print data

if __name__ == '__main__':
    s = DataTransferServer('localhost', 5990)
    s.connect()
    s.serve_forever()
#============= EOF ====================================

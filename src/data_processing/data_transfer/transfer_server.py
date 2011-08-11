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
        t = Thread(target = self.serve)
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

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

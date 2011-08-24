#============= enthought library imports =======================
#from SocketServer import BaseRequestHandler
#============= standard library imports ========================

#============= local library imports  ==========================
from messaging_handler import MessagingHandler

class TCPHandler(MessagingHandler):
    def get_packet(self):
        '''
        '''
        size = self.server.datasize
        data = self.request.recv(size).strip()

#        import shlex
#        strip off binary header
#        print data, len(data), shlex.split(data) 
#        data=''.join([i for i in data if ord(i)>=32])

#        print data, len(data), shlex.split(data) 


        return data

    def send_packet(self, response):
        '''
        '''
        if response is None:
            response = 'error'
        self.request.send(response + '\n')

#============= EOF ====================================

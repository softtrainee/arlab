#============= enthought library imports =======================

#============= standard library imports ========================
#from SocketServer import BaseRequestHandler
#============= local library imports  ==========================
from messaging_handler import MessagingHandler

class UDPHandler(MessagingHandler):
    def get_packet(self):
        '''
        '''
        data = self.request[0].strip()
        return data

    def send_packet(self, response):
        '''
            @type response: C{str}
            @param response:
        '''
        sock = self.request[1]
        sock.sendto(response + '\n', self.client_address)

#============= EOF ====================================

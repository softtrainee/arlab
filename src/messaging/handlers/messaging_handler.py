#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from SocketServer import BaseRequestHandler

class MessagingHandler(BaseRequestHandler):
    def handle(self):
        '''
        '''
        data = self.get_packet()

        if data is not None:

            self.server.info('Received: %s' % data.strip())
            response = self.server.repeater.get_response(self.server.processor_type, data)
            self.send_packet(response)

            if 'Error' in response:
                self.server.increment_repeater_fails()
            else:
                self.server.repeater.led.state = 2

            self.server.info('Sent: %s' % response.strip())
            self.server.parent.cur_rpacket = data
            self.server.parent.cur_spacket = response

            self.server.increment_packets_received()
            self.server.increment_packets_sent()

    def get_packet(self):
        '''
        '''
        pass
    def send_packet(self):
        '''
        '''
        pass
#============= EOF ====================================

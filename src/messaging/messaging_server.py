#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
class MessagingServer(object):
    '''
        G{classtree}
    '''
    parent = None

    def increment_packets_received(self):
        '''
        '''
        #called by handler everytime a packet is received
        self.parent.packets_received += 1

    def increment_packets_sent(self):
        '''
        '''
        self.parent.packets_sent += 1

    def increment_repeater_fails(self):
        '''
        '''
        self.parent.repeater_fails += 1

    def info(self, *args, **kw):
        '''

        '''
        self.parent.info(*args, **kw)

    def warning(self, *args, **kw):
        '''
        '''
        self.parent.warning(*args, **kw)
#============= views ===================================

#============= EOF ====================================

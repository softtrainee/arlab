#============= enthought library imports =======================

#============= standard library imports ========================
from SocketServer import ThreadingUDPServer

#============= local library imports  ==========================
from messaging_server import MessagingServer
class UDPServer(ThreadingUDPServer, MessagingServer):
    '''
        G{classtree}
    '''
    allow_reuse_address = True

    def __init__(self, parent, processor_type, datasize, * args, **kw):
        '''

        '''
        self.repeater = parent.repeater
        self.datasize = datasize
        self.processor_type = processor_type
        self.parent = parent

        self.connected = True
        try:
            ThreadingUDPServer.__init__(self, *args, **kw)
        except:
            #self.logger.warning(e)
            self.warning('%s: %s already bound' % args[0])
            self.connected = False


#============= EOF ====================================

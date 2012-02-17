#=============enthought library imports=======================
#============= standard library imports ========================
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from src.web.pages.bakeout_page import BakeoutPage
#============= local library imports  ==========================

class Server:
    port = 8080
    def start_server(self):
        #initalize our resources
        
        
        resource = Resource()
        resource.putChild('bakeout', BakeoutPage())
        factory = Site(resource)
        reactor.listenTCP(self.port, factory)
        reactor.run()

if __name__ == '__main__':
    s = Server()
    s.start_server()
#============= EOF =====================================

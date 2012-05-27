#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import Any
#from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

from threading import Thread


class RequestHandler(SimpleXMLRPCRequestHandler):
    pass

class RPCServer(Loggable):
    manager = Any
    _server = None
    def load_server(self):
        addr = ('localhost', 8000)
        self._server = server = SimpleXMLRPCServer(addr, RequestHandler,
                                                   allow_none=True
                                                   )

#        funcs = ['enable_laser']
#        man = self.manager
#        for f in funcs:
#            f = getattr(man, f)
#            server.register_function(f)
        server.register_introspection_functions()
        server.register_instance(self.manager)

    def start_server(self):
        if self._server:
            self._server.serve_forever()

    def bootstrap(self):
        self.load_server()
        t = Thread(name='RPCServer', target=self.start_server)
        t.setDaemon(True)
        t.start()

class DummyManager(object):
    def foo(self, a):
        print 'foo', a
        return True

    def moo(self, m, a):
        print 'moo', m, a
        return True

if __name__ == '__main__':
#    from src.lasers.laser_managers.fusions_laser_manager import FusionsLaserManager
#    lm = FusionsLaserManager()
    lm = DummyManager()
    s = RPCServer(manager=lm)
    s.bootstrap()

#============= EOF =============================================

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
#from traits.api import HasTraits, Any
#from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import xmlrpclib
#============= local library imports  ==========================
from src.loggable import Loggable

class RPCClient(Loggable):
    def connect(self):
        host = 'localhost'
        port = 8000
        handle = xmlrpclib.ServerProxy('http://{}:{}'.format(host, port))

        handle.foo('pff')
        handle.moo(1, 2)

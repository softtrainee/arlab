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
from traits.api import HasTraits, Str
from traitsui.api import View, Item, TableEditor
from src.graph.graph import Graph
#============= standard library imports ========================
#============= local library imports  ==========================

class CoreNode(HasTraits):
    name = Str
    def replot(self):
        pass
#===============================================================================
# factories
#===============================================================================
    def _graph_factory(self, shape, klass=None):
        if klass is None:
            klass = Graph
        g = klass(container_dict=dict(type='g',
                                      shape=shape,
                                      bgcolor='gray',
                                      padding=10
                                      ),
                  )
        return g
#============= EOF =============================================

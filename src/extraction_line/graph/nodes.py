#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, List, Str, Bool, Instance
from traitsui.api import View, Item
import weakref
#============= standard library imports ========================
#============= local library imports  ==========================
def flatten(nested):
#     print nested
    if isinstance(nested, str):
        yield nested
    else:
        try:
            for sublist in nested:
                for element in flatten(sublist):
                    yield element

        except TypeError:
            yield nested

class Edge(HasTraits):
    name = Str
    anode = Instance('src.extraction_line.graph.nodes.Node')
    bnode = Instance('src.extraction_line.graph.nodes.Node')
    visited = False
    def nodes(self):
        return self.anode, self.bnode

    def get_node(self, n):
        return self.bnode if self.anode == n else self.anode

class Node(HasTraits):
    edges = List

    name = Str
    state = Str
    visited = False
    fvisited = False

    def add_edge(self, n):
        self.edges.append(weakref.ref(n)())

    def __iter__(self):
        for ei in self.edges:
            n = ei.get_node(self)
            yield n

class ValveNode(Node):
    pass

class RootNode(Node):
    state = True

class GaugeNode(RootNode):
    pass

class PumpNode(RootNode):
    pass

class SpectrometerNode(RootNode):
    pass

class TankNode(RootNode):
    pass

class PipetteNode(RootNode):
    pass

class LaserNode(RootNode):
    pass



#============= EOF =============================================

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
class Edge(HasTraits):
    anode = Instance('src.extraction_line.graph.nodes.Node')
    bnode = Instance('src.extraction_line.graph.nodes.Node')

class Node(HasTraits):
#     nodes = List
    edges = List

    name = Str
    state = Str


#     def add_node(self, n):
#         self.nodes.append(weakref.ref(n)())

    def add_edge(self, n):
        self.edges.append(weakref.ref(n)())

    def find_roots(self, direction=None):
        '''
            traverse networking looking for a connection to 
            a root node
        '''
        return list(self._find_klass(RootNode, direction))

    def _find_klass(self, klass, direction):
        for ei in self.edges:
            nodes = (ei.anode, ei.bnode)
            if direction == 'left':
                nodes = (ei.anode,)
            elif direction == 'right':
                nodes = (ei.bnode,)

            for n in nodes:
#                 print self.name, 'nn', n
                if n:
                    if isinstance(n, klass):
                        yield n
                    if isinstance(n, ValveNode) and n is not self:
                        if n.state:
                            yield n.find_root()


#     def find_node(self, n):
#         if self.name == n:
#             return self
#         else:
#             for ei in self.edges:
#                 for nn in (ei.anode, ei.bnode):
#                     if nn.name == n:
#                         return nn
#                     eli
#                         return nn.find_node(n)

#             for ni in self.nodes:
#                 nn = ni.find_node(n)
#                 if nn is not None:
#                     return nn

#     def is_outlet(self):
#         for ni in self.nodes:
#             if isinstance(ni, TurboNode):
#                 return True
#             else:
#                 return ni.is_outlet()


class ValveNode(Node):
    pass

class PumpNode(Node):
    pass


class RootNode(Node):
    state = True

class SpectrometerNode(RootNode):
    pass

#     def calc_paths(self):
#         paths = []
#         for ei in self.edges:
#             p = ei.assemble_path()
#             print p
#             paths.append(p)



#     def set_state(self):
#         '''
#             visit each node
#             if node is outlet node and open
#                 state = dynamic
#             if all outlet nodes closed
#                 state= static
#         '''
#         ostates = []
#         for ni in self.nodes:
#             # does this node lead to a turbo
#             if ni.is_outlet():
#                 ostates.append((ni.name, ni.state))
#
#         ss = [x[1] for x in ostates]
#
#         self.state = 'dynamic' if any(ss) else 'static'
#         print self.state



#============= EOF =============================================

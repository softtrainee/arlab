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
    def nodes(self):
        return self.anode, self.bnode
class Node(HasTraits):
#     nodes = List
    edges = List

    name = Str
    state = Str
    visited = False

#     def add_node(self, n):
#         self.nodes.append(weakref.ref(n)())    
        
    def add_edge(self, n):
        self.edges.append(weakref.ref(n)())

    def find_roots(self):
        roots = []
        for ei in self.edges:
            for n in (ei.anode, ei.bnode):
                if n:
                    if isinstance(n, RootNode):
                        roots.append(n)
                        if not n.visited:
                            n.visited = True
                            roots.extend(n.find_roots())
                    else:
                        if n.state and n.state != 'closed':
                            if not n.visited:
                                n.visited = True
                                roots.extend(n.find_roots())
        return roots

#     def _find_klass(self, klass, parent):
#         '''
#              find klass that is farthest away
#
#         '''
#         for ei in self.edges:
#             for n in (ei.anode, ei.bnode):
#                 if n and not n is self:
#                     if isinstance(n, ValveNode):
# #                         print n.name, n.state, parent.name if parent else ''
#                         if n.state and n.state is not 'closed':
#                             if n != parent:
# #                                 print '    check name={} state={}'.format(n.name, n.state)
#                                 yield n._find_klass(klass, self)
#                     else:



    def find_closest_roots(self):
        '''
            traverse networking looking for a connection to 
            a root node
        '''

        rvs = self._find_closest_klass(RootNode, None)
        return list(flatten(rvs))
#         try:
#             for r in flatten(rvs):
#                 print r
#         except RuntimeError:
#             pass
# #         if rvs:
#         rs = []
#         for r, vs in rvs:

#             for vi in flatten(vs):
#                 vi.visited = False

#             rs.append(r)

#         return rs
    def _find_closest_klass(self, klass, parent):
#         print '------------------------------'
        for ei in self.edges:
            nodes = (ei.anode, ei.bnode)
            for n in nodes:
#                 print self.name, n.name
#                 print self.name, 'nn', n
                if n and not n is self:
#                     self._visited.append(n)
                    if isinstance(n, klass):
                        yield n

                    if isinstance(n, ValveNode):
#                         print n.name, n.state, parent.name if parent else ''
                        if n.state and n.state is not 'closed':
                            if n != parent:
#                                 print '    check name={} state={}'.format(n.name, n.state)
                                yield n._find_closest_klass(klass, self)
#                     if isinstance(n, ValveNode) \
#                         and not n.visited:
#                         if n.state:
#                             print 'find roots', n.name
# #                             print n.name
# #                             yield n._find_klass(klass, visited), visited
#                             yield n.find_roots(visited), visited

#                     n.visited = True


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



class RootNode(Node):
    state = True

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

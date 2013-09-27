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
from traits.api import HasTraits, Dict
#============= standard library imports ========================
#============= local library imports  ==========================

from src.extraction_line.graph.nodes import ValveNode, RootNode, \
    PumpNode, Edge, SpectrometerNode, LaserNode, TankNode, PipetteNode
from src.helpers.parsers.canvas_parser import CanvasParser
from src.canvas.canvas2D.scene.primitives.valves import Valve
from compiler.ast import Pass

TAG_PREDENCE = ('pump', 'spectrometer', 'pipette', 'laser', 'tank',)

from collections import deque

def BFT(G, s):
    P, Q = {s: None}, deque([s])
    while Q:
        u = Q.popleft()
        if u.state == 'closed':
            continue

        for v in G[u]:
            if v in P:
                continue
            P[v] = u
            Q.append(v)

    return P

class ExtractionLineGraph(HasTraits):
    nodes = Dict
    suppress_changes = False
    def load(self, p):

        cp = CanvasParser(p)
        if cp._root is None:
            return

        nodes = dict()
        #=======================================================================
        # load nodes
        #=======================================================================
        # load roots
        for t, klass in (('stage', RootNode),
                        ('spectrometer', SpectrometerNode),
                        ('valve', ValveNode),
                        ('rough_valve', ValveNode),
                        ('turbo', PumpNode),
                        ('ionpump', PumpNode),
                        ('laser', LaserNode),
                        ('tank', TankNode),
                        ('pipette', PipetteNode)
                        ):
            for si in cp.get_elements(t):
                n = si.text.strip()
                nodes[n] = klass(name=n)

        #=======================================================================
        # load edges
        #=======================================================================
        for ei in cp.get_elements('connection'):
            sa = ei.find('start')
            ea = ei.find('end')

            edge = Edge()
            sname = ''
            if sa.text in nodes:
                sname = sa.text
                sa = nodes[sname]
                edge.anode = sa
                sa.add_edge(edge)

            ename = ''
            if ea.text in nodes:
                ename = ea.text
                ea = nodes[ename]
                edge.bnode = ea
                ea.add_edge(edge)

            edge.name = '{}_{}'.format(sname, ename)

        self.nodes = nodes

    def set_valve_state(self, name, state, *args, **kw):
        if name in self.nodes:
            vnode = self.nodes[name]
            vnode.state = 'open' if state else 'closed'

    def set_canvas_states(self, canvas, name):
        scene = canvas.canvas2D.scene
        if not self.suppress_changes:
            if name in self.nodes:
                snode = self.nodes[name]
                '''
                    new alogrithm
                    if valve closed
                        split tree and fill each sub tree
                    else:
                        for each edge of the start node
                            breath search for the max state
                        
                        find max maxstate 
                        fill nodes with maxstate
                            using a depth traverse
                    
                    new variant
                    recursively split tree if node is closed
                '''
                self._set_state(scene, snode)
                self._clear_visited()

    def _set_state(self, scene, n):
        if n.state == 'closed' and not n.visited:
            n.visited = True
            for ni in self._split_graph(n):
                self._set_state(scene, ni)
        else:
            state, term = self._find_max_state(n)
            self._clear_fvisited()
            print n.name, state, term
            self.fill(scene, n, state, term)

    def _split_graph(self, n):
        '''
            valves only have binary connections 
            so can only split in half
        '''
        if len(n.edges) == 2:
            e1, e2 = n.edges
            return e1.get_node(n), e2.get_node(n)
        else:
            return (n.edges[0].get_node(n),)

    def _find_max_state(self, n):
        '''
            use a Breadth-First Traverse
            acumulate the max state at each node
        '''
        state, term = False, ''
        for ni in BFT(self, n):
            print '-----', n.name, ni.name
            if isinstance(ni, PumpNode):
                return 'pump', ni.name

            if isinstance(ni, LaserNode):
                state, term = 'laser', ni.name
            elif isinstance(ni, PipetteNode):
                state, term = 'pipette', ni.name
            elif isinstance(ni, SpectrometerNode):
                if state not in ('laser', 'pipette'):
                    state, term = 'spectrometer', ni.name
            elif isinstance(ni, TankNode):
                if state not in ('laser', 'pipette'):
                    state, term = 'tank', ni.name
        else:
            return state, term

    def fill(self, scene, root, state, term):
#         print 'fill', root.name, state, term
        self._set_item_state(scene, root.name, state, term)
        for ei in root.edges:
            n = ei.get_node(root)
            self._set_item_state(scene, ei.name, state, term)

            if n.state != 'closed' and not n.fvisited:
                n.fvisited = True
                self.fill(scene, n, state, term)

    def _set_item_state(self, scene, name, state, term, color=None):
        if not isinstance(name, str):
            raise ValueError('name needs to be a str. provided={}'.format(name))

        obj = scene.get_item(name)

        if obj is None \
                or obj.type_tag in ('turbo', 'tank', 'ionpump'):
            return

        if not color and state:
            nterm = scene.get_item(term)
            color = nterm.default_color

        if isinstance(obj, Valve):
            '''
                set the color of the valve to 
                the max state if the valve is open
            '''
            if obj.state != 'closed':
                if state:
                    obj.active_color = color
                else:
                    obj.active_color = 0, 255, 0
            return

        if state:
            obj.active_color = color
            obj.state = True
        else:
            obj.state = False

    def _clear_visited(self):
        for ni in self.nodes.itervalues():
            ni.visited = False
#             for ei in ni.edges:
#                 ei.visited = False

    def _clear_fvisited(self):
        for ni in self.nodes.itervalues():
            ni.fvisited = False

    def __getitem__(self, key):
        if not isinstance(key, str):
            key = key.name

        if key in self.nodes:
            return self.nodes[key]

if __name__ == '__main__':
    elg = ExtractionLineGraph()
    elg.load('/Users/ross/Pychrondata_dev/setupfiles/canvas2D/canvas.xml')

    elg.set_valve_state('C', False)
    state, root = elg.set_valve_state('H', True)
    state, root = elg.set_valve_state('H', False)

    print '-------------------------------'
    print state, root

#============= EOF =============================================


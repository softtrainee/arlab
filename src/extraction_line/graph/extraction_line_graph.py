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
from traits.api import HasTraits, List, Dict
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================

from src.extraction_line.graph.nodes import ValveNode, RootNode, \
    PumpNode, Edge, SpectrometerNode, LaserNode, flatten
from src.helpers.parsers.canvas_parser import CanvasParser
from guppy.heapy.Path import Path
from src.canvas.canvas2D.scene.primitives.primitives import Valve
import os



class ExtractionLineGraph(HasTraits):
    nodes = Dict
    color_dict = Dict

    def _load_config(self, p):
        colors = dict(pump='yellow',
                      spectrometer='green',
                      laser='red'
                      )

        di = os.path.dirname(p)
        p = os.path.join(di, 'network_config.xml')
        cp = CanvasParser(p)
        root = cp.get_root()
        network = root.find('network')
        if network is not None:
            for c in network.findall('color'):
                t = c.text.strip()
                k = c.get('tag')

                t = map(float, t.split(',')) if ',' in t else t
                colors[k] = tuple(t)

        self.color_dict = colors

    def load(self, p):
        self._load_config(p)

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
                        ('turbo', PumpNode),
                        ('ion', PumpNode),
                        ('laser', LaserNode)
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
            if sa.text in nodes:
                sa = nodes[sa.text]
                edge.anode = sa
                sa.add_edge(edge)

            if ea.text in nodes:
                ea = nodes[ea.text]
                edge.bnode = ea
                ea.add_edge(edge)

        self.nodes = nodes

    def set_canvas_states(self, canvas, states):

        '''
            if roots connected by an open valve then 
            set both roots to highest state
        '''
        maxroot = None
        maxstate = None
        for state, root in states:
            if state == 'pump':
                maxstate = 'pump'
                maxroot = root
            elif state == 'laser' and maxstate != 'pump':
                maxstate = 'laser'
                maxroot = root
            elif state == 'spectrometer' and maxstate not in ('laser', 'pump'):
                maxstate = 'spectrometer'
                maxroot = root

        for state, root in states:
            nr = root.find_roots()
            if maxroot and maxroot in nr:
                state = maxstate

            self._set_canvas_states(canvas, state, root)

    def _set_canvas_states(self, canvas, state, root):

        colors = self.color_dict
        scene = canvas.canvas2D.scene

        # set root state
        color = None
        if state:
            color = colors[state]

        self._set_item_state(scene, root.name, state, color)
#         print 'fff', root.name, state
        # gather roots paths
        for path in self.assemble_paths(root, None):
            # flatten path and set state for each element
            # use a color as the state
            for elem in flatten(path):
                self._set_item_state(scene, elem, state, color)

    def _set_item_state(self, scene, name, state, color=None):
        obj = scene.get_item(name)
        if obj is None or isinstance(obj, Valve):
            return

        if state:
            obj.active_color = color
            obj.state = True
        else:
            obj.state = False

    def set_valve_state(self, name, state, *args, **kw):
        if name in self.nodes:
            # find the root node for this node
            vnode = self.nodes[name]
            vnode.state = 'open' if state else 'closed'
            roots = vnode.find_roots()

            nstates = []
#             roots = flatten(roots)
            for root in roots:
                states = []
#                 root = list(flatten(root))
#                 print len(roots), root.name if root else '----'
                if root is not None:
                    for path in self.assemble_paths(root, None):
                        if path:
                            elems = list(flatten(path))
                            if elems:
                                print root.name, elems
                                states.append(elems[-1])

                nstate = ''
                if 'pump' in states:
                    nstate = 'pump'
                elif 'laser' in states:
                    nstate = 'laser'
                elif 'spectrometer' in states:
                    nstate = 'spectrometer'

                nstates.append(nstate)

            return zip(nstates, roots)

    def assemble_paths(self, root, parent):
        paths = []
        for ei in root.edges:
            start = ei.bnode if ei.anode is root else ei.anode
            if not start is parent:
                ps = self.assemble_path(start, root)
                paths.append(ps)

        return paths

    def assemble_path(self, start, parent):
        if start:
            if isinstance(start, SpectrometerNode):
                yield [start.name, 'spectrometer']
            elif isinstance(start, PumpNode):
                yield [start.name, 'pump']
            elif isinstance(start, LaserNode):
                yield [start.name, 'laser']
            elif start.state and start.state != 'closed':
                yield [start.name, self.assemble_paths(start, parent)]

if __name__ == '__main__':
#     f = ['C', [['ATurbo', 'pump']]]
#     f = [0, [[1, 2]]]
#     print list(flatten(f))


    elg = ExtractionLineGraph()
    elg.load('/Users/ross/Pychrondata_dev/setupfiles/canvas2D/canvas.xml')


    elg.set_valve_state('C', False)
    state, root = elg.set_valve_state('H', True)
    state, root = elg.set_valve_state('H', False)

    print '-------------------------------'
    print state, root
    # print elg.set_valve_state('C', True)

#     elg.set_valve_state('C', False)
#============= EOF =============================================

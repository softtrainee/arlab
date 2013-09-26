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
    PumpNode, Edge, SpectrometerNode, LaserNode, flatten, TankNode, PipetteNode
from src.helpers.parsers.canvas_parser import CanvasParser
from src.canvas.canvas2D.scene.primitives.primitives import Valve
import os



class ExtractionLineGraph(HasTraits):
    nodes = Dict
    color_dict = Dict

    def _load_config(self, p):
        pass
#         colors = dict(pump='yellow',
#                       spectrometer='green',
#                       laser='red'
#                       )
#
#         di = os.path.dirname(p)
# #         p = os.path.join(di, 'network_config.xml')
#
# #         cp = CanvasParser(p)
#         root = cp.get_root()
#         network = root.find('network')
#         if network is not None:
#             for c in network.findall('color'):
#                 t = c.text.strip()
#                 k = c.get('tag')
#
#                 t = map(float, t.split(',')) if ',' in t else t
#                 colors[k] = tuple(t)
#
#         self.color_dict = colors

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
                        ('rough_valve', ValveNode),
                        ('turbo', PumpNode),
                        ('ion', PumpNode),
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

    def init_states(self, canvas):
        scene = canvas.canvas2D.scene
        for ni in self.nodes.itervalues():
            for ri in ni.find_roots():
                self.clear_visited()
                obj = scene.get_item(ri.name)
                color = obj.default_color
                for ei in ri.edges:
                    obj = scene.get_item(ei.name)
                    if obj:
                        if not obj.state:
                            self._set_item_state(scene, ei.name, True, color)

    def set_canvas_states(self, canvas, states):

        '''
            if roots connected by an open valve then 
            set both roots to highest state
        '''
        maxroot = None
        maxstate = None
        maxterm = None
        for state, root, term in states:
            if state in ('pump', 'tank'):
                maxstate = state
                maxroot = root
                maxterm = term
                break
            
#             if state=='tank':
#                 maxroot=root
#                 maxterm=term
#                 maxstate=state
#                 break
            
            if state in ('laser','pipette','spectrometer'):
                maxroot=root
                maxterm=term
                maxstate=state
                

        for state, root, term in states:
            nr = root.find_roots()
            self.clear_visited()
            
            if maxroot and maxroot in nr:
                state = maxstate
                term=maxterm
            
            print 'state={} term={} maxroot={}'.format(state,term, maxroot.name if maxroot else '')
            self._set_canvas_states(canvas, state, root, term)
#             for ni in nr:
#                 self._set_canvas_states(canvas, state, ni, maxterm)

    def _set_canvas_states(self, canvas, state, root, term):

#         colors = self.color_dict
        scene = canvas.canvas2D.scene

        # set root state
        color = None
        if state:
#             color = colors[state]
            obj = scene.get_item(term)
            color = obj.default_color
        else:
            obj = scene.get_item(root.name)
            color = obj.default_color
#             print obj, root.name
#             color = 'red'
#             color = obj.active_color

#         print color
        self._set_item_state(scene, root.name, state, color)

        # set all edges for the root
#         for ei in root.edges:
# #             print root.name, ei.name, color
#             self._set_item_state(scene, ei.name, state, color)


        for path in self.assemble_paths(root, None):
            # flatten path and set state for each element
            # use a color as the state
            for elem in flatten(path):
#                 print elem, state, color
                self._set_item_state(scene, elem, state, color)

    def _set_item_state(self, scene, name, state, color=None):
        obj = scene.get_item(name)

        if obj is None or isinstance(obj, Valve) or obj.type_tag in ('turbo','tank') :
            return

#         print obj.name, obj.state, state
        if state:
            obj.active_color = color
            obj.state = True
        else:
#             obj.default_color = color
            obj.state = False
    
    def clear_visited(self):
        for ni in self.nodes.itervalues():
            ni.visited=False
            
    def set_valve_state(self, name, state, *args, **kw):
        if name in self.nodes:
            # find the root node for this node
            vnode = self.nodes[name]
            vnode.state = 'open' if state else 'closed'
#             roots = vnode.find_roots()
#             roots =[rr for ri in vnode.find_roots()
#                         for rr in ri.find_roots()]
            roots=vnode.find_roots()
            self.clear_visited()
            
#             if name=='P':
#                 print [ri.name for ri in roots]
            nstates = []
            nterminations = []
#             roots = flatten(roots)
            for root in roots:
                states = []
                terms = []
#                 root = list(flatten(root))
#                 print len(roots), root.name if root else '----'
                if root is not None:
                    for path in self.assemble_paths(root, None):
                        if path:
                            elems = list(flatten(path))
                            if elems:
#                                 if root.name=='CO2':
#                                     print elems
#                                 if root.name in ('Minibone','CocktailPipette','Bone'):
#                                     print root.name, elems
                                term = None
                                if len(elems) > 1:
                                    term = elems[-2]
                                terms.append(term)
                                states.append(elems[-1])

                nstate = ''
                nterm = ''
                if isinstance(root, PumpNode):
                    nstate='pump'
                    nterm=root.name
                elif isinstance(root, LaserNode):
                    nstate='laser'
                    nterm=root.name
                elif isinstance(root, TankNode):
                    nstate='tank'
                    nterm=root.name
                elif isinstance(root, PipetteNode):
                    nstate='pipette'
                    nterm=root.name
                    
                elif 'pump' in states:
                    nstate = 'pump'
                    nterm = terms[states.index('pump')]
                elif 'tank' in states:
                    nstate = 'tank'
                    nterm = terms[states.index('tank')]
                elif 'pipette' in states:
                    nstate = 'pipette'
                    nterm = terms[states.index('pipette')]
                elif 'laser' in states:
                    nstate = 'laser'
                    nterm = terms[states.index('laser')]
                elif 'spectrometer' in states:
                    nstate = 'spectrometer'
                    nterm = terms[states.index('spectrometer')]
#                 else:
#                     nstate = True
#                     nterm = ''
                nstates.append(nstate)
                nterminations.append(nterm)
                if root.name in ('Minibone','CocktailPipette','Bone'):
                    print root.name, nstates, nterminations

            return zip(nstates, roots, nterminations)

    def assemble_paths(self, root, parent):
        paths = []
        for ei in root.edges:
            start = ei.bnode if ei.anode is root else ei.anode
            if not start is parent:
                ps = self.assemble_path(start, root, ei.name)
                paths.append(ps)

        return paths

    def assemble_path(self, start, parent, edge):
        if start:
            if isinstance(start, SpectrometerNode):
                yield [edge, start.name, 'spectrometer']
            elif isinstance(start, PumpNode):
                yield [edge, start.name, 'pump']
            elif isinstance(start, LaserNode):
                yield [edge, start.name, 'laser']
            elif isinstance(start, PipetteNode):
                yield [edge, start.name, 'pipette']
            elif isinstance(start, TankNode):
                yield [edge, start.name, 'tank']
            else:
                if start.state and start.state != 'closed':
                    yield [edge, start.name, self.assemble_paths(start, parent)]
                else:
                    yield [edge]
                    
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

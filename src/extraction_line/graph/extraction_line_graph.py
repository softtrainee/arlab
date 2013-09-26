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
from src.canvas.canvas2D.scene.primitives.valves import Valve

TAG_PREDENCE = ('pump', 'spectrometer', 'pipette', 'laser', 'tank',)

class ExtractionLineGraph(HasTraits):
    nodes = Dict
    suppress_changes=False
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

#     def init_states(self, canvas):
#         scene = canvas.canvas2D.scene
#         for ni in self.nodes.itervalues():
#             for ri in ni.find_roots():
#                 self.clear_visited()
#                 obj = scene.get_item(ri.name)
#                 color = obj.default_color
#                 for ei in ri.edges:
#                     obj = scene.get_item(ei.name)
#                     if obj:
#                         if not obj.state:
#                             self._set_item_state(scene, ei.name, True,'', color)
    
    def set_canvas_states(self, canvas, name):
        if not self.suppress_changes:
            snode=self.nodes[name]
#             print 'start node ', name
            r=self.find_max_state(canvas.canvas2D.scene, snode,)
            self.clear_visited()
            if r:
#                 if name!='U':
#                     return
                
                print name, r
                self.flood(canvas.canvas2D.scene, snode, *r)
                self.clear_visited()
    
    def flood(self, scene, start, state, term):
#         print start.name, state
#         self._set_item_state(scene, start, state, term)
        if start.state=='closed':
#             state=False
            return
        
        for ei in start.edges:
            for n in ei.nodes():
                if n.state!='closed':
                    if not n.visited and not n is start:
                        print n.name,n.state
                        n.visited=True
                        self._set_item_state(scene, ei.name, state, term)
                        self._set_item_state(scene, n.name, state, term)
                        for ne in n.edges:
                            self._set_item_state(scene, ne.name, state, term)
                            
                        self.flood(scene, n, state, term)
#                         print n.name
                        
#             n.visited=True
#                         self.flood(scene,n, state,term)
                    
    def find_max_state(self,scene,  start, k=0):
#         print 'visiting ','='*k,start.name
        for ei in start.edges:
#             print 'ei',ei.name
            for n in ei.nodes():
#                 print 'n',n.name,n.visited,n.state
                if not n.visited and not n is start:
#                     print n.name, n.state,'dddd'
                    if n.state!='closed':
                        n.visited=True
        
                        ret=self.find_max_state(scene, n,k=k+1)
                        if ret:
#                             state,term=ret  
#                             print 'set state',n.name, state,term
#                             self._set_item_state(scene, n.name, state, term)
#                             for ne in n.edges:
#                                 self._set_item_state(scene, ne.name, state, term)
#                             self._set_item_state(scene, ei.name, state, term)
                            
                            return ret
#                         else:
#                             self._set_item_state(scene, n.name, False, '')
#                             for ne in n.edges:
#                                 self._set_item_state(scene, ne.name, False, '')
#                             self._set_item_state(scene, ei.name, False, '')
                        
                        if isinstance(n, PumpNode):
#                             self._set_item_state(scene, ei.name, 'pump', n)
#                             print n
                            return 'pump',n
                        
#                         return False,''
        
        
#                 self._set_item_state(scene, name, state, color)
        
#         snode.find_roots()
        
        
#     def set_canvas_states(self, canvas, states):
# 
#         '''
#             if roots connected by an open valve then 
#             set both roots to highest state
#         '''
# #         maxroot = None
# #         maxstate = None
# #         maxterm = None
# 
# #         for state, root, term in states:
# #             if state in ('pump', 'tank'):
# #                 maxstate = state
# #                 maxroot = root
# #                 maxterm = term
# #                 break
# # 
# #             if state in ('laser', 'pipette', 'spectrometer'):
# #                 maxroot = root
# #                 maxterm = term
# #                 maxstate = state
# #         
# #         print maxterm, maxstate 
# #         for state, root, term in states:
# #             nr = root.find_roots()
# #             self.clear_visited()
# # #             print maxroot.name if maxroot else '', root.name, set([ri.name for ri in nr])
# #             if maxroot and maxroot in nr:
# #                 state = maxstate
# #                 term = maxterm
# # 
# #             print 'state={} term={} root={}'.format(state, term, root.name)
# #             self._set_canvas_states(canvas, state, root, term)

#     def _set_canvas_states(self, canvas, state, root, term):
#         scene = canvas.canvas2D.scene
# 
#         color = None
#         if state:
#             obj = scene.get_item(term)
#             color = obj.default_color
#         else:
#             obj = scene.get_item(root.name)
#             color = obj.default_color
# 
# #         for ei in root.edges:
# #             self._set_item_state(scene, ei.name, state, color)
# 
#         self._set_item_state(scene, root.name, state, color)
# 
#         
# #         for path in self.assemble_paths(root, None):
# #             # flatten path and set state for each element
# #             for elem in flatten(path):
# #                 self._set_item_state(scene, elem, state, color)

    def _set_item_state(self, scene, name, state,term, color=None):
        
        obj = scene.get_item(name)
        if not color and state:
            nterm=scene.get_item(term.name)
#             print term,nterm
            color=nterm.default_color
            
        if obj is None \
            or isinstance(obj, Valve) \
                or obj.type_tag in ('turbo', 'tank'):
            return

        if name =='Microbone':
            print 'set item state',name,state, color
        if state:
            obj.active_color = color
            obj.state = True
        else:
            obj.state = False

    def clear_visited(self):
        for ni in self.nodes.itervalues():
            ni.visited = False

    def set_valve_state(self, name, state, *args, **kw):        
        if name in self.nodes:
            vnode = self.nodes[name]
            vnode.state = 'open' if state else 'closed'
            
#             # find the root node for this node
#             roots = vnode.find_roots()
#             self.clear_visited()
# 
#             nstates = []
#             nterminations = []
#             for root in roots:
#                 states = []
#                 terms = []
#                 if root is not None:
#                     for path in self.assemble_paths(root, None):
#                         if path:
#                             elems = list(flatten(path))
#                             if elems:
# #                                 if root.name=='CO2':
# #                                     print elems
# #                                 if root.name in ('Minibone','CocktailPipette','Bone'):
# #                                     print root.name, elems
#                                 term = None
#                                 if len(elems) > 1:
#                                     term = elems[-2]
#                                 terms.append(term)
#                                 states.append(elems[-1])
# 
#                 nstate = ''
#                 nterm = ''
#                 if isinstance(root, PumpNode):
#                     nstate = 'pump'
#                     nterm = root.name
#                 elif isinstance(root, LaserNode):
#                     nstate = 'laser'
#                     nterm = root.name
#                 elif isinstance(root, TankNode):
#                     nstate = 'tank'
#                     nterm = root.name
#                 elif isinstance(root, PipetteNode):
#                     nstate = 'pipette'
#                     nterm = root.name
# 
#                 else:
#                     for attr in ('pump', 'spectrometer', 'pipette', 'laser', 'tank',):
#                         if attr in states:
#                             nstate = attr
#                             nterm = terms[states.index(attr)]
#                             break
# 
#                 nstates.append(nstate)
#                 nterminations.append(nterm)
# 
# #                 if root.name in ('Minibone', 'CocktailPipette', 'Bone'):
# #                     print root.name, nstates, nterminations
# 
#             return zip(nstates, roots, nterminations)
# 
#     def assemble_paths(self, root, parent):
#         paths = []
#         for ei in root.edges:
#             start = ei.bnode if ei.anode is root else ei.anode
#             if not start is parent:
#                 ps = self.assemble_path(start, root, ei.name)
#                 paths.append(ps)
# 
#         return paths
# 
#     def assemble_path(self, start, parent, edge):
#         if start:
#             if isinstance(start, SpectrometerNode):
#                 yield [edge, start.name, 'spectrometer']
#             elif isinstance(start, PumpNode):
#                 yield [edge, start.name, 'pump']
#             elif isinstance(start, LaserNode):
#                 yield [edge, start.name, 'laser']
#             elif isinstance(start, PipetteNode):
#                 yield [edge, start.name, 'pipette']
#             elif isinstance(start, TankNode):
#                 yield [edge, start.name, 'tank']
#             else:
#                 if start.state and start.state != 'closed':
#                     yield [edge, start.name, self.assemble_paths(start, parent)]
#                 else:
#                     yield [edge]

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

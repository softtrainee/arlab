'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import HasTraits, Instance, Any, List, on_trait_change
from traitsui.api import View, Item, ListEditor

#============= standard library imports ========================

#============= local library imports  ==========================
from experiment import Experiment
from src.graph.graph import Graph
from analysis import AutomatedRun
class AnalysisGraphView(HasTraits):
    '''
        G{classtree}
    '''
    experiment = Instance(Experiment)

    graphs = List(Graph)
    selected = Any

    def update(self, obj, name, old, new):
        '''
            @type obj: C{str}
            @param obj:

            @type name: C{str}
            @param name:

            @type old: C{str}
            @param old:

            @type new: C{str}
            @param new:
        '''
        if name == 'selected':
            if new is not None:
                self.experiment = new
                self.graphs = []

    @on_trait_change('experiment:active_analysis')
    def _on_agraph_change(self, obj, name, old, new):
        '''
            @type obj: C{str}
            @param obj:

            @type name: C{str}
            @param name:

            @type old: C{str}
            @param old:

            @type new: C{str}
            @param new:
        '''
        if isinstance(new, AutomatedRun):
            if new.graph not in self.graphs:
                self.graphs.append(new.graph)
                self.selected = new.graph

#============= views ===================================
    def traits_view(self):
        '''
        '''
        return View(
                    Item('graphs', editor=ListEditor(use_notebook=True,
                                                       #page_name = '.name',
                                                       selected='selected'
                                                       ),
                         style='custom',
                         show_label=False,
                         )
                         )
#============= EOF =====================================

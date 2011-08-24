#============= enthought library imports =======================
from traits.api import HasTraits, Instance, Any, List, on_trait_change
from traitsui.api import View, Item, ListEditor

#============= standard library imports ========================

#============= local library imports  ==========================
from experiment import Experiment
from src.graph.graph import Graph
from analysis import Analysis
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
        if isinstance(new, Analysis):
            if new.graph not in self.graphs:
                self.graphs.append(new.graph)
                self.selected = new.graph

#============= views ===================================
    def traits_view(self):
        '''
        '''
        return View(
                    Item('graphs', editor = ListEditor(use_notebook = True,
                                                       #page_name = '.name',
                                                       selected = 'selected'
                                                       ),
                         style = 'custom',
                         show_label = False,
                         )
                         )
#============= EOF =====================================

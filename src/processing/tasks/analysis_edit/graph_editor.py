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
from traits.api import Any, List, on_trait_change, Instance, Property, Event
from traitsui.api import View, UItem, InstanceEditor
from src.envisage.tasks.base_editor import BaseTraitsEditor
#============= standard library imports ========================
from numpy import asarray
from src.processing.tasks.analysis_edit.fits import FitSelector
from src.helpers.isotope_utils import sort_isotopes
from src.graph.regression_graph import StackedRegressionGraph
#============= local library imports  ==========================


class GraphEditor(BaseTraitsEditor):
    tool = Instance(FitSelector, ())
    graph = Any
    processor = Any
    unknowns = List
    _unknowns = List
    component = Property
    component_changed = Event

    def normalize(self, xs, start=None):
        xs = asarray(xs)
        xs.sort()
        if start is None:
            start = xs[0]
        xs -= start

        # scale to hours
        xs = xs / (60.*60.)
        return xs

    @on_trait_change('unknowns[]')
    def _update_unknowns(self):

        '''
            TODO: find reference analyses using the current _unknowns
        '''
        self._make_unknowns()
        self.rebuild_graph()

        keys = set([ki  for ui in self._unknowns
                            for ki in ui.isotope_keys])
        keys = sort_isotopes(keys)

        refiso = self._unknowns[0]
        self.tool.load_fits(refiso.isotope_keys)

    @on_trait_change('tool:update_needed')
    def _tool_refresh(self):
        self.rebuild_graph()

    def rebuild_graph(self):
        graph = self.graph
        graph.clear()
        self._rebuild_graph()
        self.component_changed = True

    def _rebuild_graph(self):
        pass

    def _make_unknowns(self):
        self._unknowns = self.processor.make_analyses(self.unknowns)
        self.processor.load_analyses(self._unknowns)

    def traits_view(self):
        v = View(UItem('graph',
                       style='custom',
                       editor=InstanceEditor()))
        return v

    def _graph_default(self):
        return self._graph_factory()

    def _graph_factory(self):
        g = StackedRegressionGraph(container_dict=dict(stack_order='top_to_bottom'))
        return g

    def _graph_generator(self):
        for fit in self.tool.fits:
            if fit.fit and fit.show:
                yield fit

    def _get_component(self):
        return self.graph.plotcontainer
#============= EOF =============================================

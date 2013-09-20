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
from traits.api import HasTraits, Any, on_trait_change, List
#============= standard library imports ========================
from itertools import groupby
from src.graph.stacked_graph import StackedGraph
from src.processing.plotters.ideogram.ideogram import Ideogram
from numpy.core.numeric import Inf

#============= local library imports  ==========================
class FigurePanel(HasTraits):
    figures = List
    graph = Any
    analyses = Any
    plot_options = Any
    _index_attr = None

    @on_trait_change('analyses[]')
    def _analyses_items_changed(self):
        self.figures = self._make_figures()

    def _make_figures(self):
        key = lambda x: x.group_id
        ans = sorted(self.analyses, key=key)
        gs = [self._figure_klass(analyses=list(ais), group_id=gid)
                for gid, ais in groupby(ans, key=key)]
        return gs

    def make_graph(self):
        g = StackedGraph(panel_height=200,
                         equi_stack=False,
                         container_dict=dict(padding=0),)

        po = self.plot_options
        attr = self._index_attr
        mi, ma = -Inf, Inf
        if attr:
            xmas, xmis = zip(*[(i.max_x(attr), i.min_x(attr))
                               for i in self.figures])
            mi, ma = min(xmis), max(xmas)


        for fig in self.figures:
            fig.trait_set(xma=ma, xmi=mi,
                           options=po
                           )

            plots = list(po.get_aux_plots())

            fig.build(g, plots)
            fig.plot(g, plots)

        self.graph = g
        return g.plotcontainer
#============= EOF =============================================

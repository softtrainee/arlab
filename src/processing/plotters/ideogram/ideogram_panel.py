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
from traits.api import HasTraits, Any, on_trait_change
#============= standard library imports ========================
from itertools import groupby
from src.graph.stacked_graph import StackedGraph
from src.processing.plotters.ideogram.ideogram import Ideogram

#============= local library imports  ==========================
class IdeogramPanel(HasTraits):
    graph = Any
    analyses = Any
    plot_options = Any

    @on_trait_change('analyses[]')
    def _analyses_items_changed(self):
        self.ideograms = self._make_ideograms()

    def _make_ideograms(self):
        key = lambda x: x.group_id
        ans = sorted(self.analyses, key=key)
        gs = [Ideogram(analyses=list(ais), group_id=gid)
                for gid, ais in groupby(ans, key=key)]
        return gs

    def make_graph(self):
        g = StackedGraph(panel_height=200,
                         equi_stack=False,
                         container_dict=dict(padding=0),)

        xmas, xmis = zip(*[(i.max_x('age'), i.min_x('age'))
                            for i in self.ideograms])
        po = self.plot_options

        for ideo in self.ideograms:
            ideo.trait_set(xma=max(xmas), xmi=min(xmis))

            plots = list(po.get_aux_plots())
            ideo.build(g, plots)
            ideo.plot(g, plots)

        self.graph = g
        return g.plotcontainer
#============= EOF =============================================

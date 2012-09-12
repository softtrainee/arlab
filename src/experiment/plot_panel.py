#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, Instance, Int, Property
from traitsui.api import View, Item, TableEditor, Group
from src.loggable import Loggable
from src.graph.graph import Graph
from src.graph.stacked_graph import StackedGraph
from src.viewable import ViewableHandler, Viewable
#============= standard library imports ========================
#============= local library imports  ==========================
class PlotPanelHandler(ViewableHandler):
    pass
class PlotPanel(Viewable):
    graph = Instance(Graph)
    window_x = 0
    window_y = 0
    window_title = ''

    ncounts = Property(Int(enter_set=True, auto_set=False), depends_on='_ncounts')
    _ncounts = Int

    detector = None
    isotopes = None

    def _get_ncounts(self):
        return self._ncounts

    def _set_ncounts(self, v):
        self.info('{} set to terminate after {} counts'.format(self.window_title, v))
        self._ncounts = v

    def _graph_default(self):
        return self._graph_factory()

    def _graph_factory(self):
        return StackedGraph(container_dict=dict(padding=5, bgcolor='gray',
                                             ))
    def traits_view(self):
        v = View(
                 Item('graph', show_label=False, style='custom'),
                 Group(
                       Item('ncounts'),
                       label='controls',
                       show_border=True
                       ),

                 width=500,
                 height=700,
                 x=self.window_x,
                 y=self.window_y,
                 title=self.window_title,
                 handler=PlotPanelHandler
                 )
        return v


#============= EOF =============================================

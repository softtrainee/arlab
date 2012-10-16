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
from traits.api import HasTraits, Instance, on_trait_change, Str, List
from traitsui.api import View, Item, HGroup, VGroup, spring
from src.lasers.stage_managers.stage_map import StageMap
from src.graph.graph import Graph
import os
import numpy as np
from src.paths import paths
from chaco.abstract_overlay import AbstractOverlay
#from pylab import get_cmap
from chaco.tools.scatter_inspector import ScatterInspector
from src.displays.rich_text_display import RichTextDisplay
#import math
from kiva.constants import FILL_STROKE
from src.viewable import Viewable
from enable.markers import CircleMarker
#============= standard library imports ========================
#============= local library imports  ==========================

class MapItemSummary(HasTraits):
    display = Instance(RichTextDisplay)
    def _display_default(self):
        r = RichTextDisplay(width=180, height=80)
        return r

    def traits_view(self):
        v = View(
                 Item('display', show_label=False, style='custom'),
                 width=200,
                 height=100
                 )
        return v

class MapOverlay(AbstractOverlay):
    radius = 0.75
    def overlay(self, component, gc, *args, **kw):
        c = component
        gc.clip_to_rect(c.x + 1, c.y + 1, c.width - 1, c.height - 1)

        xs = c.index.get_data()
        ys = c.value.get_data()
        cs = c.color_data.get_data()
        p1, p2 = c.map_screen(np.array([(0, 0), (self.radius, 0)]))
        size = abs(p1[0] - p2[0])

        data = c.map_screen(np.array(zip(xs, ys)))

        gc.set_stroke_color((0, 0, 0))
        for k, color in [(-1, (0, 0, 0)), (-1.1, (1, 1, 1)), (-1.2, (0, 1, 0))]:
            gc.save_state()
            pts = [pt for pt, si in zip(data, cs) if si == k]
            if pts:
                gc.set_fill_color(color)
                marker = CircleMarker
                path = gc.get_empty_path()
                marker().add_to_path(path, size)
                gc.draw_path_at_points(pts, path, FILL_STROKE)
                gc.restore_state()

class MapView(Viewable):
    stage_map = Instance(StageMap)
    graph = Instance(Graph)

    labnumber = Str
    holenumber = Str

    labnumbers = List
    @on_trait_change('stage_map')
    def _build_map(self):
#        xs = [1, 2, 3, 4]
#        ys = [2, 4, 6, 8]
        if self.stage_map:
            if not self.stage_map.sample_holes:
                return

            xs, ys, states, labns = zip(*[(h.x, h.y, -1 , '') for h in self.stage_map.sample_holes])
            g = self.graph
            states = list(states)
            states[len(states) / 2] = -1.2
            s, _p = g.new_series(xs, ys,
                                 colors=states,
                         type='cmap_scatter',
                         marker='circle',
                         color_map_name='jet',
                         marker_size=10,
                         )

            s.tools.append(ScatterInspector(s,
                                            selection_mode='single',
                                            threshold=10
                                            ))

            s.index.on_trait_change(self._update, 'metadata_changed')

            ov = MapOverlay(s)
            s.overlays.append(ov)
            self.scatter = s
            self.labnumbers = list(labns)

            g.set_x_limits(min=min(xs), max=max(xs), pad='0.05')
            g.set_y_limits(min=min(ys), max=max(ys), pad='0.05')

    def _update(self, new):
        if new:
#            sel = self.scatter.index.metadata.get('selections')
#            if sel:
#                e = MapItemSummary()
#                e.edit_traits()


            hov = self.scatter.index.metadata.get('hover')
            if hov:
                hid = hov[0]
                self.labnumber = self.labnumbers[hid]
                self.holenumber = str(hid + 1)

    def _graph_default(self):
        g = Graph(container_dict=dict(padding=5))
        g.new_plot(padding=5)
        g.set_axis_traits(axis='y', visible=False)
        g.set_axis_traits(axis='x', visible=False)
        g.set_grid_traits(grid='x', visible=False)
        g.set_grid_traits(grid='y', visible=False)
        return g

    def traits_view(self):
        g = Item('graph', style='custom', show_label=False)
        info = HGroup(
                      Item('holenumber', width=30, style='readonly'),
                      Item('labnumber', style='readonly'),
                      )
        v = View(info,
                 g,
                 width=500,
                 height=500,
                 title='Lab Map',
                 handler=self.handler_klass
                 )
        return v

    def set_hole_state(self, holenum, state):
        d = self.scatter.color_data.get_data()
        d[holenum] = state
        self.scatter.color_data.set_data(d)

    def set_hole_labnumber(self, holenum, ln):
        self.labnumbers[holenum - 1] = ln
        self.set_hole_state(holenum - 1, -1.1)
#        self.scatter.states[holenum - 1] = 1

if __name__ == '__main__':
    import random
    sm = StageMap(file_path=os.path.join(paths.map_dir, '221-hole.txt'))
    mv = MapView(stage_map=sm)

    for i in range(0, 210, 1):
        mv.set_hole_labnumber(i, str(i))

    for i in range(0, 100, 1):
        r = random.random() * 10
        mv.set_hole_state(i, r)

    mv.configure_traits()
#============= EOF =============================================

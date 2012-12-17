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
from traits.api import HasTraits, Event, Any, on_trait_change, Tuple, Str
from traitsui.api import View, Item, TableEditor
from enable.base_tool import BaseTool
from chaco.abstract_overlay import AbstractOverlay
#============= standard library imports ========================
#============= local library imports  ==========================


class RegressionInspectorTool(BaseTool):
    metadata = Event
    graph = Any
    def normal_mouse_move(self, event):
        pos = self.component.hittest((event.x, event.y))
        if pos:
#            for e, pi in enumerate(self.graph.plots):
#                for pii in pi.plots:
#                    if pii[0] == self.component:
#                        break
#            reg = self.graph.regressors[e]
            reg = self.component.regressor
            self.metadata = dict(xy=(event.x, event.y),
                                 regressor=reg
                                 )
        else:
            self.metadata = False

class RegressionInspectorOverlay(AbstractOverlay):
    tool = Any
    visible = False
    xy = Tuple
    regressor = Any
    @on_trait_change('tool:metadata')
    def _update_(self, new):
        if new:
            self.xy = new['xy']
            self.regressor = new['regressor']

            self.visible = True
        else:
            self.visible = False

    def overlay(self, plot, gc, *args, **kw):
        if self.visible:
            with gc:
                x, y = self.xy
                gc.set_fill_color((0.8, 0.8, 0.8))

                msgs = [self.regressor.make_equation()]
                msgs += map(str.strip, map(str, self.regressor.tostring().split(',')))
                lws, lhs = zip(*[gc.get_full_text_extent(mi)[:2] for mi in msgs])

                lw = max(lws)
                lh = sum(lhs) + 2 * len(lhs)

                xoffset = 12
                yoffset = 10

                gc.rect(x + xoffset, y - yoffset - lh, lw + 4, lh)
                gc.draw_path()
                gc.set_fill_color((0, 0, 0))
                h = lhs[0]
                for i, mi in enumerate(msgs):
                    gc.set_text_position(x + xoffset + 2,
                                         y - yoffset - h * (i + 1)
                                         )
                    gc.show_text(mi)
#============= EOF =============================================

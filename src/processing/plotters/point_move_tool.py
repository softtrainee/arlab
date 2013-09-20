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
from traits.api import HasTraits, Enum, CArray
from traitsui.api import View, Item, TableEditor
from chaco.tools.api import DragTool
#============= standard library imports ========================
#============= local library imports  ==========================

class PointMoveTool(DragTool):
    event_state = Enum("normal", "dragging")
    _prev_pt = CArray
    constrain = Enum(None, 'x', 'y')
    def is_draggable(self, x, y):
        return self.component.hittest((x, y))

    def drag_start(self, event):
        data_pt = self.component.map_data((event.x, event.y), all_values=True)
        self._prev_pt = data_pt
        event.handled = True

    def dragging(self, event):
        plot = self.component
        cur_pt = plot.map_data((event.x, event.y), all_values=True)
        dy = cur_pt[1] - self._prev_pt[1]
        dx = cur_pt[0] - self._prev_pt[0]
        if self.constrain == 'x':
            dy = 0
        elif self.constrain == 'y':
            dx = 0

        index = plot.index.get_data() + dx
        value = plot.value.get_data() + dy

        aa = plot.map_data((0, 0), all_values=True)[1]
        bb = plot.map_data((0, 2), all_values=True)[1]
        dd = bb - aa
        value[value < dd] = dd

        # move the point
        plot.index.set_data(index, sort_order=plot.index.sort_order)
        plot.value.set_data(value, sort_order=plot.value.sort_order)

        self._prev_pt = cur_pt
        event.handled = True
        plot.request_redraw()
#============= EOF =============================================

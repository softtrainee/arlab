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
from traits.api import HasTraits, Event, Instance, Tuple, on_trait_change, Dict
from traitsui.api import View, Item, TableEditor
from chaco.abstract_overlay import AbstractOverlay
from enable.base_tool import BaseTool
#============= standard library imports ========================
#============= local library imports  ==========================
class InfoInspector(BaseTool):
    metadata_changed = Event
    current_position = None
    current_screen = None

    def normal_mouse_move(self, event):
        xy = event.x, event.y
        pos = self.component.hittest(xy)
        if isinstance(pos, tuple):
            self.current_position = pos
            self.current_screen = xy
            event.handled = True
        else:
            self.current_position = None
            self.current_screen = None
        self.metadata_changed = True

    def assemble_lines(self):
        return []

    def normal_mouse_leave(self, event):
        self.current_screen = None
        self.current_position = None
        self.metadata_changed = True

class InfoOverlay(AbstractOverlay):
    tool = Instance(InfoInspector)
    visible = False

    '''
        abstract class for displaying hover data
        subclasses should implement _assemble_lines
    '''

    @on_trait_change('tool:metadata_changed')
    def _update_(self, new):
        if self.tool.current_position:
            self.visible = True
        else:
            self.visible = False

        self.request_redraw()

    def overlay(self, plot, gc, *args, **kw):
        with gc:
#            if self.visible:
            lines = self.tool.assemble_lines()
            if lines:
                self._draw_info(gc, lines)
        self.visible = False

    def _draw_info(self, gc, lines):
        x, y = self.tool.current_screen

        gc.set_fill_color((0.8, 0.8, 0.8))

        lws, lhs = zip(*[gc.get_full_text_extent(mi)[:2] for mi in lines])

        lw = max(lws)
        lh = sum(lhs) + 2 * len(lhs)

        xoffset = 12
        yoffset = 10

        x += xoffset
        y -= yoffset

        x2 = self.component.x2
        if x + lw > x2:
            x = x2 - lw - 3

        gc.rect(x, y - lh, lw + 4, lh)
        gc.draw_path()
        gc.set_fill_color((0, 0, 0))
        h = lhs[0]

        #if the box doesnt fit in window 
        #move left

        for i, mi in enumerate(lines):
            gc.set_text_position(x + 2,
                                 y - h * (i + 1)
                                 )
            gc.show_text(mi)

#============= EOF =============================================

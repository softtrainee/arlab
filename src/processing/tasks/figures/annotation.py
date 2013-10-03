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
import string
from chaco.plot_component import PlotComponent
from chaco.tools.data_label_tool import DataLabelTool
from chaco.tooltip import ToolTip
from enable.tools.drag_tool import DragTool
from traits.api import HasTraits, Str, List
from traitsui.api import View, Item

#============= standard library imports ========================
#============= local library imports  ==========================
VK = string.ascii_letters

KEY_MAP = {'Enter': '\n', ' ': ' '}


class AnnotationTool(DataLabelTool):
    active = True
    _temp_border = None
    components = List

    def clear_selection(self):
        if self.component:
            if self._temp_border:
                self.component.trait_set(**self._temp_border)
                self._temp_border = None

    def select_component(self, event):
        x, y = event.x, event.y
        if self.is_draggable(x, y):
            self._temp_border = self.component.trait_get(
                'border_color',
                'border_width')

            self.component.trait_set(
                #border_visible=True,
                border_color='red',
                border_width=2)
            self.active = True

        self.component.request_redraw()

    def normal_key_pressed(self, event):

        if self.active:
            c = event.character
            label = self.component
            if not label.visible:
                label.x, label.y = self.current_mouse_pos

            if c == 'Backspace':
                if self.component:
                    pcomp = self.component.component
                    pcomp.overlays.remove(self.component)
                    self.components.remove(self.component)
                else:
                    label.text = label.text[:-1]

            elif c in KEY_MAP:
                label.text += KEY_MAP[c]
            elif c in VK:
                label.text += c

            event.handled = True

    def normal_left_down(self, event):
        x, y = event.x, event.y
        self.active = not self.component.visible

        self.clear_selection()
        self.select_component(event)
        #if self.is_draggable(x, y):
        #    self.active = True

    def is_draggable(self, x, y):
        """ Returns whether the (x,y) position is in a region that is OK to
        drag.

        Overrides DragTool.
        """
        if self.components:
            for label in self.components:
                hit = (label.x <= x <= label.x2 and \
                       label.y <= y <= label.y2)
                if hit:
                    self.component = label
                    return True
            else:
                return False
        else:
            return False

    def normal_mouse_move(self, event):
        self.current_mouse_pos = (event.x, event.y)

    def drag_start(self, event):
        """ Called when the drag operation starts.

        Implements DragTool.
        """
        if self.component:
            label = self.component
            self._original_offset = (label.x, label.y)
            event.window.set_mouse_owner(self, event.net_transform())
            event.handled = True
        return

    def dragging(self, event):
        """ This method is called for every mouse_move event that the tool
        receives while the user is dragging the mouse.

        Implements DragTool. Moves and redraws the label.
        """
        if self.component:
            label = self.component
            dx = int(event.x - self.mouse_down_position[0])
            dy = int(event.y - self.mouse_down_position[1])

            label.x, label.y = (self._original_offset[0] + dx,
                                self._original_offset[1] + dy)

            event.handled = True
            label.request_redraw()
        return


def rounded_rect(gc, x, y, width, height, corner_radius):
    with gc:
        gc.translate_ctm(x, y)  # draw a rounded rectangle
        x = y = 0
        gc.begin_path()

        hw = width * 0.5
        hh = height * 0.5
        if hw < corner_radius:
            corner_radius = hw * 0.5
        elif hh < corner_radius:
            corner_radius = hh * 0.5

        gc.move_to(x + corner_radius, y)
        gc.arc_to(x + width, y, x + width, y + corner_radius, corner_radius)
        gc.arc_to(x + width, y + height, x + width - corner_radius, y + height, corner_radius)
        gc.arc_to(x, y + height, x, y, corner_radius)
        gc.arc_to(x, y, x + width + corner_radius, y, corner_radius)
        gc.stroke_path()


class AnnotationOverlay(ToolTip):
    text = Str('')
    visible = False

    def _text_changed(self):
        self.visible = bool(self.text)
        self.lines = self.text.split('\n')
        self.component.invalidate_and_redraw()

    def _draw_border(self, gc, view_bounds=None, mode="default",
                     force_draw=False):

        if not self.border_visible:
            return

        if self.overlay_border or force_draw:
            border_width = self.border_width
            with gc:
                gc.set_line_width(border_width)
                gc.set_line_dash(self.border_dash_)
                gc.set_stroke_color(self.border_color_)
                rounded_rect(gc, self.x, self.y, self.width, self.height, 4)


#============= EOF =============================================

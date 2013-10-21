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
from chaco.abstract_overlay import AbstractOverlay
from chaco.plot_label import PlotLabel
from chaco.scatterplot import render_markers
from traits.api import Color, Instance, Str, Float, Int

#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.plotters.point_move_tool import LabelMoveTool


class Movable(object):
    current_screen_point = None
    altered_screen_point = None

    def get_current_point(self):
        data_pt = self.altered_screen_point
        if data_pt is None:
            data_pt = self.current_screen_point
        return data_pt


class XYPlotLabel(PlotLabel, Movable):
    sx = Float
    sy = Float

    def do_layout(self):
        """ Tells this component to do layout.

        Overrides PlotComponent.
        """
        if self.component is None:
            self._layout_as_component()
        return

    def hittest(self, pt):
        x, y = pt
        w, h = self.get_preferred_size()
        return abs(x - self.x) < w and abs(y - self.y) < h

    def _sx_changed(self):
        self.x = self.sx + self.get_preferred_size()[0] / 2.0 + 5

        #self.altered_screen_point=(self.x, self.y)
        #print self.altered_screen_point
        self.current_screen_point = (self.x, self.y)

    def _sy_changed(self):
        self.y = self.sy + 10
        self.current_screen_point = (self.x, self.y)

    def set_altered(self):
        self.altered_screen_point = (self.x, self.y)


class MeanIndicatorOverlay(AbstractOverlay, Movable):
    color = Color
    label = Instance(PlotLabel)
    text = Str

    x = Float
    error = Float
    nsigma = Int

    def clear(self):
        self.altered_screen_point = None

    def hittest(self, pt, tol=5):
        x, y = pt
        if self.get_current_point():
            gx, gy = self.get_current_point()
            #print abs(gx-x)<tol , abs(gy-y)<tol
            return abs(gx - x) < tol and abs(gy - y) < tol
            #print x,y, gx, gy

    def _text_changed(self):
        label = self.label
        if label is None:
            label = XYPlotLabel(component=self, text=self.text)
            self.label = label
            self.overlays.append(label)
            self.tools.append(LabelMoveTool(component=label))
            #print self.label

    def _color_changed(self):
        color = self.color
        #if isinstance(color, str):
        #    color=color_table[color]
        self._color = map(lambda x: x / 255., color.toTuple())
        #self._color=color

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):

        with gc:
            points = self._gather_data()
            #print points, self.x, self.y
            marker = 'circle'
            marker_size = 3
            color = self._color#color_table['black']
            line_width = 1
            outline_color = self._color#color_table['black']
            render_markers(gc, points, marker, marker_size,
                           color, line_width, outline_color)

            x, y = self.get_current_point()

            e = self.error / 2.0 * max(1, self.nsigma)
            p1, p2 = self.component.map_screen([(self.x - e, 0), (self.x + e, 0)])

            gc.begin_path()
            gc.set_stroke_color(self._color)
            gc.move_to(p1[0], y)
            gc.line_to(p2[0], y)
            gc.draw_path()

        for o in self.overlays:
            o.overlay(other_component, gc, view_bounds=view_bounds, mode=mode)

    def get_current_point(self):
        data_pt = self.altered_screen_point
        #print 'adsfsadf', data_pt, #len(data_pt)
        if data_pt is None:
            data_pt = self.current_screen_point
        return data_pt

    def _gather_data(self):
        if self.altered_screen_point is None:
            comp = self.component
            x = comp.map_screen([(self.x, 0)])[0, 0]
            if self.label:
                if not self.label.altered_screen_point:
                    self.label.sx = x
                    self.label.sy = self.y
            self.current_screen_point = (x, self.y)

            return [(x, self.y)]
        else:
            if self.label:
                if not self.label.altered_screen_point:
                    self.label.sx, self.label.sy = self.altered_screen_point
            return [self.altered_screen_point]

    def set_x(self, x):
        self.x = x
        comp = self.component
        x = comp.map_screen([(self.x, 0)])[0, 0]
        if self.label:
            if not self.label.altered_screen_point:
                self.label.sx = x
                self.label.sy = self.y

        if self.altered_screen_point:
            self.altered_screen_point = (x, self.altered_screen_point[1])
        else:
            self.current_screen_point = (x, self.y)

#============= EOF =============================================

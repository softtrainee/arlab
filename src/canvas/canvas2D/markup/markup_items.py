#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import HasTraits, Float, Any, Dict, Bool
from chaco.default_colormaps import color_map_name_dict
from chaco.data_range_1d import DataRange1D
#============= standard library imports ========================
import math
from numpy import array
#============= local library imports  ==========================


def calc_rotation(x1, y1, x2, y2):
    rise = y2 - y1
    run = x2 - x1

    r = math.pow((math.pow(run, 2) + math.pow(rise, 2)), 0.5) #(x ** 2 + y ** 2) ** 0.5
    if r == 0:
        return 0

    if run >= 0:
        angle = math.asin(rise / r)
    else:
        angle = -math.asin(rise / r) + math.pi

    da = math.degrees(angle)
    return da if da >= 0 else 360 + da

class MarkupItem(HasTraits):
    identifier = ''
    x = Float
    y = Float
    state = False
    default_color = (1, 0, 0)
    active_color = (0, 1, 0)
    canvas = Any(transient=True)
    line_width = 1

    def __init__(self, x, y, *args, **kw):
        self.x = x
        self.y = y
        super(MarkupItem, self).__init__(*args, **kw)

    def render(self, gc):
        gc.begin_path()
        self.set_stroke_color(gc)
        self.set_fill_color(gc)
        gc.set_line_width(self.line_width)

        self._render_(gc)
        gc.stroke_path()

    def set_stroke_color(self, gc):
        if self.state:
            gc.set_stroke_color(self.active_color)
        else:
            gc.set_stroke_color(self.default_color)

    def set_fill_color(self, gc):
        if self.state:
            gc.set_fill_color(self.active_color)
        else:
            gc.set_fill_color(self.default_color)

    def _render_(self, gc):
        pass

    def adjust(self, dx, dy):
        args = self.canvas.map_data((dx, dy))
        aargs = self.canvas.map_data((0, 0))
        dx = args[0] - aargs[0]
        dy = args[1] - aargs[1]
        self.x += dx
        self.y += dy

    def get_xy(self):
        x, y = self.canvas.map_screen([(self.x, self.y)])[0]
#        offset = self.canvas.offset
        offset = 1
        return x + offset, y + offset

    def get_wh(self):
        (w, h), (ox, oy) = self.canvas.map_screen([(self.width, self.height), (0, 0)])
        return w - ox, h - oy

    def set_canvas(self, canvas):
        self.canvas = canvas

    def set_state(self, state):
        self.state = state

class Point(MarkupItem):
    pass


class Rectangle(MarkupItem):
    width = 0
    height = 0
    x = 0
    y = 0
    use_border = True
    def _render_(self, gc):
        x, y = self.get_xy()
        w, h = self.get_wh()
#        gc.set_line_width(self.line_width)
        gc.rect(x, y, w, h)
        gc.draw_path()

        if self.use_border:
            self._render_border(gc, x, y, w, h)
        gc.set_fill_color((0, 0, 0))

        if self.name:
            t = str(self.name)
            tw = gc.get_full_text_extent(t)[0]
            x = x + w / 2.0 - tw / 2.0
            gc.set_text_position(x, y + h / 2 - 6)
            gc.show_text(str(self.name))
            gc.draw_path()

    def _render_border(self, gc, x, y, w, h):
        gc.set_stroke_color((0, 0, 0))
        gc.rect(x - self.line_width, y - self.line_width,
                w + self.line_width, h + self.line_width
                )
        gc.stroke_path()

class RoughValve(MarkupItem):
    width = 2
    height = 2
    def _render_(self, gc):
        cx, cy = self.get_xy()
        w, h = self.get_wh()

        w2 = w / 2
        h2 = h / 2
        x1 = cx - w2
        x2 = cx + w2
        x3 = cx

        y1 = cy - h2
        y2 = y1
        y3 = cy + h2

        gc.lines([(x1, y1), (x2, y2), (x3, y3), (x1, y1)])
        gc.fill_path()
        gc.set_stroke_color((0, 0, 0))
        gc.lines([(x1, y1), (x2, y2), (x3, y3), (x1, y1)])
        gc.stroke_path()


class Valve(Rectangle):
    soft_lock = False
    width = 2
    height = 2
    def _render_(self, gc):

        super(Valve, self)._render_(gc)
##        if self.state:
##                        gc.set_fill_color((0, 1, 0))
##                    else:
##                        if item.selected:
##                            gc.set_fill_color((1, 1, 0))
##                        else:
##                            gc.set_fill_color((1, 0, 0))
#
        x, y = self.get_xy()
        w, h = self.get_wh()
#        gc.rect(x, y, w, h)
#        gc.draw_path()
#        if self.use_border:
#            self._render_border(gc, w, y, w, h)
#
#        #print item.name, item.soft_lock
        if self.soft_lock:
            gc.save_state()
            gc.set_fill_color((0, 0, 0, 0))
            gc.set_stroke_color((0, 0, 1))
            gc.set_line_width(5)
            gc.rect(x - 2, y - 2, w + 4, h + 4)
            gc.draw_path()
            gc.restore_state()
#        gc.set_fill_color((0, 0, 0))
#        gc.set_text_position(x + w / 4.0, y + h / 4.0)
#        gc.show_text(self.name)
#        gc.draw_path()

class Line(MarkupItem):
    start_point = None
    end_point = None
    screen_rotation = Float
    data_rotation = Float
    width = 1
    def __init__(self, p1, p2, *args, **kw):

        if isinstance(p1, tuple):
            p1 = Point(*p1, **kw)
        if isinstance(p2, tuple):
            p2 = Point(*p2, **kw)

        self.start_point = p1
        self.end_point = p2

        super(Line, self).__init__(0, 0, *args, **kw)

    def set_canvas(self, canvas):
        self.start_point.set_canvas(canvas)
        self.end_point.set_canvas(canvas)

    def _render_(self, gc):
#        gc.begin_path()
        gc.set_line_width(self.width)
        x, y = self.start_point.get_xy()
        #x, y = self.canvas.map_screen([(self.start_point.x, self.start_point.y)])[0]
        gc.move_to(x, y)

        x, y = self.end_point.get_xy()
        #x, y = self.canvas.map_screen([(self.end_point.x, self.end_point.y)])[0]
        gc.line_to(x, y)

    def adjust(self, dx, dy):
        self.start_point.adjust(dx, dy)
        self.end_point.adjust(dx, dy)

    def get_length(self):
        dx = self.start_point.x - self.end_point.x
        dy = self.start_point.y - self.end_point.y
        return (dx ** 2 + dy ** 2) ** 0.5

    def calculate_rotation(self):

        x1, y1 = self.start_point.x, self.start_point.y
        x2, y2 = self.end_point.x, self.end_point.y
        a = calc_rotation(x1, y1, x2, y2)

        self.data_rotation = a
        x1, y1 = self.start_point.get_xy()
        x2, y2 = self.end_point.get_xy()

        b = calc_rotation(x1, y1, x2, y2)
        self.screen_rotation = b

class Triangle(MarkupItem):
    draw_text = False
    def __init__(self, *args, **kw):
        super(Triangle, self).__init__(0, 0, **kw)
        self.points = []

    def _render_(self, gc):
        points = self.points
        func = self.canvas.map_screen
        if points:

            as_lines = True
            if as_lines:
                gc.begin_path()
                gc.move_to(*func(points[0][:2]))
                for p in points[1:]:
                    gc.line_to(*func(p[:2]))

                if len(points) == 3:
                    gc.line_to(*func(points[0][:2]))
                gc.stroke_path()
            else:
                f = color_map_name_dict['hot'](DataRange1D(low_setting=0, high_setting=300))
                for x, y, v in points:
                    x, y = func((x, y))
                    gc.set_fill_color(f.map_screen(array([v]))[0])
                    gc.arc(x - 2, y - 2, 2, 0, 360)
                    gc.fill_path()

#            
            if self.draw_text:
                gc.set_font_size(9)
                for x, y, v in points:
                    x, y = self.canvas.map_screen((x, y))
                    gc.set_text_position(x + 5, y + 5)
                    gc.show_text('{:0.3f}'.format(v))


class Circle(MarkupItem):
    radius = 10
    def __init__(self, x, y, radius=10, *args, **kw):
        super(Circle, self).__init__(x, y, *args, **kw)
        self.radius = radius

    def _render_(self, gc):
        x, y = self.get_xy()
        gc.arc(x, y, self.radius, 0, 360)

    def is_in(self, event):
        x, y = self.get_xy()
        if ((x - event.x) ** 2 + (y - event.y) ** 2) ** 0.5 < self.radius:
            return True


class CalibrationObject(HasTraits):
    tweak_dict = Dict
    cx = Float
    cy = Float
    rx = Float
    ry = Float

    def get_rotation(self):
        if not (self.rx and self.rx):
            return 0

        return calc_rotation(self.cx, self.cy, self.rx, self.ry)

    def get_center_position(self):
        return self.cx, self.cy

    def set_right(self, x, y):
        self.rx = x
        self.ry = y

    def set_center(self, x, y):
        self.cx = x
        self.cy = y

    def set_canvas(self, canvas):
        self.canvas = canvas


class CalibrationItem(MarkupItem, CalibrationObject):
    center = None
    right = None
    line = None
    tool_state = 'move'

#    tweak_dict = Dict
    def __init__(self, x, y, rotation, *args, **kw):
        super(CalibrationItem, self).__init__(x, y, *args, **kw)

        self.center = Circle(x, y, 30, canvas=self.canvas)

        r = 10
        rx = x + r * math.cos(rotation)
        ry = y + r * math.cos(rotation)

        self.right = Circle(rx, ry, 19, default_color=(1, 1, 1), canvas=self.canvas)
        self.line = Line(Point(x, y, canvas=self.canvas),
                          Point(rx, ry, canvas=self.canvas),
                          default_color=(1, 1, 1),
                          canvas=self.canvas)

    def get_rotation(self):
        return self.line.data_rotation

    def get_center_position(self):
        return self.center.x, self.center.y

    def set_canvas(self, canvas):
        self.center.set_canvas(canvas)
        self.right.set_canvas(canvas)
        self.line.set_canvas(canvas)

    def adjust(self, dx, dy):
        if self.tool_state == 'move':
            self.center.adjust(dx, dy)
            self.right.adjust(dx, dy)
            self.line.adjust(dx, dy)
        else:
            self.right.adjust(dx, dy)
            self.line.end_point.adjust(dx, dy)
            self.line.calculate_rotation()

    def _render_(self, gc):
        self.center.render(gc)
        self.right.render(gc)
        self.line.render(gc)

    def is_in(self, event):
        if self.center.is_in(event):
            self.tool_state = 'move'
            return True

        elif self.right.is_in(event):
            self.tool_state = 'rotate'
            return True


class Label(MarkupItem):
    text = ''
    use_border = True

    def _render_(self, gc):
        x, y = self.get_xy()

        if self.use_border:
            gc.set_line_width(2)
            offset = 5
            w = gc.get_full_text_extent(self.text)[0] + 2 * offset
            gc.set_stroke_color((0, 0, 0))
            gc.rect(x - offset, y - offset, w, 18)
            gc.stroke_path()

        gc.set_fill_color((0, 0, 0))
        gc.set_text_position(x, y)
        gc.show_text(self.text)

class Indicator(MarkupItem):
    def __init__(self, x, y, *args, **kw):
        super(Indicator, self).__init__(x, y, *args, **kw)
        w = 0.5
        self.hline = Line(Point(x - w, y, **kw),
                          Point(x + w, y, **kw))
        h = 0.5
        self.vline = Line(Point(x, y - h, **kw),
                          Point(x, y + h, **kw))

    def _render_(self, *args, **kw):
        self.hline.render(*args, **kw)
        self.vline.render(*args, **kw)

class PointIndicator(Indicator):
    radius = 10
    active = Bool(False)
    def __init__(self, x, y, *args, **kw):
        super(PointIndicator, self).__init__(x, y, *args, **kw)
        self.circle = Circle(self.x, self.y, self.radius, *args, **kw)
        print self.identifier
        self.label = Label(self.x, self.y,
                           text=str(int(self.identifier[5:]) + 1),
                            *args, **kw)
    def set_state(self, state):
        self.state = state
        self.hline.state = state
        self.vline.state = state
        self.circle.state = state

    def is_in(self, event):
        x, y = self.get_xy()
        if ((x - event.x) ** 2 + (y - event.y) ** 2) ** 0.5 < self.radius:
            return True
    def adjust(self, dx, dy):
        super(PointIndicator, self).adjust(dx, dy)
        self.hline.adjust(dx, dy)
        self.vline.adjust(dx, dy)
        self.circle.adjust(dx, dy)
        self.label.adjust(dx, dy)

    def _render_(self, gc):
        super(PointIndicator, self)._render_(gc)

        self.circle.render(gc)
        self.label.render(gc)

        x, y = self.get_xy()

        if self.state:
            gc.rect(x - self.radius - 1,
                    y - self.radius - 1,
                    2 * self.radius + 1,
                    2 * self.radius + 1
                    )

class Dot(MarkupItem):
    radius = 5
    def _render_(self, gc):
        x, y = self.get_xy()
        gc.arc(x, y, self.radius, 0, 360)
        gc.fill_path()

#============= EOF ====================================

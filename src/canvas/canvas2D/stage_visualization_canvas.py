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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.canvas.canvas2D.markup.markup_canvas import MarkupCanvas
from src.canvas.canvas2D.markup.markup_items import Circle, Line, PointIndicator

class InfoObject(object):
    pass

class SampleHole(Circle, InfoObject):
    display_interpolation = False
    hole = None
    _radius = 1

    def _get_radius(self):
        r = self.hole.dimension / 2.0
        return self.map_dimension(r)

    def _set_radius(self, r):
        pass

    radius = property(fget=_get_radius, fset=_set_radius)

class StageVisualizationCanvas(MarkupCanvas):
    _prev_current = None

    def build_map(self, sm, calibration=None):
        sm.load_correction_file()

        cpos = 0, 0
        rot = 0
        if calibration is not None:
            cpos = calibration[0]
            rot = calibration[1]

        for si in sm.sample_holes:

            x, y = sm.map_to_calibration(si.nominal_position,
                                      cpos, rot)
            self.markupcontainer[si.id] = SampleHole(x, y, canvas=self,
                                                 default_color=(0, 0, 0),
                                                fill=True,
                                                name=si.id,
                                                hole=si,
                                                )

            if si.has_correction():
                self.record_correction(si, si.x_cor, si.y_cor)
        self.invalidate_and_redraw()

    def map_dimension(self, d):
        (w, h), (ox, oy) = self.map_screen([(d, d), (0, 0)])
        w, h = w - ox, h - oy
        return w

    def record_correction(self, h, x, y):
        name = '{}_cor'.format(h.id)
        radius = self.map_dimension(h.dimension / 2.0)
        self.markupcontainer[(name, 2)] = Circle(x, y,
                                                 canvas=self,
                                                 radius=radius
                                                 )
        self.request_redraw()

    def record_path(self, p1, p2, name):
        self.markupcontainer[(name, 2)] = Line(p1, p2, canvas=self)
        self.request_redraw()

    def record_interpolation(self, x, y, hole, color):
        for i, ih in enumerate(hole.interpolation_holes):
            n = '{}-interpolation-line-{}'.format(hole.id, i)
            self.markupcontainer[(n, 2)] = Line((x, y), (ih.x_cor, ih.y_cor),
                                                canvas=self,
                                                visible=False,
                                                default_color=color
                                                )


        r = self.map_dimension(hole.dimension / 2.0)
        self.markupcontainer[('{}-interpolation-indicator'.format(hole.id), 3)] = PointIndicator(x, y, canvas=self,
                                                                                                default_color=color,
                                                                                                radius=r
                                                                                                )
    def set_current_hole(self, h):
        if self._prev_current:
            p = self.markupcontainer[self._prev_current]
            p.state = False

        self.markupcontainer[h.id].state = True
        self._prev_current = h.id

    def _selection_hook(self, obj):
        #toggle the visiblity of the objects interpolation holes
        for k, v in self.markupcontainer.iteritems():
            if k.startswith('{}-interpolation-line'.format(obj.name)):
                v.visible = not v.visible

#============= EOF =============================================

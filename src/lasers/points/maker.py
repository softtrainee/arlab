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
from traits.api import HasTraits, Any, Button, Enum, Float, Int, Color, \
    Bool
from traitsui.api import View, Item, TableEditor, VGroup, HGroup
from src.loggable import Loggable
#============= standard library imports ========================
#============= local library imports  ==========================

class BaseMaker(Loggable):
    canvas = Any
    stage_manager = Any

    clear = Button
    clear_mode = Enum('all', 'all lines', 'all points', 'current line',
                    'current point', 'last point'
                    )
    accept_point = Button

    point_color = Color
    def save(self):
        d = dict()
        pts = [dict(identifier=pi.identifier,
                        z=float(pi.z),
                        mask=pi.mask, attenuator=pi.attenuator,
                        xy=[float(pi.x), float(pi.y)]
                        ) for pi in self.canvas.points]

        lines = []
        for li in self.canvas.lines:
            segments = []
            for i, pi in enumerate(li.points):
                v = li.velocity_segments[i / 2]
                segments.append(dict(xy=[float(pi.x), float(pi.y)],
                                     z=float(pi.z),
                                     mask=pi.mask,
                                     attenuator=pi.attenuator,
                                     velocity=v))
            lines.append(segments)

        d['points'] = pts
        d['lines'] = lines
        sd = self._save()
        if sd:
            d.update(sd)
        return d

    def _save(self):
        pass
    def _accept_point(self, ptargs):
        pass

    def _clear_fired(self):
        cm = self.clear_mode
        if cm.startswith('current'):
            if cm == 'current line':
                self.canvas.lines.pop(-1)
            else:
                self.canvas.points.pop(-1)
        elif cm.startswith('all'):
            if cm == 'all':
                self.canvas.clear_all()
            elif cm == 'all lines':
                self.canvas.lines = []
            else:
                self.canvas.points = []
        else:
            line = self.canvas.lines[-1]
            if len(line.points):
                if self.mode == 'line':
                    line.points.pop(-1)
                    if line.lines:
                        line.lines.pop(-1)
                        line.velocity_segments.pop(-1)
                else:
                    self.canvas.points.pop(-1)

        self.canvas.request_redraw()

    def _accept_point_fired(self):
        radius = 0.05  # mm or 50 um

        sm = self.stage_manager
        lm = sm.parent
        mask = lm.get_motor('mask')
        attenuator = lm.get_motor('attenuator')
        mask_value, attenuator_value = None, None
        if mask:
            radius = mask.get_discrete_value()
            if not radius:
                radius = 0.05
            mask_value = mask.data_position

        if attenuator:
            attenuator_value = attenuator.data_position

        ptargs = dict(radius=radius,
                      z=sm.get_z(),
                      mask=mask_value,
                      attenuator=attenuator_value,
                      vline_length=0.1, hline_length=0.1)

        if not self.canvas.point_exists():
            self._accept_point(ptargs)
            self.canvas.request_redraw()

    def _get_controls(self):
        pass

    def traits_view(self):
        g = VGroup(
                 Item('accept_point', show_label=False),
                 HGroup(Item('clear'), Item('clear_mode'), show_labels=False),
#                 Item('finish', show_label=False,
#                      enabled_when='mode=="line" and object.is_programming'),
#                 enabled_when='object.is_programming'
                 )

        cg = self._get_controls()
        if cg:
            v = View(cg, g)
        else:
            v = View(g)
        return v

class PointMaker(BaseMaker):
    def _accept_point(self, ptargs):
        npt = self.canvas.new_point(default_color=self.point_color,
                                    **ptargs)

        self.info('added point {}:{:0.5f},{:0.5f} z={:0.5f}'.format(npt.identifier, npt.x, npt.y, npt.z))

class FinishableMaker(BaseMaker):
    finish = Button
#    accept_enabled = Bool(True)

    def _finish_fired(self):
        self.canvas.reset_markup()

    def traits_view(self):
        g = VGroup(
                 Item('accept_point',
#                      enabled_when='accept_enabled',
                      show_label=False),
                 HGroup(Item('clear'), Item('clear_mode'), show_labels=False),
                 Item('finish', show_label=False),
                 )

        cg = self._get_controls()
        if cg:
            v = View(VGroup(cg, g))
        else:
            v = View(g)
        return v

class LineMaker(FinishableMaker):
    velocity = Float

    def _get_controls(self):
        return Item('velocity', label='Velocity mm/min')

    def _accept_point(self, ptargs):
        self.canvas.new_line_point(point_color=self.point_color,
                                           line_color=self.point_color,
                                           velocity=self.velocity,
                                           **ptargs)
class PolygonMaker(FinishableMaker):
    velocity = Float(1.0)
    use_convex_hull = Bool(True)

    def _get_controls(self):
        g = VGroup(Item('velocity', label='Velocity mm/min'),
                   Item('use_convex_hull'))
        return g

    def _save(self):
        polys = dict()
        for i, po in enumerate(self.canvas.polygons):
            pts = []
            for pi in po.points:
                d = dict(identifier=pi.identifier,
                        z=float(pi.z),
                        mask=pi.mask, attenuator=pi.attenuator,
                        xy=[float(pi.x), float(pi.y)])
                pts.append(d)
            polys[str(i)] = dict(velocity=self.velocity, points=pts)

        return {'polygons':polys}

    def _use_convex_hull_changed(self):
        poly = self.canvas.polygons[-1]
        poly.use_convex_hull = self.use_convex_hull
        self.canvas.request_redraw()

    def _accept_point(self, ptargs):
        self.canvas.new_polygon_point(point_color=self.point_color,
                                      line_color=self.point_color,
                                      use_convex_hull=self.use_convex_hull,
                                      **ptargs)
class TransectMaker(FinishableMaker):
    step = Float(1, enter_set=True, auto_set=False)
    def _save(self):
        trans = []
        for tr in self.canvas.transects:
            pts = []
            for pi in tr.points:
                d = dict(identifier=pi.identifier,
                        z=float(pi.z),
                        mask=pi.mask, attenuator=pi.attenuator,
                        xy=[float(pi.x), float(pi.y)])
                pts.append(d)
            trans.append(pts)

        return {'transects':trans}

    def _get_controls(self):
        return Item('step', label='Step (um)')

    def _step_changed(self):
        if self.step:
            self.canvas.set_transect_step(self.step)

    def _accept_point(self, ptargs):
        self.canvas.new_transect_point(point_color=self.point_color,
                               line_color=self.point_color,
                               step=self.step,
                               **ptargs
                               )
#============= EOF =============================================

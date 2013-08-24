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
from traits.api import Array
from chaco.abstract_overlay import AbstractOverlay
from chaco.lineplot import LinePlot
#============= standard library imports ========================
from numpy import array
#============= local library imports  ==========================

class ErrorEnvelopeOverlay(AbstractOverlay):
    _cache_valid = False
    upper = Array
    lower = Array
    def invalidate(self):
        self._cache_valid = False

    def _gather_points(self):
        if not self._cache_valid:
            index = self.component.index
            value = self.component.value
            if not index or not value:
                return

            xs = index.get_data()
            ls = self.lower
            us = self.upper
#             ys = value.get_data()

#             print array((xs, us)).T
#             print self.component._cached_data_pts
            self._cached_data_pts_u = [array((xs, us)).T]
            self._cached_data_pts_l = [array((xs, ls)).T]

            self._cache_valid = True

        return

    def get_screen_points(self):
        self._gather_points()
        return (self.component.map_screen(self._cached_data_pts_u),
                    self.component.map_screen(self._cached_data_pts_l))

    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        with gc:
            gc.clip_to_rect(0, 0, self.component.width, self.component.height)
            upts, lpts = self.get_screen_points()
            gc.set_line_dash((5, 5))
            gc.set_stroke_color((1, 0, 0))
            LinePlot._render_normal(gc, upts, '')
            LinePlot._render_normal(gc, lpts, '')

#============= EOF =============================================

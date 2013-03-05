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
from src.machine_vision.convex_hull import convex_hull_area
# def cached_property(function):
#    name = '{}_cache'.format(function.__name__)
#    def decorator(self):
#        result = self.__dict__.get(name, None)
#        if result is None:
#            self.__dict__[name] = result = function()
#        return result
#
#    return decorator
#============= enthought library imports =======================
from traits.api import HasTraits, cached_property, Property
#============= standard library imports ========================
#============= local library imports  ==========================

class Target(HasTraits):
    centroid_value = None
    poly_points = None
    bounding_rect = None
    threshold = None
    area = None
    convexity = Property

    @property
    def dev_centroid(self):
        return ((self.origin[0] - self.centroid_value[0]),
                (self.origin[1] - self.centroid_value[1]))

    @property
    def dev_br(self):
        return ((self.origin[0] - self.bounding_rect[0]),
                (self.origin[1] - self.bounding_rect[1]))

    @property
    def aspect_ratio(self):
        return self.bounding_rect.width / float(self.bounding_rect.height)

    @property
    def bounding_area(self):
        return self.bounding_rect.width * self.bounding_rect.height

    @cached_property
    def _get_convexity(self):
        return self.area / convex_hull_area(self.poly_points)
#============= EOF =============================================

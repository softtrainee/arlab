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

#============= standard library imports ========================
#============= local library imports  ==========================

class Target(object):
    centroid_value = None
    poly_points = None
    bounding_rect = None
    threshold = None
    area = None

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

#============= EOF =============================================

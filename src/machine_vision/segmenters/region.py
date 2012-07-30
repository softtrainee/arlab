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
from traits.api import HasTraits, Int, Property, Bool
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import zeros_like, invert
from skimage.filter import sobel, threshold_adaptive
from skimage.morphology import watershed
#============= local library imports  ==========================
from src.machine_vision.segmenters.base import BaseSegmenter

class RegionSegmenter(BaseSegmenter):
    threshold_low = Property(Int, depends_on='threshold_width,threshold_tries,threshold_base')
    threshold_high = Property(Int, depends_on='threshold_width,threshold_tries,threshold_base')

    threshold_width = Int(5)
    threshold_tries = Int(4)
    threshold_base = Int(125)
    count = Int(1)

    use_adaptive_threshold = Bool(True)
    def traits_view(self):
        return View(
                    Item('threshold_width', label='Width'),
                    Item('threshold_tries', label='N.'),
                    Item('threshold_base', label='Base'),
                    Item('threshold_low', style='readonly'),
                    Item('threshold_high', style='readonly')
                    )

    def segment(self, src):

        ndsrc = src.ndarray[:]

        markers = zeros_like(ndsrc)
        if self.use_adaptive_threshold:
            block_size = 40
            markers = threshold_adaptive(ndsrc, block_size) * 255
            markers[markers < 1] = 1
        else:
            markers[ndsrc < self.threshold_low] = 1
            markers[ndsrc > self.threshold_high] = 255

        el_map = sobel(ndsrc)
        wsrc = watershed(el_map, markers)
        return invert(wsrc)

#===============================================================================
# property get/set
#===============================================================================

    def _get_threshold_high(self):
        return min(255, self.threshold_base + (self.threshold_width * self.count))
    def _get_threshold_low(self):
        return max(0, self.threshold_base - (self.threshold_width * self.count))
#============= EOF =============================================

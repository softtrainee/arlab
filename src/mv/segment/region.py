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
from traits.api import HasTraits, Bool
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import zeros_like, invert
from skimage.filter import sobel, threshold_adaptive
from skimage.morphology import watershed
#============= local library imports  ==========================
from src.mv.segment.base import BaseSegmenter

class RegionSegmenter(BaseSegmenter):
    use_adaptive_threshold = Bool(False)
    threshold_low = 0
    threshold_high = 255
    def segment(self, src):
        image = src.ndarray[:]
        if self.use_adaptive_threshold:
            block_size = 25
            markers = threshold_adaptive(image, block_size) * 255
            markers = invert(markers)

        else:
            markers = zeros_like(image)
            markers[image < self.threshold_low] = 1
            markers[image > self.threshold_high] = 255

        elmap = sobel(image, mask=image)
        wsrc = watershed(elmap, markers, mask=image)
        return invert(wsrc)
#        elmap = ndimage.distance_transform_edt(image)
#        local_maxi = is_local_maximum(elmap, image,
#                                      ones((3, 3))
#                                      )
#        markers = ndimage.label(local_maxi)[0]
#        wsrc = watershed(-elmap, markers, mask=image)
#        fwsrc = ndimage.binary_fill_holes(out)
#        return wsrc
#        if self.use_inverted_image:
#            out = invert(wsrc)
#        else:
#            out = wsrc

#        time.sleep(1)
#        do_later(lambda:self.show_image(image, -elmap, out))
#        return out
#============= EOF =============================================

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
from numpy import zeros_like, invert, percentile, ones_like, asarray
from skimage.filter import sobel, threshold_adaptive
from skimage.morphology import watershed
#============= local library imports  ==========================
from src.mv.segment.base import BaseSegmenter
# from skimage.exposure.exposure import rescale_intensity
# from scipy.ndimage.morphology import binary_closing

cnt = 0
class RegionSegmenter(BaseSegmenter):
    use_adaptive_threshold = Bool(True)
    threshold_low = 0
    threshold_high = 255
    block_size = 20

    def segment(self, src):
        '''
            src: preprocessing cv.Mat
        '''
#        image = src.ndarray[:]
#         image = asarray(src)
        image = src[:]
        if self.use_adaptive_threshold:
#            block_size = 25
            markers = threshold_adaptive(image, self.block_size)

            n = markers[:].astype('uint8')
            n[markers == True] = 255
            n[markers == False] = 1
            markers = n
#            print markers
#            markers = markers.astype('uint8')
#            n = ones_like(markers)
#            n[markers] = 255
#            print n
#            markers[markers] = 255
#            markers[not markers] = 1
#            print markers
#            markers = n.astype('uint8')
#            markers = invert(markers).astype('uint8')

        else:
            markers = zeros_like(image)
            markers[image < self.threshold_low] = 1
            markers[image > self.threshold_high] = 255

#        global cnt
#        # remove holes
#        if cnt % 2 == 0:
#            markers = binary_closing(markers).astype('uint8') * 255
#        cnt += 1
#        print markers
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

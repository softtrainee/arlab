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
from traits.api import Int, Property, Bool
from traitsui.api import View, Item
#============= standard library imports ========================
from numpy import zeros_like, invert
from skimage.filter import sobel, threshold_adaptive
from skimage.morphology import watershed
#============= local library imports  ==========================
from src.machine_vision.segmenters.base import BaseSegmenter
from scipy import ndimage
from pyface.timer.do_later import do_later
import time
show = True
class RegionSegmenter(BaseSegmenter):
    threshold_low = Property(Int, depends_on='threshold_width,threshold_tries,threshold_base')
    threshold_high = Property(Int, depends_on='threshold_width,threshold_tries,threshold_base')

    threshold_width = Int(5)
    threshold_tries = Int(50)
    threshold_base = Int(120)
    count = Int(1)

    use_adaptive_threshold = Bool(True)
#    use_inverted_image = Bool(False)
    use_inverted_image = Bool(True)
#    use_adaptive_threshold = Bool(False)
    def traits_view(self):
        return View(
                    Item('threshold_width', label='Width'),
                    Item('threshold_tries', label='N.'),
                    Item('threshold_base', label='Base'),
                    Item('threshold_low', style='readonly'),
                    Item('threshold_high', style='readonly')
                    )

    def segment(self, src):
        image = src.ndarray[:]
        if self.use_adaptive_threshold:
            block_size = 25
            markers = threshold_adaptive(image, block_size) * 255
            markers = invert(markers)

        else:
#            print self.threshold_low, self.threshold_high
            markers = zeros_like(image)
            markers[image < self.threshold_low] = 1
            markers[image > self.threshold_high] = 255

        elmap = sobel(image, mask=image)
        wsrc = watershed(elmap, markers, mask=image)

#        elmap = ndimage.distance_transform_edt(image)
#        local_maxi = is_local_maximum(elmap, image,
#                                      ones((3, 3))
#                                      )
#        markers = ndimage.label(local_maxi)[0]
#        wsrc = watershed(-elmap, markers, mask=image)
#        fwsrc = ndimage.binary_fill_holes(out)
#        return wsrc
        if self.use_inverted_image:
            out = invert(wsrc)
        else:
            out = wsrc

#        time.sleep(1)
#        do_later(lambda:self.show_image(image, -elmap, out))
        return out

    def show_image(self, image, elmap, out):
        global show
        if show:
            import matplotlib.pyplot as plt
            fig, axes = plt.subplots(ncols=3, figsize=(8, 2.7))
            ax0, ax1, ax2 = axes

            ax0.imshow(image, cmap=plt.cm.gray, interpolation='nearest')
            ax1.imshow(elmap, cmap=plt.cm.jet, interpolation='nearest')
            ax2.imshow(out, cmap=plt.cm.gray, interpolation='nearest')

            for ax in axes:
                ax.axis('off')

            plt.subplots_adjust(hspace=0.01, wspace=0.01, top=1, bottom=0, left=0,
                            right=1)
            plt.show()
            show = False
#    def segment(self, src):
#        image = src.ndarray[:]
#        image = invert(image)
#
#        markers = zeros_like(image)
#        markers[image < self.threshold_low] = 0
#        markers[image > self.threshold_high] = 1
##        image = markers
##        if self.use_adaptive_threshold:
#        block_size = image.shape[0]
#        image = threshold_adaptive(image, block_size)
##        markers[markers < 1] = 1
##        image = markers
##        else:
#
##        import numpy as np
##        x, y = np.indices((80, 80))
##        x1, y1, x2, y2 = 28, 28, 44, 52
##        r1, r2 = 16, 20
##        mask_circle1 = (x - x1) ** 2 + (y - y1) ** 2 < r1 ** 2
##        mask_circle2 = (x - x2) ** 2 + (y - y2) ** 2 < r2 ** 2
##        fimage = np.logical_or(mask_circle1, mask_circle2)
##        print fimage.shape, image.shape
##        image = invert(image)
#
#        distance = ndimage.distance_transform_edt(image)
#        local_maxi = is_local_maximum(distance, image,
##                                      ones((5, 5))
#                                      )
#        markers = ndimage.label(local_maxi)[0]
#        wsrc = watershed(-distance, markers,
#                          mask=image
#                         )
#
#        values, bins = histogram(wsrc)
#        ind = argmax(values)
#        bi = bins[ind]
#        if not bi:
#            values = delete(values, ind)
#            bi = bins[argmax(values)]
#
#        mi = ma = bi
#        nimage = zeros_like(wsrc)
##        wsrc[wsrc < ma] = 0
#        nimage[wsrc > mi] = 255
#        nimage[wsrc > ma + 1] = 0
#
#
#        wsrc = nimage
##        el_map = sobel(image)
##        wsrc = watershed(el_map, markers)
#
#        global show
#        if show:
#            import matplotlib.pyplot as plt
#            fig, axes = plt.subplots(ncols=3, figsize=(8, 2.7))
#            ax0, ax1, ax2 = axes
#
#            ax0.imshow(image, cmap=plt.cm.gray, interpolation='nearest')
#            ax1.imshow(-distance, cmap=plt.cm.jet, interpolation='nearest')
#            ax2.imshow(wsrc, cmap=plt.cm.gray, interpolation='nearest')
#
#            for ax in axes:
#                ax.axis('off')
#
#            plt.subplots_adjust(hspace=0.01, wspace=0.01, top=1, bottom=0, left=0,
#                            right=1)
#            plt.show()
#            show = False
#
#        return wsrc
##        return invert(wsrc)

#===============================================================================
# property get/set
#===============================================================================

    def _get_threshold_high(self):
        return min(255, self.threshold_base + (self.threshold_width * self.count))
    def _get_threshold_low(self):
        return max(0, self.threshold_base - (self.threshold_width * self.count))
#============= EOF =============================================

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
from traits.api import HasTraits
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================
from numpy import invert, pi, percentile
from skimage.draw import circle

class LumenDetector(HasTraits):
    threshold = 100
    mask_radius = 25
    def get_value(self, src):
        self._preprocess(src)
        mask = self._mask(src)

        lum = src[mask]
        # use mean of the 90th percentile as lumen
        # measure. this is adhoc and should/could be modified
        d = lum.flatten()
        d = percentile(d, 99)
        lumen = d.mean()


#         area_mask = pi * self.mask_radius ** 2

        # normalize to area
#         nlumens = spx_mask / area_mask
        return lumen

    def _mask(self, src):
        r = self.mask_radius
        h, w = src.shape

        mask = circle(w / 2., h / 2., r)
        src[invert(mask)] = 0
        return mask

    def _preprocess(self, src):
        threshold = self.threshold
        src[src < threshold] = 0




#============= EOF =============================================

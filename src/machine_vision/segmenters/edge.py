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
from traits.api import HasTraits, Int, Property, Range
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import zeros_like, invert, asarray
from scipy import ndimage
from skimage.filter import canny
#from skimage.morphology import closing, square
#============= local library imports  ==========================

class EdgeSegmenter(HasTraits):
    #canny parameters
    canny_low_threshold = Range(0, 1., 0.06)
    canny_high_threshold = Range(0, 1., 0.16)
    canny_sigma = Int(5)
    def segment(self, src):


        ndsrc = src.ndarray / 255.
        edges = canny(ndsrc,
                      low_threshold=self.canny_low_threshold,
                      high_threshold=self.canny_high_threshold,
                      sigma=self.canny_sigma)
        filled = ndimage.binary_fill_holes(edges)
        filled = invert(filled) * 255
#        label_objects, _ = ndimage.label(filled)
#        sizes = bincount(label_objects.ravel())
#
#        mask_sizes = sizes > 1
#        mask_sizes[0] = 0
#        cleaned = mask_sizes[label_objects]
#        cleaned = asarray(cleaned, 'uint8')
#        cleaned = closing(cleaned, square(5))

#        self._locate_helper(invert(cleaned), **kw)
        nsrc = asarray(filled, 'uint8')
        return nsrc


#===============================================================================
# property get/set
#===============================================================================


#============= EOF =============================================

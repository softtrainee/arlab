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
from traits.api import Int
#============= standard library imports ========================
from src.image.cvwrapper import threshold
# from skimage.morphology import closing, square
#============= local library imports  ==========================
from src.machine_vision.segmenters.base import BaseSegmenter

class ThresholdSegmenter(BaseSegmenter):
    threshold = Int(125)
    def segment(self, src):
        return threshold(src, self.threshold)
#        start = self.start_threshold_search_value
#        end = start + self.threshold_search_width
#        expand_value = self.threshold_expansion_scalar
#
#        for i in range(self.threshold_tries):
#            s = start - i * expand_value
#            e = end + i * expand_value
# #            self.info('searching... thresholding image {} - {}'.format(s,
# #                                                                       e))
#            targets = []
#            for ti in range(s, e):
#                tsrc = threshold(src, ti)
#
#                targets = self._locate_targets(tsrc, **kw)
# #                self.permutations.append((ts, test))
#
# #                if ts:
# #                    targets += ts
#            self._threshold_start = s
#            self._threshold_end = e
#            return targets

#===============================================================================
# property get/set
#===============================================================================


#============= EOF =============================================

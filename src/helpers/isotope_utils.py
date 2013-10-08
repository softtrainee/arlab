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
import re
from src.constants import DETECTOR_MAP


def rank_func(x):
    if isinstance(x, (list, tuple)):
        x = x[0]
    return re.sub('\D', '', x)


def sort_isotopes(keys, reverse=True):
    return sorted(list(keys), key=rank_func, reverse=reverse)


def sort_detectors(idets):
    dets = ['', ] * len(idets)
    edets = []
    for det in idets:
        if det in DETECTOR_MAP:
            dets[DETECTOR_MAP[det]] = det
        else:
            edets.append(det)

    dets.extend(edets)
    return dets

#============= EOF =============================================

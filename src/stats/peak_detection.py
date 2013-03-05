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
from numpy import asarray, arange, Inf, NaN, array
#============= local library imports  ==========================


def find_peaks(v, delta, x=None):
    '''
     Eli Billauer, 3.4.05 (Explicitly not copyrighted).

     This function is released to the public domain; Any use is allowed.
    '''
    if x is None:
        x = arange(len(v))

    v = asarray(v)

    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN
    lookformax = True
    maxs = []
    mins = []
    for vi, xi in zip(v, x):
        if vi > mx:
            mx = vi
            mxpos = xi
        elif vi < mn:
            mn = vi
            mnpos = xi

        if lookformax:
            if vi < mx - delta:
                maxs.append((mxpos, mx))
                mn = vi
                mnpos = xi
                lookformax = False
        else:
            if vi > mn + delta:
                mins.append((mnpos, mn))
                mx = vi
                mxpos = xi
                lookformax = False
    return array(maxs), array(mins)
#============= EOF =============================================

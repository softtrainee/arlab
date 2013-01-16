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
from numpy import asarray
#============= local library imports  ==========================



def calculate_mswd(x, errs):

    mswd_w = 0
    if len(x) >= 2:
        x = asarray(x)
        errs = asarray(errs)

    #    xmean_u = x.mean()    
        xmean_w, _err = calculate_weighted_mean(x, errs)

        ssw = (x - xmean_w) ** 2 / errs ** 2
    #    ssu = (x - xmean_u) ** 2 / errs ** 2

        d = 1.0 / (len(x) - 1)
        mswd_w = d * ssw.sum()
    #    mswd_u = d * ssu.sum()

    return mswd_w

def calculate_weighted_mean(x, errs, error=0):
    x = asarray(x)
    errs = asarray(errs)

    weights = asarray(map(lambda e: 1 / e ** 2, errs))

    wtot = weights.sum()
    wmean = (weights * x).sum() / wtot

    if error == 0:
        werr = wtot ** -0.5
    elif error == 1:
        werr = 1
    return wmean, werr

def validate_mswd(n, mswd):
    '''
         is mswd acceptable based on Mahon 
    '''
    if n > 30:
        table = {
           1:(0, 0),
           2:(0, 0),
           3:(0, 0),
           4:(0, 0),
           5:(0, 0),
           6:(0, 0),
           7:(0, 0),
           8:(0, 0),
           9:(0, 0),
           10:(0, 0),
           11:(0, 0),
           12:(0, 0),
           13:(0, 0),
           14:(0, 0),
           15:(0, 0),
           16:(0, 0),
           17:(0, 0),
           18:(0, 0),
           19:(0, 0),
           20:(0, 0),
           21:(0, 0),
           22:(0, 0),
           23:(0, 0),
           24:(0, 0),
           25:(0, 0),
           26:(0, 0),
           27:(0, 0),
           28:(0, 0),
           29:(0, 0),
           30:(0, 0),
           }
        low, high = table[n]
    else:
        low, high = (0, 0)

    return low <= mswd <= high
#============= EOF =============================================

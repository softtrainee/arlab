#===============================================================================
# Copyright 2011 Jake Ross
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



from numpy import asarray

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

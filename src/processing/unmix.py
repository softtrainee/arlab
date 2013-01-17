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
import numpy as np
#============= standard library imports ========================
#============= local library imports  ==========================

def unmix(ages, errors):
    ages_errors = zip(ages, errors)

    pis = [0.5, 0.5]
    ts = [10, 20]

    niterations = 5
    for _ in range(niterations):
        tis_n = []
        pis_n = []
        for pi, tj in zip(pis, ts):
            pn, tn = _unmix(ages_errors, pi, tj, pis, ts)
            tis_n.append(tn)
            pis_n.append(pn)
        pis = pis_n
        ts = tis_n


def _unmix(ages_errors, pi_j_o, tj_o, pis, ts):
    n = len(ages_errors)
    s = sum([pi_j_o * fij(ai_ei, tj_o) / Si(pis, ai_ei, ts)
                  for ai_ei in ages_errors])

    pi_j = 1 / float(n) * s

    a = sum([pi_j_o * ai_ei[0] * fij(ai_ei, tj_o) / ai_ei[1] ** 2 * Si(pis, ai_ei, ts)
             for ai_ei in ages_errors])
    b = sum([pi_j_o * fij(ai_ei, tj_o) / ai_ei[1] ** 2 * Si(pis, ai_ei, ts)
             for ai_ei in ages_errors])
    tj = a / b
    return pi_j, tj

def fij(ai_ei, tj):
    ai, ei = ai_ei
    return 1 / (ei * (2 * np.pi) ** 0.5) * np.exp(-(ai - tj) ** 2 / (2 * ei ** 2))

def Si(pis, ai_ei, ts, nc):
    return sum([pik * fij(ai_ei, tk) for pik, tk in zip(pis, ts)])

#============= EOF =============================================

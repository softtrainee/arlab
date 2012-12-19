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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
from numpy import linspace, apply_along_axis, sign, roll, where, Inf
from src.regression.ols_regressor import OLSRegressor
#============= standard library imports ========================
#============= local library imports  ==========================

class YorkRegressor(OLSRegressor):
    def _set_degree(self, d):
        '''
            York regressor only for linear fit
        '''
        self._degree = 1

    def predict(self, x):
        '''
            based on 
             "Linear least-squares fits with errors in both coordinates", 
             Am. J. Phys 57 #7 p. 642 (1989) by B.C. Reed
        '''
        xs = self.xs
        ys = self.ys
        Wx = 1 / self.xserr ** 2
        Wy = 1 / self.yserr ** 2

        def f(mi):
            W = Wx * Wy / (mi ** 2 * Wy + Wx)

            _x_ = sum(W * self.xs) / sum(W)
            _y_ = sum(W * self.ys) / sum(W)
            U = self.xs - _x_
            V = self.ys - _y_

            suma = sum(W ** 2 * U * V / Wx)
            S = sum(W ** 2 * U ** 2 / Wx)

            a = (2 * suma) / (3 * S)

            sumB = sum(W ** 2 * V ** 2 / Wx)
            B = (sumB - sum(W * U ** 2)) / (3 * S)

            g = -sum(W * U * V) / S

            slope = mi ** 3 - 3 * a * mi ** 2 - 3 * B * mi - g
            intercept = _y_ - m * _x_
            return slope, intercept

        #get a starting slope
        m = self.coefficients[0]

        for i in range(10):
            #evaluate f(m) for m-n, m+n and find the roots
            n = 1 / float(i)
            ms = linspace(m - n, m + n, 100)
            fs, cs = apply_along_axis(f, 0, ms)

            #find roots
            #find where fs crosses zero line
            asign = sign(fs)
            signchange = ((roll(asign, 1) - asign) != 0).astype(int)

            roots = where(signchange == 1)[0]

            ss_min = Inf
            #find root that minminzes ss_resid
            for ri in roots:
                m, c = fs[ri], cs[ri]
                W = Wx * Wy / (ri ** 2 * Wy + Wx)
                ss = sum(W * ys - c - ri * xs)
                if ss < ss_min:
                    ss_min = ss
                    ri_min = ri

            #do f(m) around ri_min with tighter bounds
            m = ri_min

#============= EOF =============================================

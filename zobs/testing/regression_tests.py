# @PydevCodeAnalysisIgnore
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
import numpy as np
import unittest
#============= local library imports  ==========================
from src.regression.ols_regressor import PolynomialRegressor

class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.xs = np.linspace(0, 10)

    def test_LinearRegressor(self):
        a, b = 3, 4
        x = self.xs
        ys = a * x + b
        r = PolynomialRegressor(xs=x, ys=ys, fit='linear')
        ra, rb = r.coefficients
#
        self.assertAlmostEqual(a, ra)
        self.assertAlmostEqual(b, rb)

    def test_ParabolicRegressor(self):
        a, b, c = 3, 4, 5
        x = self.xs
        ys = x * (a * x + b) + c

        r = PolynomialRegressor(xs=x, ys=ys, fit='parabolic')
        ra, rb, rc = r.coefficients
        self.assertAlmostEqual(a, ra)
        self.assertAlmostEqual(b, rb)
        self.assertAlmostEqual(c, rc)

    def test_CubicRegressor(self):
        a, b, c, d = 3, 4, 5, 6
        x = self.xs
        ys = x * (a * x * x + b * x + c) + d

        r = PolynomialRegressor(xs=x, ys=ys, fit='cubic')
        ra, rb, rc, rd = r.coefficients
        self.assertAlmostEqual(a, ra)
        self.assertAlmostEqual(b, rb)
        self.assertAlmostEqual(c, rc)
        self.assertAlmostEqual(d, rd)




#============= EOF =============================================

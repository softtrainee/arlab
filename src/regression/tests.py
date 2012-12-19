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
#from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from unittest import TestCase
import numpy as np
from src.regression.mean_regressor import WeightedMeanRegressor
from src.regression.ols_regressor import PolynomialRegressor
from src.regression.wls_regressor import WeightedPolynominalRegressor
#============= local library imports  ==========================

class WeightedMeanRegressionTest(TestCase):
    def setUp(self):
        n = 1000
        ys = np.ones(n) * 5
#        es = np.random.rand(n)
        es = np.ones(n)
        ys = np.hstack((ys, [5.1]))
        es = np.hstack((es, [1000]))
#        print es
        self.reg = WeightedMeanRegressor(ys=ys, errors=es)

#    def testMean(self):
#        m = self.reg.mean
#        self.assertEqual(m, 5)

class RegressionTest(TestCase):
    def setUp(self):
        self.x = np.array([1, 2, 3, 4, 4, 5, 5, 6, 6, 7])
        self.y = np.array([7, 8, 9, 8, 9, 11, 10, 13, 14, 13])

    def testMeans(self):
        xm = self.x.mean()
        ym = self.y.mean()
        self.assertEqual(xm, 4.3)
        self.assertEqual(ym, 10.2)

class CITest(TestCase):
    def setUp(self):
        self.x = np.array([0, 12, 29.5, 43, 53, 62.5, 75.5, 85, 93])
        self.y = np.array([8.98, 8.14, 6.67, 6.08, 5.9, 5.83, 4.68, 4.2, 3.72])

    def testUpper(self):
        reg = PolynomialRegressor(xs=self.x, ys=self.y, degree=1)
        l, u = reg.calculate_ci([0, 10, 100])
        for ui, ti in zip(u, [9.16, 8.56, 3.83]):
            self.assertAlmostEqual(ui, ti, delta=0.01)

    def testLower(self):
        reg = PolynomialRegressor(xs=self.x, ys=self.y, degree=1)
        l, u = reg.calculate_ci([0])

        self.assertAlmostEqual(l[0], 8.25, delta=0.01)

    def testSYX(self):
        reg = PolynomialRegressor(xs=self.x, ys=self.y, degree=1)
        self.assertAlmostEqual(reg.syx, 0.297, delta=0.01)

    def testSSX(self):
        reg = PolynomialRegressor(xs=self.x, ys=self.y, degree=1)
        self.assertAlmostEqual(reg.ssx, 8301.389, delta=0.01)

class WLSRegressionTest(TestCase):
    def setUp(self):
        self.xs = np.linspace(0, 10, 10)
        self.ys = np.random.normal(self.xs, 1)

    def testPredict(self):
        xs = self.xs
        ys = self.ys
        es = np.random.normal(1, 0.5, len(xs))
        wls = WeightedPolynominalRegressor(xs=xs, ys=ys, yserr=es, fit='linear')

class OLSRegressionTest(TestCase):
    def setUp(self):
        self.xs = np.linspace(0, 10, 10)
        self.ys = np.random.normal(self.xs, 1)

    def testPredict(self):
        xs = self.xs
        ys = self.ys
        ols = PolynomialRegressor(xs=xs, ys=ys, fit='linear')
        y = ols.predict_error(5)[0]
        y1 = ols.predict_error1(5, error_calc='sd')[0]
        print y, y1
        self.assertEqual(y, y1)
#============= EOF =============================================

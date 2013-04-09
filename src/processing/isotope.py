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
from traits.api import HasTraits, Str, Float, Property, Any, Instance, \
    Bool, Int, Array, cached_property
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from uncertainties import ufloat
from numpy import array, delete
from src.regression.mean_regressor import MeanRegressor
from src.regression.ols_regressor import PolynomialRegressor
import struct
#============= local library imports  ==========================
class IsotopicMeasurement(HasTraits):
    dbrecord = Any
    dbresult = Any

    name = Str
    mass = Float
    detector = Str

    uvalue = Property(depends='value, error, _value, _error')
    value = Property(depends_on='_value,fit')
    error = Property(depends_on='_error,fit')
    _value = Float
    _error = Float

    fit = Str
    filter_outliers = Bool
    filter_outlier_iterations = Int
    filter_outlier_std_devs = Int

    xs = Array
    ys = Array
    regressor = Property(depends_on='xs,ys,fit')

    def __init__(self, *args, **kw):
        super(IsotopicMeasurement, self).__init__(*args, **kw)

        if self.dbresult:
            self._value = self.dbresult.signal_
            self._error = self.dbresult.signal_err

        if self.dbrecord:
            xs, ys = self._unpack_blob(self.dbrecord.signals[-1].data)
            self.xs = array(xs)
            self.ys = array(ys)

    def set_fit(self, fit):
        if fit is not None:
            self.fit = fit.fit
            self.filter_outliers = bool(fit.filter_outliers)
            try:
                self.filter_outlier_iterations = int(fit.filter_outlier_iterations)  # if fit.filter_outliers_iterations else 0
            except TypeError, e:
                pass
#                print '{}. fit.filter_outlier_iterations'.format(e)

            try:
                self.filter_outlier_std_devs = int(fit.filter_outlier_std_devs)  # if fit.filter_outliers_std_devs else 0
            except TypeError, e:
                pass
#                print '{}. fit.filter_outlier_std_devs'.format(e)

    def set_uvalue(self, v):
        if isinstance(v, tuple):
            self._value, self._error = v
        else:
            self._value = v.nominal_value
            self._error = v.std_dev()

    def _mean_regressor_factory(self):
        reg = MeanRegressor(xs=self.xs, ys=self.ys)
        return reg

    def _unpack_blob(self, blob, endianness='>'):
        return zip(*[struct.unpack('{}ff'.format(endianness), blob[i:i + 8]) for i in xrange(0, len(blob), 8)])

    def _set_error(self, v):
        self._error = v

    def _set_value(self, v):
        self._value = v

    @cached_property
    def _get_value(self):
        if self.xs is not None and len(self.xs) > 1:  # and self.ys is not None:
#            if len(self.xs) > 2 and len(self.ys) > 2:
#            print self.xs
#            print self._get_regression_param('coefficients')
#            return self._get_regression_param('coefficients')
            return self.regressor.predict(0)
        else:
            return self._value

    @cached_property
    def _get_error(self):
        if self.xs is not None and len(self.xs) > 1:
#            if len(self.xs) > 2 and len(self.ys) > 2:
            return self.regressor.predict_error(0)
#            return self._get_regression_param('coefficient_errors')
        else:
            return self._error

    @cached_property
    def _get_regressor(self):
        try:
            if 'average' in self.fit.lower():
                reg = self._mean_regressor_factory()
#                if self.es:
#                    reg = WeightedMeanRegressor(xs=self.xs, ys=self.ys, errors=self.es)
#                else:
#                    reg = MeanRegressor(xs=self.xs, ys=self.ys)
            else:
                reg = PolynomialRegressor(xs=self.xs, ys=self.ys, degree=self.fit)

        except Exception, e:
            reg = PolynomialRegressor(xs=self.xs, ys=self.ys, degree=self.fit)

        if self.filter_outliers:
            for _ in range(self.filter_outlier_iterations):
                excludes = list(reg.calculate_outliers(nsigma=self.filter_outlier_std_devs))
                xs = delete(self.xs, excludes, 0)
                ys = delete(self.ys, excludes, 0)
                reg.trait_set(xs=xs, ys=ys)

        return reg

    @cached_property
    def _get_uvalue(self):
        return ufloat((self.value, self.error))
#===============================================================================
# arthmetic
#===============================================================================
    def __add__(self, a):
        return self.uvalue + a
    def __radd__(self, a):
        return self.__add__(a)

    def __mul__(self, a):
        return self.uvalue * a
    def __rmul__(self, a):
        return self.__mul__(a)

    def __sub__(self, a):
        return self.uvalue - a
    def __rsub__(self, a):
#        return self.uvalue - a
        return a - self.uvalue

    def __div__(self, a):
        return self.uvalue / a
    def __rdiv__(self, a):
#        return self.uvalue / a
        return a / self.uvalue

class CorrectionIsotopicMeasurement(IsotopicMeasurement):
    def __init__(self, *args, **kw):
        super(IsotopicMeasurement, self).__init__(*args, **kw)
        if self.dbrecord:
            self._value = self.dbrecord.user_value
            self._error = self.dbrecord.user_error

class Background(CorrectionIsotopicMeasurement):
    pass

class Blank(CorrectionIsotopicMeasurement):
    pass

class Baseline(IsotopicMeasurement):
    _kind = 'baseline'

class Isotope(IsotopicMeasurement):
    _kind = 'signal'

    baseline = Instance(Baseline, ())
    blank = Instance(Blank, ())
    background = Instance(Background, ())
    def baseline_corrected_value(self):
        return self.uvalue - self.baseline.uvalue

    def get_corrected_value(self):
        return self.uvalue - self.baseline.uvalue - self.blank.uvalue - self.background.uvalue
#============= EOF =============================================

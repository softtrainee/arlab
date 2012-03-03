'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================
#from traits.api import HasTraits, Instance, DelegatesTo, String, Float
#from traitsui.api import View, Item, Group, HGroup
import math
#=============standard library imports ========================
from numpy import poly1d, array, polyfit, \
    linspace, std, vstack, polyval, mean, ones, sqrt, diagonal, exp, min, max
#import numpy.linalg as la

from tinv import tinv
#from scipy.stats import linregress
from ols import OLS
#=============local library imports  ==========================
class RegressorError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class Regressor(object):
    '''
    '''
    interpolatefactor = 1.0
    def get_value(self, kind, data, x):
        '''
            kind=linear, parabolic etc
            data= 2D array of values [xvalues, yvalues]
        '''
        func = getattr(self, kind)
        rdict = func(*data)
        return polyval(rdict['coefficients'], x)


    def calc_residuals(self, x, y, xd, yd, kind, **kw):
        '''

        '''
        res = []
        args = self._regress_(xd, yd, kind, **kw)
        if args:

            coeffs = args['coefficients']
            if coeffs is not None:
                for xi, yi in vstack((x, y)).transpose():
                    res.append(poly1d(coeffs)(xi) - yi)

        return array(res)


    def cubic(self, x, y, **kw):
        '''

        '''
        return self._regress_(x, y, 'cubic', **kw)

    def parabolic(self, x, y, **kw):
        '''
    
        '''
        return self._regress_(x, y, 'parabolic', **kw)

    def average(self, x, y, **kw):
        '''
    
        '''
        return self._regress_(x, y, 'average', **kw)

    def linear(self, x, y, **kw):
        '''
        '''
        return self._regress_(x, y, 'linear', **kw)

    def exponential(self, x, y, **kw):

        ff = lambda p, x:p[0] * exp(p[1] * x)
        ef = lambda p, x, y: ff(p, x) - y

        kw['fitfunc'] = ff
        kw['errfunc'] = ef

        #do a linear fit first to estimate the initial guess
        #p0=[intercept, slope]

        r = self.linear(x, y)
        slope, intercept = r['coefficients']
        kw['p0'] = [intercept, slope]

        args = self.least_squares(x, y, **kw)

        return args

    def least_squares(self, x, y, **kw):
        return self._regress_(x, y, 'least_squares', **kw)

    def weighted_least_squares(self, x, y, **kw):
        return self._regress_(x, y, 'weighted_least_squares', **kw)

    def get_degree(self, kind):
        degree = None
        if kind == 'linear':
            degree = 1
        elif kind == 'parabolic':
            degree = 2
        elif kind == 'cubic':
            degree = 3
        elif kind == 'average':
            degree = 0
        return degree

    def _regress_(self, x, y, kind, data_range=None, npts=None, **kw):
        '''

        '''
        x = array(x)
        y = array(y)

        dr = data_range
        if dr is None:
            dr = [min(x), max(x)]

        yreturn = []
        coeffs = None
        coeff_errors = []

        n = len(y)
        stats = None
        if n > 2:
            stddev = std(y)
            stderr = stddev / math.sqrt(n)

            sample_stddev = std(y, ddof=1)

            stderr_mean = stddev / math.sqrt(n - 1)

            stats = dict(stddev=stddev,
                       sample_stddev=sample_stddev,
                       stderr=stderr,
                       stderr_mean=stderr_mean
                       )

        if npts is None:
            npts = 5 * len(x)
        xreturn = linspace(dr[0], dr[1], npts)

        ucly = []
        lcly = []
        degree = self.get_degree(kind)
        if degree == 0:
            a = mean(y)
            coeffs = [a]
            yreturn = ones(len(xreturn)) * a
            model = ones(len(x)) * a

            stats['r_squared'] = self.calc_r_squared(y, model)

            use_stderr = kw['use_stderr'] if 'use_stderr' in kw else False
            if use_stderr:
                lc = a - stderr_mean
                uc = a + stderr_mean
                coeff_errors = [stderr_mean]
            else:
                lc = a - sample_stddev
                uc = a + sample_stddev
                coeff_errors = [sample_stddev]

            lcly = array(ones(len(xreturn)) * lc)
            ucly = array(ones(len(xreturn)) * uc)
        elif kind in ['least_squares', 'weighted_least_squares']:
            from scipy import  optimize
            try:
                errfunc = kw['errfunc']
            except KeyError:
                raise RegressorError('no errfunc specified')

            try:
                fitfunc = kw['fitfunc']
            except KeyError:
                raise RegressorError('no fitfunc specified')

            if kind == 'weighted_least_squares':
                try:
                    fiterrdata = kw['fiterrdata']
                except KeyError:
                    raise RegressorError('no fiterrdata specified')

            try:
                p0 = kw['p0']
            except KeyError:
                raise RegressorError('no initial guess specified')

            if kind == 'least_squares':
                coeffs, cov_params, _infodict, _msg, ier = optimize.leastsq(errfunc, p0[:], args=(x, y),
                                    full_output=1,
                                    #maxfev = 1000
                                     )
                while ier != 1:
                    p0 = [pi / 2.0 for pi in p0]
                    coeffs, cov_params, _infodict, _msg, ier = optimize.leastsq(errfunc, p0[:], args=(x, y),
                                        full_output=1,
                                    #    maxfev = 1000
                                    )
                coeff_errors = sqrt(diagonal(cov_params))
                stats['r_squared'] = self.calc_r_squared(y, fitfunc(coeffs, x))
                yreturn = fitfunc(coeffs, xreturn)
                ymodel = fitfunc(coeffs, x)
                lcly, ucly = self.calc_confidence_interval(95, x, y, ymodel, xreturn, yreturn)
            else:
#                    def func(self, coeffs, fitfunc, x, y, err):
#                        sum = 0
#                        for xi, yi, ei in zip(x, y, err):
#            sum += ((fitfunc(self.fitparams, xi) - yi) ** 2) / ei
            #sum += (fitfunc(coeffs, xi) - yi) ** 2
                func = lambda c, fitfunc, x, y, err:sum([(fitfunc(c, xi) - yi) ** 2 / ei for xi, yi, ei in zip(x, y, err)])
#        return sum
                #self.fitparams = p0
                a = optimize.fmin(func, p0,
                                    maxiter=100,
                                    ftol=1e-15,
                                    args=(fitfunc, x, y, fiterrdata),
                                    full_output=1,
                                    disp=0
                                    )
                coeffs = a[0]

            stats['r_squared'] = self.calc_r_squared(y, fitfunc(coeffs, x))
            yreturn = fitfunc(coeffs, xreturn)
            ymodel = fitfunc(coeffs, x)
            lcly, ucly = self.calc_confidence_interval(95, x, y, ymodel, xreturn, yreturn)

        if degree and len(x) >= degree + 1:

            #@todo: this should be redone using the OLS
            coeffs = polyfit(x, y, degree)

            yreturn = polyval(coeffs, xreturn)

            yn = polyval(coeffs, x)
            lcly, ucly = self.calc_confidence_interval(95, x, y, yn, xreturn, yreturn)
            if len(x) > degree + 1:
                o = OLS(x, y, fitdegree=degree)
                coeff_errors = o.get_coefficient_standard_errors()

            if stats is not None:
                stats['r_squared'] = self.calc_r_squared(y, yn)

        return dict(x=xreturn,
                    y=yreturn,
                    upper_x=xreturn,
                    upper_y=ucly,
                    lower_x=xreturn,
                    lower_y=lcly,
                    coefficients=coeffs,
                    coeff_errors=coeff_errors, #(slope_error, intercept_error),
                    statistics=stats)

    def calc_r_squared(self, y, ymodel):
        def sum_of_squares(data, model):
            data = array(data)
            model = array(model)
            return ((data - model) ** 2).sum()
            #return sum([(d - model[i]) ** 2 for i, d in enumerate(data)])

        ssreg = sum_of_squares(y, ymodel)
        sstot = sum_of_squares(y, ones(len(y)) * mean(y))

        return 1 - ssreg / sstot

    def calc_confidence_interval(self, confidence, x, observations, model, rx, rmodel):
        '''

        '''
        alpha = 1.0 - confidence / 100.0

        lower = []
        upper = []

        n = len(observations)

        if n > 2:
            xm = x.mean()
            observations = array(observations)
            model = array(model)

            syx = math.sqrt(1. / (n - 2) * ((observations - model) ** 2).sum())
            ssx = ((x - xm) ** 2).sum()

            #ssx = sum([(xi - xm) ** 2 for xi in x])

            ti = tinv(alpha, n - 2)

            for i, xi in enumerate(rx):
                d = 1.0 / n + (xi - xm) ** 2 / ssx
                cor = ti * syx * math.sqrt(d)
                lower.append(rmodel[i] - cor)
                upper.append(rmodel[i] + cor)


            #see http://mathworld.wolfram.com/LeastSquaresFitting.html
#            error_a = syx * ((1.0 / n + xm ** 2 / ssx)) ** 0.5
#            error_b = syx / (ssx) ** 0.5


        return array(lower), array(upper)

#    def calc_confidence_interval(self,confidence,observations,model):
#        
#        alpha=1.0-confidence/100.0
#        
#        n=len(observations)
#        
#        xm=mean(observations)
#        ssx=sum([(xi-xm)**2 for xi in observations])
#        syx=math.sqrt(1.0/(n-2)*sum([(obs-model[i])**2 for i,obs in enumerate(observations)]))
#        
#        lower=[]
#        upper=[]
#        ti=1.0/t.pdf(alpha,n-2)
#        for i,xi in enumerate(model):
#            
#            cor=ti*syx*math.sqrt((1.0/n+((observations[i]-xm)**2)/ssx))
#            lower.append(xi-cor)
#            upper.append(xi+cor)
#        
#        return array(lower),array(upper)

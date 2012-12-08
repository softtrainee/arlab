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
from traits.api import Property, cached_property
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import array, where, polyval, polyfit
#============= local library imports  ==========================
from src.processing.plotters.series import Series


#    return pb.signals[k].value

def try_decorator(func):
    def decorator(*args, **kw):
        try:
            return func(*args, **kw)
        except (IndexError, ValueError):
            pass
    return decorator

@try_decorator
def preceeding_predictors(predictors, tm, k, ts=None, attr='value'):
    ti = where(ts < tm)[0][-1]
    pb = predictors[ti]
    return getattr(pb.signals[k], attr)

@try_decorator
def bracketing_average_predictors(predictors, tm, k, attr='value', **kw):
    pb, ab = _bracketing_predictors(predictors, tm, **kw)

    ps = getattr(pb.signals[k], attr)
    aas = getattr(ab.signals[k], attr)
    return (ps + aas) / 2.0


@try_decorator
def bracketing_interpolate_predictors(predictors, tm, k, attr='value', **kw):
    pb, ab = _bracketing_predictors(predictors, tm, **kw)
    x = [pb.timestamp, ab.timestamp]
    ps = getattr(pb.signals[k], attr)
    aas = getattr(ab.signals[k], attr)
    y = [ps, aas]
    return polyval(polyfit(x, y, 1), tm)


@try_decorator
def _bracketing_predictors(predictors, tm, ts=None):
    if ts is None:
        ts = array([a.timestamp for a in predictors])
    ti = where(ts < tm)[0][-1]
    pb = predictors[ti]
    ab = predictors[ti + 1]
    return pb, ab

class FitSeries(Series):
    predictors = Property

    @cached_property
    def _get_predictors(self):
        return sorted([a for a in self.analyses if a.group_id == 0], key=lambda x:x.timestamp)

    def _get_series_error(self, a, k, i, group_id):
        if group_id == 0:
            return super(FitSeries, self)._get_series_error(a, k, i, group_id)
        else:
            t = a.timestamp
            predictors = self.predictors

            #get the interpolated value
            fit = self.fits[k].lower()
            ts = array([a.timestamp for a in predictors])
            args = (predictors, t, k)

            if fit == 'preceeding':
                n = preceeding_predictors(ts=ts, *args, attr='error')
            elif fit == 'bracketing interpolate':
                n = bracketing_interpolate_predictors(ts=ts, *args, attr='error')
            elif fit == 'bracketing average':
                n = bracketing_average_predictors(ts=ts, *args, attr='error')
            else:
                try:
                    reg = self.graph.regressors[i]
                    t = t - self.graph.get_x_limits()[0]
#                    n = reg.predict([t])[0]
                    try:
                        lci, uci = reg.calculate_ci([t])
                        n = (lci[0] + uci[0]) / 2.0
                    except TypeError, e:
                        #could not compute confidence interval
                        #use preceeding error
                        n = preceeding_predictors(ts=ts, *args, attr='error')

                except IndexError:
                    n = 0.1

            return n

    def _get_series_value(self, a, k, i, group_id):
        if group_id == 0:
            return super(FitSeries, self)._get_series_value(a, k, i, group_id)
        else:
            t = a.timestamp
            predictors = self.predictors

            #get the interpolated value
            fit = self.fits[k].lower()
            ts = array([a.timestamp for a in predictors])
            args = (predictors, t, k)
            if fit == 'preceeding':
                n = preceeding_predictors(ts=ts, *args)
            elif fit == 'bracketing interpolate':
                n = bracketing_interpolate_predictors(ts=ts, *args)
            elif fit == 'bracketing average':
                n = bracketing_average_predictors(ts=ts, *args)
            else:
                try:
                    reg = self.graph.regressors[i]
                    t = t - self.graph.get_x_limits()[0]
                    n = reg.predict([t])[0]
                except IndexError:
                    n = 0

            return n if n is not None else 0
#============= EOF =============================================

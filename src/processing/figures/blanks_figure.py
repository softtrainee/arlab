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
from traits.api import HasTraits, Event, cached_property, Property
from traitsui.api import View, Item, TableEditor
from traitsui.menu import  Action
#============= standard library imports ========================
import os
from numpy import array, where, polyfit, polyval
#============= local library imports  ==========================
from src.processing.figures.base_figure import BaseFigure
#from src.viewable import ViewableHandler
from src.processing.plotters.series import Series
from src.processing.series_config import SeriesConfig
from src.processing.figures.fit_series_figure import FitSeriesFigure
from src.processing.plotters.fit_series import FitSeries
#from src.paths import paths

#
#class BlanksSeries(Series):
#    blanks = Property
#
#    @cached_property
#    def _get_blanks(self):
#        return sorted([a for a in self.analyses if a.gid == 0], key=lambda x:x.timestamp)
#
#    def _get_series_value(self, a, k, gid):
#        if gid == 0:
#            return super(BlanksSeries, self)._get_series_value(a, k, gid)
#        else:
#            t = a.timestamp
#            blanks = self.blanks
##            blanks = sorted(blanks, key=lambda x: x.timestamp)
#            #get the interpolated value
#            fit = self.fits[k].lower()
#            ts = array([a.timestamp for a in blanks])
#            args = (blanks, t, k)
#            if fit == 'preceeding':
#                n = preceeding_blanks(ts=ts, *args)
#            elif fit == 'bracketing interpolate':
#                n = bracketing_interpolate_blanks(ts=ts, *args)
#            elif fit == 'bracketing average':
#                n = bracketing_average_blanks(ts=ts, *args)
#
##            if fit in ['preceeding', 'bracketing interpolate', 'bracketing average']:
##                fit = '{}_blanks'.format(fit.replace(' ', '_'))
##                ts = array([a.timestamp for a in blanks])
##                ti = where(ts < t)[0][-1]
##                pb = blanks[ti]
#
##                if  fit == 'preceeding':
##                    pb = preceeding_blanks(blanks, t)
##                    n = pb.signals[k].value
##                else:
##                    pb, ab = bracketing_blanks(blanks, t)
##
##                    ab = blanks[ti + 1]
##                    x = [pb.timestamp, ab.timestamp]
##                    y = [pb.signals[k].value, ab.signals[k].value]
##                    if fit == 'bracketing interpolate':
##                        n = polyval(polyfit(x, y, 1), t)
##                    else:
##                        n = sum(y) / 2.0
#            else:
#                n = self.graph.get_value_at(t)
#
#            self.graph.set_y_limits(pad='0.1')
#            return n if n is not None else 0

class BlanksSeriesConfig(SeriesConfig):

    def _get_fits(self):
        fits = super(BlanksSeriesConfig, self)._get_fits()
        fits.insert(1, 'Preceeding')
        fits.insert(2, 'Bracketing Interpolate')
        fits.insert(2, 'Bracketing Average')
        return fits

class BlanksFigure(FitSeriesFigure):
    _name = 'blanks'
#    apply_blanks_event = Event
#    series_klass = FitSeries
    series_config_klass = BlanksSeriesConfig

#    def _get_handler(self):
#        return BlanksFigureHandler

#    def load_analyses(self, fit=True, *args, **kw):
#        if fit is False:
#            pass
#    def _get_gids(self, analyses):
#        gids = list(set([(a.gid, True) for a in analyses]))
#        gids = [(g, True if i == 0 else False) for i, (g, _) in enumerate(gids)]
#        return gids
#
#    @property
#    def fit_series(self):
#        return [si for si in self.series_configs if si.show and si.fit != '---']
#
#    @property
#    def dirty(self):
#        return next((s for s in self.fit_series), None)
#============= EOF =============================================

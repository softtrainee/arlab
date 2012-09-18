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
from src.viewable import ViewableHandler
from src.processing.plotters.series import Series
from src.processing.series_config import SeriesConfig
from src.paths import paths

class BlanksFigureHandler(ViewableHandler):
    def on_apply(self, info):
        if info.object.apply():
            info.ui.dispose()

def preceeding_blanks(blanks, tm, k, ts=None):
    ti = where(ts < tm)[0][-1]
    pb = blanks[ti]
    return pb.signals[k].value

def bracketing_average_blanks(blanks, tm, k, **kw):
    pb, ab = _bracketing_blanks(blanks, tm, **kw)
    return (pb.signals[k].value +
            ab.signals[k].value) / 2.0

def bracketing_interpolate_blanks(blanks, tm, k, **kw):
    pb, ab = _bracketing_blanks(blanks, tm, **kw)
    x = [pb.timestamp, ab.timestamp]
    y = [pb.signals[k].value, ab.signals[k].value]
    return polyval(polyfit(x, y, 1), tm)

def _bracketing_blanks(blanks, tm, ts=None):
    if ts is None:
        ts = array([a.timestamp for a in blanks])
    ti = where(ts < tm)[0][-1]
    pb = blanks[ti]
    ab = blanks[ti + 1]
    return pb, ab

class BlanksSeries(Series):
    blanks = Property

    @cached_property
    def _get_blanks(self):
        return sorted([a for a in self.analyses if a.gid == 0], key=lambda x:x.timestamp)

    def _get_series_value(self, a, k, gid):
        if gid == 0:
            return super(BlanksSeries, self)._get_series_value(a, k, gid)
        else:
            t = a.timestamp
            blanks = self.blanks
#            blanks = sorted(blanks, key=lambda x: x.timestamp)
            #get the interpolated value
            fit = self.fits[k].lower()
            ts = array([a.timestamp for a in blanks])
            args = (blanks, t, k)
            if fit == 'preceeding':
                n = preceeding_blanks(ts=ts, *args)
            elif fit == 'bracketing interpolate':
                n = bracketing_interpolate_blanks(ts=ts, *args)
            elif fit == 'bracketing average':
                n = bracketing_interpolate_blanks(ts=ts, *args)

#            if fit in ['preceeding', 'bracketing interpolate', 'bracketing average']:
#                fit = '{}_blanks'.format(fit.replace(' ', '_'))
#                ts = array([a.timestamp for a in blanks])
#                ti = where(ts < t)[0][-1]
#                pb = blanks[ti]

#                if  fit == 'preceeding':
#                    pb = preceeding_blanks(blanks, t)
#                    n = pb.signals[k].value
#                else:
#                    pb, ab = bracketing_blanks(blanks, t)
#
#                    ab = blanks[ti + 1]
#                    x = [pb.timestamp, ab.timestamp]
#                    y = [pb.signals[k].value, ab.signals[k].value]
#                    if fit == 'bracketing interpolate':
#                        n = polyval(polyfit(x, y, 1), t)
#                    else:
#                        n = sum(y) / 2.0
            else:
                n = self.graph.get_value_at(t)

            self.graph.set_y_limits(pad='0.1')
            return n if n is not None else 0

class BlanksSeriesConfig(SeriesConfig):

    def _get_fits(self):
        fits = super(BlanksSeriesConfig, self)._get_fits()
        fits.insert(1, 'Preceeding')
        fits.insert(2, 'Bracketing Interpolate')
        fits.insert(2, 'Bracketing Average')
        return fits

class BlanksFigure(BaseFigure):
    apply_blanks_event = Event
    series_klass = BlanksSeries
    series_config_klass = BlanksSeriesConfig
    def _get_series_config_path(self):
        return os.path.join(paths.hidden_dir, 'blanks_series_config')

    def _get_graph_selector_path(self):
        return os.path.join(paths.hidden_dir, 'blanks_graph_selector')

    def apply(self):
        if not self.dirty:
            self.warning_dialog('No series set')
            return False
        self.info('applying blank series')
        self.apply_blanks_event = True
        return True

    def _get_buttons(self):
        return [Action(name='Apply',
                       action='on_apply'), 'Cancel']

    def _get_handler(self):
        return BlanksFigureHandler

    def close(self, isok):
        r = True
        if self.dirty:
            r = self.confirmation_dialog('Sure you want to close with out saving')
        return r
#    def load_analyses(self, fit=True, *args, **kw):
#        if fit is False:
#            pass
    def _get_gids(self, analyses):
        gids = list(set([(a.gid, True) for a in analyses]))
        gids = [(g, True if i == 0 else False) for i, (g, _) in enumerate(gids)]
        return gids
    @property
    def fit_series(self):
        return (si for si in self.series_configs if si.show and si.fit != '---')
    @property
    def dirty(self):
        return next(self.fit_series, None)
#============= EOF =============================================

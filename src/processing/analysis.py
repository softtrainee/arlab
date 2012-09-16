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
from traits.api import HasTraits, Str, Int, Float, Property, cached_property, Dict, \
    List, Color, Enum
from traitsui.api import View, Item, TableEditor
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
from numpy import polyfit, array
import random
from src.processing.argon_calculations import calculate_arar_age
#============= local library imports  ==========================


class AnalysisTabularAdapter(TabularAdapter):
    iso_keys = List
#    columns = [('RunID', 'rid'),
#               ('Age', 'age'),
#               ('Error', 'age_error'),
#               ('Ar40', 'ar40'), 
#               ('Ar39', 'ar39'),
#               ('Ar39', 'ar39'),
#               ('Ar38', 'ar38'),
#               ('Ar37', 'ar37'),
#               ('Ar36', 'ar36'),
#               ]
    columns = Property(depends_on='iso_keys')

    def _get_columns(self):
        return self._columns_factory()

    def _columns_default(self):
        return self._columns_factory()

    def _columns_factory(self):
        cols = [('RunID', 'rid'),
               ('Age', 'age'),
               ('Error', 'age_error'), ]
        cols += [(i.capitalize(), i) for i in self.iso_keys]
        for iso in self.iso_keys:
            self.add_trait('{}_format'.format(iso),
                           '%0.4f')
        return cols

    age_text = Property
    age_error_format = Str('%0.2f')

    age_width = Int(80)
    age_error_width = Int(80)
    rid_width = Int(80)

    def _get_age_text(self, trait, item):
        return '{:0.3f}'.format(self.item.age[0])

    def get_text_color(self, obj, trait, row):
        o = getattr(obj, trait)[row]
        return o.color

class Signal(HasTraits):
    isotope = Str
    detector = Str
    xs = None
    ys = None
    fit = 1

    value = Property
    value_error = Property

    @cached_property
    def _get_value(self):
        if self.xs:
            return polyfit(self.xs, self.ys, self.fit)[-1]
        else:
            return 0

    @cached_property
    def _get_value_error(self):
        if self.xs:
            return random.random()
        else:
            return 0

class Baseline():
    @cached_property
    def _get_value(self):
        if self.ys:
            return array(self.ys).mean()
        else:
            return 0

    @cached_property
    def _get_value_error(self):
        if self.ys:
            return array(self.ys).std()
        else:
            return 0

#    def __add__(self, o):
#        return o.__add__(self.intercept)
#    def __sub__(self, o):
#        return o.__sub__(self.intercept)
#    def __mul__(self, o):
#        return o.__mul__(self.intercept)
#    def __div__(self, o):
#        return o.__div__(self.intercept)
#    def __pow__(self, n):
#        return self.intercept ** n
#    def __pos__(self):
#        return self.intercept
#    def __neg__(self):
#        return -self.intercept

class Analysis(HasTraits):
    rid = Str
    sample = Str
    irradiation = Str

    analysis_type = Str
    timestamp = Float

    signals = Dict
    baseline = Signal

    age = Property
    age_error = Property

    gid = Int
    color = Color('black')
    uuid = Str
#    age_scalar = Enum({'Ma':1e6, 'ka':1e3})
    age_scalar = 1e6
    def __getattr__(self, attr):
        try:
            return self.signals[attr].value
        except KeyError:
            pass

    @cached_property
    def _get_age(self):
        signals = self.signals
        j = self._get_j()
        irradinfo = self._get_irradinfo()

#        age = 0
#        err = 0
#        age = 10 + random.random()
#        err = random.random()
#        if len(signals.keys()) == 5:

        for iso in ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']:
            if not signals.has_key(iso):
                signals[iso] = self._signal_factory(iso, None)

        fsignals = [(signals[iso].value, signals[iso].value_error) for iso in ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']]
#            fsignals = [(s.value, s.value_error) for s in signals.itervalues()]

        result = calculate_arar_age(fsignals, j, irradinfo)

        ai = result['age']
        ai = ai / self.age_scalar
        age = ai.nominal_value
        err = ai.std_dev()

        age = 10 + random.random()
        err = random.random()

        return age, err

    @cached_property
    def _get_age_error(self):
        return self.age[1]

    def load_from_file(self, df):

        #get the signals
        for iso in df.root.signals:
            name = iso._v_name
            tab = next((n for n in iso._f_iterNodes()), None)

            self.signals[name] = self._signal_factory(name, tab)

            self.signals['{}bs'.format(name)] = self._baseline_factory(name, df)
        try:
            t = df.root._v_attrs['TIMESTAMP']
        except KeyError:
            t = -1
        self.timestamp = t

    def _baseline_factory(self, iso, df):
        kw = dict()
        tab = None
        if hasattr(df.root, 'baselines'):
            try:
                for b in df.root.baselines:
                    tab = next((n for n in b._f_iterNodes()), None)
            except Exception, e:
                print e
        else:
            try:
                #load peakhop 
                for det in df.root.peakhop_baselines:
                    tab = next((n for n in det._f_iterNodes() if n._v_name == iso), None)
            except Exception, e:
                print e

        if tab:
            xs, ys = self._get_xy(tab)
            kw['xs'] = xs
            kw['ys'] = ys

        return Signal(isotope=iso, **kw)

    def _signal_factory(self, iso, tab):
        kw = dict()
        if tab is not None:
            xs, ys = self._get_xy(tab)
            kw = dict(xs=xs, ys=ys, detector=tab.name)
        return Signal(isotope=iso, **kw)

    def _get_xy(self, tab, x='time', y='value'):
        return zip(*[(r[x], r[y]) for r in tab.iterrows()])

    def _get_j(self):
        return (1, 1)

    def _get_irradinfo(self):
        return (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), 1
#============= EOF =============================================

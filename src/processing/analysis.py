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
    List, Color, Any, Event
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================

#============= local library imports  ==========================

from src.loggable import Loggable
from uncertainties import ufloat
from src.helpers import alphas
from src.constants import NULL_STR


class AnalysisTabularAdapter(TabularAdapter):
#    iso_keys = List
#    columns = Property(depends_on='iso_keys')
    age_text = Property
    age_error_format = Str('%0.2f')
    age_width = Int(60)
    age_error_width = Int(40)

#    rid_width = Int(60)
#    def get_column_keys(self):
#        '''
#            simple wrapper to add er columns
#        '''
#        isos = self.iso_keys
#        es = map(lambda xi:'{}_er'.format(xi), isos)
#        return [ci
#                for pi in zip(isos, es)
#                    for ci in pi]

    def get_font(self, obj, trait, row):
        import wx
        s = 9
        f = wx.FONTFAMILY_DEFAULT
        st = wx.FONTSTYLE_NORMAL
        w = wx.FONTWEIGHT_NORMAL
        return wx.Font(s, f, st, w)

#    def _get_columns(self):
#        return self._columns_factory()
#
#    def _columns_default(self):
#        return self._columns_factory()
#
#    def _columns_factory(self):
#        cols = [('Lab ID', 'rid'),
#               ('Age', 'age'),
#               ('Error', 'age_error'),
#               ]
#        colskeys = self.get_column_keys()
#        def get_name(n):
#            if n.endswith('_er'):
#                return u'\u00b11s'
#            else:
#                return n.capitalize()
#
#        cols += [(get_name(i), i) for i in colskeys]
#        for iso in colskeys:
#            self.add_trait('{}_format'.format(iso),
#                           '%0.4f')
#            self.add_trait('{}_width'.format(iso),
#                           60)
#        return cols

    def _get_age_text(self, trait, item):
        return '{:0.3f}'.format(self.item.age[0])

    def get_text_color(self, obj, trait, row):
        o = getattr(obj, trait)[row]
        return o.color

    def get_bg_color(self, obj, trait, row):
        o = getattr(obj, trait)[row]
        return o.bgcolor


class Analysis(Loggable):
    ''' 
    thinly wraps database.records.IsotopeRecord class
    '''

#    workspace = Any
#    repo = Any
    sample = Str
    irradiation = Str

    dbrecord = Any

    record_id = Property#(depends_on='dbrecord')
    sample = Property#(depends_on='dbrecord')
    labnumber = Property#(depends_on='dbrecord')
    aliquot = Property
    step = Property
    irradiation = Property#(depends_on='dbrecord')
    group_id = Property#(depends_on='dbrecord')
    graph_id = Property#(depends_on='dbrecord')
    analysis_type = Property#(depends_on='labnumber')
    k39 = Property
    kca = Property
    rad40 = Property
    rad40_percent = Property
    status = Property
    status_string = Property(depends_on='status')
    j = Property
    ic_factor = Property
    arar_result = Property
    isotope_keys = Property
#    timestamp = Float

#    signals = Dict
#    signals = DelegatesTo('dbrecord')
    signals = Property
#    age = Property(depends_on='age_dirty, signals[]')
    age = Property#(depends_on='age_dirty, signals[]')
    age_error = Property
#    age_dirty = Event

#    k39 = Float
#    k39err = Float

#    group_id = Int
#    graph_id
    color = Color('black')
    bgcolor = Color('white')
    uuid = Str
#    age_scalar = Enum({'Ma':1e6, 'ka':1e3})
    age_scalar = 1e6

#    ic_factor = Property
#    _ic_factor = Tuple

    temp_status = Int
#    @on_trait_change('signals:blank_signal')
#    def _change(self):
#        print 'fiafsd'
#        self.age_dirty = True
    def load_age(self):
        if self.age is not None:
            #self.info('{} age={}'.format(self.dbrecord.record_id, a))
            return True
        else:
            self.warning('could not compute age for {}'.format(self.rid))

    def get_corrected_intercept(self, key):
        '''
            return signal corrected for baseline and background only
        '''
        s = self.signals[key]
        try:
            bs = self.signals['{}bs'.format(key)]
        except KeyError:
            bs = 0

        try:
            bg = self.signals['{}bg'.format(key)]
        except KeyError:
            bg = 0

        return s - bs - bg


    def _analysis_factory(self, dbr):
        klass = self.__class__
        c = klass(repo=self.repo, workspace=self.workspace)
#        c.load_from_file(dbr.analysis.path.filename)
        return c

    def _ratio_factory(self, dbr, num_key, dem_key):
        a = self._analysis_factory(dbr)
        num = a.signals[num_key]
        dem = a.signals[dem_key]
        to_unc = lambda x: ufloat((x.nominal_value, x.std_dev()))
        r = to_unc(num) / to_unc(dem)
        return a.timestamp, r.nominal_value, r.std_dev()

    def _intercalibration_factory(self, dbr, num_key, dem_key, scalar):
        if not isinstance(scalar, tuple):
            scalar = (scalar, 0)
        scalar = ufloat(scalar)
        ti, ri, ei = self._ratio_factory(dbr, num_key, dem_key)
        ic = ufloat((ri, ei)) / scalar
        return ti, ic.nominal_value, ic.std_dev()

    @property
    def age_string(self):
        a, e = self.age
        try:
            pe = abs(e / a * 100)
        except ZeroDivisionError:
            pe = 'Inf'
        return u'{:0.3f} \u00b1{:0.3f}({:0.2f}%)'.format(a, e, pe)

    @property
    def timestamp(self):
        return self.dbrecord.timestamp

    def _get_j(self):
        return self.dbrecord.j

    def _get_rad40(self):
        rr = self.dbrecord.arar_result
        return rr['rad40']

    def _get_rad40_percent(self):
        rr = self.dbrecord.arar_result
        return rr['rad40'] / rr['tot40'] * 100

    def _get_age(self):
        return self.dbrecord.age

    def _get_kca(self):
        return self.dbrecord.kca

    def _get_k39(self):
        return self.dbrecord.k39

    def _get_age_error(self):
        return self.age[1]

    def _get_analysis_type(self):
        dbr = self.dbrecord
        return dbr.measurement.analysis_type.name

#    @cached_property
    def _get_labnumber(self):
        dbr = self.dbrecord
        return dbr.labnumber

#    @cached_property
    def _get_record_id(self):
        return self.dbrecord.record_id
#        dbr = self.dbrecord
#        return '{}-{}{}'.format(self.labnumber, dbr.aliquot, dbr.step)
#        dbr = self.dbrecord
#        ln = dbr.labnumber
#        return '{}-{}'.format(ln.labnumber, ln.aliquot)
    def _get_aliquot(self):
        return self.dbrecord.aliquot

    def _get_step(self):
        return self.dbrecord.step
#    @cached_property
    def _get_sample(self):
        dbr = self.dbrecord
        if hasattr(dbr, 'sample'):
            return dbr.sample.name
        else:
            return NULL_STR

    def _get_irradiation(self):
        dbr = self.dbrecord
        return dbr.irradiation.name

    def _get_ic_factor(self):
        return self.dbrecord.ic_factor

    def _get_signals(self):
        return self.dbrecord.signals

    def _get_isotope_keys(self):
        return self.dbrecord.isotope_keys

    def _get_arar_result(self):
        return self.dbrecord.arar_result

    def _get_status(self):
        return self.dbrecord.status

    def _get_status_string(self):
        return '' if self.status == 0 else 'X'

    def _get_group_id(self):
        return self.dbrecord.group_id

    def _get_graph_id(self):
        return self.dbrecord.graph_id

    def _set_group_id(self, g):
        self.dbrecord.group_id = g

    def _set_graph_id(self, g):
        self.dbrecord.graph_id = g


class NonDBAnalysis(HasTraits):
    record_id = Property
    labnumber = Int
    aliquot = Int
    step = ''
    age = Property
    _age = Float
    _error = Float
    graph_id = Int
    group_id = Int
    status = Int
    sample = Str

    def _set_record_id(self, r):
        al = 1
        if '-' in r:
            r, al = r.split('-')
            if al[-1].upper() in alphas:
                s = al[-1]
                al = al[:-1]
                self.step = s

        self.aliquot = int(al)
        self.labnumber = int(r)

    def _get_record_id(self):
        return '{}-{:02n}{}'.format(self.labnumber, self.aliquot, self.step)

    def _get_age(self):
        return (self._age, self._error)

    @property
    def age_string(self):
        a, e = self.age
        try:
            pe = abs(e / a * 100)
        except ZeroDivisionError:
            pe = 'Inf'
        return u'{:0.3f} \u00b1{:0.3f}({:0.2f}%)'.format(a, e, pe)

class IntegratedAnalysis(NonDBAnalysis):
    rad40_percent = Property
#    dbrecord = None

    def _get_rad40_percent(self):
        return self._rad40_percent



#timeit
if __name__ == '__main__':
    from tables import openFile
    a = Analysis()
    def time_load():
        p = '/Users/ross/Sandbox/pychron_test_data/data/b4e12e97-3526-4834-8a32-507fc37f166f.h5'
        df = openFile(p)
        a.load_from_file(df)

    from timeit import Timer
#    t = Timer('time_load()', 'from __main__ import time_load')
    t = Timer(time_load)
    print t.timeit(1)

    '''
        results = 0.0124s to load 700kb
            Users/ross/Sandbox/pychron_test_data/data/b4e12e97-3526-4834-8a32-507fc37f166f.h5
        
    '''
#============= EOF =============================================

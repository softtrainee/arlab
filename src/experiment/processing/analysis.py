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


class AnalysisTabularAdapter(TabularAdapter):
    iso_keys = List
    columns = Property(depends_on='iso_keys')
    age_text = Property
    age_error_format = Str('%0.2f')

    age_width = Int(60)
    age_error_width = Int(40)
    rid_width = Int(60)
    def get_column_keys(self):
        '''
            simple wrapper to add er columns
        '''
        isos = self.iso_keys
        es = map(lambda xi:'{}_er'.format(xi), isos)
        return [ci
                for pi in zip(isos, es)
                    for ci in pi]

    def get_font(self, obj, trait, row):
        import wx
        s = 9
        f = wx.FONTFAMILY_DEFAULT
        st = wx.FONTSTYLE_NORMAL
        w = wx.FONTWEIGHT_NORMAL
        return wx.Font(s, f, st, w)

    def _get_columns(self):
        return self._columns_factory()

    def _columns_default(self):
        return self._columns_factory()

    def _columns_factory(self):
        cols = [('Lab ID', 'rid'),
               ('Age', 'age'),
               ('Error', 'age_error'),
               ]
        colskeys = self.get_column_keys()
        def get_name(n):
            if n.endswith('_er'):
                return u'\u00b11s'
            else:
                return n.capitalize()

        cols += [(get_name(i), i) for i in colskeys]
        for iso in colskeys:
            self.add_trait('{}_format'.format(iso),
                           '%0.4f')
            self.add_trait('{}_width'.format(iso),
                           60)
        return cols

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

    rid = Property#(depends_on='dbrecord')
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
    j = Property
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

#    @cached_property
#    def _get_ic_factor(self):
#        return self._ic_factor


#        signals = self.signals
#        j = self._get_j()
#        irradinfo = self._get_irradinfo()
#
#        keys = ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']
#        for iso in keys:
#            for k in ['', 'bs', 'bl', 'bg']:
#                isok = iso + k
#                if not signals.has_key(isok):
#                    signals[isok] = self._signal_factory(isok, None)
#
#        sigs = lambda name: [(signals[iso].value, signals[iso].error)
#                                for iso in map('{{}}{}'.format(name).format, keys)]
##        try:
#        fsignals = sigs('')
#        bssignals = sigs('bs')
#        blsignals = sigs('bl')
#        bksignals = sigs('bg')
##        except Exception, e:
##            print 'analysis._get_age', e
##            return None
#
##        return 1, 0
#        ic = self.ic_factor
#        result = calculate_arar_age(fsignals, bssignals, blsignals, bksignals, j, irradinfo, ic)
#
#        if result:
#            self.k39 = result['k39'].nominal_value
#            self.k39err = result['k39'].std_dev()
#            ai = result['age']
#
#            ai = ai / self.age_scalar
#            age = ai.nominal_value
#            err = ai.std_dev()
#
##            age = 10 + random.random()
##            err = random.random()
#            return age, err

#    def _open_file(self, name):
#        p = os.path.join(self.workspace.root, name)
#        if os.path.isfile(p):
#            return openFile(p)
#        else:
#            rname = os.path.basename(p)
#
#            if self.repo.isfile(rname):
#                self.info('fetching file from repo')
##                out = open(p, 'wb')
#                self.repo.retrieveFile(rname, p)
#                return openFile(p)
#            else:
#                self.warning('{} is not a file'.format(name))

#    def load_from_database(self, dbr=None):
#        if dbr is None:
#            dbr = self.dbrecord
#
#        #load blanks
#        self._load_from_history(dbr, 'blanks', 'bl', Blank)
#
#        #load backgrounds
#        self._load_from_history(dbr, 'backgrounds', 'bg', Background)
#
        #load airs for detector intercal
#        self._load_detector_intercalibration(dbr)

#    def _load_detector_intercalibration(self, dbr):
#        self._ic_factor = (1.0, 0)
#        name = 'detector_intercalibration'
#        item = self._get_history_item(dbr, name)
#        if item:
#            if not item.fit:
##                s = Value(value=item.user_value, error=item.user_error)
#                self._ic_factor = item.user_value, item.user_error
#            else:
#                intercal = lambda x:self._intercalibration_factory(x, 'Ar40', 'Ar36', 295.5)
#                data = map(intercal, item.sets)
#                xs, ys, es = zip(*data)
#
#                s = InterpolatedRatio(timestamp=self.timestamp,
#                                      fit=item.fit,
#                                      xs=xs, ys=ys, es=es
#                                      )
#
#                self._ic_factor = s.value, s.error

#    def _load_from_history(self, dbr, name, key, klass, **kw):
#        item = self._get_history_item(dbr, name)
#        if item:
#            for bi in item:
#                isotope = bi.isotope
#                s = klass(timestamp=self.timestamp, **kw)
#                if not bi.fit:
##                if not bi.use_set:
#                    s.value = bi.user_value
#                    s.error = bi.user_error
#                else:
#                    s.fit = bi.fit.lower()
#                    xs, ys, es = zip(*[(ba.timestamp, ba.signals[isotope].value, ba.signals[isotope].error)
#                                   for ba in map(self._analysis_factory, bi.sets)])
#                    s.xs = xs
#                    s.ys = ys
#                    s.es = es
#                self.signals['{}{}'.format(isotope, key)] = s

#    def _get_history_item(self, dbr, name):
#        '''
#            get the selected history item if available else use the last history
#        '''
#
#        histories = getattr(dbr, '{}_histories'.format(name))
#        if histories:
#            hist = getattr(dbr.selected_histories, 'selected_{}'.format(name))
#            if hist is None:
#                hist = histories[-1]
#
#            return getattr(hist, name)

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

#    def load_from_file(self, name):
#        df = self._open_file(name)
#        if df:
#            try:
#                #get the signals
#                for iso in df.root.signals:
#                    name = iso._v_name
#                    tab = next((n for n in iso._f_iterNodes()), None)
#                    self.dbrecord.signals[name] = self.dbrecord._signal_factory(name, tab)
#            except Exception, e:
#                print 'load file', e
#                pass
#
#            try:
#                for biso in df.root.baselines:
#                    name = biso._v_name
#                    basetab = next((n for n in biso._f_iterNodes()), None)
#                    self.dbrecord.signals['{}bs'.format(name)] = self.dbrecord._signal_factory(name, basetab)
#            except Exception, e:
#                print 'load base file', e
#                pass
#
#            try:
#                t = df.root._v_attrs['TIMESTAMP']
#            except KeyError:
#                t = -1
#    #        print t, 'TIMESTAMP'
#            self.timestamp = t
#            return True

#    def _blank_factory(self, iso, tab):
#
#        return self._signal_factory(iso, tab)
#
#    def _signal_factory(self, iso, tab):
#        kw = dict()
#        if tab is not None:
#            xs, ys = self._get_xy(tab)
#            try:
#                fit = tab._v_attrs['fit']
#            except Exception:
#                fit = 1
#
#            kw = dict(xs=xs, ys=ys,
#                      fit=fit,
#                      detector=tab.name)
#        sig = Signal(isotope=iso, **kw)
#        return sig
#
#    def _get_xy(self, tab, x='time', y='value'):
#        return zip(*[(r[x], r[y]) for r in tab.iterrows()])

#    def _get_j(self):
#        return (1e-4, 1e-7)
#
#    def _get_irradinfo(self):
#        return (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), 1

#    def __getattr__(self, attr):
#        try:
##            print attr, self.signals[attr].value
#            return self.signals[attr].value
#        except KeyError:
#            if attr.endswith('_er'):
#                try:
#                    attr = attr.replace('_er', '')
#                    return self.signals[attr].error
#                except KeyError:
#                    print 'eee', 0
#                    return 0
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
    def _get_rid(self):
        dbr = self.dbrecord
        return '{}-{}{}'.format(self.labnumber, dbr.aliquot, dbr.step)
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
        return dbr.sample.name

#    @cached_property
    def _get_irradiation(self):
        dbr = self.dbrecord
        return dbr.irradiation.name

#    @cached_property
    def _get_signals(self):
        return self.dbrecord.signals

    def _get_status(self):
        return self.dbrecord.status

    def _get_group_id(self):
        return self.dbrecord.group_id

    def _get_graph_id(self):
        return self.dbrecord.graph_id

    def _set_group_id(self, g):
        self.dbrecord.group_id = g

    def _set_graph_id(self, g):
        self.dbrecord.graph_id = g

class DummyAnalysis(HasTraits):
    age = Property
    _age = Float
    _error = Float
    graph_id = Int
    group_id = Int

    rid = Property

    labnumber = Int
    aliquot = Str
    step = ''
    dbrecord = None

    def _set_rid(self, r):
        ln, self.aliquot = r.split('-')
        self.labnumber = int(ln)

    def _get_rid(self):
        return '{}-{}'.format(self.labnumber, self.aliquot)

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

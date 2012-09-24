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
import random
import os
from tables import openFile
#============= local library imports  ==========================
from src.processing.argon_calculations import calculate_arar_age
from src.processing.signal import Signal, Blank, Background
from src.loggable import Loggable


class AnalysisTabularAdapter(TabularAdapter):
    iso_keys = List
    columns = Property(depends_on='iso_keys')

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

    age_text = Property
    age_error_format = Str('%0.2f')

    age_width = Int(60)
    age_error_width = Int(40)
    rid_width = Int(60)

    def _get_age_text(self, trait, item):
        return '{:0.3f}'.format(self.item.age[0])

    def get_text_color(self, obj, trait, row):
        o = getattr(obj, trait)[row]
        return o.color


class Analysis(Loggable):
    workspace = Any
    repo = Any
    rid = Str
    sample = Str
    irradiation = Str

    dbresult = Any

    rid = Property(depends_on='dbresult')
    sample = Property(depends_on='dbresult')
    labnumber = Property(depends_on='dbresult')
    irradiation = Property(depends_on='dbresult')
    analysis_type = Property(depends_on='labnumber')
    timestamp = Float

    signals = Dict

    age = Property(depends_on='age_dirty, signals[]')
    age_dirty = Event
    age_error = Property

    k39 = Float
    k39err = Float

    gid = Int
    color = Color('black')
    uuid = Str
#    age_scalar = Enum({'Ma':1e6, 'ka':1e3})
    age_scalar = 1e6

#    @on_trait_change('signals:blank_signal')
#    def _change(self):
#        print 'fiafsd'
#        self.age_dirty = True
    def load_age(self):
        if self.age:
            self.info('{} age={}'.format(self.rid, self.age))
            return True
        else:
            self.warning('could not compute age for {}'.format(self.rid))

    @cached_property
    def _get_age(self):
        signals = self.signals
        j = self._get_j()
        irradinfo = self._get_irradinfo()

        keys = ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']
        for iso in keys:
            for k in ['', 'bs', 'bl', 'bg']:
                isok = iso + k
                if not signals.has_key(isok):
                    signals[isok] = self._signal_factory(isok, None)

        sigs = lambda name: [(signals[iso].value, signals[iso].error)
                                for iso in map('{{}}{}'.format(name).format, keys)]
#        try:
        fsignals = sigs('')
        bssignals = sigs('bs')
        blsignals = sigs('bl')
        bksignals = sigs('bg')
#        except Exception, e:
#            print 'analysis._get_age', e
#            return None

#        return 1, 0
        result = calculate_arar_age(fsignals, bssignals, blsignals, bksignals, j, irradinfo)

#        print result
        if result:
            self.k39 = result['k39'].nominal_value
            self.k39err = result['k39'].std_dev()
            ai = result['age']

            ai = ai / self.age_scalar
            age = ai.nominal_value
            err = ai.std_dev()

#            age = 10 + random.random()
#            err = random.random()
            return age, err

    def _open_file(self, name):
        p = os.path.join(self.workspace.root, name)

        if os.path.isfile(p):
            return openFile(p)
        else:
            rname = os.path.basename(p)
            if self.repo.isfile(rname):
                self.info('fetching file from repo')
#                out = open(p, 'wb')
                self.repo.retrieveFile(rname, p)
                return openFile(p)
            else:
                self.warning('{} is not a file'.format(name))

    def load_from_database(self, dbr=None):
        if dbr is None:
            dbr = self.dbresult

#        #load blanks
#        histories = dbr.blanks_histories
#        if histories:
#            hist = histories[-1]
#            for bi in hist.blanks:
#                isotope = bi.isotope
#                s = Blank(timestamp=self.timestamp)
#                if not bi.use_set:
#                    s.value = bi.user_value
#                    s.error = bi.user_error
#                else:
#                    #load signals
#                    s.fit = bi.fit.lower()
##                    def an_factory(bii):
##                        c = self.__class__(
###                                           dbresult=bii.analysis,
##                                            repo=self.repo,
##                                            workspace=self.workspace
##                                            )
##                        c.load_from_file(bii.analysis.path.filename)
##                        return c
#
#                    xs, ys = zip(*[(ba.timestamp, ba.signals[isotope].value)
#                                   for ba in map(self._analysis_factory, bi.sets)])
#                    s.xs = xs
#                    s.ys = ys
#
#                self.signals['{}bl'.format(isotope)] = s
        #load blanks
        self._load_from_history(dbr, 'blanks', 'bl', Blank)

        #load backgrounds
        self._load_from_history(dbr, 'backgrounds', 'bg', Background)

    def _load_from_history(self, dbr, name, key, klass, **kw):
        histories = getattr(dbr, '{}_histories'.format(name))
        if histories:
            hist = histories[-1]
            items = getattr(hist, name)
            for bi in items:
                isotope = bi.isotope
                s = klass(timestamp=self.timestamp, **kw)
                if not bi.use_set:
                    s.value = bi.user_value
                    s.error = bi.user_error
                else:
                    s.fit = bi.fit.lower()
                    xs, ys = zip(*[(ba.timestamp, ba.signals[isotope].value)
                                   for ba in map(self._analysis_factory, bi.sets)])
                    s.xs = xs
                    s.ys = ys
                self.signals['{}{}'.format(isotope, key)] = s

    def _analysis_factory(self, dbr):
        klass = self.__class__
        c = klass(repo=self.repo, workspace=self.workspace)
        c.load_from_file(dbr.analysis.path.filename)
        return c

    def load_from_file(self, name):
        df = self._open_file(name)
        if df:
            try:
                #get the signals
                for iso in df.root.signals:
                    name = iso._v_name
                    tab = next((n for n in iso._f_iterNodes()), None)
                    self.signals[name] = self._signal_factory(name, tab)
            except Exception:
                pass

            try:
                for biso in df.root.baselines:
                    name = biso._v_name
                    basetab = next((n for n in biso._f_iterNodes()), None)
                    self.signals['{}bs'.format(name)] = self._signal_factory(name, basetab)
            except Exception:
                pass

            try:
                t = df.root._v_attrs['TIMESTAMP']
            except KeyError:
                t = -1
    #        print t, 'TIMESTAMP'
            self.timestamp = t
            return True

    def _blank_factory(self, iso, tab):

        return self._signal_factory(iso, tab)

    def _signal_factory(self, iso, tab):
        kw = dict()
        if tab is not None:
            xs, ys = self._get_xy(tab)
            try:
                fit = tab._v_attrs['fit']
            except Exception:
                fit = 1

            kw = dict(xs=xs, ys=ys,
                      fit=fit,
                      detector=tab.name)
        sig = Signal(isotope=iso, **kw)
        return sig

    def _get_xy(self, tab, x='time', y='value'):
        return zip(*[(r[x], r[y]) for r in tab.iterrows()])

    def _get_j(self):
        return (1e-4, 1e-7)

    def _get_irradinfo(self):
        return (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), 1

    def __getattr__(self, attr):
        try:
#            print attr, self.signals[attr].value
            return self.signals[attr].value
        except KeyError:
            if attr.endswith('_er'):
                try:
                    attr = attr.replace('_er', '')
                    return self.signals[attr].error
                except KeyError:
                    print 'eee', 0
                    return 0

    @cached_property
    def _get_age_error(self):
        return self.age[1]

    @cached_property
    def _get_analysis_type(self):
        dbr = self.dbresult
        return dbr.measurement.analysis_type.name

    @cached_property
    def _get_labnumber(self):
        dbr = self.dbresult
        ln = dbr.labnumber
        return ln.labnumber

    @cached_property
    def _get_rid(self):
        dbr = self.dbresult
        ln = dbr.labnumber
        return '{}-{}'.format(ln.labnumber, ln.aliquot)

    @cached_property
    def _get_sample(self):
        dbr = self.dbresult
        return dbr.sample.name

    @cached_property
    def _get_irradiation(self):
        dbr = self.dbresult
        return dbr.irradiation.name
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

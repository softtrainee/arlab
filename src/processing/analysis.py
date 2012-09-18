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
from src.processing.signal import Signal, Blank
from src.loggable import Loggable


class AnalysisTabularAdapter(TabularAdapter):
    iso_keys = List
    columns = Property(depends_on='iso_keys')

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


class Analysis(Loggable):
    workspace = Any
    repo = Any
    rid = Str
    sample = Str
    irradiation = Str

    analysis_type = Str

    dbresult = Any

    rid = Property(depends_on='dbresult')
    sample = Property(depends_on='dbresult')
    labnumber = Property(depends_on='dbresult')
    irradiation = Property(depends_on='dbresult')

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

    def __getattr__(self, attr):
        try:
            return self.signals[attr].value
        except KeyError:
            return 0

    @cached_property
    def _get_rid(self):
        dbr = self.dbresult
        ln = dbr.labnumber
        return '{}-{}'.format(ln.labnumber, ln.aliquot)

    @cached_property
    def _get_age(self):
        signals = self.signals
        j = self._get_j()
        irradinfo = self._get_irradinfo()

#        print 'agege'
#        age = 0
#        err = 0
#        age = 10 + random.random()
#        err = random.random()
#        if len(signals.keys()) == 5:
        keys = ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']
        for iso in keys:
            for k in ['', 'bs', 'bl']:
                isok = iso + k
                if not signals.has_key(isok):
                    signals[isok] = self._signal_factory(isok, None)

        fsignals = [(signals[iso].value, signals[iso].error)
                    for iso in keys]

        bssignals = [(signals[iso].value, signals[iso].error)
#                     if signals.has_key(iso) else (0, 0)
                        for iso in map('{}bs'.format, keys)]

        blsignals = [(signals[iso].value, signals[iso].error)
#                     if signals.has_key(iso) else (0, 0)
                        for iso in map('{}bl'.format, keys)]
#        return 1, 0
        result = calculate_arar_age(fsignals, bssignals, blsignals, j, irradinfo)
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
            age = 10
            err = 1
        else:
            age = 0
            err = 0
        return age, err

    @cached_property
    def _get_age_error(self):
        return self.age[1]

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

        #load blanks
        histories = dbr.blanks_histories
        if histories:
            hist = histories[-1]
            for bi in hist.blanks:
                isotope = bi.isotope
                s = Blank(timestamp=self.timestamp)
                if not bi.use_set:
                    s.value = bi.user_value
                    s.error = bi.user_error
                else:
                    #load signals
                    s.fit = bi.fit
                    def an_factory(bii):
                        c = self.__class__(
#                                           dbresult=bii.analysis,
                                            repo=self.repo,
                                            workspace=self.workspace
                                            )
                        c.load_from_file(bii.analysis.path.filename)
                        return c

                    xs, ys = zip(*[(ba.timestamp, ba.signals[isotope].value)
                                   for ba in map(an_factory, bi.sets)])
                    s.xs = xs
                    s.ys = ys

                self.signals['{}bl'.format(isotope)] = s

    def load_from_file(self, name):
        df = self._open_file(name)
        if df:
            #get the signals
            for iso in df.root.signals:
                name = iso._v_name
                tab = next((n for n in iso._f_iterNodes()), None)
                self.signals[name] = self._signal_factory(name, tab)

            for biso in df.root.baselines:
                name = biso._v_name
                basetab = next((n for n in biso._f_iterNodes()), None)
                self.signals['{}bs'.format(name)] = self._signal_factory(name, basetab)

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
            kw = dict(xs=xs, ys=ys, detector=tab.name)
        sig = Signal(isotope=iso, **kw)
        return sig

    def _get_xy(self, tab, x='time', y='value'):
        return zip(*[(r[x], r[y]) for r in tab.iterrows()])

    def _get_j(self):
        return (1e-4, 1e-7)

    def _get_irradinfo(self):
        return (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), 1


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

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
from src.database.core.database_adapter import DatabaseAdapter
from src.database.pychron_orm import Analyses, Paths, Intercepts, \
     AnalysisTypes, Spectrometers
from src.database.bakeout_orm import BakeoutTable, ControllerTable, PathTable

from traits.api import HasTraits, Str, Button, List, Any, Long, Event, Date, Time
from traitsui.api import View, Item, TabularEditor, EnumEditor, HGroup
from traitsui.tabular_adapter import TabularAdapter

from datetime import datetime, timedelta
from src.helpers.datetime_tools import get_datetime, get_date

class DBResult(HasTraits):
    id = Long
    _db_result = Any

    rundate = Date
    runtime = Time

    directory = Str
    filename = Str
    window_x = 0.1
    window_y = 0.1
    title = Str

    def load(self):
        dbr = self._db_result
        if dbr is not None:
            self.id = dbr.id
            self.rundate = dbr.rundate
            self.runtime = dbr.runtime
            p = dbr.path
            if p is not None:
                self.directory = p.root
                self.filename = p.filename

            self.title = 'Bakeout {}'.format(self.id)

    def traits_view(self):
        return View(
                    Item('id', style='readonly', label='ID'),
                    Item('rundate', style='readonly', label='Run Date'),
                    Item('runtime', style='readonly', label='Run Time'), # enabled_when='0',)
                    Item('directory', style='readonly'),
                    Item('filename', style='readonly'),

                    width=600,
                    height=300,
                    resizable=True,
                    x=self.window_x,
                    y=self.window_y,
                    title=self.title
                    )

class DBResultsAdapter(TabularAdapter):
    columns = [('ID', 'id')]

COMPARISONS = dict(num=['=', '<', '>', '<=', '>='],
                   negative_num=['=', '<', '<=']
                   )
COMPARATOR_TYPE = {'id':'num',
                    'this month':'negative_num'
                    }

class DBSelector(HasTraits):
    parameter = Str('rundate')
    comparator = Str('=')
    _comparisons = List(COMPARISONS['num'])
    criteria = Str('this month')

    execute = Button
    results = List

    _db = DatabaseAdapter

    dclicked = Event
    selected = Any

    wx = 0.5
    wy = 0.5

    def _dclicked_fired(self):
        s = self.selected

        if s is not None:
            s.load()

            s.window_x = self.wx
            s.window_y = self.wy

            s.edit_traits()
            self.wx += 0.005
            self.wy += 0.03

            if self.wy > 0.65:
                self.wx = 0.5
                self.wy = 0.5

    def _parameter_changed(self):
        c = COMPARATOR_TYPE[self.parameter]
        self._comparisons = COMPARISONS[c]

    def _criteria_changed(self):
        try:
            c = COMPARATOR_TYPE[self.criteria]
            self._comparisons = COMPARISONS[c]
        except KeyError, e:
            pass

    def _get_filter_str(self):
        if self.parameter == 'rundate':
#            c = datetime.strptime(self.criteria, '%Y-%m-%d')
#            c = datetime.strptime(self.criteria, '%Y-%m-%d')

            c = self.criteria.replace('/', '-')

            if self.criteria == 'today':
                c = get_date()
            elif self.criteria == 'this month':
                d = datetime.today().date()
                today = get_date()
                if self.comparator == '=':
                    d = d - timedelta(days=d.day)
                    c = '{}{}"{}" AND {}{}"{}"'.format(self.parameter,
                                                   '>=',
                                                   d,
                                                   self.parameter,
                                                   '<=',
                                                   today
                                                   )

                    return c
                else:
                    c = d - timedelta(days=d.day - 1)
            c = '"{}"'.format(c)
        else:
            c = self.criteria

        s = ''.join((self.parameter,
                   self.comparator,
                   c
#                   self.criteria
                   ))
        return s

    def _execute_fired(self):
        self.results = []
        db = self._db
        if db is not None:
            s = self._get_filter_str()
            print s
            dbs = db.get_bakeouts(filter_str=s)
            print dbs
            if dbs:
                for di in dbs:
                    d = DBResult(_db_result=di)
                    d.load()
                    self.results.append(d)

    def traits_view(self):

        qgrp = HGroup(
                Item('parameter'),
                Item('comparator', editor=EnumEditor(name='_comparisons')),
                Item('criteria'),
                show_labels=False
                )

        editor = TabularEditor(adapter=DBResultsAdapter(),
                               dclicked='object.dclicked',
                               selected='object.selected'
                               )
        v = View(

                 Item('results', style='custom',
                      editor=editor,
                      show_label=False
                      ),
                 qgrp,
                 Item('execute'),

                 resizable=True,
                 width=500,
                 height=500,
                 x=0.1,
                 y=0.1
                 )
        return v


class BakeoutAdapter(DatabaseAdapter):
    test_func = None
#===============================================================================
#    getters
#===============================================================================

    def get_bakeouts(self, filter_str=None):
        try:
            q = self._get_query(BakeoutTable, filter_str=filter_str)
            return q.all()
        except Exception:
            pass

#    def get_analyses_path(self):
##        sess = self.get_session()
##        q = sess.query(Paths)
##        s = q.filter_by(name='analyses')
#        q = self._get_query(Paths, name='analyses')
#        p = q.one()
#        p = p.path
#        return p
#
#    def get_intercepts(self, analysis_id):
#        q = self._get_query(Intercepts, analysis_id=analysis_id)
#        return q.all()
#
#    def get_analysis_type(self, **kw):
#        q = self._get_query(AnalysisTypes, **kw)
#        return q.one()
#
#    def get_spectrometer(self, **kw):
#        q = self._get_query(Spectrometers, **kw)
#        return q.one()

    def _get_query(self, klass, filter_str=None, **clause):
        sess = self.get_session()
        q = sess.query(klass)
        if filter_str:
            q = q.filter(filter_str)
        else:
            q = q.filter_by(**clause)
        return q

    def open_selector(self):
        s = DBSelector(_db=self)
        s.edit_traits(kind='livemodal')

#==============================================================================
#   adder
#==============================================================================
    def add_bakeout(self, commit=True, **kw):
        b = BakeoutTable(**kw)
        self._add_item(b, commit)
        return b

    def add_controller(self, bakeout, commit=True, **kw):
        c = ControllerTable(**kw)
        bakeout.controllers.append(c)
        if commit:
            self.commit()
#        self._add_item(c, commit)
        return c

    def add_path(self, bakeout, commit=True, **kw):
        p = PathTable(**kw)
        bakeout.path = p
        if commit:
            self.commit()
#        self._add_item(c, commit)
        return p

    def _add_item(self, obj, commit):
        sess = self.get_session()
        sess.add(obj)
        if commit:
            sess.commit()


#======== EOF ================================
#    def add_intercepts(self, **kw):
#        o = Intercepts(**kw)
#        self._add_item(o)
#
#    def add_analysis(self, atype=None, spectype=None, **kw):
#        if atype is not None:
#            a = self.get_analysis_type(name=atype)
#            kw['type_id'] = a.id
#
#        if spectype is not None:
#            s = self.get_spectrometer(name=spectype)
#            kw['spectrometer_id'] = s.id
#
#        o = Analyses(**kw)
#        self._add_item(o)
#        return o.id

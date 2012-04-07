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
from traits.api import HasTraits, Str, String, Button, List, Any, Long, Event, \
    Date, Time, Instance, Dict, DelegatesTo, Property
from traitsui.api import View, Item, TabularEditor, EnumEditor, \
    HGroup, VGroup, Group, spring
from traitsui.tabular_adapter import TabularAdapter

from datetime import datetime, timedelta
from wx import GetDisplaySize
import os

from src.database.core.database_adapter import DatabaseAdapter
from src.database.bakeout_orm import BakeoutTable, ControllerTable, PathTable
from src.helpers.datetime_tools import  get_date
from src.loggable import Loggable
from src.bakeout.bakeout_graph_viewer import BakeoutGraphViewer

DISPLAYSIZE = GetDisplaySize()


class DBResult(HasTraits):
    _id = Long
    _db_result = Any

    rundate = Date
    runtime = Time

    directory = Str
    filename = Str
    window_x = 0.1
    window_y = 0.1
    title = Str

#    graph = Instance(Graph)
    viewer = Instance(BakeoutGraphViewer)
#    bakeouts = DelegatesTo('viewer')
    graph = DelegatesTo('viewer')
    summary = DelegatesTo('viewer')
    export_button = DelegatesTo('viewer')

    def load_graph(self):
        self.viewer = BakeoutGraphViewer(title=self.title)
        p = os.path.join(self.directory,
                                      self.filename
                                      )
        self.viewer.load(p)

    def load(self):
        dbr = self._db_result
        if dbr is not None:
            self._id = dbr.id
            self.rundate = dbr.rundate
            self.runtime = dbr.runtime
            p = dbr.path
            if p is not None:
                self.directory = p.root
                self.filename = p.filename

            self.title = 'Bakeout {}'.format(self._id)

    def traits_view(self):
        interface_grp = VGroup(
                          VGroup(Item('_id', style='readonly', label='ID'),
                    Item('rundate', style='readonly', label='Run Date'),
                    Item('runtime', style='readonly', label='Run Time'),
                    Item('directory', style='readonly'),
                    Item('filename', style='readonly')),
                VGroup(Item('summary',
                            show_label=False,
                            style='custom')),
                       HGroup(spring, Item('export_button',
                                            show_label=False),),
                    label='Info',
                    )

        return View(
                    Group(
                    interface_grp,
                    Item('graph', width=0.75, show_label=False,
                         style='custom'),
                    layout='tabbed'
                    ),

                    width=800,
                    height=0.85,
                    resizable=True,
                    x=self.window_x,
                    y=self.window_y,
                    title=self.title
                    )


class DBResultsAdapter(TabularAdapter):
    columns = [('ID', '_id'),
               ('Date', 'rundate'),
               ('Time', 'runtime')
               ]

COMPARISONS = dict(num=['=', '<', '>', '<=', '>='],
                   negative_num=['=', '<', '<=']
                   )
#COMPARATOR_TYPE = {'id': 'num',
##                    'this month': 'negative_num'
#                    }


class DBSelector(Loggable):
    parameter = String('BakeoutTable.rundate')
    _parameters = Property
    comparator = Str('=')
#    _comparisons = List(COMPARISONS['num'])
    _comparisons = List(['=', '<', '>', '<=', '>=', '!=', 'like'])
    criteria = Str('this month')
    comparator_types = Property
    execute = Button
    results = List

    _db = DatabaseAdapter

    dclicked = Event
    selected = Any

    wx = 0.4
    wy = 0.1
    opened_windows = Dict

#    def _get_comparator_types(self):
#        return ['=', '<', '>', '<=', '>=', '!=', 'like']

    def _get__parameters(self):

        b = BakeoutTable

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = f(b)
        c = ControllerTable
        params += f(c)
        return list(params)

    def _dclicked_fired(self):
        s = self.selected

        if s is not None:
            if s._id in self.opened_windows:
                c = self.opened_windows[s._id].control
                if c is None:
                    self.opened_windows.pop(s._id)
                else:
                    try:
                        c.Raise()
                    except:
                        self.opened_windows.pop(s._id)

            else:
                try:
                    s.load_graph()
                    s.window_x = self.wx
                    s.window_y = self.wy

                    info = s.edit_traits()
                    self.opened_windows[s._id] = info

                    self.wx += 0.005
                    self.wy += 0.03

                    if self.wy > 0.65:
                        self.wx = 0.4
                        self.wy = 0.1
                except Exception, e:
                    self.warning(e)

#    def _parameter_changed(self):
#
##        c = COMPARATOR_TYPE[self.parameter]
#        c = self.comparator_types[self.parameter]
#        self._comparisons = COMPARISONS[c]

#    def _criteria_changed(self):
#        try:
#            c = COMPARATOR_TYPE[self.criteria]
#            self._comparisons = COMPARISONS[c]
#        except KeyError, _:
#            pass
    def _between(self, p, l, g):
        return '{}<="{}" AND {}>="{}"'.format(p, l, p, g)

    def _get_filter_str(self):
        if 'rundate' in self.parameter:
            c = self.criteria.replace('/', '-')
            if self.criteria == 'today':
                c = get_date()
            elif self.criteria == 'this month':
                d = datetime.today().date()
                today = get_date()
                if '=' in self.comparator:
                    d = d - timedelta(days=d.day)
                    c = self._between(self.parameter, today, d)
                    return c
                else:
                    c = d - timedelta(days=d.day - 1)
            c = '"{}"'.format(c)
        elif 'runtime' in self.parameter:
            args = self.criteria.split(':')
            if len(args) in [1, 2] and self.comparator == '=':
                base = ['00', ] * (3 - len(args))
                g = ':'.join(args + base)
                try:
                    a = [int(ai) + (1 if len(args) - 1 == i else 0)
                        for i, ai in enumerate(args)]
                except ValueError:
                    return None

                f = ':'.join(['{:n}', ] * (len(args)) + base)
                l = f.format(*a)
                c = self._between(self.parameter, l, g)
                return c
            else:
                c = ':'.join(args + ['00', ] * (3 - len(args)))

        else:
            c = self.criteria

        c = '"{}"'.format(c)
        s = ''.join((self.parameter,
                   self.comparator,
                   c))
        return s

    def _execute_fired(self):
        self._execute_()

    def _execute_(self):
        db = self._db
        if db is not None:
#            self.info(s)
            s = self._get_filter_str()
            if s is None:
                return

            table, _col = self.parameter.split('.')
            kw = dict(filter_str=s)
            if not table == 'BakeoutTable':
                kw['join_table'] = table

            dbs = db.get_bakeouts(**kw)

            self.info('query {} returned {} results'.format(s,
                                    len(dbs) if dbs else 0))
            if dbs:
                self.results = []
                for di in dbs:
                    d = DBResult(_db_result=di)
                    d.load()
                    self.results.append(d)

    def traits_view(self):

        qgrp = HGroup(
                Item('parameter', editor=EnumEditor(name='_parameters')),
                Item('comparator', editor=EnumEditor(name='_comparisons')),
                Item('criteria'),
                show_labels=False
                )

        editor = TabularEditor(adapter=DBResultsAdapter(),
                               dclicked='object.dclicked',
                               selected='object.selected',
                               editable=False
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
                 y=0.1,
                 title='Recall'
                 )
        return v


class BakeoutAdapter(DatabaseAdapter):
    test_func = None
#==============================================================================
#    getters
#==============================================================================

    def get_bakeouts(self, join_table=None, filter_str=None):
        try:
            if isinstance(join_table, str):
                join_table = globals()[join_table]

            q = self._get_query(BakeoutTable, join_table=join_table,
                                 filter_str=filter_str)
            return q.all()
        except Exception, e:
            print e

    def _get_query(self, klass, join_table=None, filter_str=None, **clause):
        sess = self.get_session()
        q = sess.query(klass)

        if join_table is not None:
            q = q.join(join_table)

        if filter_str:
            q = q.filter(filter_str)
        else:
            q = q.filter_by(**clause)
        return q

    def open_selector(self):
        s = DBSelector(_db=self)
        s._execute_()
        s.edit_traits()

#=============================================================================
#   adder
#=============================================================================
    def add_bakeout(self, commit=False, **kw):
        b = BakeoutTable(**kw)
        self._add_item(b, commit)
        return b

    def add_controller(self, bakeout, commit=False, **kw):
        c = ControllerTable(**kw)
        bakeout.controllers.append(c)
        if commit:
            self.commit()
#        self._add_item(c, commit)
        return c

    def add_path(self, bakeout, commit=False, **kw):
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

#    def get_bakeouts2(self):
#        sess = self.get_session()
##        clause = dict(ControllerTable.script='---')
#        qcol = 'setpoint'
#        col = getattr(ControllerTable, qcol)
#        cond = 100
#        q = sess.query(BakeoutTable).join(ControllerTable).filter(col < cond)
#        print q.all()

if __name__ == '__main__':
    db = BakeoutAdapter(dbname='bakeoutdb',
                            password='Argon')
    db.connect()

    dbs = DBSelector(_db=db)
    dbs._execute_()
    dbs.configure_traits()
#    print db.get_bakeouts(join_table='ControllerTable',
#                    filter_str='ControllerTable.script="---"'
#                    )


#======== EOF ================================
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
#    def add_intercepts(self, **kw):
#        o = Intercepts(**kw)
#        self._add_item(o)
#
#    def add_analysis(self, atype=None, spectype=None, **kw):
#        if atype is not None:
#            a = self.get_analysis_type(name=atype)
#            kw['type_id'] = a._id
#
#        if spectype is not None:
#            s = self.get_spectrometer(name=spectype)
#            kw['spectrometer_id'] = s._id
#
#        o = Analyses(**kw)
#        self._add_item(o)
#        return o._id

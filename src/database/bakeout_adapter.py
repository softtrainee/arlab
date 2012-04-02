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
from traits.api import HasTraits, Str, Button, List, Any, Long, Event, \
    Date, Time, Instance, Dict, DelegatesTo
from traitsui.api import View, Item, TabularEditor, EnumEditor, \
    HGroup, VGroup, Group, ListEditor, HSplit
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
    id = Long
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

    def load_graph(self):
        self.viewer = BakeoutGraphViewer()
        p = os.path.join(self.directory,
                                      self.filename
                                      )
        self.viewer.load(p)

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
        info_grp = VGroup(
                          VGroup(Item('id', style='readonly', label='ID'),
                    Item('rundate', style='readonly', label='Run Date'),
                    Item('runtime', style='readonly', label='Run Time'), # enabled_when='0',)
                    Item('directory', style='readonly'),
                    Item('filename', style='readonly')),
                VGroup(Item('summary',
                            show_label=False,
#                            enabled_when='0', 
                            style='custom')),
                          label='Info'
                          )
#                    Group(Item('bakeouts',
#                               show_label=False,
#                               style='custom',
#                               editor=ListEditor(use_notebook=True,
#                                                           dock_style='tab',
#                                                           page_name='.name'
#                                                           ))),
#                    layout='tabbed'
#                    )

        return View(
#                    VGroup(
#                    Item('viewer', show_label=False, style='custom'),
#                    Group(info_grp,
#                          layout='tabbed'),
#                    Group(Item('viewer', show_label=False, style='custom'),
#                          layout='tabbed'),
                    Group(
                    Item('graph', width=0.75, show_label=False, style='custom'),
                    info_grp,
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
    columns = [('ID', 'id'),
               ('Date', 'rundate'),
               ('Time', 'runtime')
               ]

COMPARISONS = dict(num=['=', '<', '>', '<=', '>='],
                   negative_num=['=', '<', '<=']
                   )
COMPARATOR_TYPE = {'id':'num',
                    'this month':'negative_num'
                    }


class DBSelector(Loggable):
    parameter = Str('rundate')
    comparator = Str('=')
    _comparisons = List(COMPARISONS['num'])
    criteria = Str('this month')

    execute = Button
    results = List

    _db = DatabaseAdapter

    dclicked = Event
    selected = Any

    wx = 0.4
    wy = 0.1
    opened_windows = Dict

    def _dclicked_fired(self):
        s = self.selected

        if s is not None:
            if s.id in self.opened_windows:
                c=self.opened_windows[s.id].control
                if c is None:
                    self.opened_windows.pop(s.id)
                else:
                    try:
                        c.Raise()
                    except:
                        self.opened_windows.pop(s.id)
                        
            else:
                s.load_graph()
                s.window_x = self.wx
                s.window_y = self.wy

                info = s.edit_traits()
                self.opened_windows[s.id] = info

                self.wx += 0.005
                self.wy += 0.03

                if self.wy > 0.65:
                    self.wx = 0.4
                    self.wy = 0.1

    def _parameter_changed(self):
        c = COMPARATOR_TYPE[self.parameter]
        self._comparisons = COMPARISONS[c]

    def _criteria_changed(self):
        try:
            c = COMPARATOR_TYPE[self.criteria]
            self._comparisons = COMPARISONS[c]
        except KeyError, _:
            pass

    def _get_filter_str(self):
        if self.parameter == 'rundate':
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
                   c))
        return s

    def _execute_fired(self):
        self._execute()

    def _execute_(self):
        self.results = []
        db = self._db
        if db is not None:
            s = self._get_filter_str()
            dbs = db.get_bakeouts(filter_str=s)
            self.info('query {} returned {} results'.format(s,
                                    len(dbs) if dbs else 0))
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
        s._execute_()
        s.edit_traits()#kind='livemodal')

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

#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import HasTraits, Str, String, Button, List, Any, Long, Event, \
    Date, Time, Instance, Dict, Property, Bool, on_trait_change

from traitsui.api import View, Item, TabularEditor, EnumEditor, \
    HGroup, VGroup, Group, spring
#============= standard library imports ========================
from datetime import datetime, timedelta
#============= local library imports  ==========================
from src.helpers.datetime_tools import  get_date
from src.loggable import Loggable
from src.database.adapters.database_adapter import DatabaseAdapter
from src.database.selectors.base_results_adapter import BaseResultsAdapter
from src.graph.graph import Graph
import os
from src.managers.data_managers.h5_data_manager import H5DataManager
import csv
from src.managers.data_managers.csv_data_manager import CSVDataManager


class BaseDBResult(HasTraits):
    _id = Long
    _db_result = Any


class DBResult(BaseDBResult):
    title = Str
    summary = Str
    graph = Instance(Graph)
    rundate = Date
    runtime = Time

    directory = Str
    filename = Str
    window_x = 0.1
    window_y = 0.1

    title_str = Str('Base')
    data_manager = None

    _loadable = True

    export_button = Button('Export CSV')

    def _export_button_fired(self):
        self._export_csv()

    def _export_csv(self):
        p = os.path.join(self.directory, self.filename)
        if os.path.isfile(p) and self.graph is not None:
            self.graph.export_data(plotid=0)

    def load(self):
        dbr = self._db_result
        if dbr is not None:
            self._id = dbr.id
            self.rundate = dbr.rundate
            self.runtime = dbr.runtime
            p = dbr.path
            if p is not None:
                self.directory = p.root if p.root else ''
                self.filename = p.filename if p.filename else ''

            self.title = '{} {}'.format(self.title_str, self._id)
            self._load_hook(dbr)

    def _load_hook(self, dbr):
        pass

    def isloadable(self):
        return self._loadable

    def _data_manager_factory(self):
        dm = self.data_manager
        if dm is None:
            data = os.path.join(self.directory, self.filename)
            _, ext=os.path.splitext(self.filename)
            if ext=='.h5':
                dm = H5DataManager()
                if os.path.isfile(data):
                    self._loadable = dm.open_data(data)
            else:
                self._loadable=False
                dm=CSVDataManager()

        return dm

    def load_graph(self):
        pass

    def _get_additional_tabs(self):
        return []

    def traits_view(self):
        interface_grp = VGroup(
                          VGroup(Item('_id', style='readonly', label='ID'),
                    Item('rundate', style='readonly', label='Run Date'),
                    Item('runtime', style='readonly', label='Run Time'),
                    Item('directory', style='readonly'),
                    Item('filename', style='readonly')),
                VGroup(Item('summary',
                            show_label=False,
                            style='readonly',
                            )
                       ),
                HGroup(spring,
                              Item('export_button', height=0.15,
                                            show_label=False)),
                    label='Info',
                    )


        grps = Group(interface_grp, layout='tabbed')

        agrps = self._get_additional_tabs()
        if self.graph is not None:
            g = Item('graph',
                    show_label=False,
                    style='custom')

            agrps.append(g)

        for ai in agrps:
            grps.content.append(ai)

        return View(grps,

                    width=800,
                    height=0.85,
                    resizable=True,
                    x=self.window_x,
                    y=self.window_y,
                    title=self.title
                    )


class DBSelector(Loggable):
    parameter = String
    _parameters = Property
    comparator = Str('=')
#    _comparisons = List(COMPARISONS['num'])
    _comparisons = List(['=', '<', '>', '<=', '>=', '!=', 'like',
                         'contains'
#                         'match'
                         ])
    criteria = Str('this month')
    comparator_types = Property
    search = Button
    results = List

    _db = DatabaseAdapter

    dclicked = Event
    selected = Any
    column_clicked = Any

    wx = 0.4
    wy = 0.1
    opened_windows = Dict
    title = 'Recall'

    tabular_adapter = BaseResultsAdapter

    query_table = None
    result_klass = None

    omit_bogus = Bool(False)

    reverse_sort = False
    _sort_field = None

    def _column_clicked_changed(self, event):
        values = event.editor.value

        fields = [name for _, name in event.editor.adapter.columns]
        field = fields[event.column]
        self.reverse_sort = not self.reverse_sort

        self._sort_columns(values, field)

    def _sort_columns(self, values, field=None):
        #get the field to sort on
        if field is None:
            field = self._sort_field
            if field is None:
                return

        values.sort(key=lambda x: getattr(x, field),
                    reverse=self.reverse_sort)
        self._sort_field = field

    def _search_fired(self):
        self._execute_query()

#    def _get_comparator_types(self):
#        return ['=', '<', '>', '<=', '>=', '!=', 'like']

    def _convert_comparator(self, c):
        if c == '=':
            c = '__eq__'
        elif c == '<':
            c = '__lt__'
        elif c == '>':
            c = '__gt__'
        elif c == '<=':
            c = '__le__'
        elif c == '>=':
            c = '__ge__'
        return c

    def _between(self, p, l, g):
        return '{}<="{}" AND {}>="{}"'.format(p, l, p, g)

    def _get_filter_str(self):

        if self.date_str in self.parameter:
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
            c = '{}'.format(c)
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

        comp = self.comparator
        if comp == 'like':
            c += '%'
        elif comp == 'contains':
            comp = 'like'
            c = '%' + c + '%'

        c = '"{}"'.format(c)
        ps = self.parameter

        s = ' '.join((ps, comp, c))

        return s

    def traits_view(self):

        qgrp = HGroup(
                Item('parameter', editor=EnumEditor(name='_parameters')),
                Item('comparator', editor=EnumEditor(name='_comparisons')),
                Item('criteria'),
                show_labels=False
                )


        editor = TabularEditor(adapter=self.tabular_adapter(),
                               dclicked='object.dclicked',
                               selected='object.selected',
                               column_clicked='object.column_clicked',
                               editable=False,
                               operations=['move', ],
                               multi_select=True
                               )
        v = View(

                 Item('results', style='custom',
                      editor=editor,
                      show_label=False
                      ),
                 qgrp,
                 HGroup(Item('omit_bogus'),
                        spring, Item('search', show_label=False)),


                 resizable=True,
                 width=500,
                 height=500,
                 x=0.1,
                 y=0.1,
                 title=self.title
                 )
        return v
    def _get_selector_records(self):
        pass

    @on_trait_change('omit_bogus')
    def _execute_query(self):
        db = self._db
        if db is not None:
#            self.info(s)

#            if self.comparator == 'like':
#                sess = self._db.get_session()
#
#                from src.database.orms.video_orm import VideoTable
#                c = '{}%'.format(self.criteria)
#                q = sess.query(VideoTable).filter(VideoTable.rid.like(c))
#                s = 'VideoTable.rid.like({})'.format(c)
#                dbs = q.all()
#            else:

            s = self._get_filter_str()
            if s is None:
                return

            table, _col = self.parameter.split('.')
            kw = dict(filter_str=s)

            if not table == self.query_table:
                kw['join_table'] = table

            dbs = self._get_selector_records(**kw)

            self.info('query {} returned {} results'.format(s,
                                    len(dbs) if dbs else 0))
            self.results = []
            if dbs:
                for di in dbs:
                    d = self.result_klass(_db_result=di)
                    d.load()
                    if d.isloadable() or not self.omit_bogus:
                        self.results.append(d)

            self._sort_columns(self.results)

    def _dclicked_fired(self):
        s = self.selected

        if s is not None:
            for si in s:
                sid = si._id
                if sid in self.opened_windows:
                    c = self.opened_windows[sid].control
                    if c is None:
                        self.opened_windows.pop(sid)
                    else:
                        try:
                            c.Raise()
                        except:
                            self.opened_windows.pop(sid)

                else:
                    try:
                        si.load_graph()
                        si.window_x = self.wx
                        si.window_y = self.wy

                        info = si.edit_traits()
                        self.opened_windows[sid] = info

                        if self._db.application is not None:
                            self._db.application.uis.append(info)

                        self.wx += 0.005
                        self.wy += 0.03

                        if self.wy > 0.65:
                            self.wx = 0.4
                            self.wy = 0.1
                    except Exception, e:
                        self.warning(e)
#============= EOF =============================================

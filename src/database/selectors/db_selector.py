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
from traits.api import Str, String, Button, List, Any, Event, \
    Dict, Property, Bool, Int

from traitsui.api import View, Item, TabularEditor, EnumEditor, \
    HGroup, VGroup, spring
#============= standard library imports ========================
from datetime import datetime, timedelta
#============= local library imports  ==========================
from src.helpers.datetime_tools import  get_date
from src.loggable import Loggable
from src.database.adapters.database_adapter import DatabaseAdapter
from src.database.selectors.base_results_adapter import BaseResultsAdapter
from src.graph.time_series_graph import TimeSeriesGraph


class DBSelector(Loggable):
    parameter = String
    _parameters = Property

    join_table_parameter = String
    _join_table_parameters = Property
    join_table_col = String
    join_table = String

    comparator = Str('=')
    _comparisons = List(['=', '<', '>', '<=', '>=', '!=',
                         'like',
                         'contains'
                         ])
    criteria = String('this month')
    results = List

    search = Button
    open_button = Button('Open')

    _db = DatabaseAdapter

    dclicked = Event
    selected = Any
    column_clicked = Any

    wx = 0.4
    wy = 0.1
    opened_windows = Dict
    title = ''

    tabular_adapter = BaseResultsAdapter

    query_table = None
    result_klass = None

    omit_bogus = Bool(True)

    reverse_sort = False
    _sort_field = None

    limit = Int(100)
    date_str = 'rundate'

    multi_select_graph = Bool(False)
    multi_graphable = Bool(False)

    def __init__(self, *args, **kw):
        super(DBSelector, self).__init__(*args, **kw)
        self._load_hook()

    def load_recent(self):
        self._execute_query(
                            param='{}.{}'.format(self.query_table.__tablename__,
                                           'rundate'),
                            comp='=',
                            criteria='this month'
                            )

    def traits_view(self):

        qgrp = HGroup(
                Item('parameter', editor=EnumEditor(name='_parameters')),
                Item('comparator', editor=EnumEditor(name='_comparisons')),
                Item('criteria'),
                show_labels=False
                )

        jt = self._get__join_table_parameters()
#        print jt
        if jt is not None:
            qgrp = VGroup(
                      Item('join_table_parameter',
                           label='Device',
                            editor=EnumEditor(name='_join_table_parameters'),
                           ),
                      qgrp
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
                 HGroup(Item('multi_select_graph',
                             defined_when='multi_graphable'
                             ),
                             spring, Item('limit')),
                 Item('results', style='custom',
                      editor=editor,
                      show_label=False
                      ),

                 qgrp,
                 HGroup(
                        Item('open_button', show_label=False),
                        spring, Item('search', show_label=False)),


                 resizable=True,
                 width=500,
                 height=500,
                 x=0.1,
                 y=0.1,
                 title=self.title
                 )
        return v

    def _get_filter_str(self, param, comp, criteria):

        if self.date_str in param:
            c = criteria.replace('/', '-')
            if criteria == 'today':
                c = get_date()
            elif criteria == 'this month':
                d = datetime.today().date()
                today = get_date()
                if '=' in comp:
                    d = d - timedelta(days=d.day)
                    c = self._between(param, today, d)
                    return c
                else:
                    c = d - timedelta(days=d.day - 1)
            c = '{}'.format(c)
        elif 'runtime' in param:
            args = criteria.split(':')
            if len(args) in [1, 2] and comp == '=':
                base = ['00', ] * (3 - len(args))
                g = ':'.join(args + base)
                try:
                    a = [int(ai) + (1 if len(args) - 1 == i else 0)
                        for i, ai in enumerate(args)]
                except ValueError:
                    return None

                f = ':'.join(['{:n}', ] * (len(args)) + base)
                l = f.format(*a)
                c = self._between(param , l, g)
                return c
            else:
                c = ':'.join(args + ['00', ] * (3 - len(args)))
        else:
            c = criteria

        if comp == 'like':
            c += '%'
        elif comp == 'contains':
            comp = 'like'
            c = '%' + c + '%'

        c = '"{}"'.format(c)
        return ' '.join((param, comp, c))

    def _get_order(self):
        from sqlalchemy.sql.expression import desc
        return [desc(getattr(self.query_table, attr)) for attr in ['rundate', 'runtime']]

    def _execute_query(self, param=None, comp=None, criteria=None):
        if param is None:
            param = self.parameter

        if comp is None:
            comp = self.comparator

        if criteria is None:
            criteria = self.criteria

        db = self._db
        if db is not None:

            s = self._get_filter_str(param, comp, criteria)
            if s is None:
                return

            table, _col = param.split('.')
            kw = dict(filter_str=s,
                      limit=self.limit,
                      order=self._get_order()
                      )

            if not table == self.query_table.__tablename__:
                kw['join_table'] = table

            elif self.join_table:
                kw['join_table'] = self.join_table
                kw['filter_str'] = s + ' and {}.{}=="{}"'.format(self.join_table,
                                                               self.join_table_col,
                                                                        self.join_table_parameter
                                                                        )


            dbs = self._get_selector_records(**kw)

            self.info('query {} returned {} results'.format(s,
                                    len(dbs) if dbs else 0))
            self.results = []
            if dbs:
                for di in dbs:
                    d = self.result_klass(_db_result=di)
                    d.load()
                    d._loadable = True
                    self.results.append(d)
#                    if d.isloadable() or not self.omit_bogus:
#                        self.results.append(d)

            self._sort_columns(self.results)

    def _open_selected(self):
        s = self.selected

        if s is not None:

            if self.multi_select_graph:
                self._open_multiple(s)
            else:
                self._open_individual(s)

    def _open_multiple(self, s):
        graph = None
        xoffset = 0
        for si in s:
            if not si._loadable:
                continue

            if graph is None:
                graph = si._graph_factory(klass=TimeSeriesGraph)
                graph.new_plot(xtitle='Time',
                               ytitle='Signal')

            xoffset += si.load_graph(graph=graph, xoffset=xoffset)

        wid = '.'.join([str(si._id) for si in s])
        did = ', '.join([str(si._id) for si in s])
        graph.window_title = '{} {}'.format(si.title_str, did)

        info = graph.edit_traits()

        self._open_window(wid, info)

    def _open_individual(self, s):
        for si in s:
            if not si._loadable:
                continue

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
                    if not si.initialize():
                        si._isloadable = False
                        return

                    si.load_graph()
                    si.window_x = self.wx
                    si.window_y = self.wy

                    info = si.edit_traits()
                    self._open_window(si._id, info)
                except Exception, e:
                    self.warning(e)

    def _open_window(self, wid, ui):
        self.opened_windows[wid] = ui
        self._update_windowxy()

        if self._db.application is not None:
            self._db.application.uis.append(ui)

    def _update_windowxy(self):
        self.wx += 0.005
        self.wy += 0.03

        if self.wy > 0.65:
            self.wx = 0.4
            self.wy = 0.1

    def _sort_columns(self, values, field=None):
        #get the field to sort on
        if field is None:
            field = self._sort_field
            if field is None:
                return

        values.sort(key=lambda x: getattr(x, field),
                    reverse=self.reverse_sort)
        self._sort_field = field

    def _dclicked_fired(self):
        self._open_selected()

    def _open_button_fired(self):
        self._open_selected()

    def _search_fired(self):
        self._execute_query()

    def _omit_bogus_changed(self):
        self._execute_query()

    def _limit_changed(self):
        self._execute_query()

    def _column_clicked_changed(self, event):
        values = event.editor.value

        fields = [name for _, name in event.editor.adapter.columns]
        field = fields[event.column]
        self.reverse_sort = not self.reverse_sort

        self._sort_columns(values, field)

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

    def _get__parameters(self):

        b = self.query_table

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = f(b)
        return list(params)

    def _between(self, p, l, g):
        return '{}<="{}" AND {}>="{}"'.format(p, l, p, g)

    def _get_selector_records(self):
        pass

    def _get__join_table_parameters(self):
        pass

    def _load_hook(self):
        pass
#============= EOF =============================================

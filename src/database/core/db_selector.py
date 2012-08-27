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
    Dict, Property, Bool, Int, Enum

from traitsui.api import View, Item, TabularEditor, EnumEditor, ButtonEditor, \
    HGroup, VGroup, spring, ListEditor, InstanceEditor, Spring
#============= standard library imports ========================
from datetime import datetime, timedelta
#============= local library imports  ==========================
from src.helpers.datetime_tools import  get_date
from src.loggable import Loggable
from src.database.core.database_adapter import DatabaseAdapter
from src.database.core.base_results_adapter import BaseResultsAdapter
from src.graph.time_series_graph import TimeSeriesGraph


#@todo: added multiple parameter queries

from traits.api import HasTraits
from pyface.timer.do_later import do_later
class TableSelector(HasTraits):
    parameter = String
    parameters = Property

    def _get_parameters(self):
        params = [
                'Material',
                'Sample',
                'Detector',
                'IrradiationPosition',
                ]
        self.parameter = params[0]
        return params

    def traits_view(self):
        v = View(Item('parameter',
                      show_label=False,
                       editor=EnumEditor(name='parameters')),
                 buttons=['OK', 'Cancel'],
                 kind='livemodal'
                 )
        return v

class Query(HasTraits):
    parameter = String
    parameters = Property

    comparator = Str('=')
    comparisons = List(['=', '<', '>', '<=', '>=', '!=',
                         'like',
                         'contains'
                         ])
    criteria = String('this month')
    query_table = Any

    parent = Any
    add = Button('+')
    remove = Button('-')
    removable = Bool(True)

    def _get_parameters(self):

        b = self.query_table

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = list(f(b))
        self.parameter = params[0]
        return params

    def _add_fired(self):

        g = TableSelector()
        info = g.edit_traits()
        if info.result:
            self.parent.add_query(g.parameter)

    def _remove_fired(self):
        self.parent.remove_query(self)

    def traits_view(self):
        qgrp = HGroup(
                Item('parameter', editor=EnumEditor(name='parameters'), width= -150),
                spring,
                Item('comparator', editor=EnumEditor(name='comparisons')),
                Item('criteria'),
                Item('add'),
                Spring(springy=False,
                       width=50, visible_when='not removable'),
                Item('remove', visible_when='removable'),
                show_labels=False
                )
        v = View(qgrp)
        return v


class DBSelector(Loggable):
#    parameter = String
#    _parameters = Property

    join_table_parameter = String
    _join_table_parameters = Property
    join_table_col = String
    join_table = String

#    comparator = Str('=')
#    _comparisons = List(['=', '<', '>', '<=', '>=', '!=',
#                         'like',
#                         'contains'
#                         ])
#    criteria = String('this month')
    results = List

    search = Button
    open_button = Button
    open_button_label = 'Open'

    _db = DatabaseAdapter

#    dclicked = Event
    dclicked = Any
    selected = Any
#    activated = Any
#    selected_row = Int
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

    limit = Int(30)
    date_str = 'rundate'

    multi_select_graph = Bool(False)
    multi_graphable = Bool(False)

    queries = List(Query)

    style = Enum('normal', 'simple')

    def __init__(self, *args, **kw):
        super(DBSelector, self).__init__(*args, **kw)
        self._load_hook()

#    def _activated_changed(self):
#        print self.activated
#        if self.activated:
#            print self.activated.rid
#
#    def _selected_changed(self):
#        print self.selected

    def _queries_default(self):
        return [self._query_factory(removable=False)]

    def _query_factory(self, removable=True, table=None):
        if table is None:
            table = self.query_table
        else:
            table = '{}Table'.format(table)
            m = __import__(self.orm_path, fromlist=[table])
            table = getattr(m, table)

        q = Query(parent=self,
                  removable=removable,
                  query_table=table)
        return q

    def add_query(self, table):
        self.queries.append(self._query_factory(table=table))

    def remove_query(self, q):
        self.queries.remove(q)

    def load_recent(self):
#        self._execute_query(
#                            param='{}.{}'.format(self.query_table.__tablename__,
#                                           'id'),
#                            comp='=',
#                            criteria='1')
        try:
            self._execute_query(
                            param='{}.{}'.format(self.query_table.__tablename__,
                                           self.date_str),
                            comp='=',
                            criteria='this month'
                            )
        except AttributeError:
            pass

    def _get_button_grp(self):
        return HGroup(
                        Item('open_button', editor=ButtonEditor(label_value='open_button_label'),
                             show_label=False),
                        spring, Item('search', show_label=False), defined_when='style=="normal"')

    def traits_view(self):

#        qgrp = HGroup(
#                Item('parameter', editor=EnumEditor(name='_parameters')),
#                Item('comparator', editor=EnumEditor(name='_comparisons')),
#                Item('criteria'),
#                show_labels=False
#                )
        qgrp = Item('queries', show_label=False,
                    style='custom',
                    editor=ListEditor(mutable=False,
                                      style='custom',
                                      editor=InstanceEditor()),
                     defined_when='style=="normal"')
#        jt = self._get__join_table_parameters()
##        print jt
#        if jt is not None:
#            qgrp = VGroup(
#                      Item('join_table_parameter',
#                           label='Device',
#                            editor=EnumEditor(name='_join_table_parameters'),
#                           ),
#                      qgrp
#                      )

        editor = TabularEditor(adapter=self.tabular_adapter(),
                               dclicked='object.dclicked',
                               selected='object.selected',
#                               activated='object.activated',
#                               selected_row='selected_row',
                               column_clicked='object.column_clicked',
                               editable=False,
                               operations=['move', ],
                               multi_select=True
                               )
        button_grp = self._get_button_grp()
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
                 button_grp,

                 resizable=True,
                 width=600,
                 height=650,
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
        try:
            return [desc(getattr(self.query_table, attr)) for attr in ['rundate', 'runtime']]
        except AttributeError:
            pass

    def _execute_query(self, param=None, comp=None, criteria=None):
        if param is None:
            param = self.parameter
        self.parameter = param
        if comp is None:
            comp = self.comparator
        self.comparator = comp

        if criteria is None:
            criteria = self.criteria
        self.criteria = criteria

        db = self._db
        if db is not None:

            s = self._get_filter_str(param, comp, criteria)
            if s is None:
                return

            kw = dict(filter_str=s,
                      limit=self.limit,
                      order=self._get_order()
                      )
#            table, _ = param.split('.')
#            if not table == self.query_table.__tablename__:
#                kw['join_table'] = table

#            elif self.join_table:
#                kw['join_table'] = self.join_table
#                kw['filter_str'] = s + ' and {}.{}=="{}"'.format(self.join_table,
#                                                               self.join_table_col,
#                                                                        self.join_table_parameter
#                                                                        )


            dbs = self._get_selector_records(**kw)

            self.info('query {} returned {} results'.format(s,
                                    len(dbs) if dbs else 0))
            self.results = []
            if dbs:
                for di in dbs:
                    d = self._result_factory(di)
#                    d = self.result_klass(_db_result=di)
                    d.load()
                    d._loadable = True
                    self.results.append(d)
#                    if d.isloadable() or not self.omit_bogus:
#                        self.results.append(d)

            self._sort_columns(self.results)

#            self.activated = self.results[-1:]
#            self.selected = self.results[-1:]
#            self.selected_row = 10
#            f = lambda: self.trait_set(selected=self.results[30:31],
#                                       activated=self.results[30:31]
#                                       )
#
#            do_later(f)
#            
    def _result_factory(self, di, **kw):
        return self.result_klass(_db_result=di, **kw)

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

        wid = '.'.join([str(si.rid) for si in s])
        did = ', '.join([str(si.rid) for si in s])
        graph.window_title = '{} {}'.format(si.title_str, did)

        info = graph.edit_traits()

        self._open_window(wid, info)

    def _open_individual(self, s):
        for si in s:
            if not si._loadable:
                continue

            sid = si.rid
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
                    self._open_window(si.rid, info)
                except Exception, e:
                    import traceback
                    traceback.print_exc()
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

#    def _dclicked_fired(self):
    def _dclicked_changed(self):
        self._open_selected()

    def _open_button_fired(self):
        self._open_selected()

#    def _search_fired(self):
#        self._execute_query()
#
#    def _omit_bogus_changed(self):
#        self._execute_query()
#
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



    def _between(self, p, l, g):
        return '{}<="{}" AND {}>="{}"'.format(p, l, p, g)

    def _get_selector_records(self):
        pass

    def _get__join_table_parameters(self):
        pass

    def _load_hook(self):
        pass
#============= EOF =============================================

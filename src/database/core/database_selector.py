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
from traits.api import Button, List, Any, Dict, Bool, Int, Enum

from traitsui.api import View, Item, ButtonEditor, \
    HGroup, spring, ListEditor, InstanceEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
from src.database.core.base_results_adapter import BaseResultsAdapter
from src.graph.time_series_graph import TimeSeriesGraph

import os
from src.database.core.query import Query
from src.viewable import Viewable

from traits.api import HasTraits
from src.traits_editors.tabular_editor import myTabularEditor

class ColumnSorterMixin(HasTraits):
    _sort_field = None
    _reverse_sort = False
    column_clicked = Any

    def _column_clicked_changed(self, event):
        values = event.editor.value

        fields = [name for _, name in event.editor.adapter.columns]
        field = fields[event.column]
        self._reverse_sort = not self._reverse_sort

        self._sort_columns(values, field)

    def _sort_columns(self, values, field=None):
        #get the field to sort on
        if field is None:
            field = self._sort_field
            if field is None:
                return

        values.sort(key=lambda x: getattr(x, field),
                    reverse=self._reverse_sort)
        self._sort_field = field


class DatabaseSelector(Viewable, ColumnSorterMixin):
    results = List

    search = Button
    open_button = Button
    open_button_label = 'Open'

    _db = DatabaseAdapter

    dclicked = Any
    selected = Any
    scroll_to_row = Int
#    activated = Any
    selected_row = Any

    wx = 0.4
    wy = 0.1
    opened_windows = Dict
    title = ''

    tabular_adapter = BaseResultsAdapter

    query_table = None
    result_klass = None

    omit_bogus = Bool(True)

    limit = Int(30)
    date_str = 'rundate'

    multi_select_graph = Bool(False)
    multi_graphable = Bool(False)

    queries = List(Query)

    style = Enum('normal', 'panel', 'simple')

    data_manager = None

    def __init__(self, *args, **kw):
        super(DatabaseSelector, self).__init__(*args, **kw)
        self._load_hook()

#    def _activated_changed(self):
#        print self.activated
#        if self.activated:
#            print self.activated.rid
#
#    def _selected_changed(self):
#        print self.selected


    def add_query(self, table):
        self.queries.append(self._query_factory(table=table))

    def remove_query(self, q):
        self.queries.remove(q)

    def load_recent(self):
        dbs = self._get_recent()
        self.load_results(dbs)

    def execute_query(self, filter_str=None):
        dbs = self._execute_query(filter_str)
        self.load_results(dbs)

    def get_recent(self):
        return self._get_recent()
#===============================================================================
# private
#===============================================================================
    def _get_recent(self):
        param = '{}.{}'.format(self.query_table.__tablename__, self.date_str)
        comp = '='
        criterion = 'this month'
        q = self.queries[0]
        q.parameter = param
        q.comparator = comp
        q.criterion = criterion
        fs = q.get_filter_str()
        return self._execute_query(fs)

    def _generate_filter_str(self):
        qs = 'and '.join([q.get_filter_str() for q in self.queries])
        return qs

    def _execute_query(self, filter_str):
#        db = self._db
        if filter_str is None:
            filter_str = self._generate_filter_str()

        query_dict = dict(filter_str=filter_str,
                      limit=self.limit,
                      order=self._get_order()
                      )

        dbs = self._get_selector_records(**query_dict)

        self.info('query {} returned {} results'.format(query_dict['filter_str'],
                                len(dbs) if dbs else 0))
        return dbs

    def load_results(self, dbs):
        self.results = []
        self._load_results(dbs)
        self._sort_columns(self.results)

#        self.selected = self.results[-1:]
        self.scroll_to_row = len(self.results)
#        self.selected_row = [29, 30]#len(self.results) - 1
#        print self.scroll_to_row
#        print self.selected
#        print self.selected_row

    def _load_results(self, results):
        db = self._db
        if results:
            for di in results:
                d = self._result_factory(di,
                                         root=os.path.dirname(db.name))
#                    d = self.result_klass(_db_result=di)
                d.load()
                d._loadable = True
                self.results.append(d)

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

    def _get_order(self):
        from sqlalchemy.sql.expression import desc
        try:
            return [desc(getattr(self.query_table, attr)) for attr in ['rundate', 'runtime']]
        except AttributeError:
            pass

    def _get_selector_records(self):
        pass

    def _load_hook(self):
        pass


#===============================================================================
# handlers
#===============================================================================
    def _dclicked_changed(self):
        self._open_selected()

    def _open_button_fired(self):
        self._open_selected()

    def _search_fired(self):
        self.execute_query()

    def _limit_changed(self):
        self.execute_query()

#===============================================================================
# factories
#===============================================================================
    def _query_factory(self, removable=True, table=None):
        if table is None:
            table = self.query_table
        else:
            table = '{}Table'.format(table)
            m = __import__(self.orm_path, fromlist=[table])
            table = getattr(m, table)

        q = Query(parent=self,
                  removable=removable,
                  query_table=table,
                  date_str=self.date_str
                  )
        return q

    def _result_factory(self, di, **kw):
        return self.result_klass(_db_result=di,
                                 selector=self,
                                 **kw)

#===============================================================================
# views
#===============================================================================
    def _get_button_grp(self):
        return HGroup(
                        Item('open_button', editor=ButtonEditor(label_value='open_button_label'),
                             show_label=False),
                        spring, Item('search', show_label=False), defined_when='style=="normal"')

    def panel_view(self):
        v = self._view_factory()
        return v

    def traits_view(self):
        v = self._view_factory()
        v.title = self.title
        v.width = 600
        v.height = 650
        v.x = 0.1
        v.y = 0.1

        return v

    def _view_factory(self):
        editor = myTabularEditor(adapter=self.tabular_adapter(),
                               dclicked='object.dclicked',
                               selected='object.selected',
                               auto_update=True,
                               column_clicked='object.column_clicked',
                               editable=False,
                               operations=[
#                                           'move', 
#                                           'drag'
                                           ],
                               multi_select=True,

                               )

        button_grp = self._get_button_grp()
        qgrp = Item('queries', show_label=False,
                    style='custom',
                    editor=ListEditor(mutable=False,
                                      style='custom',
                                      editor=InstanceEditor()),
                     defined_when='style in ["normal","panel"]')
        v = View(
#                 HGroup(Item('multi_select_graph',
#                             defined_when='multi_graphable'
#                             ),
#                             spring, Item('limit')),
                 Item('results',
                      style='custom',
                      editor=editor,
                      show_label=False,
                      height= -400,
                      width= -300,
                      ),

                 qgrp,
                 button_grp,

                 resizable=True,
                 )
        return v

#===============================================================================
# defaults
#===============================================================================
    def _queries_default(self):
        return [self._query_factory(removable=False)]


#============= EOF =============================================
#        if criteria is None:
#            criteria = self.criteria
#        self.criteria = criteria
#
#        db = self._db
#        if db is not None:
#
#            s = self._get_filter_str(param, comp, criteria)
#            if s is None:
#                return

#            kw = dict(filter_str=s,
#                      limit=self.limit,
#                      order=self._get_order()
#                      )
#            table, _ = param.split('.')
#            if not table == self.query_table.__tablename__:
#                kw['join_table'] = table

#            elif self.join_table:
#                kw['join_table'] = self.join_table
#                kw['filter_str'] = s + ' and {}.{}=="{}"'.format(self.join_table,
#                                                               self.join_table_col,
#                                                                        self.join_table_parameter
#                                                                        )

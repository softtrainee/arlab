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
from traits.api import Button, List, Any, Dict, Bool, Int, Enum, Event

from traitsui.api import View, Item, ButtonEditor, \
    HGroup, spring, ListEditor, InstanceEditor, Handler, VGroup
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
from pyface.timer.do_later import do_later

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


class SelectorHandler(Handler):
    def init(self, info):
        pass
##        if info.initialized:
#        import wx
#        for control in info.ui.control.GetChildren()[0].GetChildren():
#            if isinstance(control, wx.Button):
#                if control.GetLabel() == 'Search':
#                    control.Bind(wx.EVT_KEY_DOWN, info.object.onKeyDown)
#                    control.SetFocus()
#                    info.ui.control.SetDefaultItem(control)
#                    break

class DatabaseSelector(Viewable, ColumnSorterMixin):
    records = List

    search = Button
    open_button = Button
    open_button_label = 'Open'

    db = DatabaseAdapter

    dclicked = Any
    selected = Any
    scroll_to_row = Int
#    activated = Any
    update = Event
    selected_row = Any

    wx = 0.4
    wy = 0.1
    opened_windows = Dict
    title = ''

    tabular_adapter = BaseResultsAdapter

    query_table = None
    record_klass = None

    omit_bogus = Bool(True)

    limit = Int(200)
    date_str = 'Run Date'

    multi_select_graph = Bool(False)
    multi_graphable = Bool(False)

    queries = List(Query)

    style = Enum('normal', 'panel', 'simple', 'single')

    data_manager = None
    verbose = False
    def onKeyDown(self, evt):
        import wx
        print evt
        if evt.GetKeyCode() == wx.WXK_RETURN:
            print 'ffoasdf'
        evt.Skip()
    def _selected_changed(self):
        if self.selected:
            sel = self.selected
            if self.style != 'single':
                sel = sel[0]
            self.selected_row = self.records.index(sel)
            self.update = True

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

    def query_factory(self, **kw):
        return self._query_factory(**kw)

    def add_query(self, table):
        self.queries.append(self._query_factory(table=table))

    def remove_query(self, q):
        self.queries.remove(q)

    def load_recent(self):
        dbs = self._get_recent()
        self.load_records(dbs, load=False)

    def load_last(self, n=None):
        dbs, _stmt = self._get_selector_records(limit=n)
        self.load_records(dbs, load=False)

#    def execute_query(self, filter_str=None):
    def execute_query(self, queries=None, load=True):
        dbs = self._execute_query(queries)
        self.load_records(dbs, load=load)

    def get_recent(self):
        return self._get_recent()
#===============================================================================
# private
#===============================================================================
    def _get_recent(self):
        #param = '{}.{}'.format(self.query_table.__tablename__, self.date_str)
        comp = '='
        criterion = 'this month'
        q = self.queries[0]
        q.parameter = self.date_str
        q.comparator = comp
#        q.criterion = criterion
        q.trait_set(criterion=criterion, trait_change_notify=False)

        return self._execute_query(queries=[q])

#    def _generate_filter_str(self):
#        qs = 'and '.join([q.get_filter_str() for q in self.queries])
#        return qs

    def _execute_query(self, queries=None):
#        db = self.db
#        if filter_str is None:
#            filter_str = self._generate_filter_str()
        if queries is None:
            queries = self.queries
        query_dict = dict(
#                          filter_str=filter_str,
                      limit=self.limit,
                      order=self._get_order(),
                      queries=queries
                      )

        dbs, query_str = self._get_selector_records(**query_dict)

        if not self.verbose:
            query_str = str(query_str)
            query_str = query_str.split('WHERE')[-1]
            query_str = query_str.split('ORDER BY')[0]

        self.info('query {} returned {} records'.format(query_str,
                                len(dbs) if dbs else 0))
        return dbs

    def load_records(self, dbs, load=True, append=False):
        if not append:
            self.records = []
        self._load_records(dbs, load)
        self._sort_columns(self.records)

#        self.selected = self.records[-1:]
        self.scroll_to_row = len(self.records)
#        self.selected_row = [29, 30]#len(self.records) - 1
#        print self.scroll_to_row
#        print self.selected
#        print self.selected_row

    def _load_records(self, records, load):
#        db = self.db
#        r = os.path.dirname(db.name)
        if records:
#            nd = [self._result_factory(di, root=r) for di in records]
            nd = [self._result_factory(di, load) for di in records]
            self.records.extend(nd)
#            for di in records:
#                r = os.path.dirname(db.name)
#                d = self._result_factory(di,
#                                         root=r
#                                         )
#                    d = self.record_klass(_db_result=di)


#                self.records.append(d)

    def _changed(self, new):
        db = self.db
        db.commit()

    def open_record(self, records):
        self._open_selected(records)

    def _open_selected(self, records=None):
        if records is None:
            records = self.selected

        if records is not None:

            if self.multi_select_graph:
                self._open_multiple(records)
            else:
                self._open_individual(records)

    def _open_multiple(self, s):
        graph = None
        xoffset = 0
        for si in s:
            if not si.loadable:
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
        if not isinstance(s, (list, tuple)):
            s = (s,)

        for si in s:

            if isinstance(si, str):
                di = self.db.get_analysis_uuid(si)
                si = self._result_factory(di, False)

            if not si.initialize():
                continue

            sid = si.record_id
            if sid in self.opened_windows:
                c = self.opened_windows[sid].control
                if c is None:
                    self.opened_windows.pop(sid)
                else:
                    do_later(c.Raise)

            else:
                try:
                    si.load_graph()
                    si.window_x = self.wx
                    si.window_y = self.wy
                    def do(si, sid):
                        info = si.edit_traits()
                        self._open_window(sid, info)

                    do_later(do, si, sid)

                except Exception, e:
                    import traceback
                    traceback.print_exc()
                    self.warning(e)

    def _open_window(self, wid, ui):
        self.opened_windows[wid] = ui
        self._update_windowxy()

        if self.db.application is not None:
            self.db.application.uis.append(ui)

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
        self.execute_query(load=False)

    def _limit_changed(self):
        self.execute_query(load=False)

#===============================================================================
# factories
#===============================================================================
    def _query_factory(self, removable=True, **kw):
        q = Query(selector=self,
                  removable=removable,
                  date_str=self.date_str,
                  )

        q.trait_set(trait_change_notify=False, **kw)
        return q

    def _result_factory(self, di, load, **kw):

        d = self.record_klass(_dbrecord=di,
                                 selector=self,
                                 **kw)
        if load:
            d.load()

        d.on_trait_change(self._changed, 'changed')
        return d
#===============================================================================
# views
#===============================================================================
    def _get_button_grp(self):
        return HGroup(spring, Item('search', show_label=False), defined_when='style=="normal"')

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
                               selected_row='object.selected_row',
                               update='update',
                               auto_update=True,
                               column_clicked='object.column_clicked',
                               editable=False,
                               multi_select=not self.style == 'single',

                               )

        button_grp = self._get_button_grp()
        qgrp = Item('queries', show_label=False,
                    style='custom',
                    height=0.25,
                    editor=ListEditor(mutable=False,
                                      style='custom',
                                      editor=InstanceEditor()),
                     defined_when='style in ["normal","panel"]')
        v = View(
#                 HGroup(Item('multi_select_graph',
#                             defined_when='multi_graphable'
#                             ),
#                             spring, Item('limit')),
                VGroup(
                       Item('records',
                          style='custom',
                          editor=editor,
                          show_label=False,
                          height=0.75,
                          width=600,
                          ),

                          qgrp,
                          button_grp,
                    ),
                 resizable=True,
                 handler=SelectorHandler
                 )

        if self.style == 'single':
            v.buttons = ['OK', 'Cancel']
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
#        db = self.db
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

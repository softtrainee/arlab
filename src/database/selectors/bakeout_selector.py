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
from traits.api import String, Instance, DelegatesTo
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.bakeout.bakeout_graph_viewer import BakeoutGraphViewer
from src.database.orms.bakeout_orm import BakeoutTable, ControllerTable
from .db_selector import DBSelector
from src.database.selectors.base_db_result import DBResult


class BakeoutDBResult(DBResult):
    title_str = 'Bakeout'

    viewer = Instance(BakeoutGraphViewer)
    graph = DelegatesTo('viewer')
    summary = DelegatesTo('viewer')
    export_button = DelegatesTo('viewer')

    def load_graph(self):
        self.viewer = BakeoutGraphViewer(title=self.title)
        p = os.path.join(self.directory,
                                      self.filename
                                      )
        self.viewer.load(p, dm=self.data_manager)

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

            self.data_manager = self._data_manager_factory()

#    def traits_view(self):
#        interface_grp = VGroup(
#                          VGroup(Item('_id', style='readonly', label='ID'),
#                    Item('rundate', style='readonly', label='Run Date'),
#                    Item('runtime', style='readonly', label='Run Time'),
#                    Item('directory', style='readonly'),
#                    Item('filename', style='readonly')),
#                VGroup(Item('summary',
#                            show_label=False,
#                            style='custom')),
#                       HGroup(spring, Item('export_button',
#                                            show_label=False),),
#                    label='Info',
#                    )
#
#        return View(
#                    Group(
#                    interface_grp,
#                    Item('graph', width=0.75, show_label=False,
#                         style='custom'),
#                    layout='tabbed'
#                    ),
#
#                    width=800,
#                    height=0.85,
#                    resizable=True,
#                    x=self.window_x,
#                    y=self.window_y,
#                    title=self.title
#                    )


class BakeoutDBSelector(DBSelector):
    parameter = String('BakeoutTable.rundate')
    date_str = 'rundate'
    query_table = 'BakeoutTable'
    result_klass = BakeoutDBResult

    def _get__parameters(self):

        b = BakeoutTable

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = f(b)
        c = ControllerTable
        params += f(c)
        return list(params)

    def _get_selector_records(self, **kw):
        return self._db.get_bakeouts(**kw)
#    def _dclicked_fired(self):
#        s = self.selected
#
#        if s is not None:
#            for si in s:
#                sid = si._id
#                if sid in self.opened_windows:
#                    c = self.opened_windows[sid].control
#                    if c is None:
#                        self.opened_windows.pop(sid)
#                    else:
#                        try:
#                            c.Raise()
#                        except:
#                            self.opened_windows.pop(sid)
#
#                else:
#                    try:
#                        si.load_graph()
#                        si.window_x = self.wx
#                        si.window_y = self.wy
#
#                        info = si.edit_traits()
#                        self.opened_windows[sid] = info
#
#                        self.wx += 0.005
#                        self.wy += 0.03
#
#                        if self.wy > 0.65:
#                            self.wx = 0.4
#                            self.wy = 0.1
#                    except Exception, e:
#                        self.warning(e)

#    def _execute_(self):
#        db = self._db
#        if db is not None:
##            self.info(s)
#            s = self._get_filter_str()
#            if s is None:
#                return
#
#            table, _col = self.parameter.split('.')
#            kw = dict(filter_str=s)
#            if not table == 'BakeoutTable':
#                kw['join_table'] = table
#
#            dbs = db.get_bakeouts(**kw)
#
#            self.info('query {} returned {} results'.format(s,
#                                    len(dbs) if dbs else 0))
#            if dbs:
#                self.results = []
#                for di in dbs:
#                    d = BakeoutDBResult(_db_result=di)
#                    d.load()
#                    self.results.append(d)

#============= EOF =============================================


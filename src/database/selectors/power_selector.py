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
from traits.api import String, Float
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector, DBResult
from src.database.orms.power_orm import PowerTable
from src.graph.graph import Graph
from src.managers.data_managers.h5_data_manager import H5DataManager

class PowerResult(DBResult):
    title_str = 'PowerRecord'
    request_power = Float

    def load_graph(self):

        g = Graph()
        dm = self.data_manager
        internal = dm.get_table('internal', 'Power')
        brightness = dm.get_table('brightness', 'Power')
        g.new_plot()

        xi, yi = zip(*[(r['time'], r['value']) for r in internal.iterrows()])
        g.new_series(xi, yi)
        xb, yb = zip(*[(r['time'], r['value']) for r in brightness.iterrows()])
        g.new_series(xb, yb)

        self.graph = g

    def _load_hook(self, dbr):
        data = os.path.join(self.directory, self.filename)
        dm = H5DataManager()
        if os.path.isfile(data):
            dm.open_data(data)

            tab = dm.get_table('internal', 'Power')
            if tab is not None:
                if hasattr(tab.attrs, 'request_power'):
                    self.summary = 'request power ={}'.format(tab.attrs.request_power)

        self.data_manager = dm

class PowerSelector(DBSelector):
    parameter = String('PowerTable.rundate')
    date_str = 'rundate'
    query_table = 'PowerTable'
    result_klass = PowerResult

    def _get__parameters(self):

        b = PowerTable

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = f(b)
        return list(params)

    def _get_selector_records(self, **kw):
        return self._db.get_power_records(**kw)

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
#            if not table == 'PowerTable':
#                kw['join_table'] = table
#
#            dbs = db.get_power_records(**kw)
#
#            self.info('query {} returned {} results'.format(s,
#                                    len(dbs) if dbs else 0))
#            if dbs:
#                self.results = []
#                for di in dbs:
#                    d = PowerResult(_db_result=di)
#                    d.load()
#                    self.results.append(d)

#============= EOF =============================================

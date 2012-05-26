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
from traits.api import String
from traitsui.api import View, Item, Group, VGroup
#============= standard library imports ========================
import os
import csv
#============= local library imports  ==========================
from .db_selector import DBSelector
from src.database.orms.power_map_orm import PowerMapTable
from src.database.selectors.base_db_result import DBResult


class PowerMapResult(DBResult):
    title_str = 'PowerMap'
    def load_graph(self):
        data = os.path.join(self.directory, self.filename)
        from src.data_processing.power_mapping.power_map_processor import PowerMapProcessor
        pmp = PowerMapProcessor()
        if data.endswith('.h5'):
            reader = self._data_manager_factory()
        else:
            with open(data, 'r') as f:
                reader = csv.reader(f)
                #trim off header
                reader.next()
        self.graph = pmp.load_graph(reader)


    def traits_view(self):
        interface_grp = VGroup(
                          VGroup(Item('_id', style='readonly', label='ID'),
                    Item('rundate', style='readonly', label='Run Date'),
                    Item('runtime', style='readonly', label='Run Time'),
                    Item('directory', style='readonly'),
                    Item('filename', style='readonly')),
                VGroup(Item('summary',
                            show_label=False,
                            style='readonly')),
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


class PowerMapSelector(DBSelector):
    parameter = String('PowerMapTable.rundate')
    date_str = 'rundate'
#    tabular_adapter = PowerMapResultsAdapter
    result_klass = PowerMapResult
    query_table = 'PowerMapTable'

    def _get__parameters(self):

        b = PowerMapTable

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = f(b)
        return list(params)

    def _get_selector_records(self, **kw):
        return self._db.get_powermaps(**kw)

#============= EOF =============================================

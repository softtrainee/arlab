#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, Long, Str, Any, Instance, Date, Time, \
    Button
from traitsui.api import View, Item, Group, HGroup, VGroup, spring
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.graph.graph import Graph
from src.managers.data_managers.h5_data_manager import H5DataManager


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
    exportable = True

    def _export_button_fired(self):
        self._export_csv()

    def _export_csv(self):
        p = os.path.join(self.directory, self.filename)
        if os.path.isfile(p) and self.graph is not None:
            self.graph.export_data(plotid=0)

    def initialize(self):
        pass

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
            _, ext = os.path.splitext(self.filename)
            if ext == '.h5':
                dm = H5DataManager()
                if os.path.isfile(data):
                    self._loadable = dm.open_data(data)
            else:
                self._loadable = False
                dm = CSVDataManager()

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
                                            show_label=False),
                       visible_when='object.exportable'
                       ),
                    label='Info',
                    )


        grps = Group(interface_grp, layout='tabbed')

        agrps = self._get_additional_tabs()
        if self.graph is not None:
            g = Item('graph',
                    show_label=False,
                    style='custom')

            agrps.append(g)

        for i, ai in enumerate(agrps):
            grps.content.insert(i, ai)

        return View(grps,

                    width=800,
                    height=0.85,
                    resizable=True,
                    x=self.window_x,
                    y=self.window_y,
                    title=self.title
                    )

class RIDDBResult(DBResult):
    runid = Str
#============= EOF =============================================

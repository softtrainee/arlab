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
from traits.api import HasTraits, Instance, Any, List, Str
from traitsui.api import View, Item, HSplit, VSplit, TableEditor
from traitsui.table_column import ObjectColumn

#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.graph.contour_graph import ContourGraph

from src.data_processing.power_mapping.power_map_processor import PowerMapProcessor
from src.loggable import Loggable
class DataFile(HasTraits):
    '''
    '''
    name = Str
    root = Str
    def __init__(self, root, name, *args, **kw):
        '''

        '''
        super(DataFile, self).__init__(*args, **kw)
        self.name = name
        self.root = root
    def get_path(self):
        '''
        '''
        return os.path.join(self.root, self.name)
class DataTable(HasTraits):
    '''
    '''
    name = Str
    table = Any
    def __init__(self, name, table, *args, **kw):
        '''
        '''
        super(DataTable, self).__init__(*args, **kw)
        self.name = name
        self.table = table

class PowerMapViewer(Loggable):
    '''
    '''
    graph = Instance(ContourGraph)
    data_files = List
    data_tables = List

    _selected_file = Any
    _selected_table = Any
    _processor = Instance(PowerMapProcessor)
    def __selected_file_changed(self):
        '''
        '''
        if self._selected_file is not None:

            p = self._selected_file.get_path()

            names, tables = self._processor._get_tables(path=p)


            tables = [DataTable(tab, tables[tab]) for tab in names]
            self.data_tables = tables
            self._selected_table = tables[0]

    def __selected_table_changed(self):
        '''
        '''
        if self._selected_table is not None:
#            n = self._selected_file.name
#            r = self._selected_file.root
            self.graph = self._processor.load_graph(self._selected_table.table)

    def set_data_files(self, root):
        '''
        '''
        files = os.listdir(root)
        files = [DataFile(root, f) for f in files
                    if not os.path.basename(f).startswith('.') and
                        os.path.isfile(os.path.join(root, f)) ]

        self.data_files = files
#============= views ===================================
    def traits_view(self):
        '''
        '''
        graph = Item('graph', show_label=False, style='custom',
                   width=0.85)
        cols = [ObjectColumn(name='name'), ]
        ftable_editor = TableEditor(columns=cols,
                                 editable=False,
                                 selected='_selected_file')
        ttable_editor = TableEditor(columns=cols,
                                 editable=False,
                                 selected='_selected_table')
        data = VSplit(Item('data_files', editor=ftable_editor, show_label=False),
                    Item('data_tables', editor=ttable_editor, show_label=False))

        v = View(
                 HSplit(data, graph),
               resizable=True,
               width=900,
               height=700,
               title='Power Map Viewer')
        return v
    def __processor_default(self):
        '''
        '''
        return PowerMapProcessor()
#============= EOF ====================================

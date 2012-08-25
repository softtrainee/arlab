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
from traits.api import HasTraits, Instance, Any, List, Str, Enum
from traitsui.api import View, Item, TreeEditor, TreeNode
#============= standard library imports ========================
#============= local library imports  ==========================
#from src.managers.manager import Manager
#from src.arar.arar_engine import ArArEngine
from src.envisage.core.envisage_editor import EnvisageEditor
from src.arar.workspace import  ArArWorkspace
from src.arar.nodes.experiment import ExperimentNode
from src.arar.nodes.analysis import AnalysisNode
import os
from src.paths import paths
from src.envisage.core.envisage_manager import EnvisageManager
from src.arar.nodes.series import SeriesNode

class ArArEditor(EnvisageEditor):
    '''
    '''
    id_name = 'ArAr'
    view_name = 'graph_view'


class Engine(HasTraits):
    name = Str('foo')
    workspaces = List(ArArWorkspace)

class ArArManager(EnvisageManager):
#    engine = Instance(ArArEngine)
    engine = Instance(Engine)
    workspace = Instance(ArArWorkspace)

    selection = Any
    selected = Any
    mode = Enum('sample', 'runid')

    def _active_workspace(self, ws):
        w = self.application.workbench.windows[0]
#                w.active_editor = w.editors[0]
#                w.active_part = w.editors[0]   
        ind = self.engine.workspaces.index(ws)
        try:
            w.activate_editor(w.editors[ind])
        except IndexError:
            pass
#===============================================================================
# handlers
#===============================================================================
    def _workspace_changed(self):
        self._active_workspace(self.workspace)

    def _selected_changed(self):
        selected = self.selected
        if selected:
            if isinstance(selected, ArArWorkspace):
                self.workspace = self.selected
            else:
                if not self.workspace.has_node(selected):
                    for ws in self.engine.workspaces:
                        if ws.has_node(selected):
                            self.workspace = ws
                            break

                graph = selected.replot()
                if graph:
                    self.workspace.graph = graph
                if isinstance(selected, ExperimentNode):
                    self.workspace.current_experiment = self.selected

    def update_db_selection(self, obj, name, old, new):

        if self.selection:
            if self.mode == 'runid':
                self.workspace.add_analysis(self.selection)
            else:
                self.workspace.add_sample(self.selection[0])
        self._selected_changed()

    def update_db_selected(self, obj, name, old, new):
        self.selection = new

    def _pre_open(self):
        db = self.application.get_service('src.database.adapters.massspec_database_adapter.MassSpecDatabaseAdapter')
        db.selector.on_trait_change(self.update_db_selection, 'add_selection_changed')
        db.selector.on_trait_change(self.update_db_selected, 'selected')


    def demo_open(self):
        self._pre_open()

        for i in range(2):
            self.new_workspace(name='Workspace {:02n}'.format(i))

        for ws in self.engine.workspaces:
            ws.new_experiment('newexp', kind='ideogram')

            self.application.workbench.edit(ws,
                                           kind=ArArEditor,
                                           use_existing=False
                                           )

    def new_engine(self):
        self.engine = Engine()

    def new_workspace(self, name=None):
        db = self.application.get_service('src.database.adapters.massspec_database_adapter.MassSpecDatabaseAdapter')
        ws = ArArWorkspace(db=db)
        if name is not None:
            ws.name = name

        ws.root = os.path.join(paths.arar_dir, ws.name)
        ws.init()

        self.engine.workspaces.append(ws)
        self.workspace = ws
        return ws

#    def traits_view(self):
#        return View(Item('engine', style='custom', show_label=False))

    def traits_view(self):
        nodes = [
#            TreeNode(node_for=[Engine],
#                     label='name'
#                     ),
#
            TreeNode(node_for=[Engine],
                     children='workspaces',
                     label='=workspaces',
                     auto_open=True
                     ),

               TreeNode(
                        node_for=[ArArWorkspace],
                        label='name',
                        ),
               TreeNode(
                        node_for=[ArArWorkspace],
                        children='experiments',
                        label='=experiments',
                        auto_open=True,
                        ),
               TreeNode(
                        node_for=[ExperimentNode],
                        label='name',
                        ),
               TreeNode(
                        node_for=[ExperimentNode],
                        children='analyses',
                        label='=analyses',
                        auto_open=True,
                        ),
               TreeNode(
                        node_for=[ExperimentNode],
                        children='series',
                        label='=series',
                        auto_open=True,
                        ),
#               TreeNode(
#                        node_for=[ExperimentNode],
#                        children='blank_series',
#                        label='=blanks',
#                        auto_open=True,
#                        ),
                TreeNode(node_for=[AnalysisNode],
                         label='rid',
                         ),
                TreeNode(node_for=[SeriesNode],
                         label='name',
                         ),
                TreeNode(node_for=[SeriesNode],
                        children='analyses',
                        label='=analyses',
                        auto_open=True,
                         )
               ]

        tree_editor = TreeEditor(nodes=nodes,
                                 editable=False,
                                 selected='selected',
                                 hide_root=True,
                                 lines_mode='on'
                                 )
        v = View(Item('engine',
                      show_label=False,
                      height= -1.0,
                      editor=tree_editor
                      ),
                 width=500,
                 height=500,
                 resizable=True
                 )
        return v


#============= EOF =============================================

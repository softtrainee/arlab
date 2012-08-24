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
from traits.api import Instance, Any, Enum
from traitsui.api import View, Item, TreeEditor, TreeNode
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.graph.graph import Graph
from src.paths import paths
from src.loggable import Loggable
from src.arar.workspace import Workspace
from src.arar.nodes.api import AnalysisNode, ExperimentNode
from src.database.core.database_adapter import DatabaseAdapter


class ArArEngine(Loggable):
    name = 'ArAr Engine'

    workspace = Instance(Workspace)
    graph = Instance(Graph)

    db = Instance(DatabaseAdapter)
    selected = Any

    def new_workspace(self, name=None):
        self.workspace = ws = Workspace()
        if name is not None:
            ws.name = name

        ws.root = os.path.join(paths.arar_dir, ws.name)
        ws.init()
        return ws

    def add_data(self, data):
        exp = self.workspace.current_experiment
        db = self.db
        for d in data:
            ref = db.get_analysis(d.rid)
            irrad_pos = db.get_irradiation_position(ref.IrradPosition)
#
            arar_analysis = ref.araranalyses[-1]
            rid = ref.RID
            kwargs = dict(
                        sample=ref.sample.Sample,
                        irradiation=irrad_pos.IrradiationLevel,
                        age=arar_analysis.Age,
                        age_err=arar_analysis.ErrAge
                        )
            exp.load_database_reference(ref, rid, kwargs)

        #refresh the plot
        self._selected_changed()
#===============================================================================
# handlers
#===============================================================================
    def _selected_changed(self):
        selected = self.selected
        if selected and not isinstance(selected, Workspace):
            graph = selected.replot()
            if graph:
                self.graph = graph
            if isinstance(selected, ExperimentNode):
                self.workspace.current_experiment = self.selected

#===============================================================================
# factories
#===============================================================================
    def _graph_factory(self, shape):
        g = Graph(container_dict=dict(type='g',
                                      shape=shape,
                                      bgcolor='gray',
                                      padding=10
                                      ),
                  )
        return g
#===============================================================================
# defaults
#===============================================================================
    def _workspace_default(self):
        return Workspace()

    def _graph_default(self):
        return self._graph_factory((1, 1))
#===============================================================================
# views
#===============================================================================
#    def configure_view(self):
#        v = View()
#        return v

    def graph_view(self):
        v = View(Item('graph',
                      show_label=False,
                      style='custom'))
        return v
    def traits_view(self):
        nodes = [
               TreeNode(
                        node_for=[Workspace],
                        label='name',
                        ),
               TreeNode(
                        node_for=[Workspace],
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
                        children='experiments',
                        label='=experiments',
                        auto_open=True,
                        ),
                TreeNode(node_for=[AnalysisNode],
                         label='rid',
                         )
               ]

        tree_editor = TreeEditor(nodes=nodes,
                                 editable=False,
                                 selected='selected',
                                 hide_root=True,
                                 lines_mode='on'
                                 )
        v = View(Item('workspace',
                      show_label=False,
                      height= -1.0,
                      editor=tree_editor
                      ),
                 width=500,
                 height=500,
                 resizable=True
                 )
        return v
if __name__ == '__main__':
    m = ArArEngine()
    m.workspace = Workspace()
    m.configure_traits()
#============= EOF =============================================

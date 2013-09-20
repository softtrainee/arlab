#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import on_trait_change
from src.envisage.tasks.editor_task import EditorTask
from src.processing.tasks.recall.recall_editor import RecallEditor
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from pyface.tasks.task_layout import Splitter, TaskLayout, PaneItem
from src.processing.tasks.analysis_edit.panes import ControlsPane
from src.processing.tasks.analysis_edit.plot_editor_pane import PlotEditorPane
from src.loading.actions import SaveLoadingAction
from pyface.tasks.action.schema import SToolBar
from pyface.tasks.action.task_action import TaskAction
from pyface.image_resource import ImageResource
from src.paths import paths
#============= standard library imports ========================
#============= local library imports  ==========================

class AddIsoEvoAction(TaskAction):
    method = 'add_iso_evo'
    image = ImageResource(name='chart_curve_add.png',
                        search_path=paths.icon_search_path
                        )

class RecallTask(AnalysisEditTask):
    name = 'Recall'

    tool_bars = [
                 SToolBar(AddIsoEvoAction(),
                          image_size=(16, 16)
                          )
                 ]

    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.recall',
#                          left=Splitter(
#                                     PaneItem('pychron.analysis_edit.unknowns'),
#                                     orientation='vertical'
#                                     ),
                          left=Splitter(
                                         PaneItem('pychron.search.results'),
                                         PaneItem('pychron.search.query'),
                                         orientation='vertical'
                                         ),
                          right=Splitter(
                                         PaneItem('pychron.analysis_edit.controls'),
                                         PaneItem('pychron.processing.editor'),
                                         orientation='vertical'
                                         ),

#                                     PaneItem('pychron.pyscript.editor')
#                                     ),
#                          top=PaneItem('pychron.pyscript.description'),
#                          bottom=PaneItem('pychron.pyscript.example'),

                          )

    def create_dock_panes(self):
        self.controls_pane = ControlsPane()
        self.plot_editor_pane = PlotEditorPane()
        panes = [
#                self._create_unknowns_pane(),
                self.controls_pane,
                self.plot_editor_pane

                ]
        ps = self._create_db_panes()
        if ps:
            panes.extend(ps)
        return panes

    def recall(self, records):

        ans = self.manager.make_analyses(records)

        def func(rec):
#             rec.load_isotopes()
            rec.calculate_age()
            reditor = RecallEditor(model=rec)
            self.editor_area.add_editor(reditor)
#             self.add_iso_evo(reditor.name, rec)

        if ans:
            for ri in ans:
                func(ri)
#             self.manager._load_analyses(ans, func=func)

            ed = self.editor_area.editors[-1]
            self.editor_area.activate_editor(ed)

    def add_iso_evo(self, name=None, rec=None):
        if rec is None:
            if self.active_editor is not None:
                rec = self.active_editor.model
                name = self.active_editor.name

        if rec is None:
            return

        from src.processing.tasks.isotope_evolution.isotope_evolution_editor import IsotopeEvolutionEditor
        ieditor = IsotopeEvolutionEditor(
                                        name='IsoEvo {}'.format(name),
                                        processor=self.manager,
                                        )

        ieditor.unknowns = [rec]
        self.editor_area.add_editor(ieditor)

#============= EOF =============================================

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
#============= standard library imports ========================
#============= local library imports  ==========================

class RecallTask(AnalysisEditTask):
    name = 'Recall'
    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.recall',
#                          left=Splitter(
#                                     PaneItem('pychron.analysis_edit.unknowns'),
#                                     orientation='vertical'
#                                     ),
                          left=Splitter(
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
        return [
#                self._create_unknowns_pane(),
                self._create_query_pane(),
                self.controls_pane,
                self.plot_editor_pane

                ]

    def recall(self, records):

        ans = self.manager.make_analyses(records)

        def func(rec):
            rec.initialize()
            reditor = RecallEditor(model=rec.isotope_record)


            from src.processing.tasks.isotope_evolution.isotope_evolution_editor import IsotopeEvolutionEditor
            ieditor = IsotopeEvolutionEditor(
                                            name='IsoEvo {}'.format(reditor.name),
                                            processor=self.manager,
                                            )
            ieditor.unknowns = [rec]
            self.editor_area.add_editor(reditor)
            self.editor_area.add_editor(ieditor)

        if ans:
            self.manager._load_analyses(ans, func=func)

            ed = self.editor_area.editors[-2]
            self.editor_area.activate_editor(ed)

#============= EOF =============================================

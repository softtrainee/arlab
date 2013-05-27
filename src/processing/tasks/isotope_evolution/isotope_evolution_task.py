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
from traits.api import HasTraits
from traitsui.api import View, Item
from src.envisage.tasks.editor_task import EditorTask
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from pyface.tasks.task_layout import PaneItem, Splitter, TaskLayout
# from src.processing.tasks.analysis_edit.adapters import UnknownsAdapter
from src.processing.tasks.analysis_edit.panes import UnknownsPane, ControlsPane
#============= standard library imports ========================
#============= local library imports  ==========================


class IsotopeEvolutionTask(AnalysisEditTask):
    iso_evo_editor_count = 1
    id = 'pychron.analysis_edit.isotope_evolution',

    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.analysis_edit.isotope_evolution',
                          left=Splitter(
                                     PaneItem('pychron.analysis_edit.unknowns'),
                                     PaneItem('pychron.analysis_edit.controls'),
                                     orientation='vertical'
                                     ),
                          right=Splitter(
                                         PaneItem('pychron.search.query'),
                                         PaneItem('pychron.search.results'),
                                         orientation='vertical'
                                         )

#                                     PaneItem('pychron.pyscript.editor')
#                                     ),
#                          top=PaneItem('pychron.pyscript.description'),
#                          bottom=PaneItem('pychron.pyscript.example'),


                          )

    def create_dock_panes(self):
        self.unknowns_pane = UnknownsPane(adapter_klass=self.unknowns_adapter)
        self.controls_pane = ControlsPane()
        return [

                self.unknowns_pane,
                self.controls_pane
                ]
#        panes = super(FluxTask, self).create_dock_panes()
#        return panes + [
#                      IrradiationPane(model=self.manager)
#                      ]
    def new_isotope_evolution(self):
        from src.processing.tasks.isotope_evolution.isotope_evolution_editor import IsotopeEvolutionEditor
        editor = IsotopeEvolutionEditor(name='Iso Evo {:03n}'.format(self.iso_evo_editor_count),
                              processor=self.manager
                              )
        selector = self.manager.db.selector

        selector.queries[0].criterion = 'NM-251'
        selector._search_fired()
        selector = self.manager.db.selector
        self.unknowns_pane.items = selector.records[150:160]
        editor.unknowns = self.unknowns_pane.items
        self._open_editor(editor)
        self.iso_evo_editor_count += 1
#============= EOF =============================================

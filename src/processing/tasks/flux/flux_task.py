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
from traits.api import HasTraits, on_trait_change, Property
from traitsui.api import View, Item
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem
from src.processing.tasks.flux.panes import IrradiationPane
from traitsui.tabular_adapter import TabularAdapter
from src.processing.tasks.analysis_edit.interpolation_task import InterpolationTask
#============= standard library imports ========================
#============= local library imports  ==========================
class LevelAdatper(TabularAdapter):
    columns = [('Run ID', 'name')]
    name_text = Property
    font = 'helvetica 10'
    def _get_name_text(self):
        return self.item.labnumber.identifier

class UnknownsAdapter(LevelAdatper):
    pass
class ReferencesAdapter(LevelAdatper):
    pass

class FluxTask(InterpolationTask):
    id = 'pychron.analysis_edit.flux'
    flux_editor_count = 1
    unknowns_adapter = UnknownsAdapter
    references_adapter = ReferencesAdapter

    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.analysis_edit',
                          left=Splitter(
                                     PaneItem('pychron.analysis_edit.unknowns'),
                                     PaneItem('pychron.analysis_edit.references'),
                                     PaneItem('pychron.analysis_edit.controls'),
                                     orientation='vertical'
                                     ),
                          right=Splitter(
                                         PaneItem('pychron.analysis_edit.irradiation'),
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
        panes = super(FluxTask, self).create_dock_panes()
        return panes + [
                      IrradiationPane(model=self.manager)
                      ]

    def new_flux(self):
        from src.processing.tasks.flux.flux_editor import FluxEditor
#        editor = FluxEditor(name='Flux {:03n}'.format(self.flux_editor_count),
#                              processor=self.manager
#                              )
#
#        self._open_editor(editor)

        from src.processing.tasks.flux.flux_editor import FluxEditor3D
        editor = FluxEditor3D(name='Flux3D {:03n}'.format(self.flux_editor_count),
                              processor=self.manager
                              )

        self._open_editor(editor)
        self.flux_editor_count += 1

    @on_trait_change('manager:level')
    def _level_changed(self, new):
        if new:
            level = self.manager.get_level(new)
            if self.active_editor:
                self.active_editor.level = level

            def monitor_filter(pos):
                if pos.labnumber.sample:
                    if pos.labnumber.sample.name == 'FC-2':
                        return True

            if level:
                positions = level.positions
                refs = []
                unks = []
                if positions:
                    for pi in positions:
                        if monitor_filter(pi):
                            refs.append(pi)
                        else:
                            unks.append(pi)

                self.unknowns_pane.items = unks
                self.references_pane.items = refs
#============= EOF =============================================

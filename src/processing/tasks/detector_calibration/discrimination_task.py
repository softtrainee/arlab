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
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem
from src.processing.tasks.analysis_edit.adapters import ReferencesAdapter
#============= standard library imports ========================
#============= local library imports  ==========================

class IntercalibrationFactorTask(AnalysisEditTask):
    id = 'pychron.analysis_edit.ic_factor'
    ic_factor_editor_count = 1
    references_adapter = ReferencesAdapter

    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.analysis_edit.ic_factor',
                          left=Splitter(
                                     PaneItem('pychron.analysis_edit.unknowns'),
                                     PaneItem('pychron.analysis_edit.references'),
                                     PaneItem('pychron.analysis_edit.controls'),
                                     orientation='vertical'
                                     ),
                          right=Splitter(
                                         PaneItem('pychron.search.query'),
                                         PaneItem('pychron.search.results'),
                                         orientation='vertical'
                                         )
                          )
    def new_ic_factor(self):
        from src.processing.tasks.detector_calibration.intercalibration_factor_editor import IntercalibrationFactorEditor
        editor = IntercalibrationFactorEditor(name='ICFactor {:03n}'.format(self.ic_factor_editor_count),
                                              processor=self.manager
                                              )
        self._open_editor(editor)
        self.ic_factor_editor_count += 1

        selector = self.manager.db.selector
        self.unknowns_pane.items = selector.records[156:159]
        self.references_pane.items = selector.records[150:155]

#============= EOF =============================================

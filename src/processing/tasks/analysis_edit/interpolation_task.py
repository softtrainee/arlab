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
from traits.api import HasTraits, Instance, on_trait_change
from traits.api import Any
from traitsui.api import View, Item
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from src.processing.tasks.analysis_edit.panes import ReferencesPane
from src.processing.tasks.analysis_edit.adapters import ReferencesAdapter
#============= standard library imports ========================
#============= local library imports  ==========================

class InterpolationTask(AnalysisEditTask):
    references_pane = Any
    references_adapter = ReferencesAdapter
    references_pane_klass = ReferencesPane

    def create_dock_panes(self):
        panes = super(InterpolationTask, self).create_dock_panes()
        self._create_references_pane()
        return panes + [self.references_pane]

    def _create_references_pane(self):
        self.references_pane = self.references_pane_klass(adapter_klass=self.references_adapter)
        self.references_pane.load()

    @on_trait_change('references_pane:[items, update_needed]')
    def _update_references_runs(self, obj, name, old, new):
        if not obj._no_update:
            if self.active_editor:
                self.active_editor.references = self.references_pane.items

    @on_trait_change('references_pane:previous_selection')
    def _update_rp_previous_selection(self, obj, name, old, new):
        print new
        self._set_previous_selection(obj, new)
#============= EOF =============================================

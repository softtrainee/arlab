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
from traits.api import HasTraits, Instance, on_trait_change, List
from src.envisage.tasks.editor_task import EditorTask
from src.processing.tasks.analysis_edit.panes import UnknownsPane, \
    ReferencesPane, ControlsPane
from src.processing.tasks.search_panes import QueryPane, ResultsPane
from src.processing.tasks.analysis_edit.adapters import UnknownsAdapter
from pyface.tasks.task_window_layout import TaskWindowLayout
from src.database.records.isotope_record import IsotopeRecordView

#============= standard library imports ========================
#============= local library imports  ==========================

class AnalysisEditTask(EditorTask):
    unknowns_pane = Instance(UnknownsPane)
    controls_pane = Instance(ControlsPane)
    results_pane = Instance(ResultsPane)

    unknowns_adapter = UnknownsAdapter

    def create_dock_panes(self):
        selector = self.manager.db.selector
        selector.queries[0].criterion = 'NM-251'
        selector._search_fired()

        self.unknowns_pane = UnknownsPane(adapter_klass=self.unknowns_adapter)
        self.controls_pane = ControlsPane()
        self.results_pane = ResultsPane(model=selector)

        return [
                self.unknowns_pane,
                self.controls_pane,
                self.results_pane,
                QueryPane(model=selector),
                ]

    def _active_editor_changed(self):
        if self.active_editor:
            if self.controls_pane:
                tool = None
                if hasattr(self.active_editor, 'tool'):
                    tool = self.active_editor.tool
                self.controls_pane.tool = tool

    @on_trait_change('unknowns_pane:items')
    def _update_unknowns_runs(self, obj, name, old, new):
        if not obj._no_update:
            if self.active_editor:
                self.active_editor.unknowns = self.unknowns_pane.items

    @on_trait_change('''unknowns_pane:dclicked, 
references_pane:dclicked,
manager:db:selector:dclicked
''')
    def _selected_changed(self, new):
        if new:
            if isinstance(new.item, IsotopeRecordView):
                self._open_recall_editor(new.item)

    def _open_recall_editor(self, recview):
        app = self.window.application
        _id = 'pychron.recall'
        for win in app.windows:
            if win.active_task.id == _id:
                win.activate()
                break
        else:
            win = app.create_window(TaskWindowLayout(_id))
            win.open()

        task = win.active_task
        task.recall([recview])

#    @on_trait_change('unknowns_pane:[+button]')
#    def _update_unknowns(self, name, new):
#        print name, new
#        '''
#            get selected analyses and append/replace to unknowns_pane.items
#        '''
#        sel = None
#        if sel:
#            if name == 'replace_button':
#                self.unknowns_pane.items = sel
#            else:
#                self.unknowns_pane.items.extend(sel)

#    @on_trait_change('references_pane:[+button]')
#    def _update_items(self, name, new):
#        print name, new
#        sel = None
#        if sel:
#            if name == 'replace_button':
#                self.references_pane.items = sel
#            else:
#                self.references_pane.items.extend(sel)

    @on_trait_change('controls_pane:save_button')
    def _save_fired(self):
        self._save_to_db()

    def _save_to_db(self):
        if self.active_editor:
            if hasattr(self.active_editor, 'save'):
                self.active_editor.save()


#===============================================================================
#
#===============================================================================



#============= EOF =============================================

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
from traits.api import Instance, on_trait_change, Any
from src.envisage.tasks.editor_task import BaseEditorTask
from src.processing.tasks.analysis_edit.panes import UnknownsPane, ControlsPane
from src.processing.tasks.search_panes import QueryPane
from src.processing.tasks.analysis_edit.adapters import UnknownsAdapter
from pyface.tasks.task_window_layout import TaskWindowLayout
from src.database.records.isotope_record import IsotopeRecordView
from src.processing.tasks.analysis_edit.plot_editor_pane import PlotEditorPane
from src.processing.analysis import Analysis

#============= standard library imports ========================
#============= local library imports  ==========================

class AnalysisEditTask(BaseEditorTask):
    unknowns_pane = Any
    controls_pane = Instance(ControlsPane)
#    results_pane = Instance(ResultsPane)
    plot_editor_pane = Instance(PlotEditorPane)
    unknowns_adapter = UnknownsAdapter
    unknowns_pane_klass = UnknownsPane
    def _save_file(self, path):
        if self.active_editor:
            self.active_editor.save_file(path)

    def prepare_destroy(self):
        if self.unknowns_pane:
            self.unknowns_pane.dump()

        if self.manager:
            self.manager.db.close()

    def create_dock_panes(self):

        self._create_unknowns_pane()

        self.controls_pane = ControlsPane()
        self.plot_editor_pane = PlotEditorPane()
        panes = [
                self.unknowns_pane,
                self.controls_pane,
                self.plot_editor_pane,
#                self.results_pane,
                ]
        cp = self._create_query_pane()
        if cp:
            panes.append(cp)
        return panes

    def _create_query_pane(self):
        if self.manager.db:
            selector = self.manager.db.selector
            selector._search_fired()

            from src.processing.selection.data_selector import DataSelector
            ds = DataSelector(database_selector=selector)

            return QueryPane(model=ds)

    def _create_unknowns_pane(self):
        self.unknowns_pane = up = self.unknowns_pane_klass(adapter_klass=self.unknowns_adapter)
        up.load()
        return up

    def _open_ideogram_editor(self, ans, name):
        _id = 'pychron.processing.figures'
        task = self._open_external_task(_id)
        task.new_ideogram(ans=ans, name=name)

    def _open_external_task(self, tid):
        app = self.window.application
        return app.open_task(tid)

    def _open_recall_editor(self, recview):
        _id = 'pychron.recall'
        task = self._open_external_task(_id)
        task.recall([recview])

    def _save_to_db(self):
        if self.active_editor:
            if hasattr(self.active_editor, 'save'):
                self.active_editor.save()

    def _set_previous_selection(self, pane, new):
        if new:
            db = self.manager.db
            def func(pi):
                iso = IsotopeRecordView(
                              graph_id=pi.graph_id,
                              group_id=pi.group_id
                              )
                dbrecord = db.get_analysis(pi.uuid, key='uuid')
                if iso.create(dbrecord):
                    return iso
#
            ps = [func(si) for si in new.analysis_ids]
            ps = [pi for pi in ps if pi]
            pane.items = ps
#===============================================================================
# handlers
#===============================================================================
    def _active_editor_changed(self):
        if self.active_editor:
            if self.controls_pane:
                tool = None
                if hasattr(self.active_editor, 'tool'):
                    tool = self.active_editor.tool
                self.controls_pane.tool = tool
                if hasattr(self.active_editor, 'unknowns'):
                    self.unknowns_pane.items = self.active_editor.unknowns

    @on_trait_change('active_editor:component_changed')
    def _update_component(self):
        if self.plot_editor_pane:
            self.plot_editor_pane.component = self.active_editor.component

    @on_trait_change('unknowns_pane:[items, update_needed]')
    def _update_unknowns_runs(self, obj, name, old, new):
#         print self.active_editor, obj, name, old, new
#         if not obj._no_update:
        if self.active_editor:

            self.active_editor.unknowns = self.unknowns_pane.items

    @on_trait_change('''unknowns_pane:dclicked, 
references_pane:dclicked,
manager:db:selector:dclicked
''')
    def _selected_changed(self, new):
        if new:
            if isinstance(new.item, (IsotopeRecordView, Analysis)):
                self._open_recall_editor(new.item)

    @on_trait_change('controls_pane:save_button')
    def _save_fired(self):
        self._save_to_db()
        if not self.controls_pane.dry_run:
            self.manager.db.commit()
            self.info('committing changes')
        else:
            self.info('dry run- not committing changes')

    @on_trait_change('unknowns_pane:previous_selection')
    def _update_up_previous_selection(self, obj, name, old, new):
        self._set_previous_selection(obj, new)

#===============================================================================
#
#===============================================================================
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


#============= EOF =============================================

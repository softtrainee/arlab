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
from traits.api import Instance, on_trait_change, Any, List
from src.envisage.tasks.editor_task import BaseEditorTask
from src.processing.tasks.analysis_edit.panes import UnknownsPane, ControlsPane, \
    TablePane
from src.processing.tasks.search_panes import QueryPane
from src.processing.tasks.analysis_edit.adapters import UnknownsAdapter
# from pyface.tasks.task_window_layout import TaskWindowLayout
from src.database.records.isotope_record import IsotopeRecordView
from src.processing.tasks.analysis_edit.plot_editor_pane import PlotEditorPane
from src.processing.analysis import Analysis
from src.processing.selection.data_selector import DataSelector

#============= standard library imports ========================
#============= local library imports  ==========================

class AnalysisEditTask(BaseEditorTask):
    unknowns_pane = Instance(TablePane)
    controls_pane = Instance(ControlsPane)
#    results_pane = Instance(ResultsPane)
    plot_editor_pane = Instance(PlotEditorPane)
    unknowns_adapter = UnknownsAdapter
    unknowns_pane_klass = UnknownsPane

    data_selector = Instance(DataSelector)
    _analysis_cache = List
    def _get_tagname(self):
        from src.processing.tasks.analysis_edit.tags import TagTableView
        db = self.manager.db
        with db.session_ctx():
            v = TagTableView()
            v.table.db = db
            v.table.load()

        info = v.edit_traits()
        if info.result:
            tag = v.selected
            return tag.name

    def set_tag(self):
        '''
            set tag for either
            
            analyses in a figure with temp_status==1
            if no analyses set all analyses to valid and remove tag
            
            analyses is the active_editor Analyses
            
            if tag is valid or invalid  set the status instead
        '''
        items = self.unknowns_pane.selected
#         items = self.active_editor._unknowns
        if items:
#             selection = [ai for ai in items if ai.temp_status]
#             if not selection:
#                 name = 'valid'
#                 selection = items
#             else:
            name = self._get_tagname()

            db = self.manager.db
            with db.session_ctx():
#                 if name in ('valid', 'invalid'):
#                     def func(it, x):
#                         self.debug('setting {} status= {}'.format(it.record_id, name))
#                         x.status = 0 if name == 'valid' else 1
#                         x.tag = ''
#                 else:
                def func(it, x):
                    self.debug('setting {} tag= {}'.format(it.record_id, name))
                    x.tag = name
                    it.tag = name
                    it.temp_status = 1 if name else 0

                for it in items:
                    ma = db.get_analysis_uuid(it.uuid)
                    func(it, ma)

            self.active_editor.rebuild(refresh_data=False)

    def prepare_destroy(self):
        if self.unknowns_pane:
            self.unknowns_pane.dump()

#         if self.manager:
#             self.manager.db.close()

    def create_dock_panes(self):

        self.unknowns_pane = self._create_unknowns_pane()

#         self.controls_pane = ControlsPane()
        self.plot_editor_pane = PlotEditorPane()
        panes = [
                self.unknowns_pane,
#                 self.controls_pane,
                self.plot_editor_pane,
#                self.results_pane,
                ]
        cp = self._create_control_pane()
        if cp:
            self.controls_pane = cp
            panes.append(cp)

        ps = self._create_db_panes()
        if ps:
            panes.extend(ps)

        return panes

    def _create_control_pane(self):
        return ControlsPane()

    def _create_db_panes(self):
        if self.manager.db:
            if self.manager.db.connected:
                selector = self.manager.db.selector
                selector._search_fired()

    #             from src.processing.selection.data_selector import DataSelector
    #             from src.processing.tasks.search_panes import ResultsPane

                ds = DataSelector(database_selector=selector)
                self.data_selector = ds
    #             return (QueryPane(model=ds), ResultsPane(model=ds))
                return QueryPane(model=ds),

    def _create_unknowns_pane(self):
        up = self.unknowns_pane_klass(adapter_klass=self.unknowns_adapter)
        up.load()
        return up

    def _open_ideogram_editor(self, ans, name, task=None):
        _id = 'pychron.processing.figures'
        task = self._open_external_task(_id)
        task.new_ideogram(ans=ans, name=name)
        return task

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

    def _record_view_factory(self, pi, **kw):
        db = self.manager.db
        iso = IsotopeRecordView(**kw)
        dbrecord = db.get_analysis(pi.uuid, key='uuid')
        if iso.create(dbrecord):
            return iso

    def _set_previous_selection(self, pane, new):
        if new:
            db = self.manager.db
            with db.session_ctx():
                func = self._record_view_factory
                ps = [func(si, graph_id=si.graph_id,
                                group_id=si.group_id) for si in new.analysis_ids]
                ps = [pi for pi in ps if pi]

                pane.items = self.manager.make_analyses(ps)

    def _save_file(self, path):
        if self.active_editor:
            self.active_editor.save_file(path)
            return True

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

            if self.unknowns_pane:
                self.unknowns_pane.previous_selection = ''
                if hasattr(self.active_editor, 'unknowns'):
                    if self.active_editor.unknowns:
                        self.unknowns_pane.items = self.active_editor.unknowns


    @on_trait_change('active_editor:component_changed')
    def _update_component(self):
        if self.plot_editor_pane:
            self.plot_editor_pane.component = self.active_editor.component

    @on_trait_change('unknowns_pane:[items, update_needed]')
    def _update_unknowns_runs(self, obj, name, old, new):
        if not obj._no_update:
            if self.active_editor:
#                 self.active_editor._unknowns = self.unknowns_pane.items
                self.active_editor.unknowns = self.unknowns_pane.items
                self._append_cache(self.active_editor)

    def _append_cache(self, editor):
        if hasattr(editor, 'unknowns'):
            ans = editor.unknowns
            ids = [ai.uuid for ai in self._analysis_cache]
            c = [ai for ai in ans if ai.uuid not in ids]

            if c:
                self._analysis_cache.extend(c)

        editor.analysis_cache = self._analysis_cache

    @on_trait_change('''unknowns_pane:dclicked, data_selector:selector:dclicked''')
    def _selected_changed(self, new):
        if new:
            if isinstance(new.item, (IsotopeRecordView, Analysis)):
                self._open_recall_editor(new.item)

    @on_trait_change('controls_pane:save_button')
    def _save_fired(self):
        db = self.manager.db
        commit = not self.controls_pane.dry_run
        with db.session_ctx(commit=commit):
            self._save_to_db()

        if commit:
            self.info('committing changes')
        else:
            self.info('dry run- not committing changes')

    @on_trait_change('unknowns_pane:previous_selection')
    def _update_up_previous_selection(self, obj, name, old, new):
        self._set_previous_selection(obj, new)

    @on_trait_change('unknowns_pane:[append_button, replace_button]')
    def _append_unknowns(self, obj, name, old, new):
        s = self.data_selector.selector.selected
        s = self.manager.make_analyses(s)

        if name == 'append_button':
            self.unknowns_pane.items.extend(s)
        else:
            self.unknowns_pane.items = s

    @on_trait_change('data_selector:selector:key_pressed')
    def _key_press(self, obj, name, old, new):
        '''
            use 'u' to add selected analyses to unknowns pane
        '''
        s = self.data_selector.selector.selected
        s = self.manager.make_analyses(s)

        if new and s:
            c = new.text
#             shift = new.shift
            if c == 'u':
                self.unknowns_pane.items.extend(s)
            elif c == 'U':
                self.unknowns_pane.items = s
            else:
                self._handle_key_pressed(c)

    def _handle_key_pressed(self, c):
        pass
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

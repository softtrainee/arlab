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
from traitsui.api import View, Item
from src.envisage.tasks.base_task import BaseManagerTask
from src.envisage.tasks.editor_task import EditorTask
from src.processing.tasks.analysis_edit.panes import UnknownsPane, \
    ReferencesPane, ControlsPane
from pyface.tasks.task_layout import TaskLayout, PaneItem, Tabbed, Splitter
#============= standard library imports ========================
#============= local library imports  ==========================

class AnalysisEditTask(EditorTask):
    unknowns_pane = Instance(UnknownsPane)
    references_pane = Instance(ReferencesPane)
    blank_editor_count = 1

    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.analysis_edit',
                          left=Splitter(
                                     PaneItem('pychron.analysis_edit.unknowns'),
                                     PaneItem('pychron.analysis_edit.references'),
                                     PaneItem('pychron.analysis_edit.controls'),
                                     orientation='vertical'
                                     ),
#                                     PaneItem('pychron.pyscript.editor')
#                                     ),
#                          top=PaneItem('pychron.pyscript.description'),
#                          bottom=PaneItem('pychron.pyscript.example'),


                          )

    def create_dock_panes(self):
        self.unknowns_pane = UnknownsPane()
        self.references_pane = ReferencesPane()
        self.controls_pane = ControlsPane()
        return [
                self.unknowns_pane,
                self.references_pane,
                self.controls_pane
                ]

    def new_blank(self):
        from src.processing.tasks.analysis_edit.blanks_editor import BlanksEditor
        editor = BlanksEditor(name='Blanks {:03n}'.format(self.blank_editor_count))
        self._open_editor(editor)
        self.blank_editor_count += 1

    def _active_editor_changed(self):
        if self.active_editor:
            self.controls_pane.tool = self.active_editor.tool



    @on_trait_change('unknowns_pane:[+button]')
    def _update_unknowns(self, name, new):
        print name, new
        '''
            get selected analyses and append/replace to unknowns_pane.items
        '''
        sel = None
        if sel:
            if name == 'replace_button':
                self.unknowns_pane.items = sel
            else:
                self.unknowns_pane.items.extend(sel)

    @on_trait_change('references_pane:[+button]')
    def _update_items(self, name, new):
        print name, new
        sel = None
        if sel:
            if name == 'replace_button':
                self.references_pane.items = sel
            else:
                self.references_pane.items.extend(sel)

#============= EOF =============================================

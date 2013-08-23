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
from traits.api import HasTraits, List, Str, Property, Any, cached_property
from traitsui.api import View, Item
from src.envisage.tasks.editor_task import EditorTask, BaseEditorTask
from src.processing.tasks.browser.panes import BrowserPane
from pyface.tasks.task_layout import TaskLayout, PaneItem
from src.processing.tasks.recall.recall_editor import RecallEditor
from src.experiment.utilities.identifier import make_runid, strip_runid
#============= standard library imports ========================
#============= local library imports  ==========================

class BrowserTask(BaseEditorTask):
    projects = List
    samples = Property(depends_on='selected_project')
    analyses = Property(depends_on='selected_sample')
    project_filter = Str
    sample_filter = Str

    selected_project = Any
    selected_sample = Any
    selected_analysis = Any

    def activated(self):
        editor = RecallEditor()
        self._open_editor(editor)

        ps = self.manager.db.get_projects()
        self.projects = [p.name for p in ps]


    def _default_layout_default(self):
        return TaskLayout(left=PaneItem('pychron.browswer'))

    def _selected_analysis_changed(self):
        if self.selected_analysis:
            s = self.selected_analysis
            l, a, s = strip_runid(s)
            an = self.manager.db.get_unique_analysis(l, a, s)
            an = self.manager.make_analyses([an])[0]
            an.load_isotopes(refit=False)
            self.active_editor.analysis_summary = an.analysis_summary

    @cached_property
    def _get_samples(self):
        samples = []
        if self.selected_project:
            samples = self.manager.db.get_samples(project=self.selected_project)
        return [s.name for s in samples]

    @cached_property
    def _get_analyses(self):
        ans = []
        if self.selected_sample:
            sample = self.manager.db.get_sample(self.selected_sample,
                                                project=self.selected_project
                                                )
            ans = [make_runid(ln.identifier,
                              a.aliquot, a.step) for ln in sample.labnumbers
                            for a in ln.analyses]
#             ans = self.manager.db.get_analyses(sample=self.s)
        return ans

    def create_dock_panes(self):
        return [BrowserPane(model=self)]


#============= EOF =============================================

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
from traits.api import HasTraits, List, Str, Bool, Any
from traitsui.api import View, Item
from pyface.tasks.task_layout import TaskLayout, PaneItem
from pyface.tasks.action.schema import SToolBar
from pyface.tasks.action.task_action import TaskAction
from pyface.image_resource import ImageResource
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.editor_task import BaseEditorTask
from src.processing.tasks.browser.panes import BrowserPane
from src.processing.tasks.recall.recall_editor import RecallEditor
from src.paths import paths
from src.database.orms.isotope_orm import gen_SampleTable, gen_ProjectTable
# from sqlalchemy.orm import subqueryload
from src.database.records.isotope_record import IsotopeRecordView
'''
add toolbar action to open another editor tab


'''
class NewBrowserEditorAction(TaskAction):
    method = 'new_editor'
    image = ImageResource(name='add.png',
                         search_path=[paths.resources,
                                      paths.app_resources
                                      ]
                         )
class SampleRecordView(HasTraits):
    name = Str
    material = Str
    def __init__(self, dbrecord):
        self._create(dbrecord)

    def _create(self, dbrecord):
        self.name = dbrecord.name
        if dbrecord.material:
            self.material = dbrecord.material.name

class BrowserTask(BaseEditorTask):
    projects = List
    oprojects = List

    samples = List  # Property(depends_on='selected_project')
    osamples = List

    analyses = List  # Property(depends_on='selected_sample')
    oanalyses = List

    project_filter = Str
    sample_filter = Str
    analysis_filter = Str

    selected_project = Any
    selected_sample = Any
    selected_analysis = Any
    dclicked_sample = Any

    omit_bogus = Bool(False)

    tool_bars = [SToolBar(NewBrowserEditorAction(),
                          image_size=(16, 16)
                          )]

    def activated(self):
        editor = RecallEditor()
        self._open_editor(editor)
        self.load_projects()

    def load_projects(self):
        db = self.manager.db
        with db.session_ctx():
            ps = db.get_projects()
            self.projects = [p.name for p in ps]
            self.oprojects = [p.name for p in ps]

    def new_editor(self):
        editor = RecallEditor()
        self._open_editor(editor)

    def _default_layout_default(self):
        return TaskLayout(left=PaneItem('pychron.browser'))

    def _selected_analysis_changed(self):
        an = self.selected_analysis
        if an and isinstance(self.active_editor, RecallEditor):
#             l, a, s = strip_runid(s)
#             an = self.manager.db.get_unique_analysis(l, a, s)
            an = self.manager.make_analyses([an])[0]
            an.load_isotopes(refit=False)
            self.active_editor.analysis_summary = an.analysis_summary

#     @cached_property
#     def _get_samples(self):
#         samples = []
#         if self.selected_project:
#             samples = self.manager.db.get_samples(project=self.selected_project)
#         return [s.name for s in samples]

#     @cached_property
#     def _get_analyses(self):
#         ans = []
#         if self.selected_sample:
#             sample = self.manager.db.get_sample(self.selected_sample,
#                                                 project=self.selected_project
#                                                 )
#             ans = [make_runid(ln.identifier,
#                               a.aliquot, a.step) for ln in sample.labnumbers
#                             for a in ln.analyses]
# #             ans = self.manager.db.get_analyses(sample=self.s)
#         return ans

    def create_dock_panes(self):
        return [BrowserPane(model=self)]

#===============================================================================
# handlers
#===============================================================================
    def _selected_project_changed(self, new):
        if new:
            db = self.manager.db
            with db.session_ctx() as sess:
#                 q = sess.query(gen_SampleTable)
#                 q = q.join(gen_ProjectTable)
#                 q = q.filter(gen_ProjectTable.name == new)
#
#                 ss = q.all()
#                 print ss[0].material

#             with db.session_ctx():
#             with db.session_ctx
#                 q = sess.query(gen_SampleTable)
#                 q = q.join(gen_ProjectTable)

#                 q = q.filter(gen_ProjectTable.name == new)
#                 q = q.options(subqueryload(gen_SampleTable.material))

#                 ss = q.all()
                ss = db.get_samples(project=new)
#             sa = ss[0]
#             print sa.material
#                 def f(si):
#                     x = SampleRecordView()
#                     x.create(si)
#                     return x

                ss = [SampleRecordView(s) for s in ss]
#                 sss = [f(s) for s in ss]
                self.samples = ss
                self.osamples = ss
    #             self.analyses = []
    #             self.onalyses = []
                if ss:
                    self.selected_sample = ss[:1]

    def _get_sample_analyses(self, srv):
        db = self.manager.db
        with db.session_ctx():
            sample = db.get_sample(srv.name, project=self.selected_project)
            def f(ai):
                iso = IsotopeRecordView()
                iso.create(ai)
                return iso

            return [f(a) for ln in sample.labnumbers
                            for a in ln.analyses
                                ]

    def _selected_sample_changed(self, new):
        if new:
            ans = self._get_sample_analyses(new[0])


#             ans = self._get_sample_analyses(new[0])
            self.oanalyses = ans
#
            if self.omit_bogus:
                ans = filter(self._omit_bogus_filter, ans)
#
            self.analyses = ans
            if ans:
                self.selected_analysis = ans[0]

    def _filter_func(self, new):
        def func(x):
            return x.lower().startswith(new.lower())
        return func

    def _omit_bogus_filter(self, x):
        return x.status == 0

    def _project_filter_changed(self, new):
        self.projects = filter(self._filter_func(new), self.oprojects)

    def _sample_filter_changed(self, new):
        self.samples = filter(self._filter_func(new), self.osamples)

    def _analysis_filter_changed(self, new):
        self.analyses = filter(self._filter_func(new), self.oanalyses)

    def _omit_bogus_changed(self, new):
        if new:
            self.analyses = filter(self._omit_bogus_filter, self.oanalyses)
        else:
            self.analyses = self.oanalyses
#============= EOF =============================================

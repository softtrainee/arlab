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
from traits.api import Instance, HasTraits, Any
from pyface.tasks.action.schema import SToolBar
# from pyface.action.action import Action
# from pyface.tasks.action.task_action import TaskAction
# from pyface.tasks.task_layout import TaskLayout, PaneItem
# from pyface.timer.do_later import do_later
import time
import subprocess
# from pyface.tasks.action.schema import SToolBar
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.tasks.tables.laser_table_pdf_writer import LaserTablePDFWriter
from src.processing.tasks.tables.table_actions import  ToggleStatusAction, \
    SummaryTableAction, AppendSummaryTableAction, MakeTableAction
# from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from src.processing.tasks.browser.panes import BrowserPane, TableEditorPane
from src.processing.tasks.browser.browser_task import BrowserTask
from src.processing.tasks.tables.editors.laser_table_editor import LaserTableEditor
from src.processing.tasks.tables.table_task_editor import TableTaskEditor
from src.processing.tasks.tables.editors.adapters import TableBlank
from src.processing.tasks.tables.editors.summary_table_editor import SummaryTableEditor


from traits.api import Str, Float
from pyface.timer.do_later import do_later
from src.processing.analysis_means import Mean
from src.processing.tasks.tables.summary_table_pdf_writer import SummaryTablePDFWriter
class Summary(Mean):
    sample = Str
    material = Str
#     age = Float
#     age_error = Float

    irradiation = Str



class TableTask(BrowserTask):
    tool_bars = [
                 SToolBar(
                          MakeTableAction(),
                          ToggleStatusAction(),
                          SummaryTableAction(),
                          AppendSummaryTableAction(),
                          image_size=(32, 32)
                          ),
                 ]

    editor = Instance(TableTaskEditor, ())

    def activated(self):
        editor = LaserTableEditor()
        self._open_editor(editor)
        self.load_projects()

        self.selected_project = self.projects[2]
        self._dclicked_sample_changed('')

#         super(TableTask, self).activated()
#         self.make_laser_table()
    def _dclicked_sample_changed(self, new):

        man = self.manager

        ans = [ai for ai in self.analyses if not ai.step][:5]
        ans = man.make_analyses(ans)
        man.load_analyses(ans)

        aa = []
        for ai in ans:
            aa.append(ai)
            aa.append(TableBlank(analysis=ai))

        self.active_editor.oitems = aa
        self.active_editor.items = aa

        self.active_editor.name = self.selected_sample[0].name

#===============================================================================
# task actions
#===============================================================================

    def make_table(self):
        title = self.editor.make_title()

        p = self.active_editor.make_table(title)
        self.view_pdf(p)

    def toggle_status(self):
        for s in self.active_editor.selected:
            s.temp_status = int(not s.temp_status)

    def append_summary_table(self):
        do_later(self._append_summary_table)

    def _append_summary_table(self):
        ss = self.active_editor.items
        items = self._make_summary_table(ss)
        self.active_editor.items.extend(items)

    def open_summary_table(self):
        do_later(self._open_summary_table)

    def _open_summary_table(self):
        items = self._make_summary_table()
        editor = SummaryTableEditor(items=items,
                                    name='Summary')
        self._open_editor(editor)

    def _make_summary_table(self, pitems=None):

        def factory(s):
            sam = s.name
            if s.material:
                mat = s.material.name

            ans = self._get_sample_analyses(sam)
            ans = [ai for ai in ans if ai.step == ''][:5]
            ans = self.manager.make_analyses(ans)

            ref = ans[0]
            dbpos = ref.dbrecord.labnumber.irradiation_position
            pos = dbpos.position
            irrad = dbpos.level.irradiation.name
            level = dbpos.level.name
            irrad_str = '{} {}{}'.format(irrad, level, pos)
            ss = Summary(
                         sample=sam,
                         material=mat,
                         irradiation=irrad_str,
                         analyses=ans
                         )
            return ss

        if pitems is None:
            pitems = []

        def test(si):
            return next((ss for ss in pitems if ss.sample == si.name), None)

        items = [factory(si)
                    for si in self.selected_sample
                        if not test(si)]

        ans = [ai for si in items
                    for ai in si.analyses]

        self.manager.load_analyses(ans)
        return items

#     def make_laser_table(self):
#         ans = self.active_editor.items
#         if ans:
#             means = self.active_editor.means
#             ans = self.active_editor.clean_rows()
#
#             title = self.editor.make_title(ans)

#             ans = [ai for ai in ans if not isinstance(ai, TableBlank)]
#             t = LaserTablePDFWriter(
#                                     orientation='landscape'
#                                     )
#
#             t.col_widths = self._get_column_widths()
#
#             p = '/Users/ross/Sandbox/aaatable.pdf'
#
#             t.build(p, ans, means, title=title)

#             self._view_pdf(p)

#     def make_summary_table(self):
#         samples = self.active_editor.items
#         if samples:
#             title = self.editor.make_title(samples)
#
#             t = SummaryTablePDFWriter(
#                                     orientation='landscape'
#                                     )
#
#             t.col_widths = self._get_column_widths()
#
#             p = '/Users/ross/Sandbox/aaasumtable.pdf'
#
#             t.build(p, samples, title=title)
#
#             self._view_pdf(p)



#     def _view_pdf(self, p):
#         preview_path = '/Applications/Preview.app'
# #         acrobatPath = r'C:\Program Files\Adobe\Reader 9.0\Reader\AcroRd32.exe'
#         subprocess.call(['open', '-a', preview_path, p])

    def create_dock_panes(self):
        return [
                BrowserPane(model=self),
                TableEditorPane(model=self.editor)
                ]
#============= EOF =============================================

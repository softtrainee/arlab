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
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from pyface.tasks.action.schema import SToolBar
from pyface.action.action import Action
from pyface.tasks.action.task_action import TaskAction
from src.processing.tasks.tables.laser_table_pdf_writer import LaserTablePDFWriter
from src.processing.tasks.tables.table_actions import MakeLaserTableAction
from src.processing.tasks.browser.panes import BrowserPane
from src.processing.tasks.browser.browser_task import BrowserTask
from src.processing.tasks.tables.laser_table_editor import LaserTableEditor
from pyface.tasks.task_layout import TaskLayout, PaneItem
from pyface.timer.do_later import do_later
# from pyface.tasks.action.schema import SToolBar
#============= standard library imports ========================
#============= local library imports  ==========================



class TableTask(BrowserTask):
    tool_bars = [
                 SToolBar(MakeLaserTableAction(),
                          image_size=(32, 32)
                          ),

                 ]

    def activated(self):
        super(TableTask, self).activated()
        self.make_laser_table()

    def make_laser_table(self):
        self.selected_project = self.projects[2]
        if self.analyses:
            ans = self.analyses[:5]

            man = self.manager

            ans = man.make_analyses(ans)
            man.load_analyses(ans)

            editor = LaserTableEditor(analyses=ans)
            self._open_editor(editor)

            t = LaserTablePDFWriter(orientation='landscape')
            p = '/Users/ross/Sandbox/aaatable.pdf'
            t.build(p, ans)

#     def create_dock_panes(self):
#         return [
#                 BrowserPane(model=self)
#                 ]
#============= EOF =============================================

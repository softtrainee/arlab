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
# from traits.api import HasTraits
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem, HSplitter, Tabbed

from src.processing.tasks.analysis_edit.interpolation_task import InterpolationTask
from src.processing.tasks.analysis_edit.panes import ControlsPane
#============= standard library imports ========================
#============= local library imports  ==========================

class BlanksTask(InterpolationTask):
    id = 'pychron.analysis_edit.blanks'
    blank_editor_count = 1
    name = 'Blanks'
    default_reference_analysis_type = 'blank_unknown'

    def _default_layout_default(self):
        return TaskLayout(
            id='pychron.analysis_edit.blanks',
            left=HSplitter(
                Tabbed(
                    PaneItem('pychron.browser'),
                    PaneItem('pychron.search.query'),
                ),
                Tabbed(
                    PaneItem('pychron.analysis_edit.unknowns'),
                    PaneItem('pychron.analysis_edit.references'),
                    PaneItem('pychron.analysis_edit.controls')
                ),
            ),
        )

    def new_blank(self):
    #         self.manager.auto_blank_fit('NM-205', 'E', 'preceeding')

    #        for pi in level.positions:
    #            ln = pi.labnumber
    #            sample = ln.sample
    #            if sample.project.name in ('j', 'Minna Bluff'):
    #                for ai in ln.analyses:
    #                    self.manager.preceeding_blank_correct(ai)
    #         return

        from src.processing.tasks.blanks.blanks_editor import BlanksEditor

        editor = BlanksEditor(name='Blanks {:03n}'.format(self.blank_editor_count),
                              processor=self.manager,
                              task=self,
                              default_reference_analysis_type=self.default_reference_analysis_type)

        self._open_editor(editor)
        self.blank_editor_count += 1

#        selector = self.manager.db.selector
#        self.unknowns_pane.items = selector.records[156:159]
#        self.references_pane.items = selector.records[150:155]
#============= EOF =============================================

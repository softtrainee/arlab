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
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem

from src.processing.tasks.analysis_edit.interpolation_task import InterpolationTask
#============= standard library imports ========================
#============= local library imports  ==========================

class BlanksTask(InterpolationTask):
    id = 'pychron.analysis_edit.blanks'
    blank_editor_count = 1

    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.analysis_edit.blanks',
                          left=Splitter(
                                     PaneItem('pychron.analysis_edit.unknowns'),
                                     PaneItem('pychron.analysis_edit.references'),
                                     PaneItem('pychron.analysis_edit.controls'),
                                     orientation='vertical'
                                     ),
                          right=Splitter(
                                         PaneItem('pychron.search.query'),
                                         PaneItem('pychron.search.results'),
                                         orientation='vertical'
                                         )
                          )
    def new_blank(self):
        from src.processing.tasks.blanks.blanks_editor import BlanksEditor
        editor = BlanksEditor(name='Blanks {:03n}'.format(self.blank_editor_count),
                              processor=self.manager
                              )

        self._open_editor(editor)
        self.blank_editor_count += 1

#        selector = self.manager.db.selector
#        self.unknowns_pane.items = selector.records[156:159]
#        self.references_pane.items = selector.records[150:155]
#============= EOF =============================================

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
from traits.api import on_trait_change
from src.envisage.tasks.editor_task import EditorTask
from src.processing.tasks.recall.recall_editor import RecallEditor
#============= standard library imports ========================
#============= local library imports  ==========================

class RecallTask(EditorTask):
    name = 'Recall'

    def recall(self, records=None):
        if records is None:
            records = self.manager.recall()

        ans = self.manager.make_analyses(records)

        def func(rec):
            rec.initialize()
            editor = RecallEditor(model=rec.isotope_record)
            self.editor_area.add_editor(editor)

        if ans:
            self.manager._load_analyses(ans, func=func)

            ed = self.editor_area.editors[-1]
            self.editor_area.activate_editor(ed)

#============= EOF =============================================

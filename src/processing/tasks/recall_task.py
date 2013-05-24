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
from src.processing.tasks.recall_editor import RecallEditor
#============= standard library imports ========================
#============= local library imports  ==========================

class RecallTask(EditorTask):
    name = 'Recall'
#    record = Instance(IsotopeRecord)
#    display_item = Property(Instance(Any), depends_on='record, record:selected')
#    def create_central_pane(self):
#        pass
#        return DisplayPane(model=self)

#    def _record_default(self):
#        return IsotopeRecord()

    def recall(self):
        records = self.manager.recall()
        def func(rec):
            rec.initialize()
            editor = RecallEditor(model=rec.isotope_record)
            self.editor_area.add_editor(editor)

        if records:
            self.manager._load_analyses(records, func=func)

#            self.editor_area._activate_tab(-1)
            ed = self.editor_area.editors[-1]
            self.editor_area.activate_editor(ed)
#            self.manager._load_analyses()
#            for record in records:
#
#                irecord = record.isotope_record
#                self.manager._load_analyses()

#                irecord.initialize()
#                editor = RecallEditor(record=irecord)
#                self.editor_area.add_editor(editor)


#                self._open_editor(editor)
#                time.sleep(0.1)
#            print self.record.selected
#            print self.record.display_item
#            for ri in records:


#    def _get_display_item(self):
#        return self.record.display_item
#============= EOF =============================================

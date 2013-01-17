#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import Property, cached_property
from traitsui.api import View, Item, CodeEditor, TextEditor
from src.database.isotope_analysis.summary import Summary
from src.database.isotope_analysis.selectable_readonly_texteditor import SelectableReadonlyTextEditor

#============= standard library imports ========================
#============= local library imports  ==========================

class ScriptSummary(Summary):
    script_text = Property
    editor_klass = CodeEditor
    style = 'readonly'
    def traits_view(self):
        v = View(Item('script_text',
                      width=755,
                      style=self.style,
                      editor=self.editor_klass(), show_label=False))
        return v

class MeasurementSummary(ScriptSummary):
    @cached_property
    def _get_script_text(self):
        try:
            txt = self.record.dbrecord.measurement.script.blob
        except AttributeError:
            pass

        if txt is None:
            txt = 'No Measurement script saved with analysis'


        return txt

class ExtractionSummary(ScriptSummary):

    @cached_property
    def _get_script_text(self):
        try:
            txt = self.record.dbrecord.extraction.script.blob
        except AttributeError:
            pass
        if txt is None:
            txt = 'No Extraction script saved with analysis'
        return txt


class ExperimentSummary(ScriptSummary):
    editor_klass = SelectableReadonlyTextEditor
    style = 'custom'
    @cached_property
    def _get_script_text(self):
        try:
            txt = self.record.dbrecord.extraction.experiment.blob
        except AttributeError:
            pass

        if txt is None:
            txt = 'No Experiment Set saved with analysis'
        return txt

#============= EOF =============================================

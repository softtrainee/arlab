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
from traits.api import Bool, on_trait_change
from traitsui.wx.tabular_editor import TabularEditor as wxTabularEditor
from traitsui.editors.tabular_editor import TabularEditor

#============= standard library imports ========================
#============= local library imports  ==========================

class _TabularEditor(wxTabularEditor):

#    def init(self, parent):
#        wxTabularEditor.init(self, parent)

    def update_editor(self):
        control = self.control
        wxTabularEditor.update_editor(self)

        if self.factory.scroll_to_bottom:
            if not self.selected and not self.multi_selected:
                control.EnsureVisible(control.GetItemCount() - 1)
        else:
            if not self.selected and not self.multi_selected:
                control.EnsureVisible(0)

    def _key_down(self, event):
        key = event.GetKeyCode()
#        print event.GetModifiers()

        super(_TabularEditor, self)._key_down(event)

class myTabularEditor(TabularEditor):
    scroll_to_bottom = Bool(True)

    def _get_klass(self):
        return _TabularEditor
#============= EOF =============================================

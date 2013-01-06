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
from traits.api import List, Dict
from traitsui.wx.text_editor import CustomEditor
#============= standard library imports ========================
import wx
#============= local library imports  ==========================
from traitsui.editors.text_editor \
    import ToolkitEditorFactory

class _TextEditor(CustomEditor):
#    evaluate = evaluate_trait
#    parent = Any
    def init(self, parent):
        super(_TextEditor, self).init(parent)
        self.control.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        p = 0
        for i, l in enumerate(self.value.split('\n')):
            e = len(l)
            st = next((st for st in self.factory.styles if st == i or
                                                            (i in st if isinstance(st, tuple) else False)

                       ), None)

            if st:
                sa = self.factory.styles[st]
                self.control.SetStyle(p, p + e + 1, sa)
            p += e + 1


    def onKeyDown(self, event):
        if event.CmdDown():
            event.Skip()


class SelectableReadonlyTextEditor(ToolkitEditorFactory):
    tabs = List
    styles = Dict
    def _get_custom_editor_class(self):
        return _TextEditor
#============= EOF =============================================

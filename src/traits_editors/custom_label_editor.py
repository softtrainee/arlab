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
from traits.api import HasTraits, Str, Int, Color, Button, Any, Instance
from traitsui.api import View, Item, TableEditor, UItem, Label
from traitsui.wx.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
# from traitsui.wx.basic_editor_factory import BasicEditorFactory
import wx
import random
#============= standard library imports ========================
#============= local library imports  ==========================

class _CustomLabelEditor(Editor):
    txtctrl = Any

    def init(self, parent):
        self.control = self._create_control(parent)

    def update_editor(self):
        self.txtctrl.SetLabel(self.value)

    def _create_control(self, parent):
        panel = wx.Panel(parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        txtctrl = wx.StaticText(panel, label=self.value)
        family = wx.FONTFAMILY_DEFAULT
        style = wx.FONTSTYLE_NORMAL
        weight = wx.FONTWEIGHT_NORMAL
        font = wx.Font(self.item.size, family, style, weight)
        txtctrl.SetFont(font)
        txtctrl.SetForegroundColour(self.item.color)
        self.txtctrl = txtctrl

        sizer.Add(txtctrl)
        panel.SetSizer(sizer)
        return panel

class CustomLabelEditor(BasicEditorFactory):
    klass = _CustomLabelEditor


class CustomLabel(UItem):
    editor = Instance(CustomLabelEditor, ())
    size = Int
    color = Color('green')

#===============================================================================
# demo
#===============================================================================
class Demo(HasTraits):
    a = Str('asdfsdf')
    foo = Button
    def _foo_fired(self):
        self.a = 'fffff {}'.format(random.random())

    def traits_view(self):
        v = View(
                 'foo',
                 CustomLabel('a',
                             color='blue',
                             size=10), width=100,
                 height=100)
        return v

if __name__ == '__main__':
    d = Demo()
    d.configure_traits()
#============= EOF =============================================

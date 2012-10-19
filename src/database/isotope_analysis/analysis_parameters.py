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
from traits.api import HasTraits, Str, Enum, Float, Any, List
from traitsui.api import View, Item, HGroup, Label, Spring, EnumEditor
#============= standard library imports ========================
import wx
#============= local library imports  ==========================
from traitsui.api import CustomEditor
from traitsui.wx.enum_editor import ListEditor, SimpleEditor
from traitsui.editors.enum_editor \
    import ToolkitEditorFactory

class _BoundEnumEditor(SimpleEditor):
#class _BoundEnumEditor(ListEditor):
#class _BoundEnumEditor(CustomEditor):
    def init(self, parent):
#        super(_BoundEnumEditor, self).init(parent)

        self.control = control = wx.ComboBox(parent, -1, self.names[0],
                               wx.Point(0, 0),
                               wx.Size(-1, -1),
                                self.names,
                                style=wx.CB_DROPDOWN
                               )

#         wx.EVT_CHOICE(parent, self.control.GetId(), self.update_object)
        control.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
#        parent.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        parent.Bind(wx.EVT_COMBOBOX, self.update_object, control)

        self._no_enum_update = 0
        self.set_tooltip()
#        parent.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
#        self.control.Bind(wx.EVT_TEXT, None)
#        wx.EVT_CHOICE(parent, self.control.GetId(), None)
#        s = self.control.GetWindowStyle()
#        self.control.SetWindowStyle(s | wx.WANTS_CHARS)
#        self.control.Bind(wx.EVT_CHAR, self.onKeyDown)
#        parent.Bind(wx.EVT_CHAR, self.onKeyDown)
#        self.control.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)

#        print self.control
    def update_object(self, event):
        super(_BoundEnumEditor, self).update_object(event)
        if self._bind:
            for fi in self.object.analyzer.fits:
                fi.fit = self.value

        self._bind = False

    def onKeyDown(self, event):
#        print event.GetKeyCode()
        if event.CmdDown():
            self._bind = True
#        else:
#            self._bind = False
#        event.RequestMore()
#        event.Skip()

class BoundEnumEditor(ToolkitEditorFactory):
    evaluate = lambda x: x
    def _get_custom_editor_class(self):
        return _BoundEnumEditor

    def _get_simple_editor_class(self):
        return _BoundEnumEditor

class AnalysisParameters(HasTraits):
    fit = Str#Enum('linear', 'parabolic', 'cubic')
    filterstr = Str(enter_set=True, auto_set=False)
    name = Str
    intercept = Float
    error = Float
    analysis = Any
    fittypes = List(['linear', 'parabolic', 'cubic', 'averageSD', 'averageSEM'])
    def traits_view(self):
        v = View(HGroup(Label(self.name),
                        Spring(width=50 - 10 * len(self.name), springy=False),
                        Item('fit', editor=EnumEditor(name='fittypes'),
                             show_label=False),
#                        Item('fit[]', style='custom',
#                              editor=BoundEnumEditor(values=['linear', 'parabolic', 'cubic'],
#
#                                                     )),
                        Item('filterstr[]'),
                        Spring(width=50, springy=False),
                        Item('intercept', format_str='%0.5f',
                              style='readonly'),
                        Item('error', format_str='%0.5f',
                              style='readonly')
                        )
                 )
        return v
#============= EOF =============================================

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
from traits.api import Float
from traitsui.wx.editor import Editor

from traitsui.basic_editor_factory import BasicEditorFactory
#============= standard library imports ========================
import wx
#============= local library imports  ==========================
from matplotlib.cm import get_cmap

class Bar(wx.Control):
    value = None
    low = 0
    high = 1
    def __init__(self, parent, ident= -1):
        super(Bar, self).__init__(parent, ident, (0, 0), (100, 15), style=wx.NO_BORDER)
        self.Bind(wx.EVT_PAINT, self._on_paint, self)
        self._cmap = get_cmap('jet')

    def _on_paint(self, event):
        if self.value:
            dc = wx.PaintDC(self)
            dc.Clear()
            dc.BeginDrawing()
            dc.SetBrush(wx.Brush(self.value, wx.SOLID))
            dc.DrawRectangle(0, 0, 100, 15)
            dc.EndDrawing()
            del dc

    def set_value(self, v):
        nv = v / (self.high - self.low)
        vs = self._cmap(nv)[:3]
        self.value = map(lambda x:x * 255, vs)
        self.Refresh()


class _BarGaugeEditor(Editor):
    def init(self, parent):
        self.control = Bar(parent)
        self.control.low = self.factory.low
        self.control.high = self.factory.high

    def update_editor(self):
        self.control.set_value(self.value)

class BarGaugeEditor(BasicEditorFactory):
    klass = _BarGaugeEditor
    low = Float
    high = Float
#============= EOF =============================================

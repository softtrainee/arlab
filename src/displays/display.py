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
from traits.api import HasTraits, Instance, Int, Color, Str, List
from traitsui.api import View, Item, UItem
from src.lasers.scanner import ApplicationController
from src.ui.display_editor import DisplayEditor
#============= standard library imports ========================
#============= local library imports  ==========================
# from src.viewable import Viewable

class DisplayModel(HasTraits):
    messages = List
    max_messages = Int(300)
    def add_text(self, txt, color, **kw):
        ms = self.messages[-self.max_messages:]
        ms.append((txt, color))
        self.messages = ms

class DisplayController(ApplicationController):
    x = Int
    y = Int
    width = Int
    height = Int(500)
    title = Str

    default_color = Color
    default_size = Int
    bg_color = Color

    def add_text(self, txt, **kw):
        if 'color' not in kw:
            kw['color'] = self.default_color

        self.model.add_text(txt, **kw)

    def traits_view(self):
        v = View(UItem('messages', editor=DisplayEditor()),
                 x=self.x, y=self.y, width=self.width,
                 height=self.height)
        return v

    def close_ui(self):
        if self.info:
            if self.info.ui:
                self.info.ui.dispose()

class ErrorDisplay(DisplayController):
    pass
#============= EOF =============================================

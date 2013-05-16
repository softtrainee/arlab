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
from traits.api import HasTraits, Instance, Int, Color, Str, List, Tuple, Event
from traitsui.api import View, Item, UItem
from src.lasers.scanner import ApplicationController
from src.ui.display_editor import DisplayEditor
from src.deprecate import deprecated
#============= standard library imports ========================
#============= local library imports  ==========================
# from src.viewable import Viewable

class DisplayModel(HasTraits):
#     messages = List
#     max_messages = Int(300)
    message=Tuple
    clear_event=Event
    def add_text(self, txt, color, force=False,**kw):
        '''
            if txt,color same as previous txt,color than message only added if force=True
        '''
#         ms = self.messages[-self.max_messages:]
#         ms.append((txt, color))
        self.message = (txt,color, force)

class DisplayController(ApplicationController):
    x = Int
    y = Int
    width = Int
    height = Int(500)
    title = Str

    default_color = Color('black')
    default_size = Int
    bg_color = Color
    font_name=Str
    
    def __init__(self, *args, **kw):
        super(DisplayController, self).__init__(model=DisplayModel(),
                                                *args, **kw)
    
    def clear(self, **kw):
        self.model.clear_event=True
#         self.model.message=('%%clear%%',)
#         self.model.messages = []

    @deprecated
    def freeze(self):
        pass

    @deprecated
    def thaw(self):
        pass

    def add_text(self, txt, **kw):
        if 'color' not in kw or kw['color'] is None:
            kw['color'] = self.default_color

        self.model.add_text(txt, **kw)

    def traits_view(self):
        v = View(UItem('message', editor=DisplayEditor(bg_color=self.bg_color,
                                                       clear='clear_event'
                                                       )),
                 x=self.x, y=self.y, width=self.width,
                 height=self.height,
                 title=self.title)
        return v

    def close_ui(self):
        if self.info:
            if self.info.ui:
                self.info.ui.dispose()

class ErrorDisplay(DisplayController):
    pass


#============= EOF =============================================

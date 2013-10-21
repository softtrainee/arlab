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
from traits.api import HasTraits, Int, Color, Str, Event, Bool
from traitsui.api import View, UItem
from src.lasers.scanner import ApplicationController
from src.ui.display_editor import DisplayEditor
from src.deprecate import deprecated
from src.ui.gui import invoke_in_main_thread
#============= standard library imports ========================
from threading import Lock
from Queue import Queue
#============= local library imports  ==========================
# from src.viewable import Viewable

class DisplayModel(HasTraits):
#     messages = List
#     max_messages = Int(300)
#    message = Tuple
    clear_event = Event
    refresh = Event


    #    message = Queue
    def __init__(self, *args, **kw):
        super(DisplayModel, self).__init__(*args, **kw)

        self.qmessage = Queue()

    def add_text(self, txt, color, force=False, **kw):
        '''
            if txt,color same as previous txt,color than message only added if force=True
        '''
        #         ms = self.messages[-self.max_messages:]
        #         ms.append((txt, color))
        #        self.message = (txt, color, force)
        self.qmessage.put((txt, color, force))
        invoke_in_main_thread(self.trait_set, refresh=True)

        #        self.refresh = True


class DisplayController(ApplicationController):
    x = Int
    y = Int
    width = Int
    height = Int(500)
    title = Str

    default_color = Color('black')
    #    default_size = Int
    bg_color = Color
    font_name = Str
    font_size = Int(12)
    max_blocks = Int(0)

    editor_klass = DisplayEditor
    _lock = None
    visible = Bool

    opened = Bool(False)
    was_closed = Bool(False)
    text_added = Event

    def __init__(self, *args, **kw):
        super(DisplayController, self).__init__(model=DisplayModel(),
                                                *args, **kw)
        self._lock = Lock()

    def init(self, info):
        self.opened = True
        super(DisplayController, self).init(info)

    #        print 'rrrrr', info
    #        info.object.ui = info.ui

    def clear(self, **kw):
    #        self.clear_event = True
        self.model.clear_event = True

    #        self.model.clear_event = True
    #         self.model.message=('%%clear%%',)
    #         self.model.messages = []

    # @deprecated
    def freeze(self):
        pass

    # @deprecated
    def thaw(self):
        pass

    def add_text(self, txt, **kw):
        if 'color' not in kw or kw['color'] is None:
            kw['color'] = self.default_color

        with self._lock:
            self.model.add_text(txt, **kw)

        self.text_added = True


    def traits_view(self):
        self.visible = True
        v = View(UItem('qmessage', editor=self.editor_klass(bg_color=self.bg_color,
                                                            clear='clear_event',
                                                            refresh='refresh',
                                                            font_name=self.font_name,
                                                            font_size=self.font_size,
                                                            max_blocks=self.max_blocks
        )),
                 x=self.x, y=self.y, width=self.width,
                 height=self.height,
                 title=self.title)
        return v

    def close_ui(self):
        if self.info:
            if self.info.ui:
                self.info.ui.dispose()

    def closed(self, info, result):
        self.opened = False
        self.was_closed = True


#    def show(self):
#        if not self.visible:
#            invoke_in_main_thread(self.edit_traits)
#        elif self.info:
#            self.info.ui.control.raise_()


class ErrorDisplay(DisplayController):
    pass


#============= EOF =============================================

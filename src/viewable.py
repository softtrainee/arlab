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
from traits.api import HasTraits, Either, Int, Float, Any, Str, List
from traitsui.api import View, Item, TableEditor, Controller
from traitsui.api import Handler
from pyface.timer.do_later import do_after
#============= standard library imports ========================
#============= local library imports  ==========================

from src.loggable import Loggable


# class ViewableHandler(Controller):
class ViewableHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui
        try:
            info.object.opened()
        except AttributeError:
            pass

    def close(self, info, is_ok):
        return info.object.close(is_ok)

    def closed(self, info, is_ok):
        info.object.closed(is_ok)
        info.object.ui = None

class Viewable(Loggable):
    ui = Any
    id = ''
    handler_klass = ViewableHandler

    window_x = Either(Int, Float)
    window_y = Either(Int, Float)

    window_width = Either(Int, Float)
    window_height = Either(Int, Float)

    title = Str
    associated_windows = List

    def opened(self):
        pass

    def close(self, ok):
        return True

    def closed(self, ok):
        for ai in self.associated_windows:
            ai.close_ui()

        return True

    def close_ui(self):
        if self.ui is not None:
            # disposes 50 ms from now
            do_after(50, self.ui.dispose)
            # sleep a little so everything has time to update
            # time.sleep(0.05)

    def show(self, **kw):
        if self.ui is None or self.ui.control is None:
            func = lambda:do_after(10, self.edit_traits, **kw)
        else:
            func = lambda:do_after(10, self.ui.control.Raise)

        func()

    def view_factory(self, *args, **kw):
        if self.window_x:
            kw['x'] = self.window_x
        if self.window_y:
            kw['y'] = self.window_y
        if self.window_width:
            kw['width'] = self.window_width
        if self.window_y:
            kw['height'] = self.window_height

        if not 'resizable' in kw:
            kw['resizable'] = True

        if not 'title' in kw:
            kw['title'] = self.title

        if not 'id' in kw and self.id:
            kw['id'] = self.id

        return View(
                    handler=self.handler_klass,
#                    x=self.window_x,
#                    y=self.window_y,
#                    width=self.window_width,
#                    height=self.window_height,
#                    title=self.title,
#                    resizable=True,
                    *args,
                    **kw
                    )

    def _window_width_default(self):
        return 500

    def _window_height_default(self):
        return 500
    def _window_x_default(self):
        return 0.5

    def _window_y_default(self):
        return 0.5


#============= EOF =============================================

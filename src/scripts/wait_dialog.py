'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import HasTraits, Float, Property, Bool
from traitsui.api import View, Item, RangeEditor, Handler
from pyface.timer.timer import Timer

#============= standard library imports ========================

#============= local library imports  ==========================
class WDHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui

    def closed(self, info, is_okd):
        info.object.closed()
        return True
class WaitDialog(HasTraits):
    condition = None
    wtime = Float
    low_name = Float(2)
    current_time = Property(depends_on = '_current_time')
    _current_time = Float
    auto_start = Bool(True)
    timer = None
    title = 'Wait'
    def __init__(self, *args, **kw):
        super(WaitDialog, self).__init__(*args, **kw)
        self._current_time = self.wtime
        if self.auto_start:
            self.timer = Timer(1000, self._update_time)

    def start(self, condition = None):
        self.condition = condition
        self.timer = Timer(1000, self._update_time)

    def _get_current_time(self):
        return self._current_time

    def _set_current_time(self, v):
        self._current_time = v

    def _current_time_changed(self):
        if self._current_time <= 0:
            if self.timer is not None:
                self.timer.Stop()

            try:
                self.condition.notify()
                self.condition.release()
            except (RuntimeError, AttributeError):
                pass

    def _update_time(self):
        if self._current_time == self.wtime:
            if self.condition is not None:

                self.condition.acquire()
        self._current_time -= 1

    def close(self):
        self.ui.dispose()

    def closed(self):
        self._current_time = -1

    def traits_view(self):

        kw = dict(buttons = ['Cancel'],
                  handler = WDHandler,
                  )
        if self.title is not None:
            kw['title'] = self.title
        return View(Item('current_time', show_label = False, editor = RangeEditor(mode = 'slider',
                                                           low_name = 'low_name',
                                                           high_name = 'wtime'
                                                           )),
                    **kw
#                    title = self.title,
#                    buttons = ['Cancel'],
#                    handler = WDHandler
                    )
#============= views ===================================
#============= EOF ====================================

#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import Float, Property, Bool, Str
from traitsui.api import View, Item, RangeEditor
from pyface.timer.timer import Timer
from traitsui.menu import Action
from src.viewable import ViewableHandler, Viewable

#============= standard library imports ========================

#============= local library imports  ==========================
class WDHandler(ViewableHandler):
#    def init(self, info):
#        info.object.ui = info.ui
#
#    def closed(self, info, is_ok):
#        info.object.closed(is_ok)
#        return True
#    def close(self, info, isok):
#        print 'close', isok
#        
#        return True

    def _continue(self, info):
        info.object._continue()

class WaitDialog(Viewable):
#    condition = None
    end_evt = None
    wtime = Float
    low_name = Float(2)
    current_time = Property(depends_on='_current_time')
    _current_time = Float
    auto_start = Bool(True)
    timer = None
    title = 'Wait'
    message = Str

    _continued = False
    _canceled = False

    window_width = Float(0.45)
    dispose_at_end = True

    def __init__(self, *args, **kw):
        super(WaitDialog, self).__init__(*args, **kw)
        self._current_time = self.wtime
        if self.auto_start:
#            if self.condition is not None:
#                self.condition.acquire()
            if self.end_evt is not None:
                self.end_evt.clear()
            self.timer = Timer(1000, self._update_time)

    def start(self, evt=None):
        evt.clear()
        self.end_evt = evt
#        self.condition = condition
#        if self.condition is not None:
#            self.condition.acquire()

        self.timer = Timer(1000, self._update_time)
        self._continued = False

    def stop(self):
        self._end()

    def _get_current_time(self):
        return self._current_time

    def _set_current_time(self, v):
        self._current_time = v

    def _current_time_changed(self):
        if self._current_time <= 0:
            self._end()
            self._canceled = False

    def _update_time(self):
        self._current_time -= 1

    def _end(self):
        if self.timer is not None:
            self.timer.Stop()
        if self.end_evt is not None:
            self.end_evt.set()

        if self.dispose_at_end:
            self.debug('disposing {}'.format(self))
            self.disposed = True

    def close(self, isok):
        super(WaitDialog, self).close(isok)
        self._canceled = not isok

        if self.timer is not None:
            self.timer.Stop()
        if self.end_evt is not None:
            self.end_evt.set()
        return True

#    def closed(self, isok):
#        self.debug('closed {}'.format(isok))
##        self._current_time = -1
##        self._end()
##        if isok is not None:
#
#        self._end()
#        return True
#
    def _continue(self):
        self._canceled = False
        self._continued = True
        self._end()
#        self.close(True)

    def traits_view(self):

        kw = dict(buttons=['Cancel',
                           Action(name='Continue',
                                  action='_continue')
                           ],
                  handler=WDHandler,
                  width=self.window_width
                  )
        if self.title is not None:
            kw['title'] = self.title

        return View(

                    Item('message', width=1.0, show_label=False, style='readonly'),
                    Item('current_time', show_label=False, editor=RangeEditor(mode='slider',
                                                           low_name='low_name',
                                                           high_name='wtime',
                                                           )),
                    **kw
#                    title = self.title,
#                    buttons = ['Cancel'],
#                    handler = WDHandler
                    )
#============= views ===================================
#============= EOF ====================================

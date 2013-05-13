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


from traits.etsconfig.etsconfig import ETSConfig
from src.helpers.timer import Timer
ETSConfig.toolkit = 'qt4'
from src.ui.gui import invoke_in_main_thread
#============= enthought library imports =======================
from traits.api import Float, Property, Bool, Str
from traitsui.api import View, Item, RangeEditor
# from pyface.timer.timer import Timer
from traitsui.menu import Action
from src.viewable import ViewableHandler, Viewable
from threading import Event
import time
from src.helpers import logger_setup
from src.helpers.logger_setup import logging_setup

#============= standard library imports ========================

#============= local library imports  ==========================
class WDHandler(ViewableHandler):
#    def init(self, info):
#        info.object.ui = info.ui
#
    def closed(self, info, is_ok):
        info.object.closed(is_ok)
        return True
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
#            if self.end_evt is not None:
#                self.end_evt.clear()
#            self.timer = Timer(1000, self._update_time)
            self.start(evt=self.end_evt)

    def start(self, evt=None):
        if evt:
            evt.clear()
            self.end_evt = evt
#        self.condition = condition
#        if self.condition is not None:
#            self.condition.acquire()
        self.timer = Timer(1000, self._update_time,
                           delay=1000)
#        self.timer = Timer(1000, self._update_time)
#        print self.timer
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

    def closed(self, isok):
        self._end()
        return True

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

from traits.api import HasTraits, Button
class Demo(HasTraits):
    test = Button
    def traits_view(self):
        v = View('test')
        return v

    def _test_fired(self):
        from src.ui.thread import Thread
        t = Thread(target=self._wait)
        t.start()
        self._t = t

    def _wait(self):
        timeout = 5
        message = 'foo'
        evt = Event()

        wd = WaitDialog(wtime=timeout,
                            end_evt=evt,
    #                        parent=self,
    #                        title='{} - Wait'.format(self.logger_name),
                            message='Waiting for {:0.1f}  {}'.format(timeout, message)
                            )
        invoke_in_main_thread(wd.edit_traits)
        evt.wait(timeout=timeout + 0.25)
#        wd.edit_traits(kind='livemodal')

#
#        from threading import Thread
#        def wait():
#            st = time.time()
#            t = 0
#            while t < (timeout + 0.25) and not evt.is_set():
#                time.sleep(0.5)
#                t = time.time() - st
# #
#
#        t = Thread(target=wait)
#        t.start()
#        t.join()
        print 'wati comi'

#        st = time.time()
#        t = 0
#        while t < (timeout + 0.25) and not evt.is_set():
#            time.sleep(0.5)
#            t = time.time() - st
#
# #        evt.wait(timeout=timeout + 0.25)
#        wd.stop()

if __name__ == '__main__':
    logging_setup('foo')
    Demo().configure_traits()
#============= views ===================================
#============= EOF ====================================

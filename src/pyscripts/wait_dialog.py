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


# from traits.etsconfig.etsconfig import ETSConfig
# ETSConfig.toolkit = 'qt4'
#============= enthought library imports =======================
from traits.api import Float, Property, Bool, Str, Button
from traitsui.api import View, Item, RangeEditor, spring, HGroup, VGroup, \
    UItem, Spring

#============= standard library imports ========================
from threading import Event
import time
#============= local library imports  ==========================
from src.helpers.timer import Timer
from src.loggable import Loggable
from src.ui.custom_label_editor import CustomLabel


class WaitDialog(Loggable):

    end_evt = None
    wtime = Float(10)
    low_name = Float(1)

    high = Float(10, enter_set=True, auto_set=False)

    current_time = Property(depends_on='_current_time')
    _current_time = Float
    auto_start = Bool(False)
    timer = None

    message = Str

    _continued = False
    _canceled = False

    window_width = Float(0.45)
    dispose_at_end = False

    cancel_button = Button('Cancel')
    continue_button = Button('Continue')

    def __init__(self, *args, **kw):
        self.reset()
        super(WaitDialog, self).__init__(*args, **kw)
        if self.auto_start:
            self.start(evt=self.end_evt)

    def reset(self):
        self.high = self.wtime
        self.current_time = self.wtime

    def was_canceled(self):
        return self._canceled

    def was_continued(self):
        return self._continued

    def start(self, block=True, evt=None):
        if evt is None:
            evt = Event()

        if evt:
            evt.clear()
            self.end_evt = evt

        self.timer = Timer(1000, self._update_time,
                           delay=1000)
        self._continued = False

        if block:
            while not evt.is_set():
                time.sleep(0.05)

    def stop(self):
        self._end()

    def _continue_button_fired(self):
        self._continue()

    def _cancel_button_fired(self):
        self._cancel()

    def _high_changed(self, v):
        self.wtime = v
        self._current_time = v

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

    def _end(self, dispose=True):
        self.message = ''

        if self.timer is not None:
            self.timer.Stop()
        if self.end_evt is not None:
            self.end_evt.set()

        if self.dispose_at_end and dispose:
            self.debug('disposing {}'.format(self))
            self.disposed = True


#    def close(self, isok):
#        super(WaitDialog, self).close(isok)
#        self._canceled = not isok
#        self._end(dispose=False)
    def _cancel(self):
        self._canceled = True
        self._end(dispose=False)

    def _continue(self):
        self._canceled = False
        self._continued = True
        self._end()
#        self.close(True)

    def traits_view(self):
        v = View(VGroup(
                        CustomLabel('message',
                                    size=14,
                                    weight='bold'
                                    ),
                        HGroup(
                               Spring(width=-5, springy=False),
                               Item('high', label='Set Max. Seconds'),
                               spring, UItem('continue_button')
                               ),
                        HGroup(
                               Spring(width=-5, springy=False),
                               Item('current_time', show_label=False, editor=RangeEditor(mode='slider',
                                                           low_name='low_name',
                                                           high_name='wtime',
                                                           ))
                               ),
                        ),
               )
        return v

# from traits.api import HasTraits, Button
# class Demo(HasTraits):
#     test = Button
#     def traits_view(self):
#         v = View('test')
#         return v
#
#     def _test_fired(self):
#         from src.ui.thread import Thread
#         t = Thread(target=self._wait)
#         t.start()
#         self._t = t
#
#     def _wait(self):
#         timeout = 50
#         message = 'foo'
#         evt = Event()
#         wd = WaitDialog(wtime=timeout,
#                             end_evt=evt,
#     #                        parent=self,
#     #                        title='{} - Wait'.format(self.logger_name),
#                             message='Waiting for {:0.1f}  {}'.format(timeout, message)
#                             )
#         invoke_in_main_thread(wd.edit_traits)
#         evt.wait(timeout=timeout + 0.25)
# #        print time.time() - st
#         print wd._canceled
#         print 'c', wd.was_canceled()
#         print 'o', wd.was_continued()
#
# #        wd.edit_traits(kind='livemodal')
#
# #
# #        from threading import Thread
# #        def wait():
# #            st = time.time()
# #            t = 0
# #            while t < (timeout + 0.25) and not evt.is_set():
# #                time.sleep(0.5)
# #                t = time.time() - st
# # #
# #
# #        t = Thread(target=wait)
# #        t.start()
# #        t.join()
#         print 'wati comi'
#
# #        st = time.time()
# #        t = 0
# #        while t < (timeout + 0.25) and not evt.is_set():
# #            time.sleep(0.5)
# #            t = time.time() - st
# #
# # #        evt.wait(timeout=timeout + 0.25)
# #        wd.stop()
#
# if __name__ == '__main__':
# #     logging_setup('foo')
#     Demo().configure_traits()
#============= views ===================================
#============= EOF ====================================

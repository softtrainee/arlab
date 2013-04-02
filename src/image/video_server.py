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
from traits.api import Instance, Button, Property, Bool
from traitsui.api import View, Item, ButtonEditor
#============= standard library imports ========================
from threading import Thread, Event
import time
from numpy import array
#============= local library imports  ==========================
from src.image.video import Video
from src.loggable import Loggable
class VideoServer(Loggable):
    video = Instance(Video)
    port = 1084

    _started = False
    use_color = True
    start_button = Button
    start_label = Property(depends_on='_started')
    _started = Bool(False)
    def _get_start_label(self):
        return 'Start' if not self._started else 'Stop'

    def _start_button_fired(self):
        if self._started:
            self.stop()
        else:
            self.start()

    def traits_view(self):
        v = View(Item('start_button', editor=ButtonEditor(label_value='start_label')))
        return v

    def _video_default(self):
        return Video()

    def stop(self):
#        if self._started:
        self.info('stopping video server')
        self._stop_signal.set()
        self._started = False

    def start(self):
        self.info('starting video server')
        self._new_frame_ready = Event()
        self._stop_signal = Event()

        self.video.open(user='server')
        bt = Thread(name='broadcast', target=self._broadcast)
        bt.start()

        self.info('video server started')
        self._started = True

    def _broadcast(self):
        stop = self._stop_signal
#        new_frame = self._new_frame_ready
        video = self.video
        use_color = self.use_color


        self.info('video broadcast thread started')
        import zmq
        context = zmq.Context()
        sock = context.socket(zmq.PUB)
        sock.bind('tcp://*:{}'.format(self.port))
        fps = 5

#        if use_color:
#            kw = dict(swap_rb=True)
#            depth = 3
#        else:
#            kw = dict(gray=True)
#            depth = 1

        import Image
        from cStringIO import StringIO
        pt = time.time()
        while not stop.isSet():

            f = video.get_frame()

#            new_frame.clear()
#            im = Image.fromarray(f.ndarray)
#            s = StringIO()
#            im.save(s, 'JPEG')
#            sock.send(s.getvalue())
#            w, h = f.size()
#            header = array([w, h, fps, depth])
#            data = array([header.tostring(), f.ndarray.tostring()], dtype='str')
#            sock.send(header.tostring())
#            sock.send(f.ndarray.tostring())


            nt = time.time()
            st = ((1.0 / fps) - (nt - pt))
            if st > 0:
                time.sleep(st)
            pt = nt

#            time.sleep(max(0.001 /, fp - (time.time() - t)))

# class VideoServer2(Loggable):
#    video = Instance(Video)
#    port = 5556
#
#    _frame = None
#
#    _new_frame_ready = None
#    _stop_signal = None
#
#
#    use_color = False
#    def _video_default(self):
#        v = Video()
#        return v
#
#
#
#    def stop(self):
#        if self._started:
#            self.info('stopping video server')
#            self._stop_signal.set()
#            self._started = False
#
#    def start(self):
#        if not self._started:
#            self.info('starting video server')
#            self._new_frame_ready = Event()
#            self._stop_signal = Event()
#
#            self.video.open(user='server')
#            bt = Thread(name='broadcast', target=self._broadcast, args=(
#                                                                        self.video,
#                                                                        self.use_color,
#                                                                        self._stop_signal,
#                                                                        self._new_frame_ready
#                                                                        ))
#            bt.start()
#
#            self._started = True
#            self.info('video server started')
#
#    def _broadcast(self, video, use_color, stop, new_frame):
#        self.info('video broadcast thread started')
#        import zmq
#        context = zmq.Context()
#        sock = context.socket(zmq.PUB)
#        sock.bind('tcp://*:{}'.format(self.port))
#        fp = 1 / 5.
#
#        if self.use_color:
#            kw = dict(swap_rb=True)
#            depth = 3
#        else:
#            kw = dict(gray=True)
#            depth = 1
#
#        while not stop.isSet():
#            t = time.time()
#
#            f = video.get_frame(**kw)
#
#            new_frame.clear()
#            w, h = f.size()
#            header = array([w, h, fp, depth])
# #            data = array([header.tostring(), f.ndarray.tostring()], dtype='str')
#            sock.send(header.tostring())
#            sock.send(f.ndarray.tostring())
#            time.sleep(max(0.001, fp - (time.time() - t)))


if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('vs')
    s = VideoServer()
    s.configure_traits()
#    s.video.open(user='server')
#    s.start()

#============= EOF =============================================

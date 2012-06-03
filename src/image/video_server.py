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
from traits.api import Instance
#============= standard library imports ========================
from threading import Thread, Lock, Event
import time
from numpy import array
#============= local library imports  ==========================
from src.image.video import Video
from src.loggable import Loggable

class VideoServer(Loggable):
    video = Instance(Video)
    port = 5556

    _frame = None

    _lock = None
    _new_frame_ready = None
    _stop_signal = None

    _started = False
    use_color = False
    def _video_default(self):
        v = Video()
        return v

    def stop(self):
        if self._started:
            self.info('stopping video server')
            self._stop_signal.set()
            self._started = False

    def start(self):
        if not self._started:
            self.info('starting video server')
            self._lock = Lock()
            self._new_frame_ready = Event()
            self._stop_signal = Event()

            self.video.open(user='server')
            bt = Thread(name='broadcast', target=self._broadcast)
            bt.start()

            self._started = True
            self.info('video server started')

    def _broadcast(self):
        self.info('video broadcast thread started')
        import zmq
        context = zmq.Context()
        self._bsocket = context.socket(zmq.PUB)
        self._bsocket.bind('tcp://*:{}'.format(self.port))
        fp = 1 / 15.

        if self.use_color:
            kw = dict(swap_rb=True)
            depth = 3
        else:
            kw = dict(gray=True)
            depth = 1

        while not self._stop_signal.isSet():
            t = time.time()

            f = self.video.get_frame(**kw)

            self._new_frame_ready.clear()
            w, h = f.size()
            header = array([w, h, fp, depth])
#            data = array([header.tostring(), f.ndarray.tostring()], dtype='str')
            self._bsocket.send(header.tostring())
            self._bsocket.send(f.ndarray.tostring())
            time.sleep(max(0.001, fp - (time.time() - t)))


if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('vs')
    s = VideoServer()
#    s.video.open(user='server')
    s.start()

#============= EOF =============================================

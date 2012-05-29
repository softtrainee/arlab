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
from traits.api import HasTraits, Instance
from src.image.video import Video
from threading import Thread, Lock, Event
import select
import socket
import cPickle as pickle
from src.loggable import Loggable
import time

class VideoServer(Loggable):
    video = Instance(Video)
#    host = None
    host = '127.0.0.1'
    port = 1084

    _frame = None

    _lock = None
    _new_frame_ready = None
    _stop_signal = None

    _started = False

    def _video_default(self):
        v = Video()
        v.open()
        return v

    def stop(self):
        if self._started:
            self.info('stopping video server')
#            self._stop_signal.set()
            self._started = False

    def start(self):
        if not self._started:
            self.info('starting video server')
            self._lock = Lock()
            self._new_frame_ready = Event()
#            self._stop_signal = Event()

            self.video.open(user='server')
            st = Thread(name='grab', target=self._grab)
            bt = Thread(name='broadcast', target=self._broadcast)

            st.start()
            bt.start()
            self._started = True
            self.info('video server started')


    def _grab(self):
        self.info('video grab thread started')
#        while not self._stop_signal.isSet():
        while 1:
            with self._lock:
                self._frame = self.video.get_frame(gray=True)
#                print 'rame'
            #  need to wait moment allowing the _broadcast thread 
            #  a chance to acquire the _lock
#            time.sleep(1)
            self._new_frame_ready.wait(1e-5)
            self._new_frame_ready.set()

    def _socket_factory(self, host=None, port=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if host is None:
            host = self.host
            if host is None:
                host = socket.gethostbyname(socket.gethostname())

        if port is None:
            port = self.port
        sock.bind((host, port))
        sock.listen(2)

        return sock

    def _broadcast(self):
        self.info('video broadcast thread started')
        sock = self._socket_factory()

        inp = [sock]
#        while not self._stop_signal.isSet():
        while 1:
            inputready, out, _ = select.select(inp, inp, [], 2)
            for s in inputready:
                if s == sock:
                    # handle the sock socket
                    client, _address = sock.accept()
                    inp.append(client)

            for so in out:
                if self._new_frame_ready.isSet():
                    with self._lock:
                        if self._frame is not None:
#                            d = self._frame.as_numpy_array()
                            d = self._frame.ndarray
                            try:
                                so.sendall(pickle.dumps(d))
                            except socket.error:
                                so.close()
                                inp.remove(so)
                    self._new_frame_ready.clear()

        sock.close()



if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('vs')
    s = VideoServer()
    s.start()



#======== EOF ================================

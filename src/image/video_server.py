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
from traits.api import HasTraits, Instance
from src.image.video import Video
from threading import Thread, Lock, Event
import select
import socket
import cPickle as pickle

class VideoServer(HasTraits):
    video = Instance(Video)
#    host = '129.138.12.141'
    host = '127.0.0.1'
    port = 1084

    _frame = None
    def _video_default(self):
        v = Video()
        v.open()
        return v

    def start_server(self):
        self.lock = Lock()
        self.new_frame_ready = Event()
        st = Thread(name='grab', target=self._grab)
        bt = Thread(name='broadcast', target=self._broadcast)

        st.start()
        bt.start()

    def _grab(self):
        while 1:
            with self.lock:
                self._frame = self.video.get_frame(gray=True)
            #  need to wait moment allowing the _broadcast thread 
            #  a chance to acquire the lock

            self.new_frame_ready.wait(1e-7)
            self.new_frame_ready.set()

    def _socket_factory(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(2)

        return sock

    def _broadcast(self):
        sock = self._socket_factory(self.host, self.port)

        inp = [sock]
        while 1:
            inputready, out, _ = select.select(inp, inp, [], 2)
            for s in inputready:
                if s == sock:
                    # handle the sock socket
                    client, _address = sock.accept()
                    inp.append(client)

            for so in out:
                if self.new_frame_ready.isSet():
                    with self.lock:
                        d = self._frame.as_numpy_array()
                        try:
                            so.sendall(pickle.dumps(d))
                        except socket.error:
                            so.close()
                            inp.remove(so)
                    self.new_frame_ready.clear()

        sock.close()



if __name__ == '__main__':
    s = VideoServer()
    s.start_server()



#======== EOF ================================

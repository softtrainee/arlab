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
import time
import cPickle as pickle
from numpy import array_split
import zlib
import zmq

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
                self._frame = self.video.get_frame()

            #  need to wait moment allowing the _broadcast thread 
            #  a chance to acquire the lock

            self.new_frame_ready.wait(1e-7)
            self.new_frame_ready.set()

    def _zmq_socket_factory(self, host, port):
        context = zmq.Context()
        sock = context.socket(zmq.PUB)

        sock.bind('tcp://{}:{}'.format(host, port))
        return sock

    def _socket_factory(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
#        sock.listen(2)

        return sock

    def _send_data(self, sock, data):
#        print sock.accept()
        print sock.recvfrom(1500)

    def _broadcast(self):
#        sock = self._zmq_socket_factory(self.host, self.port)
        inp = []
        for i in range(4):
            sock = self._socket_factory(self.host, self.port + i)
            inp.append(sock)

#        sock.bind((self.host, self.port))

#        sock.listen(2)
#        while 1:
#            if self.new_frame_ready.isSet():
#                with self.lock:
#                    #if sock.recv(1024):
#                    sock.send('<frame>' + pickle.dumps(self._frame.as_numpy_array()))
#
#                self.new_frame_ready.clear()
#
#        inp = [sock]
        while 1:
            inputready, out, _ = select.select(inp, [], [], 0.25)
            for o in out:
                da = 'foo'
                t = Thread(target=self._send_data, args=(o, da))
                t.start()
                t.join()

#            for s in inputready:
#                if s == sock:
#                    # handle the sock socket
#                    client, _address = sock.accept()
#                    inp.append(client)

#            for so in out:
#                if self.new_frame_ready.isSet():
#                    with self.lock:
#                        #print self._frame.as_numpy_array().tostring()
#                        d = self._frame.as_numpy_array()
#                        try:
#                            so.send(pickle.dumps(d))
#                        except socket.error, e:
#                            so.close()
#                            inp.remove(so)
#                    self.new_frame_ready.clear()

#                else:
##                    print 'seeend'
#                    if self.new_frame_ready.isSet():
#                       # data = s.recv(1024)
#                       # if data:
#                        with self.lock:
#                            #print self._frame.as_numpy_array().tostring()
#                            d = self._frame.as_numpy_array()
#                            try:
#                                s.send(pickle.dumps(d))
#                            except socket.error, e:
#                                print e
#                        self.new_frame_ready.clear()
#                        else:
#                            s.close()
#                            inp.remove(s)

        sock.close()



if __name__ == '__main__':
    s = VideoServer()
    s.start_server()



#======== EOF ================================

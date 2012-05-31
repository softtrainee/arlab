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
#import cPickle as pickle
from src.loggable import Loggable
import time
from SocketServer import ThreadingTCPServer, BaseRequestHandler, TCPServer

#def convert_to_jpeg(ndsrc):
#    import Image
##    import StringIO
##    from scipy.misc import imsave
##    s = StringIO.StringIO()
##    imsave(s, ndsrc.ndarray)
##    return ndsrc
#    ndsrc = ndsrc.ndarray
#    a = Image.frombuffer(ndsrc)
class TCPHandler(BaseRequestHandler):
    def handle(self):
        print self.request.recv(1024)
#        self.request.sendall('fffff')

#        self.request.close()
#        data = self.request.recv()
class VideoServer(Loggable):
    video = Instance(Video)
#    host = None
    host = 'localhost'
    port = 1084

    _frame = None

    _lock = None
    _new_frame_ready = None
    _stop_signal = None

    _started = False

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
#            st = Thread(name='grab', target=self._grab)
            bt = Thread(name='broadcast', target=self._broadcast)



#            st.start()
            bt.start()
#            time.sleep(0.1)
            self._started = True
            self.info('video server started')


#    def _grab(self):
#        self.info('video grab thread started')
#        while not self._stop_signal.isSet():
#        self._frame = self.video.get_frame()
#        while 1:
#            with self._lock:
##                pass
#                self._frame = self.video.get_frame(lock=False, gray=True)
#                time.sleep(0.01)
#            self._frame = 'ddddd'
#                print 'rame'
        #  need to wait moment allowing the _broadcast thread 
        #  a chance to acquire the _lock
#            time.sleep(1)
#            self._new_frame_ready.wait(1e-7)
#            self._new_frame_ready.set()

#    def _socket_factory(self, host=None, port=None):
#        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##        sock.setblocking(False)
#        if host is None:
#            host = self.host
#            if host is None:
#                host = socket.gethostbyname(socket.gethostname())
##
#        if port is None:
#            port = self.port
#
#        sock.bind((host, port))
#        sock.listen(1)
#
#        return sock

    def _broadcast(self):
        self.info('video broadcast thread started')
        import zmq
        context = zmq.Context()
        self._bsocket = context.socket(zmq.PUB)
        self._bsocket.bind('tcp://*:5556')

        while not self._stop_signal.isSet():
#            if self._new_frame_ready.isSet():
#                with self._lock:
#            print 'asd'
                f = self.video.get_frame(swap_rb=True)
#                print f.ndarray.shape
                self._bsocket.send(f.ndarray.tostring())
                time.sleep(1e-7)
#                self._new_frame_ready.clear()
#            self._new_frame_ready.wait(1e-7)
#            print 'aa'

#        t = ThreadingTCPServer((self.host,
#                                self.port), TCPHandler)
#        t = TCPServer((self.host,
#                                self.port), TCPHandler)
#        t.socket.setsockopt(socket.SOL_SOCKET,
#                            socket.SO_REUSEADDR, True)
#        t.serve_forever()
#        sock = self._socket_factory()
#        inp = [sock]
##        while not self._stop_signal.isSet():
#        while 1:
#            self.info('looping')
#            inputready, out, _ = select.select(inp, op, 1)
#            time.sleep(1e-5)
##            self.info(','.join([str(ss) for ss in out]))
#            for s in inputready:
#                if s == sock:
##                    # handle the sock socket
#                    client, _address = sock.accept()
#                    inp.append(client)
#            for so in out:
#                print so, self._frame
#                if self._new_frame_ready.isSet():
##                    with self._lock:
#                    print 'send', self._frame
#                    if self._frame is not None:
##                            d = self._frame.as_numpy_array()
#                        d = self._frame.ndarray.tostring()
#
##                            d = convert_to_jpeg(self._frame)
#                        try:
##                                so.sendall(pickle.dumps(d))
#                            so.send(d)
#                        except socket.error:
#                            pass
##                                so.close()
##                                inp.remove(so)
#
#                self._new_frame_ready.clear()
#            self._new_frame_ready.wait(1e-5)
#            time.sleep(0.1)

#        sock.close()



if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('vs')
    s = VideoServer()
#    s.video.open(user='server')
    s.start()




#======== EOF ================================

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
import cPickle as pickle

from traits.api import HasTraits, Instance, Button
from traitsui.api import View, Item
import select
import socket

import os
import sys
from threading import Thread
from numpy import array, vstack
import Queue

# add src to the path

# always change back to pychron_beta before committing

SRC_DIR = os.path.join(os.path.expanduser('~'), 'Programming',
                       'mercurial', 'pychron_beta')
sys.path.insert(0, SRC_DIR)

from src.image.image_editor import ImageEditor
from src.image.image import Image
from src.image.video import Video

import time
class VideoClient(HasTraits):
    _sock = None
    host = '127.0.0.1'
    port = 1084

    frame_width = 640
    frame_height = 480
    frame_depth = 1

    test = Button
    image = Instance(Image, ())

#    video = Instance(Video)
#    def _video_default(self):
#        v = Video()
#        v.open()
#        return v
#    def _test_fired(self):
#        udp = True
#        self.img_que = Queue.Queue(maxsize=4)
#        self.connect(udp=udp)
#        self.listen(udp=udp)

    def traits_view(self):
        v = View('test',
                 Item('image', style='custom', show_label=False, editor=ImageEditor(),
                                            width=self.frame_width, height=self.frame_height
                ))
        return v

    @property
    def frame_size(self):
        return self.frame_width * self.frame_height * self.frame_depth

    def unpickle(self, d):
        try:
            return pickle.loads(d)
        except Exception, e:
            pass
#            print e

    def listen(self, udp=False):
        func = self._listen_udp if udp else  self._listen

        t = Thread(target=func)
        t.start()
#
#        t = Thread(target=self._update)
#        t.start()


#    def _update(self):
#        q = self.img_que
#        while 1:
#            img = None
#
#            if q.full():
#                print q.qsize(), 'foo'
#                try:
#                    d = q.get()
#
#                    if img is None:
#                        img = d
#                    else:
#                        img = vstack((img, d))
#                    print img.shape
#                except Exception, e:
#                    print e
#                except Queue.Empty, e:
#                    print e
##                except Exception, e:#Queue.Empty:
##                    print e
#
#            time.sleep(0.25)
#                    print 'show im'
#                    self.image.load(img)



    def _get_data(self, s):
        print 'sent', s.sendto('1', (self.host, self.port))

        data, addr = s.recvfrom(self.frame_size)
        print data, addr
#        data = pickle.loads(data)
#        self.img_que.put(data)


    def _listen_udp(self):
        print 'listening udp'
        while 1:
            for i in range(4):
                s = self._socks[i]

#            _, out, _ = select.select([], self._socks, [], 0.25)
#            img = None
#            print out
#            for s in out:
                t = Thread(target=self._get_data, args=(s,))
                t.start()
                t.join()

#                out_q.put(pickle.loads(data))
#                ok = True
#                s.sendto('1', (self.host, self.port))
#                for i in range(self.frame_height):
#                    try:
#                        data, addr = s.recvfrom(4096)
#
#                        data = pickle.loads(data)
#
#                        if img is None:
#                            img = data
#                        else:
#                            img = vstack((img, data))
#                    except:
#                        ok = False
##                print type(data), i
##                print data.shape
#                print ok
#                if ok:
#                    self.image.load(img)
#                    self.image.swap_rb()


    def _listen(self):
        print 'lisenting'


        while self._stream_video:
#            for i in range(4):
#                self._socks[i].send('1')

#            self._sock.send('1')
#            data = self._sock.recv()#self.frame_size)
#            d = self.unpickle(data[7:])
##            print type(d)
#            self.image.load(d)
#            self.image.swap_rb()
            _, _out, _ = select.select([], [self._sock], [], 1)
#            print _out
            for s in _out:
#                print s.send('1')
#                s.send('1')
                d = None
                data = s.recv(self.frame_size)
#                print len(data)
                while 1:

                    d = self.unpickle(data)
                    if d is not None:
                        break
                    else:
                        data += s.recv(self.frame_size)
#
                self.image.load(d, nchannels=1)

    def connect(self, udp=False):
        if udp:

            self._socks = si = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for i in range(4)]
#            for i in range(4):
#                si[i].connect((self.host, self.port + i))
        else:
#            import zmq
#            context = zmq.Context()
#            sock = context.socket(zmq.SUB)
#            sock.connect("udp://{}:{}".format(self.host, self.port))
#            sock.setsockopt(zmq.SUBSCRIBE, '<frame>')
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self.host, self.port))
#        self._sock = sock
#        self._sock.settimeout(1e-3)
        self._stream_video = True



if __name__ == '__main__':
    c = VideoClient()
    udp = False
#    self.img_que = Queue.Queue(maxsize=4)
    c.connect(udp=udp)
    c.listen(udp=udp)
    c.configure_traits()

#======== EOF ================================

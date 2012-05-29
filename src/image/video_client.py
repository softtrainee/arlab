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
from traits.api import HasTraits, Instance, Button
from traitsui.api import View, Item
#============= standard library imports ========================
import cPickle as pickle
import select
import socket
import os
import sys
from threading import Thread
import time
#============= local library imports  ==========================

# add src to the path

# always change back to pychron_beta before committing
SRC_DIR = os.path.join(os.path.expanduser('~'), 'Programming',
                       'mercurial', 'pychron_beta')
sys.path.insert(0, SRC_DIR)

from src.image.image_editor import ImageEditor
from src.image.image import Image

class VideoClient(HasTraits):
    _sock = None
#    host = '129.138.12.141'
    host = 'localhost'
    port = 1084

    frame_width = 640
    frame_height = 480
    frame_depth = 1

    test = Button
    image = Instance(Image, ())

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

    def listen(self):

        t = Thread(target=self._listen)
        t.start()

    def _listen(self):
#        print 'lisenting'

        fp = 1 / 10.0
        while self._stream_video:
            t = time.time()
            _, _out, _ = select.select([], [self._sock], [], 1)

            for s in _out:
                d = None
                data = s.recv(self.frame_size)
#                d = self.unpickle(data)

                while 1:
                    d = self.unpickle(data)
                    if d is not None:
                        break
                    else:
                        data += s.recv(self.frame_size)

                self.image.load(d, nchannels=1)

            time.sleep(max(0.001, fp - (time.time() - t)))

    def connect(self, udp=False):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        self._stream_video = True


if __name__ == '__main__':
    c = VideoClient()
    udp = False
#    self.img_que = Queue.Queue(maxsize=4)
    c.connect()
    c.listen()
    c.configure_traits()

#============= EOF =============================================

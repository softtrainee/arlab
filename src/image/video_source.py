#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, File, Str, Int
from traitsui.api import View, Item
#============= standard library imports ========================
import zmq
from cStringIO import StringIO
import Image as PILImage
import os
from numpy import asarray, array

#============= local library imports  ==========================
from src.image.image import Image
from src.image.cv_wrapper import resize


def parse_url(url):
    if url.startswith('file://'):
        r = url[7:]
        islocal = True
    else:
        islocal = False
        # strip off 'lan://'
        url = url[6:]
        if ':' in url:
            host, port = url.split(':')
        else:
            host = url
            port = 8080

        r = host, int(port)

    return islocal, r

class VideoSource(HasTraits):
#     _cached_image = None
#     def __init__(self, *args, **kw):
#         super(VideoSource, self).__init__(*args, **kw)
#         self._cached_image = self._get_image_data()
    _cached_image = None

    image_path = File('/Users/ross/Sandbox/archive/images/diodefailsnapshot.jpg')
    host = Str('localhost')
    port = Int(1080)
    fps = Int
    _sock = None
    poller = None

    def __init__(self, *args, **kw):
        super(VideoSource, self).__init__(*args, **kw)
        self.poller = zmq.Poller()
        self.reset_connection()

#===============================================================================
# capture protocol
#===============================================================================
    def release(self):
        pass

    def read(self):
        return True, self.get_image_data()

    def set_url(self, url):
        islocal, r = parse_url(url)
        if islocal:
            self.image_path = r
        else:
            self.host, self.port = r
            self.reset_connection()

    def reset_connection(self):
        if self._sock:
            self.poller.unregister(self._sock)

        context = zmq.Context()
        self._sock = context.socket(zmq.SUB)

        self._sock.connect('tcp://{}:{}'.format(self.host,
                                                  self.port))
        self._sock.setsockopt(zmq.SUBSCRIBE, '')
        self.poller.register(self._sock, zmq.POLLIN)
        self._no_connection_cnt = 0

    def get_image_data(self, size=None):
        if self._sock is None:
            img = self._get_image_data()
        else:
            img = self._get_video_data()

        if img is not None:
            if size:
                img = resize(img, *size)
            return asarray(img[:, :])

    def _image_path_changed(self):
        if self.image_path:
            self._cached_image = Image.new_frame(self.image_path, swap_rb=True)

    def _get_video_data(self):
        evts = self.poller.poll(10)
        if evts:
            sock, _id = evts[0]
            resp = sock.recv()
            self.fps = int(resp)
            evts = self.poller.poll(50)
            if evts:
                sock, _id = evts[0]
                resp = sock.recv()
                buf = StringIO()
                buf.write(resp)
                buf.seek(0)
                img = PILImage.open(buf)
                img = img.convert('RGB')
                self._cached_image = array(img)
            self._no_connection_cnt = 0

        else:
            self._no_connection_cnt += 1

        if self._no_connection_cnt > 20:
            p = os.path.join(os.path.dirname(__file__), 'no_connection.jpg')
            self._cached_image = Image.new_frame(p,
                                                swap_rb=True)
            self._no_connection_cnt = 0

        return self._cached_image

    def _get_image_data(self):
        '''
            return ndarray
        '''
        img = self._cached_image
        if img is None:
            self._image_path_changed()

        return self._cached_image
#============= EOF =============================================

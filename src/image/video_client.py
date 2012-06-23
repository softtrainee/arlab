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
from threading import Thread, Lock
import time
from numpy import fromstring
from enable.component_editor import ComponentEditor
from chaco.plot import Plot
from chaco.array_plot_data import ArrayPlotData
from pyface.timer.do_later import do_later
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
    data = None
#    image = Instance(Image, ())

#    def traits_view(self):
#        v = View('test',
#                 Item('image', style='custom', show_label=False, editor=ImageEditor(),
#                                            width=self.frame_width, height=self.frame_height
#                ))
#        return v
#    imgplot = Instance(Plot)
#    def _imgplot_default(self):
#        pd = ArrayPlotData()
#        p = Plot(pd)
#        return p
#
#
#    def traits_view(self):
#        v = View(Item('imgplot', show_label=False,
#                      editor=ComponentEditor()))
#        return v

    @property
    def frame_size(self):
        return self.frame_width * self.frame_height * self.frame_depth

#    def unpickle(self, d):
#        try:
#            return pickle.loads(d)
#        except Exception, e:
#            pass

    def listen(self):

        t = Thread(target=self._listen)
        t.start()

    def _listen(self):
#        print 'lisenting'
#        plot = self.imgplot
#
#        fp = 1 / 10.0
#        check = True
        import zmq
        self._lock = Lock()
        context = zmq.Context()
        self._sock = context.socket(zmq.SUB)
        self._sock.connect('tcp://localhost:5556')
        self._sock.setsockopt(zmq.SUBSCRIBE, '')

        while 1:
            data = self._sock.recv()
            data = fromstring(data, dtype='uint8')
            with self._lock:
                self.data = data.reshape(720, 1280, 3)

    def get_frame(self):
        with self._lock:
            return self.data
#            self.data = data
#            do_later(self._update_image)
#            time.sleep(0.1)

#    def _update_image(self, *args, **kw):
#        plot = self.imgplot
#        plot.data.set_data('imagedata', self.data)
#        if not 'imagedata' in plot.plots.keys():
#            plot.img_plot('imagedata')

#        plot.invalidate_and_redraw()

#            print len(data) if data else 0
#            self.image.load(data)
#            time.sleep(max(0.001, fp - (time.time() - t)))

#            t = time.time()
#            print t
#            try:
#                
#            except:
#                pass

#            self._sock.send('get')

#            d = self._sock.recv(self.frame_size)
#            print d
#            try:
#                d = self._sock.recv(self.frame_size)
##                print d
#                if d:
##                    self._sock.close()
#            except Exception, e:
#                pass
#                self._sock.close()

#            _, _out, _ = select.select([], [self._sock], [], 1)
#            i = 0
#            for s in _out:
#                d = None
#                img = None
#                while not d and i < 10:
#                    try:
#                        d = s.recv(self.frame_size)
#                    except:
#                        i += 1
##                d = self.unpickle(data)
#                j = 0
#                while 1 and d:
##                    print img
#                    try:
#                        img = fromstring(d)
#                        break
#                    except ValueError:
#                        d += s.recv(self.frame_size)
#                    time.sleep(1e-5)
#                    j += 1
#
#
##                    d = self.unpickle(data)
##                    if d is not None:
##                        break
##                    else:
##                        data += s.recv(self.frame_size)
#                print 'got ', len(d) if d else 0
#                if img is not None:
#                    self.image.load(img, nchannels=1)

#                print self.image.source_frame
#            time.sleep(max(0.001, fp - (time.time() - t)))

#    def connect(self, udp=False):



if __name__ == '__main__':
    c = VideoClient()
#    self.img_que = Queue.Queue(maxsize=4)
    c.listen()
    c.configure_traits()

#============= EOF =============================================

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
from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = 'qt4'


#============= enthought library imports =======================
from traits.api import HasTraits, Instance, Float
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import time
from threading import Timer
from numpy import asarray
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.image.video import Video
# from src.image.image import StandAloneImage
from src.image.cv_wrapper import get_size, crop, grayspace
from src.image.standalone_image import StandAloneImage
# from src.image.cvwrapper import get_size, crop, grayspace

from src.mv.co2_locator import CO2Locator

class MachineVisionManager(Manager):
    video = Instance(Video)
#     target_image = Instance(StandAloneImage)
    pxpermm = Float(23)

    def new_co2_locator(self):
        c = CO2Locator(pxpermm=self.pxpermm)
        return c

    def new_image_frame(self):
        src = self.video.get_frame()
        return src

#===============================================================================
# image manipulation
#===============================================================================
    def _crop_image(self, src, cw, ch):
        CX, CY = 0, 0
        cw_px = int(cw * self.pxpermm)
        ch_px = int(ch * self.pxpermm)
        w, h = get_size(src)

        x = int((w - cw_px) / 2 + CX)
        y = int((h - ch_px) / 2 + CY)

#        print w / self.pxpermm, cw_px / self.pxpermm
#        ra = 1
#        print self.pxpermm * ra
#        print w / float(cw)
#        self.cpxpermm = w / float(cw) / 2.
#        print h / float(ch), w / float(cw)
#        print self.pxpermm * float(w) / cw_px
#        self.cpxpermm = self.pxpermm * w / cw
#        print self.cpxpermm, w / cw
#        print w, cw_px
#        print cw, w / (cw * self.pxpermm)
#        self.croppixels = (cw_px, ch_px)
#        self.croprect = (x, y, cw_px, ch_px)
#        cw_px = ch_px = 107

        r = 4 - cw_px % 4
        cw_px = ch_px = cw_px + r



        return asarray(crop(src, x, y, cw_px, ch_px))

    def _gray_image(self, src):
        return grayspace(src)

    def view_image(self, im, auto_close=True):
        # use a manager to open so will auto close on quit
        self.open_view(im)
        if auto_close:
            minutes = 0.25
            t = Timer(60 * minutes, im.close_ui)
            t.start()

    def new_image(self, frame=None):

#         if self.target_image is not None:
#             self.target_image.close_ui()

        im = StandAloneImage(
#                             title=self.title,
#                              view_identifier='pychron.fusions.co2.target'
                             )

#         self.target_image = im
        if frame is not None:
            im.load(frame, swap_rb=True)

        return im

    def _test(self, im):

        paths = (
#                 ('/Users/ross/Sandbox/pos_err/snapshot007.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_221_0-005.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_207_0-002.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_209_0-001.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_210_0-001.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_220_0-001.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_221_0-001.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_221_0-002.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_221_0-003.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_221_0-004.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_200_0-001.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_200_0-002.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_201_0-001.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_202_0-001.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_203_0-001.jpg', 1.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_204_0-001.jpg', 1.25),
                 ('/Users/ross/Sandbox/pos_err/pos_err_206_0-001.jpg', 1.25),
#                  ('/Users/ross/Sandbox/pos_err/pos_err_206_1-001.jpg', 1.25),
#                  ('/Users/ross/Sandbox/pos_err/pos_err_207_0-001.jpg', 1.25),
#                  ('/Users/ross/Sandbox/pos_err/pos_err_52001.jpg', 2.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_52001.tiff', 2.25),
#                  ('/Users/ross/Sandbox/pos_err/pos_err_52002.jpg', 2.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_53001.jpg', 2.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_53002.jpg', 2.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_53003.jpg', 2.25),
#                 ('/Users/ross/Sandbox/pos_err/pos_err_54001.jpg', 2.25),
                )
        fails = 0
        times = []

#         im = self.target_image
        for p, dim in paths[:]:
            from src.globals import globalv
            # force video to reload test image
            self.video.source_frame = None
            globalv.video_test_path = p
#             return
#             im.source_frame = self.new_image_frame()
            frm = self.new_image_frame()
#             self.target_image.load()

            cw = ch = dim * 3.2
#            cw = ch = dim
            frame = self._crop_image(frm, cw, ch)
            im.source_frame = frame
#            time.sleep(1)
#            continue
#            self.target_image.set_frame(0, frame)

#            loc.pxpermm = self.cpxpermm

#            loc.croppixels = (cw * self.pxpermm, ch * self.pxpermm)

            loc = self.new_co2_locator()

            st = time.time()
            dx, dy = loc.find(im, frame, dim * self.pxpermm)

            times.append(time.time() - st)
            if dx and dy:
                self.info('SUCCESS path={}'.format(p))
                self.info('calculated deviation {:0.3f},{:0.3f}'.format(dx, dy))
            else:
                fails += 1
                self.info('FAIL    path={}'.format(p))
            time.sleep(1)

        if times:
            n = len(paths)
            self.info('failed to find center {}/{} times'.format(fails, n))
            self.info('execution times: min={} max={} avg={}'.format(min(times), max(times), sum(times) / n))

#        def foo():
#            from pylab import show, plot
#            plot(times)
#            show()
#        do_later(foo)
    def setup_image(self):
        frame = self.new_image_frame()
        im = self.new_image(frame)
        self.view_image(im)
        return im

    def _test_fired(self):
        im = self.setup_image()

        from src.ui.thread import Thread
        t = Thread(target=self._test, args=(im,))
        t.start()
        self._t = t

#         from threading import Thread
#         t = Thread(target=self._test)
#         t.start()

    def traits_view(self):
        return View('test')

def test():
    from src.globals import globalv
    globalv.video_test = True
    globalv.video_test_path = '/Users/ross/Sandbox/pos_err/snapshot007.jpg'
#    globalv.video_test_path = '/Users/ross/Sandbox/pos_err/pos_err_53002.jpg'
    globalv.video_test_path = '/Users/ross/Sandbox/pos_err/pos_err_221_0-005.jpg'

#    globalv.video_test_path = '/Users/ross/Sandbox/pos_err/diodefailsnapshot.jpg'
    video = Video()
    video.open()
    mv = MachineVisionManager(video=video)
    mv.configure_traits()

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('mv')
    test()
#============= EOF =============================================

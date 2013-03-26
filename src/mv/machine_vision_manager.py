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
from traits.api import HasTraits, Instance, Float
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.image.video import Video
from src.image.image import StandAloneImage
from threading import Timer
from src.image.cvwrapper import get_size, crop, grayspace
from pyface.timer.do_later import do_later
import time


class MachineVisionManager(Manager):
    video = Instance(Video)
    target_image = Instance(StandAloneImage)
    pxpermm = Float(23)

    def new_co2_locator(self):
        from src.mv.co2_locator import CO2Locator
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

#        self.croppixels = (cw_px, ch_px)
#        self.croprect = (x, y, cw_px, ch_px)

        return crop(src, x, y, cw_px, ch_px)

    def _gray_image(self, src):
        return grayspace(src)

    def view_image(self, im, auto_close=True):
        # use a manager to open so will auto close on quit
        self.open_view(im)
        if auto_close:
            minutes = 1
            t = Timer(60 * minutes, im.close)
            t.start()

    def new_image(self, frame=None):
        if self.target_image is not None:
            self.target_image.close()

        im = StandAloneImage(
#                             title=self.title,
                             view_identifier='pychron.fusions.co2.target'
                             )

        self.target_image = im
        if frame is not None:
            self.target_image.load(frame, swap_rb=True)
        return im

    def _test(self):
        frame = self.new_image_frame()
        im = self.new_image(frame)

        self.view_image(im)

        loc = self.new_co2_locator()

        dim = 2.25
        cw = ch = dim * 2.5
        frame = self._crop_image(self.target_image.source_frame, cw, ch)

        loc.croppixels = (cw * self.pxpermm, ch * self.pxpermm)

        dx, dy = loc.find(self.target_image, frame, dim * self.pxpermm)
        if dx and dy:
            self.info('calculated deviation {:0.3f},{:0.3f}'.format(dx, dy))

    def _test_fired(self):
        from threading import Thread
        t = Thread(target=self._test)
        t.start()

    def traits_view(self):
        return View('test')

def test():
    from globals import globalv
    globalv.video_test = True
    globalv.video_test_path = '/Users/ross/Sandbox/pos_err/snapshot007.jpg'
    globalv.video_test_path = '/Users/ross/Sandbox/pos_err/pos_err_53002.jpg'
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

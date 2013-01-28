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
from traits.api import HasTraits, Int, Float
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import time
from PIL import Image
import os
from src.paths import paths
from src.machine_vision.machine_vision_manager import MachineVisionManager
from src.helpers.filetools import unique_path, unique_dir
#============= local library imports  ==========================

class CompositeImageManager(MachineVisionManager):
    nrows = Int(3)
    ncols = Int(3)
    image_width = 640
    image_height = 480

    step_mmx = Float(2)
    step_mmy = Float(2)

    def collect_images(self):
        nrows = self.nrows
        ncols = self.ncols
        imgdir = os.path.join(paths.data_dir, 'composite_images')
        if not os.path.exists(imgdir):
            os.mkdir(imgdir)

        self.current_directory = unique_dir(imgdir, 'data')
        try:
            controller = self.laser_manager.stage_manager.stage_controller
        except AttributeError:
            controller = None

        dx = self.step_mmx
        dy = self.step_mmy
        if controller is not None:
            for r in range(nrows):
                for c in range(ncols):
                    #move to position
                    controller.linear_move(c * dx, r * dy)
                    #take picture
                    image_name = 'img_{:02n}{:02n}.png'.format(r, c)
                    path = os.path.join(self.current_directory, image_name)
                    self.video.record_frame(path)

    def generate_stitched(self):
        from mapping.stitch import hor_stitch, ver_stitch
        for r in range(self.nrows):
            image_names = ['img_{:02n}{:02n}.png'.format(r, c)
                                for c in range(self.ncols)]
            hor_stitch(self.current_directory, image_names, name='row{}'.format(r))

#        for r in range(1, self.nrows):
#            stitchh()

    def generate_composite(self):
        #create a blank image to hold images
        size = (self.ncols * self.image_width, self.nrows * self.image_height)
        im = Image.new('RGB', size)
        w, h = self.image_width, self.image_height
        x = 0
        y = 0
        imgdir = os.path.join(paths.data_dir, 'composite_images')
        for r in range(self.nrows):
            for c in range(self.ncols):
                impath = os.path.join(imgdir, 'img_{:02n}{:02n}.png'.format(r, c))
                pi = Image.open(impath)
                x = c * self.image_width
                y = r * self.image_height
#                print x, y,
                im.paste(pi, (x, y, x + w, y + h))

        im = im.resize((640, 480))
        im.save(os.path.join(imgdir, 'composite.png'))

    def _test_fired(self):
        self.collect_images()
        self.generate_composite()

if __name__ == '__main__':
    m = CompositeImageManager()
    m.configure_traits()
#============= EOF =============================================

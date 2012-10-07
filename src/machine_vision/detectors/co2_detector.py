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

#============= enthought library imports =======================
from traits.api import on_trait_change
#============= standard library imports ========================
from numpy import histogram, array, argmax
#============= local library imports  ==========================
from src.image.cvwrapper import  grayspace, colorspace

from src.image.image import StandAloneImage
from hole_detector import HoleDetector

'''
todo remove all permutations 
make another class to do all perms
'''

class CO2HoleDetector(HoleDetector):

#    def close_images(self):
##        if self.brightness_image is not None:
##            self.brightness_image.close()
#
#        if self.target_image is not None:
#            self.target_image.close()
    def open_image(self):
        if self.target_image is not None:
            self.target_image.close()

        im = StandAloneImage(title=self.title,
                             view_identifier='pychron.fusions.co2.target'
                             )
        self.target_image = im
        if self.parent is not None:
            #use a manager to open so will auto close on quit
            self.parent.open_view(im)
        else:
            from pyface.timer.do_later import do_later
            do_later(im.edit_traits)

    def locate_sample_well(self, cx, cy, holenum, holedim, new_image=True, **kw):
        '''
        '''
        def hist(d):
            f, v = histogram(array(d))
            i = len(f)  if argmax(f) == len(f) - 1 else argmax(f)
            return v[i]

        self._nominal_position = (cx, cy)
        self.current_hole = str(holenum)
        self.info('locating CO2 sample hole {}'.format(holenum if holenum else ''))

        #convert hole dim to pxpermm
        holedim *= self.pxpermm
        self.holedim = holedim
        if new_image:
            self.open_image()

        im = self.target_image
        im.load(self.parent.get_new_frame())

        src = grayspace(im.source_frame)
        im.set_frame(0, colorspace(src.clone()))

        cw = None
        ch = None
        if self.use_crop:
            ci = 0
            cw = (1 + ci * self.crop_expansion_scalar) * self.cropwidth
            ch = (1 + ci * self.crop_expansion_scalar) * self.cropheight

            self.info('cropping image to {}mm x {}mm'.format(cw, ch))
            src = self._crop_image(src, cw, ch, image=im)

        width = 3
        ba = lambda v: [bool((v >> i) & 1) for i in xrange(width - 1, -1, -1)]
        test = [ba(i) for i in range(2 ** width)]

        pos_argss = []
        ntests = 3
#        test = [(False, False, False, False)]

        osrc = src.clone()
        seg = self.segmentation_style
#        seg = 'region'
        for sharpen, smooth, contrast in test:
            src = self._apply_filters(osrc, smooth, contrast, sharpen)
            targets = self._segment_source(src, seg)
            if targets:
                nx, ny = self._get_positioning_error(targets, cx, cy, holenum)
                pos_argss.append((nx, ny))
            else:
                self.info('Failed segmentation={}. Trying alternates'.format(seg))
                test_alternates = False
                if test_alternates:
                    for aseg in ['region', 'edge', 'threshold']:
                        if aseg == seg:
                            continue

                        src = self._apply_filters(osrc, smooth, contrast, sharpen)
                        targets = self._segment_source(src, aseg)
                        if targets is not None:
                            nx, ny = self._get_positioning_error(targets, cx, cy, holenum)
                            pos_argss.append((nx, ny))
                            break

                        self.info('Failed segmentation={}'.format(aseg))

            if len(pos_argss) >= ntests:
                nxs, nys = zip(*pos_argss)

                nx = hist(nxs)
                ny = hist(nys)

                src = self.target_image.get_frame(0)
                tcx, tcy = self._get_true_xy(src)
                self._draw_indicator(src, (tcx - nx, tcy - ny) , shape='crosshairs',
                                     size=10)
                self._draw_center_indicator(src, size=5)
                return nx, ny

#============= EOF =====================================

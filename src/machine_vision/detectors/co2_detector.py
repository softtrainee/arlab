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

#============= local library imports  ==========================
from src.image.cvwrapper import  grayspace, colorspace

from src.image.image import StandAloneImage
from hole_detector import HoleDetector

'''
todo remove all permutations 
make another class to do all perms
'''

class CO2HoleDetector(HoleDetector):

    @on_trait_change('target_image:ui')
    def _add_target_window(self, new):
        try:
            #added windows will be closed by the application on exit
            self.parent.add_window(new)
        except AttributeError:
            pass

    def close_images(self):
#        if self.brightness_image is not None:
#            self.brightness_image.close()

        if self.target_image is not None:
            self.target_image.close()

    def locate_sample_well(self, cx, cy, holenum, holedim, new_image=True, **kw):
        '''
            if do_all== true

        '''
        self._nominal_position = (cx, cy)
        self.current_hole = str(holenum)
        self.info('locating CO2 sample hole {}'.format(holenum if holenum else ''))

        #convert hole dim to pxpermm
        holedim *= self.pxpermm
        if new_image:
            if self.target_image is not None:
                self.target_image.close()

            im = StandAloneImage(title=self.title,
                                 view_identifier='pychron.fusions.co2.target'
                                 )
            self.target_image = im

            #use a manager to open so will auto close on quit
            self.parent.open_view(im)
        else:
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

        width = 4
        ba = lambda v: [bool((v >> i) & 1) for i in xrange(width - 1, -1, -1)]
        test = [ba(i) for i in range(2 ** 4)]

#        pos_argss = []
#        ntests = 1
#        test = [(False, False, False, False)]

        osrc = src.clone()
        seg = self.segmentation_style
#        seg = 'region'
        for convextest, sharpen, smooth, contrast in test:

            src = self._apply_filters(osrc, smooth, contrast, sharpen)
            params = self._segment_source(src, seg,
                                         cx, cy,
                                         holenum, holedim)

            if params is not None:
                nx, ny = params
#                pos_argss.append(params)
#                if len(pos_argss) >= ntests:
#                nxs, nys = zip(*pos_argss)
#                nx = sum(nxs) / len(nxs)
#                ny = sum(nys) / len(nys)

                src = self.target_image.get_frame(0)

                cx, cy = self._get_true_xy(src)
                nomx, nomy = self._nominal_position

                dx = (nomx - nx) * self.pxpermm
                dy = (nomy - ny) * self.pxpermm

                self._draw_indicator(src, (cx - dx, cy + dy), shape='crosshairs',
                                     size=10)
                return nx, ny
            else:
                self.info('Failed segmentation={}. Trying alternates'.format(seg))
                test_alternates = False
                if test_alternates:
                    for aseg in ['region', 'edge', 'threshold']:
                        if aseg == seg:
                            continue

                        src = self._apply_filters(osrc, smooth, contrast, sharpen)
                        params = self._segment_source(src, aseg,
                                                        cx, cy,
                                                        holenum, holedim,
#                                                        convextest=False
                                                        )
                        if params is not None:
                            break
                        self.info('Failed segmentation={}'.format(aseg))

    def _apply_filters(self, src, smooth=False,
                        contrast=False, sharpen=False):
        self.info('applying filters. smooth={} contrast={} sharpen={}'.format(smooth, contrast, sharpen))
        if sharpen:
            src = self.sharpen(src)
        if contrast:
            src = self.contrast_equalization(src)
        if smooth:
            src = self.smooth(src)
        return src

    def _segment_source(self, src, style, cx, cy, holenum, holedim, **kw):
        def segment(seg, si):
            targets = self._locate_helper(seg.segment(si), **kw)
            if targets:
                miholedim = 0.75 * holedim
                maholedim = 1.25 * holedim
                mi = miholedim ** 2 * 3.1415
                ma = maholedim ** 2 * 3.1415

                #use only targets that are close to cx,cy
                targets = [t for t in targets
                           if self._near_center(*t.centroid_value) and  ma > t.area > mi]
                if targets:
                    nx, ny = self._get_positioning_error(targets, cx, cy, holenum)
                    return nx, ny

        self.info('using {} segmentation'.format(style))

        klass = '{}Segmenter'.format(style.capitalize())
        m = __import__('src.machine_vision.segmenters.{}'.format(style), fromlist=[klass])

        segmenter = getattr(m, klass)()

        if style == 'region':
            retries = 4

            for j in range(1, retries):
                segmenter.threshold_nwidth = j
                npos = segment(segmenter, src)
                if npos:
                    break
            return npos
        else:
            return segment(segmenter, src)



#============= EOF =====================================

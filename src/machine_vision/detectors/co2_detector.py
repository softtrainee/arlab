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
from traits.api import Bool
#============= standard library imports ========================
from numpy import histogram, array, argmax
#============= local library imports  ==========================
from src.image.cvwrapper import  grayspace

from src.image.image import StandAloneImage
from hole_detector import HoleDetector
from threading import Timer

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
    display_results = Bool(True)
    holedim = None

    @property
    def crop_dimensions(self):

        if self.holedim:

            #holedim is in px convert to mm
            hd = self.holedim / self.pxpermm
            ff = 2.5 #empirical fugde factor, 2<=ff<=2.6
            cw = ch = hd * ff
        else:
            cw = self.cropwidth
            ch = self.cropheight
        return cw, ch

    def open_image(self, auto_close=True):
        if self.target_image is not None:
            self.target_image.close()

        im = StandAloneImage(title=self.title,
                             view_identifier='pychron.fusions.co2.target'
                             )

        self.target_image = im
        if self.parent is not None:
            #use a manager to open so will auto close on quit
            self.parent.open_view(im)
            if auto_close:
                minutes = 1
                t = Timer(60 * minutes, self.target_image.close)
                t.start()

        else:
            from pyface.timer.do_later import do_later
            do_later(im.edit_traits)

    def _get_new_frame(self, verbose=True):
        im = self.target_image
        im.load(self.parent.get_new_frame())

        src = grayspace(im.source_frame)
#        im.set_frame(0, colorspace(src.clone()))
#
        if self.use_crop:
#            ci = 0
#            cw = (1 + ci * self.crop_expansion_scalar) * self.cropwidth
#            ch = (1 + ci * self.crop_expansion_scalar) * self.cropheight
            cw , ch = self.crop_dimensions
            if verbose:
                self.info('cropping image to {:0.3f}mm x {:0.3f}mm'.format(cw, ch))
            src = self._crop_image(src, cw, ch, image=im)

        return src.clone()

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

        seg = self.segmentation_style

        def get_npos(osrc):
            tests = [
                     (False, False),
                     (True, True),
                     (False, True),
                     (True, False)
                     ]
            for sh, cr in tests:
                src = self._apply_filters(osrc, sh, cr)
                targets = self._segment_source(src, seg)
                if targets:
                    nx, ny = self._get_positioning_error(targets, cx, cy, holenum)

                    src = self.target_image.get_frame(0)
                    self._draw_center_indicator(src, size=2,
                                                shape='rect')
                    if self.display_results:
                        tcx, tcy = self._get_true_xy(src)
                        self._draw_targets(src, targets)

                        self._draw_indicator(src, (tcx - nx, tcy - ny),
                                             shape='rect',
                                             size=2,
                                             color=(0, 255, 255)
                                             )
                    return nx, ny

        osrc = self._get_new_frame()
        return get_npos(osrc)

    #        width = 3
#        ba = lambda v: [bool((v >> i) & 1) for i in xrange(width - 1, -1, -1)]
#        tests = [ba(i) for i in range(2 ** width)]

        #best set of parameters
#        tests.insert(0, (False, True, False))


#        pos_argss = []
#        ntests = 3
#        test = [(False, False, False, False)]

#        osrc = src.clone()


#        i = 0
#        ntries = 10
#        ntests = 2
#        nposs = []
#        while len(nposs) < ntests and i < ntries:
#            npos = get_npos()
#            if npos:
#                nposs.append(npos)
#            else:
#                i += 1

#        while len(pos_argss) < ntests:
#            osrc = self._get_new_frame()
#            for sharpen, smooth, contrast in tests:
#                src = self._apply_filters(osrc, smooth, contrast, sharpen)
#                targets = self._segment_source(src, seg)
#                if targets:
#                    nx, ny = self._get_positioning_error(targets, cx, cy, holenum)
#                    pos_argss.append((nx, ny))
#                    break
#            else:
#                self.info('Failed segmentation={}. Trying alternates'.format(seg))
#                test_alternates = False
#                if test_alternates:
#                    for aseg in ['region', 'edge', 'threshold']:
#                        if aseg == seg:
#                            continue
#
#                        src = self._apply_filters(osrc, smooth, contrast, sharpen)
#                        targets = self._segment_source(src, aseg)
#                        if targets is not None:
#                            nx, ny = self._get_positioning_error(targets, cx, cy, holenum)
#                            pos_argss.append((nx, ny))
#                            break
#
#                        self.info('Failed segmentation={}'.format(aseg))

#        if len(nposs) >= ntests:
#            nxs, nys = zip(*nposs)
##
#            nx = hist(nxs)
#            ny = hist(nys)
##
#            src = self.target_image.get_frame(0)
#            tcx, tcy = self._get_true_xy(src)
#            self._draw_indicator(src, (tcx - nx, tcy - ny) ,
##                                 shape='circle',
#                                 color=(100, 100, 0),
#                                 size=10)
##            self._draw_center_indicator(src, size=5)
#            return nx, ny

#============= EOF =====================================

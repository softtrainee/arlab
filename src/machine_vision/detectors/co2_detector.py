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
from numpy import percentile
#============= local library imports  ==========================
from src.image.cvwrapper import asMat, grayspace, colorspace, smooth, \
    dilate
from hole_detector import HoleDetector


class CO2HoleDetector(HoleDetector):
    def _segmentation_style_changed(self):
        self.locate_sample_well(0, 0)

    def _reset_image(self):
        self.image.frames = [None]
#        if self._debug:
        self.working_image.frames = [None]

    def locate_sample_well(self, cx, cy, holenum=None, **kw):
        from skimage.exposure import rescale_intensity
        self._reset_image()

#        self.cropwidth = 4
#        self.cropheight = 4
        self._nominal_position = (cx, cy)
        self.current_hole = holenum
        self.info('locating CO2 sample hole {}'.format(holenum if holenum else ''))

#        for ci in range(self.crop_tries):
#        self.parent.close_image()
        self.parent.show_image()

        src = self.parent.load_source().clone()
        src = grayspace(src)

        self.image.frames[0] = colorspace(src)
#        print self.working_image.
        self.working_image.frames[0] = colorspace(src)

        cw = None
        ch = None
        if self.use_crop:
            ci = 0
            cw = (1 + ci * self.crop_expansion_scalar) * self.cropwidth
            ch = (1 + ci * self.crop_expansion_scalar) * self.cropheight

            self.info('cropping image to {}mm x {}mm'.format(cw, ch))
            src = self._crop_image(src, cw, ch)

        if self.use_contrast_equalization:
            self.info('maximizing image contrast')
            src = src.ndarray
            # Contrast stretching
            p2 = percentile(src, 2)
            p98 = percentile(src, 98)
            img_rescale = rescale_intensity(src, in_range=(p2, p98))

            src = asMat(img_rescale)

        if self.use_smoothing:
            self.info('smoothing image')
            src = smooth(src)

        self.image.frames[0] = colorspace(src)
        self.working_image.frames[0] = colorspace(src)

        self.info('using {} segmentation'.format(self.segmentation_style))
        func = getattr(self, '_{}_segmentation'.format(self.segmentation_style))

        def foo(si):
            args = func(si)
            if args:
                npos = self._get_corrected_position(args, cx, cy, holenum)
                if npos:
                    return npos

        if self.use_dilation:
            ndilation = 2
            for i in range(ndilation):
                self.info('target not found. increasing dilation')
                self.info('dilating image (increase white areas). value={}'.format(i + 1))
    #            src = dilate(src, self._dilation_value)
                src = dilate(src, i + 1)
                self.image.frames[0] = colorspace(src)
                self.working_image.frames[0] = colorspace(src)
                npos = foo(src)

                if npos:
                    return npos
#                return self._get_corrected_position(args, cx, cy, holenum)

    def _get_corrected_position(self, args, cx, cy, holenum):

        mi = 0
        if args is None:
            return

        targets = [t for t in args if t.area > mi]

        #use only targets that are close to cx,cy
        targets = [t for t in targets
                   if self._near_center(*t.centroid_value)]
        if targets:
            nx, ny = self._get_positioning_error(targets, cx, cy, holenum)
            self.info('found a target at {},{}'.format(nx, ny))
            return nx, ny


                #do not dilation on the first try

#            if args is not None:
#                break

#        else:
#            self.warning('no target found during search. threshold {} - {}'.
#                         format(s, e))
#            self._draw_center_indicator(self.image.frames[0])
#            return


#============= EOF =====================================

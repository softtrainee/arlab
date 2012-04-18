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
from numpy import percentile, sum, asarray
#============= local library imports  ==========================
from src.image.cvwrapper import asMat, grayspace, colorspace, smooth, \
    dilate
from hole_detector import HoleDetector


class CO2HoleDetector(HoleDetector):
    intensity_cropwidth = 4
    intensity_cropheight = 4
    def _segmentation_style_changed(self):
        self._segmentation_style_hook()

    def _segmentation_style_hook(self):
        self.locate_sample_well(0, 0)

    def _reset_image(self):
        self.image.frames = [None]
#        if self._debug:
        self.working_image.frames = [None]

    def smooth(self, src):
        if self.use_smoothing:
            self.info('smoothing image')
            src = smooth(src)
        return src

    def contrast_equalization(self, src):
        if self.use_contrast_equalization:
            from skimage.exposure import rescale_intensity
            self.info('maximizing image contrast')
            src = src.ndarray
            # Contrast stretching
            p2 = percentile(src, 2)
            p98 = percentile(src, 98)
            img_rescale = rescale_intensity(src, in_range=(p2, p98))

            src = asMat(img_rescale)
        return src

    def get_intensity(self):
        self._reset_image()

        s = self.parent.load_source().clone()
#        if self._debug:
#            p = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321-an4.tiff'
#            s = self.parent.load_source(path=p).clone()

        s = self._crop_image(grayspace(s), self.intensity_cropwidth,
                             self.intensity_cropheight)

        iar = s.ndarray[:]
        niar = iar - self.baseline
        thres = 0

        niar[niar < thres] = 0
        src = asMat(asarray(niar, dtype='uint8'))

        self.working_image.frames[0] = colorspace(src)

        spx = sum(src.ndarray)

        #normalize to area
#        print spx, iar.shape[0] * iar.shape[1]
        spx /= float(iar.shape[0] * iar.shape[1])

        return spx

    def collect_baseline_intensity(self, ncounts=5, period=25):
#        self.parent.show_image()
        import time
#        import numpy as np
        ss = None
#        p5 = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321-an2.tiff'
#        p = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321.tiff'
        self._reset_image()
        for i in range(ncounts):
            self.info('collecting baseline image {} of {}'.format(i + 1, ncounts))
            ps = self.parent.load_source().clone()
            gs = grayspace(ps)
            cs = self._crop_image(gs, self.intensity_cropwidth,
                                  self.intensity_cropheight)
            if ss is None:
                #convert to array to we can sum >255
                ss = asarray(cs.ndarray, dtype='uint32')
            else:
                ss += cs.ndarray

            time.sleep(period / 1000.0)

        self.baseline = ss / float(ncounts)

    def locate_sample_well(self, cx, cy, holenum=None, **kw):
        self._reset_image()

#        self.cropwidth = 4
#        self.cropheight = 4
        self._nominal_position = (cx, cy)
        self.current_hole = holenum
        self.info('locating CO2 sample hole {}'.format(holenum if holenum else ''))

#        for ci in range(self.crop_tries):
#        self.parent.close_image()

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

        src = self.contrast_equalization(src)
        src = self.smooth(src)
        self.image.frames[0] = colorspace(src)
        self.working_image.frames[0] = colorspace(src)
        self.parent.show_image()

        npos = self._segment_source(src, self.segmentation_style, cx, cy, holenum)
        if not npos:
            #try another segementation style
            for s in ['threshold', 'edge', 'region']:
                if s is not self.segmentation_style:
                    npos = self._segment_source(src, s, cx, cy, holenum)
                    if npos:
                        break
        return npos

#                return self._get_corrected_position(args, cx, cy, holenum)
    def _segment_source(self, src, style, cx, cy, holenum):
        def segment(si, **kw):
            args = func(si, **kw)
            if args:
                npos = self._get_corrected_position(args, cx, cy, holenum)
                if npos:
                    return npos

        self.info('using {} segmentation'.format(style))
        func = getattr(self, '_{}_segmentation'.format(style))
        retries = 5
        s = 5
        for j in range(retries):
            params = dict()
            if self.use_dilation:
                ndilation = 2
                for i in range(ndilation):
                    #self.info('target not found. increasing dilation')
                    #self.info('dilating image (increase white areas). value={}'.format(i + 1))
        #            src = dilate(src, self._dilation_value)
                    osrc = dilate(src, i)
                    self.image.frames[0] = colorspace(osrc)
                    self.working_image.frames[0] = colorspace(osrc)
            else:
                osrc = src

            if self.segmentation_style == 'region':
                params['tlow'] = 125 - s * j
                params['thigh'] = 125 + s * j
            import time
#            time.sleep(2)
            npos = segment(osrc, **params)
            if npos:
                return npos

    def _get_corrected_position(self, args, cx, cy, holenum):

        mi = 500
        if args is None:
            return

        targets = [t for t in args if t.area > mi]

        #use only targets that are close to cx,cy
        targets = [t for t in targets
                   if self._near_center(*t.centroid_value)]
        if targets:
            nx, ny = self._get_positioning_error(targets, cx, cy, holenum)
            #self.info('found a target at {},{}'.format(nx, ny))
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

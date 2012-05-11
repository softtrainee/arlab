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
from traits.api import on_trait_change, Any
#============= standard library imports ========================
from numpy import percentile, sum, asarray, ogrid, pi, invert
import time
#============= local library imports  ==========================
from src.image.cvwrapper import asMat, grayspace, colorspace, smooth, \
    dilate
from src.image.image import StandAloneImage
from hole_detector import HoleDetector


class CO2HoleDetector(HoleDetector):
    brightness_cropwidth = 4
    brightness_cropheight = 4
    brightness_threshold = 10
    brightness_image = Any
    target_image = Any
#    target_area = None
    running_avg = None
    _hole_radius = None

    @on_trait_change('brightness_image:ui, target_image:ui')
    def _add_window(self, new):
        #added windows will be closed by the application on exit
        self.parent.add_window(new)

    def close_images(self):
        if self.brightness_image is not None:
            self.brightness_image.close()

        if self.target_image is not None:
            self.target_image.close()

    def _segmentation_style_changed(self):
        self._segmentation_style_hook()

    def _segmentation_style_hook(self):
        self.locate_sample_well(0, 0)

    def smooth(self, src, verbose=True):
        if self.use_smoothing:
            if verbose:
                self.info('smoothing image')
            src = smooth(src)
        return src

    def contrast_equalization(self, src, verbose=True):
        if self.use_contrast_equalization:
            from skimage.exposure import rescale_intensity

            if verbose:
                self.info('maximizing image contrast')

            if hasattr(src, 'ndarray'):
                src = src.ndarray
            # Contrast stretching
            p2 = percentile(src, 2)
            p98 = percentile(src, 98)
            img_rescale = rescale_intensity(src, in_range=(p2, p98))

            src = asMat(img_rescale)
        return src

    def _get_mask_radius(self):
        r = self._hole_radius
        if not r:
            r = self.pxpermm * self.radius_mm * 0.85
        return r

    def get_intensity_area(self, src, verbose):

        seg_src = self.contrast_equalization(src, verbose=verbose)
#        seg_src = self.smooth(seg_src, verbose=verbose)
        targets = self._region_segmentation(seg_src, hole=True,
                                            convextest=False)

        ma = 6000
        mi = 200
        target = None
        ta = None
        if targets:

            #no need to filter out targets not near the center using the circle mask does the inherently
            targets = [t for t in targets
                       if ma > t.area > mi]

            #sort targets by distance from center
            cx, cy = self._get_center()
            cmpfunc = lambda t:((t.centroid_value[0] - cx) ** 2 + (t.centroid_value[1] - cy) ** 2) ** 0.5
            targets = sorted(targets, key=cmpfunc)

            if targets:
                tt = targets[0]
                target = tt
                ta = tt.area

        if ta is None:
            r = self._get_mask_radius()
            ta = pi * r * r

        if self.running_avg is None:
            self.running_avg = [ta]
        else:
            self.running_avg.append(ta)

        n = len(self.running_avg)
        if n > 5:
            self.running_avg.pop(0)

        tarea = sum(self.running_avg) / max(1, float(n - 1))


#        if tarea is None:
#            tarea = self.target_area
#        if tarea is None:
#            if self.running_avg:
#                tarea = sum(self.running_avg) / float(len(self.running_avg))
#        if tarea is None:
#            tarea = float(src.ndarray.shape[0] * src.ndarray.shape[1])

        return tarea, target

    def get_intensity(self, verbose=True):
#        self.brightness_image.frames = [None]
        p = None
        if self._debug:
            p = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321-an6.tiff'

        s = self.parent.get_new_frame(path=p)
        self.brightness_image.load(s)

        self.brightness_image.set_frames([None])
        s = self.brightness_image.source_frame.clone()

        s = self._crop_image(grayspace(s), self.brightness_cropwidth,
                             self.brightness_cropheight
                             )

        iar = s.ndarray[:]
        niar = iar - self.baseline

        thres = self.brightness_threshold
        niar[niar < thres] = 0

        src = asMat(asarray(niar, dtype='uint8'))

        #mask the image with a circle
        x, y = niar.shape
        X, Y = ogrid[0:x, 0:y]
        r = self._get_mask_radius()
        mask = (X - x / 2) ** 2 + (Y - y / 2) ** 2 > r * r
        src.ndarray[mask] = 100

        tarea, target = self.get_intensity_area(src, verbose)

        csrc = colorspace(src)
        if target:
            self._draw_result(csrc, target)
        self.brightness_image.set_frame(0, csrc)

        gndarray = grayspace(src).ndarray
        gg = gndarray[invert(mask)]
        spx = sum(gg)

        #normalize to area
        bm = spx / tarea
        if verbose:
            self.info('bm params bm={} spx={} tarea={}'.format(bm, spx, tarea))
        return bm

    def collect_baseline_intensity(self, ncounts=5, period=25):
        if self.brightness_image is not None:
            self.brightness_image.close()

        self.running_avg = None
        im = StandAloneImage(title='Brightness',
                             view_identifier='pychron.fusions.co2.brightness')
        self.brightness_image = im

        im.show()

        sr = 0
        ss = None
        n = 0
        for i in range(ncounts):
            self.info('collecting baseline image {} of {}'.format(i + 1, ncounts))
            p = None
            if self._debug:
                p = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321.tiff'

            ps = self.parent.get_new_frame(path=p)
            im.load(ps)

            ps = im.source_frame.clone()
            gs = grayspace(ps)
            cs = self._crop_image(gs,
                                  self.brightness_cropwidth,
                                  self.brightness_cropheight,
                                  image=im
                                  )
            mi = 1500
            targets = self._region_segmentation(cs)
            if targets:
                targets = [t for t in targets
                       if self._near_center(*t.centroid_value) and t.area > mi]
                for t in targets:
                    sr += max(*t.bounding_rect) / 2.0
                n += len(targets)
            #convert to array to we can sum >255
            ncs = asarray(cs.ndarray, dtype='uint32')
            if ss is None:
                ss = ncs
            else:
                ss += ncs
            time.sleep(period / 1000.0)

        self._hole_radius = sr / max(1, n)
        self.baseline = ss / float(ncounts)

    def locate_sample_well(self, cx, cy, holenum=None, **kw):
        if self.target_image is not None:
            self.target_image.close()

        im = StandAloneImage(title='Positioning Error',
                             view_identifier='pychron.fusions.co2.target')
        self.target_image = im
        im.show()

        self._nominal_position = (cx, cy)
        self.current_hole = holenum
        self.info('locating CO2 sample hole {}'.format(holenum if holenum else ''))

        src = self.parent.get_new_frame()
        im.load(src)

        src = grayspace(im.source_frame)

        im.set_frame(0, colorspace(src))

        cw = None
        ch = None
        if self.use_crop:
            ci = 0
            cw = (1 + ci * self.crop_expansion_scalar) * self.cropwidth
            ch = (1 + ci * self.crop_expansion_scalar) * self.cropheight

            self.info('cropping image to {}mm x {}mm'.format(cw, ch))
            src = self._crop_image(src, cw, ch, image=im)

        src = self.contrast_equalization(src)
        src = self.smooth(src)
        im.set_frame(0, colorspace(src))

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
                    self.target_image.set_frame(0, colorspace(osrc))
#                    self.image.frames[0] = colorspace(osrc)
#                    self.working_image.frames[0] = colorspace(osrc)
            else:
                osrc = src

            if self.segmentation_style == 'region':
                params['tlow'] = 125 - s * j
                params['thigh'] = 125 + s * j
#            import time
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

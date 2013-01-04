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
from traits.api import Any, Bool, Float
from traitsui.api import View, Item
#============= standard library imports ========================
from numpy import pi, invert, asarray, ones_like, hsplit, ogrid
import time
from matplotlib.cm import get_cmap
#============= local library imports  ==========================
from src.image.cvwrapper import asMat, colorspace, grayspace, draw_polygons
#from src.image.image import StandAloneImage
from co2_detector import CO2HoleDetector


def colormap(mag, name='hot', cmin=0, cmax=1, scalar=None):
    cm = get_cmap(name)
    return hsplit(cm(mag), [3, ])[0] * 255


class BrightnessDetector(CO2HoleDetector):

    brightness_threshold = 10

    running_avg = None

    use_colormap = Bool(True)

    colormapper = None
    _hole_radius = Float
    baseline = 0

    def traits_view(self):
        return View('_hole_radius')

    def get_value(self, verbose=True):

#        p = self.parent.get_new_frame()
#        self.target_image.load(p)
#
#        s = self._crop_image(p,
#                             self.cropwidth,
#                             self.cropheight,
#                             image=self.target_image
#                             )
#
#        s = grayspace(s)

        s = self._get_new_frame(verbose=verbose)

        iar = s.ndarray[:]
        niar = iar - self.baseline

        #high pass filter
        thres = self.brightness_threshold
        niar[niar < thres] = 0

        #mask the image with a circle
        mask_radius = self._get_mask_radius()
        mask = self._apply_circular_mask(niar, radius=mask_radius)
        src = asarray(niar, dtype='uint8')

        #colormap image
        if self.use_colormap:
            cm_src = asarray([colormap(ci, cmax=255.) for ci in src], 'uint8')
        else:
            cm_src = src

        csrc = colorspace(asMat(cm_src))

        gsrc = asMat(src)

#        self.target_image.set_frame(0, gsrc)

        #calculate the masked area intensity
        spx_mask = sum(src[invert(mask)])
        area_mask = pi * mask_radius ** 2
#        #normalize to area
        bm_m = nspx = spx_mask / area_mask

        #find and draw a target
        area_target, target = self._get_intensity_area(gsrc, verbose)
        if target:
            self._draw_result(csrc, target)

            #make a blank image
            #make the mask
            target_mask = colorspace(asMat(ones_like(gsrc.ndarray) * 255))

            #draw filled polygon representing target
            draw_polygons(target_mask, [target.poly_points], thickness= -1, color=(0, 0, 0))

            #subtract target mask from image
            d = niar - grayspace(target_mask).ndarray
            d[d < 0] = 0

            #calculate sum of all target pixels
            spx_target = d.sum()
            #normalize to area
            bm_t = nspx = spx_target / area_target
        else:
            bm_t = 0
            spx_target = 0

        #draw the mask circle
        x, y = src.shape
        self._draw_indicator(csrc, (x / 2, y / 2),
                             size=int(mask_radius) + 1, thickness=1)

        self.target_image.set_frame(0, csrc)

        if verbose:
            self.info('spx_mask - sum={:0.1f}, area={:0.1f}'.format(spx_mask, area_mask))
            self.info('spx_target - sum={:0.1f}, area={:0.1f}'.format(spx_target, area_target))
            self.info('bm_mask={:0.1f}, bm_target={:0.1f}'.format(bm_m, bm_t))

        return nspx

    def collect_baseline(self, ncounts=5, period=100):
        if self.target_image is not None:
            self.target_image.close()

        self.open_image(auto_close=False)
        self.running_avg = None
#        im = self.target_image
        sr = 0
        ss = None
        n = 0
        for i in range(ncounts):
            self.info('collecting baseline image {} of {}'.format(i + 1, ncounts))

#            p = self.parent.get_new_frame()
#            im.load(p)
##            cs = im.source_frame.clone()
#            gs = grayspace(p)
#            cs = self._crop_image(gs,
#                                  self.cropwidth,
#                                  self.cropheight,
#                                  image=im
#                                  )
            cs = self._get_new_frame()
            mask_radius = self._get_mask_radius()
            nd = cs.ndarray
            self._apply_circular_mask(nd, radius=mask_radius)
#            src = asMat(invert(asarray(nd, dtype='uint8')))
            src = asMat(asarray(nd, dtype='uint8'))
###            src = self._apply_filters(src)
            self.display_processed_image = False
            targets = self._segment_source(src, self.segmentation_style,
                                           verbose=False)
##
#            dsrc = im.get_frame(0)
#            x, y = nd.shape
#            self._draw_indicator(dsrc, (x / 2, y / 2),
#                             size=int(mask_radius) + 1, thickness=1)
            if targets:
                for t in targets:
                    sr += max(*t.bounding_rect) / 2.0
                n += len(targets)
#            #convert to array to we can sum >255
            ncs = asarray(cs.ndarray, dtype='uint32')
            if ss is None:
                ss = ncs
            else:
                ss += ncs
            time.sleep(period / 1000.0)

        self._hole_radius = sr / max(1, n)

        self.baseline = ss / float(ncounts)

    def _get_intensity_area(self, osrc, verbose):
        tests = [
                     (False, False),
#                     (True, True),
#                     (False, True),
#                     (True, False)
                     ]

        self.target_image.set_frame(0, osrc)
        for sh, cr in tests:
            src = self._apply_filters(osrc, sh, cr)
            targets = self._segment_source(src, self.segmentation_style, verbose=verbose)

            if targets:
                #sort targets by distance from center
                cx, cy = self._get_center()
                cmpfunc = lambda t:((t.centroid_value[0] - cx) ** 2 + (t.centroid_value[1] - cy) ** 2) ** 0.5
                targets = sorted(targets, key=cmpfunc)

                if targets:
                    target = targets[0]
                    ta = target.area
                    if self.running_avg is None:
                        self.running_avg = [ta]
                    else:
                        self.running_avg.append(ta)

                    n = len(self.running_avg)
                    if n > 5:
                        self.running_avg.pop(0)

                    tarea = sum(self.running_avg) / max(1, float(n - 1))

                    return tarea, target
        else:
            return 0, None

    def _get_filter_target_area(self):
        return 100, 6000

    def _get_mask_radius(self):
        r = self._hole_radius
        if not r:
            r = self.pxpermm * self.radius_mm * 0.95
        return r

    def _apply_circular_mask(self, src, radius=None):
        '''
            src should be a grapscale ndarray
        '''
        if radius is None:
            radius = self._get_mask_radius()

        x, y = src.shape
        X, Y = ogrid[0:x, 0:y]
        mask = (X - x / 2) ** 2 + (Y - y / 2) ** 2 > radius * radius
        src[mask] = 0
        return mask
#============= EOF =============================================

#if __name__ == '__main__':
#    from timeit import Timer
#    n = 92
#    testd = ones(n * n).reshape(n, n)
#
#    f = lambda:colormap(testd)
#    t = Timer(f)
#    print t.timeit(1)
#    print colormap(array([0]))
#
#    f = lambda:colormap_mp(testd)
#    t = Timer(f)
#    print t.timeit(1)
#    print colormap_mp(array([0]))
#
#    b = BrightnessDetector(_debug=True)
#    b.collect_baseline_intensity()
#    f = lambda:b.get_intensity()
#    t = Timer(f)
#    print t.timeit(1)
#
#    b.use_colormap = False
#    print t.timeit(1)

#def colormap(mag, cmin=0, cmax=1, scalar=None):
#    n = mag.shape[0]
#    z = zeros(n)
#    o = ones(n)
#
#    x = (mag - cmin) / float(cmax - cmin)
#    if scalar is None:
#        scalar = cmax
#
##    print x, 4 * (x - 0.25), 4 * abs(x - 0.5) - 1, 4 * (0.75 - x)
#    b = minimum(maximum(4 * (0.75 - x), z), o) * scalar
#    r = minimum(maximum(4 * (x - 0.25), z), o) * scalar
#    g = minimum(maximum(4 * abs(x - 0.5) - 1., z), o) * scalar
#    return zip(r, g, b)
#def colormap_scalar(mag, cmin=0, cmax=1, scalar=None):
##    n = mag.shape[0]
##    z = zeros(n)
##    o = ones(n)
#
#    x = (mag - cmin) / float(cmax - cmin)
#    if scalar is None:
#        scalar = cmax
#    z = 0
#    o = 1
#
##    print x, 4 * (x - 0.25), 4 * abs(x - 0.5) - 1, 4 * (0.75 - x)
#    b = min(max(4 * (0.75 - x), z), o) * scalar
#    r = min(max(4 * (x - 0.25), z), o) * scalar
#    g = min(max(4 * abs(x - 0.5) - 1., z), o) * scalar
#    return (r, g, b)
#
#
#def colormap1(v, cmin=0, cmax=1, scalar=None):
#    cmi = min(cmin, cmax)
#    cma = max(cmin, cmax)
#    n = v.shape[0]
#    r = ones(n)
#    g = ones(n)
#    b = ones(n)
#    dv = cma - cmi
#    if v < (cmi + 0.25 * dv):
#        r = zeros(n)
#        g = 4 * (v - cmi) / dv
#    elif v < (cmi + 0.5 * dv):
#        r = 0
#        b = 1 + 4 * (cmi + 0.25 * dv - v) / dv
#    elif v < (cmi + 0.75 * dv):
#        r = 4 * (v - cmi - 0.5 * dv) / dv
#        b = 0
#    else:
#        g = 1 + 4 * (cmi + 0.75 * dv - v) / dv
#        b = 0
#    return zip(r, g, b)
#
#

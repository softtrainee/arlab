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
from traits.api import Any, Bool
#============= standard library imports ========================
from numpy import pi, invert, asarray, ones_like, hsplit
import time
from matplotlib.cm import get_cmap
#============= local library imports  ==========================
from src.image.cvwrapper import asMat, colorspace, grayspace, draw_polygons
from src.image.image import StandAloneImage
from co2_detector import CO2HoleDetector


def colormap(mag, name='hot', cmin=0, cmax=1, scalar=None):
    cm = get_cmap(name)
    return hsplit(cm(mag), [3, ])[0] * 255


class BrightnessDetector(CO2HoleDetector):
    brightness_cropwidth = 4
    brightness_cropheight = 4
    brightness_threshold = 10
    brightness_image = Any

    running_avg = None

    use_colormap = Bool(True)
    colormapper = None
    def close_images(self):
        super(BrightnessDetector, self).close_images()
        if self.brightness_image is not None:
            self.brightness_image.close()



    def _get_intensity_area(self, src, verbose):

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

        if ta is not None:

            if self.running_avg is None:
                self.running_avg = [ta]
            else:
                self.running_avg.append(ta)

            n = len(self.running_avg)
            if n > 5:
                self.running_avg.pop(0)

            tarea = sum(self.running_avg) / max(1, float(n - 1))
        else:
            r = self._get_mask_radius()
            tarea = pi * r * r

        return tarea, target

    def get_intensity(self, verbose=True):
#        self.brightness_image.frames = [None]
        p = None
        if self._debug:
            p = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321-an6.tiff'

        if self.parent is not None:
            p = self.parent.get_new_frame(path=p)
        self.brightness_image.load(p)

        self.brightness_image.set_frames([None])
        s = self.brightness_image.source_frame.clone()

        s = self._crop_image(grayspace(s), self.brightness_cropwidth,
                             self.brightness_cropheight
                             )

        iar = s.ndarray[:]
        niar = iar - self.baseline

        #not sure this is necessary
        thres = self.brightness_threshold
        niar[niar < thres] = 0

        #mask the image with a circle
#        x, y = niar.shape
#        X, Y = ogrid[0:x, 0:y]
        mask_radius = self._get_mask_radius()
#        mask = (X - x / 2) ** 2 + (Y - y / 2) ** 2 > mask_radius * mask_radius
#        niar[mask] = 0
        mask = self._apply_circular_mask(niar, radius=mask_radius)

        src = asarray(niar, dtype='uint8')

        #colormap image
        if self.use_colormap:
            cm_src = asarray([colormap(ci, cmax=255.) for ci in src], 'uint8')

        csrc = colorspace(asMat(cm_src))

        spx = None
        #find and draw a target
        area_target, target = self._get_intensity_area(src, verbose)
        if target:
            self._draw_result(csrc, target)
            # @todo: calculate the sum of pixels inscribed by the polygon
            #make a blank image
            target_mask = colorspace(asMat(ones_like(src) * 255))

            #make the mask
            #draw filled polygon representing target
            draw_polygons(target_mask, [target.poly_points], thickness= -1, color=(0, 0, 0))

            #subtract target mask from image
            d = niar - grayspace(target_mask).ndarray
            d[d < 0] = 0

            #calculate sum of all target pixels
            spx_target = spx = d.sum()

        #draw the mask circle
        x, y = src.shape
        self._draw_indicator(csrc, (x / 2., y / 2.), size=int(mask_radius), thickness=1)

        self.brightness_image.set_frame(0, csrc)

        spx_mask = 0
        spx_target = 0
        if spx is None:
            #no target was found using entire region
            #calculate sum of pixels in the masked region
            gg = src[invert(mask)]
            spx_mask = spx = sum(gg)

        #normalize to area
        area_mask = (pi * mask_radius * mask_radius)
        bm_t = spx_target / area_target
        bm_m = spx_mask / area_mask

        if verbose:
            self.info('spx_mask - sum={:0.1f}, area={:0.1f}'.format(spx_mask, area_mask))
            self.info('spx_target - sum={:0.1f}, area={:0.1f}'.format(spx_target, area_target))

            self.info('bm_mask={:0.1f}, bm_target={:0.1f}'.format(bm_m, bm_t))

        return spx

    def collect_baseline_intensity(self, ncounts=5, period=25):
        if self.brightness_image is not None:
            self.brightness_image.close()

        self.running_avg = None
        im = StandAloneImage(title='Brightness',
                             view_identifier='pychron.fusions.co2.brightness')
        self.brightness_image = im

        #use a manager to open so will auto close on quit
        self.parent.open_view(im)

        sr = 0
        ss = None
        n = 0
        for i in range(ncounts):
            self.info('collecting baseline image {} of {}'.format(i + 1, ncounts))
            p = None
            if self._debug:
                p = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321.tiff'

            if self.parent is not None:
                p = self.parent.get_new_frame(path=p)

            im.load(p)

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

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

#=============enthought library imports=======================
from traits.api import  Float, Range, Property, Tuple, Bool, Enum, \
    Instance, Str, on_trait_change
from traitsui.api import View, Item, VGroup, HGroup, spring
#============= standard library imports ========================
from scipy import ndimage
from numpy import histogram, argmax, array, asarray, ogrid, percentile, zeros_like, \
    delete, zeros, asarray, ones_like, rot90, max
from skimage.exposure import rescale_intensity
from skimage.draw import polygon
from skimage.morphology import is_local_maximum, watershed

import random
import os

#============= local library imports  ==========================
from src.image.cvwrapper import draw_polygons, crop, centroid, \
    new_point, contour, get_polygons, \
    draw_rectangle, draw_lines, colorspace, draw_circle, get_size, \
    asMat, sharpen_src, smooth_src, draw_contour_list

from src.paths import paths
from src.helpers.filetools import unique_path
from detector import Detector
from src.image.image import StandAloneImage
from src.machine_vision.detectors.target import Target
from src.machine_vision.segmenters.base import BaseSegmenter
from pyface.timer.do_later import do_later
from globals import globalv
import time
#from src.image.pyopencv_image_helper import grayspace


DEVX = random.randint(-10, 10)
DEVY = random.randint(-10, 10)
DEVX = 10
DEVY = 0
CX = 0
CY = 0

class HoleDetector(Detector):
    target_image = Instance(StandAloneImage, transient=True)

    radius_mm = Float(1.5)

    _hole_radius = None

    cropwidth = Float(5)
    cropheight = Float(5)


#    crop_expansion_scalar = Float(0.5)
    crosshairs_offsetx = 0
    crosshairs_offsety = 0

    save_positioning_error = Bool(False)
    use_histogram = Bool(True)
    display_processed_image = Bool(True)
    filter_targets = Bool(True)
#    filter_targets = Bool(False)
#    display_processed_image = Bool(False)
#    use_smoothing = Bool(True)
    use_crop = Bool(True)
#    use_dilation = Bool(False)
#    _dilation_value = 1
#    use_contrast_equalization = Bool(True)

    segmentation_style = Enum(
                              'region',
                              'edge',
                              'threshold',
                              'adaptivethreshold',
                               )
#    segmentation_style = Enum('edge', 'threshold', 'edge', 'region')

#    start_threshold_search_value = Int(80)
#    threshold_search_width = Int(40)
#    crop_tries = Range(0, 102, 1)  # > 101 makes it a spinner

#    threshold_tries = Range(0, 102, 2)
#    threshold_expansion_scalar = Int(5)

#    _threshold_start = None
#    _threshold_end = None
    title = Property
    current_hole = Str

    corrected_position = Property(depends_on='_corrected_position')
    _corrected_position = Tuple(0, 0)

    nominal_position = Property(depends_on='_nominal_position')
    _nominal_position = Tuple(0, 0)

    segmenter = Instance(BaseSegmenter)

    @on_trait_change('target_image:ui')
    def _add_target_window(self, new):
        try:
            #added windows will be closed by the application on exit
            self.parent.add_window(new)
        except AttributeError:
            pass
#===============================================================================
# image filters
#===============================================================================
    def sharpen(self, src, verbose=True):
        if verbose:
            self.info('sharpening image')
        src = sharpen_src(src)
        return src

    def smooth(self, src, verbose=True):
#        if self.use_smoothing:
        if verbose:
            self.info('smoothing image')
        src = smooth_src(src)
        return src

    def contrast_equalization(self, src):

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

    def _apply_circular_mask(self, src, radius=None):
        if radius is None:
            radius = self._get_mask_radius()

        x, y = src.shape
        X, Y = ogrid[0:x, 0:y]
        mask = (X - x / 2) ** 2 + (Y - y / 2) ** 2 > radius * radius
        src[mask] = 0
        return mask

    def _locate_helper(self, src, *args, **kw):
        try:
            src = asMat(asarray(src, 'uint8'))
        except ValueError:
            pass

        t = self._locate_targets(src, **kw)
        if self.display_processed_image:
            self.target_image.load(colorspace(src))

        return t

    def _locate_targets(self, src, **kw):
#        dsrc = self.working_image.frames[0]
        contours, hieararchy = contour(src)
        draw_contour_list(self.target_image.get_frame(0), contours, hieararchy)

#        do polygon approximation
        polygons, brs, areas = get_polygons(contours, hieararchy,
#                                            convextest=False,
#                                            hole=False,
                                            **kw
                                            )
        if not polygons:
            return

        targets = []
        for pi, br, ai in zip(polygons, brs, areas):
            if len(pi) < 4:
                continue

            cx, cy = centroid(pi)

            tr = Target()
            tr.origin = self._get_true_xy(src)
            tr.centroid_value = cx, cy
            tr.poly_points = pi
            tr.bounding_rect = br
            tr.area = ai

            targets.append(tr)

        return targets

    def _get_positioning_error(self, targets, cx, cy, holenum):
        def hist(d):
            f, v = histogram(array(d))
            i = len(f)  if argmax(f) == len(f) - 1 else argmax(f)
            return v[i]

        devxs, devys = zip(*[r.dev_centroid for r in targets])

        if self.use_histogram:
            dx = hist(devxs)
            dy = hist(devys)
        else:
            avg = lambda s: sum(s) / len(s)
            dx = avg(devxs)
            dy = avg(devys)

        #calculate the data position to move to nx,ny
        dxmm = (dx) / float(self.pxpermm)

        dymm = (dy) / float(self.pxpermm)
        nx = cx - dxmm
        ny = cy + dymm

        try:
            #verify that this target is within 1 radius of the uncorrected by calibrated position
            lm = self.parent.laser_manager
            h = lm.stage_manager.get_hole(holenum)
            calpos = lm.stage_manager.get_calibrated_position((h.x, h.y))

            if h is None:
                return

            if abs(calpos[0] - nx) > r or abs(calpos[1] - ny) > r:
                return
        except Exception, e:
            #debugging 
            pass

#        self._draw_markup(self.target_image.get_frame(0), targets, dev=(dx, dy))

#        self.parent._nominal_position = cx, cy
#        self.parent._corrected_position = nx, ny
        self._nominal_position = cx, cy
        self._corrected_position = nx, ny

        args = cx, cy, nx, ny, dxmm, dymm, round(dx), round(dy)#int(dx), int(dy)

        self.info('current pos: {:0.3f},{:0.3f} calculated pos: {:0.3f}, {:0.3f} dev: {:0.3f},{:0.3f} ({:n},{:n})'.format(*args))
        if self.save_positioning_error and holenum:
            self._save_(holenum, cx, cy, nx, ny, dxmm, dymm)

        return dx, dy

    def _save_(self, holenum, cx, cy, nx, ny, dxmm, dymm):
        path, _ = unique_path(paths.positioning_error_dir,
                              'positioning_error{:03n}_'.format(int(holenum)),
                            extension='jpg')
        self.target_image.save(path)
        #save an associated text file with some metadata
        head, _ = os.path.splitext(path)
        with open(head + '.txt', 'w') as f:
            f.write('hole={}\n'.format(holenum))
            f.write('nominal pos=   {:5f}, {:5f}\n'.format(cx, cy))
            f.write('corrected pos= {:5f}, {:5f}\n'.format(nx, ny))
            f.write('deviation=     {:5f}, {:5f}'.format(dxmm, dymm))

    def _draw_center_indicator(self, src, color=(0, 0, 255), shape='crosshairs', size=10):
        self._draw_indicator(src, new_point(*self._get_true_xy(src)),
#                             shape='crosshairs',
                             shape=shape,
                             color=color,
                             size=size)

    def _draw_targets(self, src, results):
        for r in results:
            self._draw_result(src, r)

    def _draw_result(self, src, result, with_br=False, thickness=1, color=(255, 0, 0)):
#        print 'rrrrr', result.centroid_value
        self._draw_indicator(src, new_point(*result.centroid_value),
                             color=(0, 255, 0),
                             size=10,
                             shape='crosshairs')
        draw_polygons(src, [result.poly_points])
        if with_br:
            draw_rectangle(src, result.bounding_rect.x,
                                result.bounding_rect.y,
                                result.bounding_rect.width,
                                result.bounding_rect.height,
                                thickness=thickness,
                                color=color
                                )

    def _draw_markup(self, src, results, dev=None):
        #add to indicators to ensure the indicator is drawn on top
        for pi in results:

#            f0 = self.target_image.get_frame(0)
            draw_polygons(src, [pi.poly_points], color=(255, 255, 0), thickness=1)

            #draw the centroid in blue
            pi.center = new_point(*pi.centroid_value)

        #draw the center of the image
        true_cx, true_cy = self._get_true_xy(src)

#        #draw the calculated center
        if dev:
            self._draw_indicator(src, new_point(true_cx - dev[0],
                                               true_cy - dev[1]), (255, 255, 0), 'circle', size=2)

    def _draw_indicator(self, src, center, color=(255, 0, 0), shape='circle', size=4, thickness= -1):
        if isinstance(center, tuple):
            center = new_point(*center)
        r = size
        if shape == 'rect':
            draw_rectangle(src, center.x - r / 2., center.y - r / 2., r, r,
                           color=color,
                           thickness=thickness)
        elif shape == 'crosshairs':
            draw_lines(src,
                   [[(center.x - size, center.y),
                    (center.x + size, center.y)],
                    [(center.x, center.y - size),
                     (center.x, center.y + size)]],
                       color=color,
                       thickness=1
                   )
        else:
            draw_circle(src, center, r, color=color, thickness=thickness)

    def _radius_filter(self, pi, cx, cy):
        tol = 1.4 * self.pxpermm * self.radius_mm
        disp = lambda p:((p.x - cx) ** 2 + (p.y - cy) ** 2) ** 0.5
        disps = map(disp, pi)

        #filter by tol
        fpi = filter(lambda p:p[1] < tol, zip(pi, disps))
        if fpi:
            pii, disps = zip(*fpi)
        else:
            pii = pi
        # 3. recalc centroid
        return centroid(pii), pii

    def _get_center(self):
        cx = self.croppixels[0] / 2.0
        cy = self.croppixels[1] / 2.0
        return cx, cy

    def _near_center(self, x, y, tol=0.75):
        cx, cy = self._get_center()

        tol *= self.pxpermm
        return abs(x - cx) < tol and abs(y - cy) < tol

    def _get_true_xy(self, src):
#        cw_px = self.cropwidth * self.pxpermm
#        ch_px = self.cropheight * self.pxpermm
#
#        true_cx = cw_px / 2.0 + self.crosshairs_offsetx
#        true_cy = ch_px / 2.0 + self.crosshairs_offsety
        w, h = get_size(src)
        x = float(w / 2)
        y = float(h / 2)

        return x, y

    def _crop_image(self, src, cw, ch, image=None):
        cw_px = int(cw * self.pxpermm)
        ch_px = int(ch * self.pxpermm)
        w, h = get_size(src)
        x = int((w - cw_px) / 2 + CX)
        y = int((h - ch_px) / 2 + CY)
        self.croppixels = (cw_px, ch_px)

        self.croprect = (x, y, cw_px, ch_px)
        src = crop(src, x, y, cw_px, ch_px)

        if image:
#            image.set_frame(colorspace(src))
            image.set_frame(0, colorspace(src.clone()))
#            image.save('/Users/ross/Sandbox/machine_vision/crop.jpg', width=cw_px, height=ch_px)

        return src

    def traits_view(self):
        return View(
                    VGroup(
                        HGroup(Item('use_histogram'),
                               Item('save_positioning_error'),
                               Item('display_processed_image')
                               ),
                        VGroup(
                              HGroup(spring, Item('segmentation_style', show_label=False)),
                              Item('segmenter', style='custom', show_label=False),
                              show_border=True,
                              label='Segmentation',
                              )
                           )
                    )
#==============================================================================
# getter/setters
#==============================================================================
    def _get_corrected_position(self):
        try:
            return '{:3f}, {:3f}'.format(*self._corrected_position)
        except IndexError:
            pass

    def _get_nominal_position(self):
        try:
            return '{:3f}, {:3f}'.format(*self._nominal_position)
        except IndexError:
            pass

    def _get_title(self):
        return 'Positioning Error Hole {}'.format(self.current_hole) \
                    if self.current_hole else 'Positioning Error'

    def _segmentation_style_changed(self):
        self.segmenter = self._segmenter_factory(self.segmentation_style)

    def _segmenter_factory(self, style):
        klass = '{}Segmenter'.format(style.capitalize())
        m = __import__('src.machine_vision.segmenters.{}'.format(style), fromlist=[klass])
        segmenter = getattr(m, klass)()
        return segmenter

    def _segmenter_default(self):
        return self._segmenter_factory(self.segmentation_style)

    def _apply_filters(self, src,
#                        smooth=False,
                        contrast=True,
                        sharpen=True,
                        verbose=False):
        if verbose:
            self.debug('applying filters. contrast={} sharpen={}'.format(contrast, sharpen))

        if sharpen:
            src = self.sharpen(src)
        if contrast:
            src = self.contrast_equalization(src)
#        if smooth:
#            src = self.smooth(src)

        try:
            return asMat(src)
        except TypeError:
            return src

    def _segment_source(self, src, style, verbose=True, **kw):
        if verbose:
            self.info('using {} segmentation'.format(style))
        kw['verbose'] = verbose

        npos = None
        segmenter = self.segmenter
        if style == 'region':
            def _region_iteration(ni, si):
                segmenter.count = 0
                for j in range(1, ni):
                    segmenter.count = j
                    segmenter.use_inverted_image = not segmenter.use_inverted_image
                    npos = self._segment_hook(si, segmenter,
                                               **kw)
                    if npos:
                        break

                    segmenter.use_inverted_image = not segmenter.use_inverted_image
                    npos = self._segment_hook(si, segmenter,
                                               **kw)
                    if npos:
                        break

                return npos

            ni = segmenter.threshold_tries
            if segmenter.use_adaptive_threshold:
                npos = self._segment_hook(src, segmenter, **kw)
                if not npos:
                    segmenter.use_inverted_image = not segmenter.use_inverted_image
                    npos = self._segment_hook(src, segmenter, **kw)
                    if not npos:
                        segmenter.use_adaptive_threshold = False
                        npos = _region_iteration(ni, src)
                        segmenter.use_adaptive_threshold = True

            else:
                npos = _region_iteration(ni, src)

            return npos
        else:
            return self._segment_hook(src, segmenter, **kw)

    def _segment_hook(self, src, segmenter, **kw):
        targets = self._locate_helper(segmenter.segment(src), **kw)
        if targets:
            if self.filter_targets:
                #use only targets that are close to cx,cy and the right size
                targets = self._filter_targets(targets)
            return targets

    def _get_filter_target_area(self):
        holedim = self.holedim
        miholedim = 0.5 * holedim
        maholedim = 1.25 * holedim
        mi = miholedim ** 2 * 3.1415
        ma = maholedim ** 2 * 3.1415
        return mi, ma

    def _filter_targets(self, targets, threshold=0.95):
        mi, ma = self._get_filter_target_area()

        def test_target(tar):
            '''
                if the convexity of the target is <threshold try to do a watershed segmentation
                
                make black image with white polygon
                do watershed segmentation
                find polygon center
                
            '''
            def test(ti):
                ctest = ti.convexity > threshold
                centtest = self._near_center(*ti.centroid_value)
                atest = ma > ti.area > mi
                return ctest, centtest, atest

            ctest, centtest, atest = test(tar)
            if not ctest and (atest and centtest):
#                src = self.target_image.get_frame(0)
#                self._draw_result(src, tar)
#                w, h = self.croppixels
#                self.target_image.save('/Users/ross/Sandbox/machine_vision/polygon.jpg', width=w, height=h)

                src = self.target_image.get_frame(0)
                draw_polygons(src, [tar.poly_points], color=(0, 255, 255))

                #make image with polygon
                image = zeros(self.croppixels)
                points = asarray(tar.poly_points)

                points = asarray([(pi.x, pi.y) for pi in points])
                rr, cc = polygon(points[:, 0], points[:, 1])

                image[cc, rr] = 255

                #do watershedding
                distance = ndimage.distance_transform_edt(image)
                local_maxi = is_local_maximum(distance, image)
                markers, ns = ndimage.label(local_maxi)
                wsrc = watershed(-distance, markers,
                                  mask=image
                                 )

                #find the label with the max area ie max of histogram
                def get_limits(values, bins):
                    ind = argmax(values)
                    if ind == 0:
                        bil = bins[ind]
                        biu = bins[ind + 1]
                    elif ind == len(bins) - 1:
                        bil = bins[ind - 1]
                        biu = bins[ind]
                    else:
                        bil = bins[ind - 1]
                        biu = bins[ind + 1]

                    return bil, biu, ind

                #bins = 3 * number of labels. this allows you to precisely pick the value of the max area
                values, bins = histogram(wsrc, bins=ns * 3)
                bil, biu, ind = get_limits(values, bins)

                if not bil:
                    values = delete(values, ind)
                    bins = delete(bins, (ind, ind + 1))
                    bil, biu, ind = get_limits(values, bins)

#                print values
#                print bins
#                print bil, biu

                nimage = ones_like(wsrc, dtype='uint8')
                nimage[wsrc < bil] = 0
                nimage[wsrc > biu] = 0

                img = asMat(nimage)

                #locate new polygon from the segmented image
                tars = self._locate_targets(img)
                if globalv.show_autocenter_debug_image:
                    do_later(lambda: self.debug_show(image, distance, wsrc, nimage))

                if tars:
                    tar = tars[0]
                    ctest, centtest, atest = test(tar)
#                    ctest = tar.convexity > threshold
#                    centtest = self.
                else:
                    return None, False

            return tar, ctest and atest and centtest

        ts = [test_target(ti) for ti in targets]
        return [ta[0] for ta in ts if ta[1]]

    def debug_show(self, image, distance, wsrc, nimage):

        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(ncols=4, figsize=(8, 2.7))
        ax0, ax1, ax2, ax3 = axes

        ax0.imshow(image, cmap=plt.cm.gray, interpolation='nearest')
        ax1.imshow(-distance, cmap=plt.cm.jet, interpolation='nearest')
        ax2.imshow(wsrc, cmap=plt.cm.jet, interpolation='nearest')
        ax3.imshow(nimage, cmap=plt.cm.jet, interpolation='nearest')

        for ax in axes:
            ax.axis('off')

        plt.subplots_adjust(hspace=0.01, wspace=0.01, top=1, bottom=0, left=0,
                        right=1)
        plt.show()
#============= EOF =====================================
#    def _watershed_segmentation(self, src, **kw):
##        from scipy import ndimage
#        from skimage.morphology import watershed, is_local_maximum
##        ndsrc = src.ndarray
##
##
##        distance = ndimage.distance_transform_edt(ndsrc)
##        local_maxi = is_local_maximum(distance, ndsrc,
##                                    ones((3, 3)))
##
##        markers = ndimage.label(local_maxi)[0]
##
###        wsrc = watershed(-distance, markers)
##
###        src = invert(src)
##        p = asMat(asarray(markers, 'uint8'))
##        self.target_image.set_frame(0, colorspace(p))
#
#        from scipy import ndimage
#        import numpy as np
#        import matplotlib.pyplot as plt
#        debug = True
#        if debug:
#            x, y = np.indices((80, 80))
#            x1, y1, x2, y2 = 28, 28, 44, 52
#            r1, r2 = 16, 20
#            mask_circle1 = (x - x1) ** 2 + (y - y1) ** 2 < r1 ** 2
#            mask_circle2 = (x - x2) ** 2 + (y - y2) ** 2 < r2 ** 2
#            image = np.logical_or(mask_circle1, mask_circle2)
#        else:
#            image = src.ndarray[:]
#
#            im = invert(image)
#            r = self._get_mask_radius()
#            self._apply_circular_mask(im, radius=r * 2)
#
#        distance = ndimage.distance_transform_edt(image)
#
#        local_maxi = is_local_maximum(distance, image, np.ones((3, 3)))
#        markers = ndimage.label(local_maxi)[0]
#        labels = watershed(-distance, markers, mask=image)
#
#        fig, axes = plt.subplots(ncols=3, figsize=(8, 2.7))
#        ax0, ax1, ax2 = axes
#
#        ax0.imshow(image, cmap=plt.cm.gray, interpolation='nearest')
#        ax1.imshow(-distance, cmap=plt.cm.jet, interpolation='nearest')
#        ax2.imshow(labels, cmap=plt.cm.spectral, interpolation='nearest')
#
#        from pyface.timer.do_later import do_later
##        do_later(plt.show)
#    def _random_walker_segmentation(self, src, **kw):
#        from skimage.segmentation import random_walker
#        import numpy as np
#        ndsrc = src.ndarray[:]
##        ndsrc += np.random.randn(*ndsrc.shape)
#        tlow = 100
#        thigh = 150
#        markers = zeros_like(ndsrc)
#        markers[ndsrc < tlow] = 1
#        markers[ndsrc > thigh] = 2
#
#        labels = random_walker(ndsrc, markers,
##                               beta=10
##                               , mode='bf'
#                               )
##        labels = markers
#
#        import matplotlib.pyplot as plt
#        plt.figure(figsize=(8, 3.2))
#        plt.subplot(131)
#        plt.imshow(ndsrc, cmap='gray', interpolation='nearest')
#        plt.axis('off')
#        plt.title('Noisy data')
#
#        plt.subplot(132)
#        plt.imshow(markers, cmap='hot', interpolation='nearest')
#        plt.axis('off')
#        plt.title('Markers')
#
#        plt.subplot(133)
#        plt.imshow(labels, cmap='gray', interpolation='nearest')
#        plt.axis('off')
#        plt.title('Segmentation')
#
#        plt.subplots_adjust(hspace=0.01, wspace=0.01, top=1, bottom=0, left=0,
#                            right=1)
#        from pyface.timer.do_later import do_later
#        do_later(plt.show)
#
#        return self._locate_helper(labels)#  
#  def _watershed(self, ndsrc):
#        from skimage.filter import sobel
#        from skimage.morphology import watershed, is_local_maximum
#        import matplotlib.pyplot as plt
#        from scipy import ndimage
#        image = ndsrc.ndarray
##        image = invert(ndsrc)
#        distance = ndimage.distance_transform_edt(image)
#        local_maxi = is_local_maximum(distance, image, ones((3, 3)))
#        markers = ndimage.label(local_maxi)[0]
#
#        labels = watershed(-distance, markers, mask=image) * 100
#        x, y = ndimage.find_objects(labels == 100)[0]
##        print
#        s = image[x, y]
#        print s.shape
##        labels = asarray(labels, 'uint8')
##        labels = invert(labels)
#
#        self.working_image.frames[0] = colorspace(asMat(s))
##        self.working_image.frames[0] = colorspace(asMat(labels))
##        plt.imshow(labels, cmap=plt.cm.spectral, interpolation='nearest')
#        do_later(plt.show)
#    def _co2_well(self, results):
#        devx, devy = zip(*[r.dev_centroid for r in results])
#
#        ind = max(0, len(results) / 2)
##        ind = 0
#        ts = results[ind].threshold_value
#        es = results[ind].erode_value
#        ds = results[ind].dilate_value
##        print ts, es, ds
#        return [], [], devx, devy, ts, ds, es


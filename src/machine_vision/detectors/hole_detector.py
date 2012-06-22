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
from traits.api import  Float, Range, Int, Bool, Enum
from traitsui.api import View, Item, VGroup, Group
#============= standard library imports ========================
from numpy import histogram, argmax, array, asarray, zeros_like, invert, \
    ones, ogrid, bincount
import random
import os
#============= local library imports  ==========================
from src.image.cvwrapper import draw_polygons, \
    threshold, grayspace, crop, centroid, new_point, contour, get_polygons, \
    draw_rectangle, draw_lines, colorspace, draw_circle, get_size, \
    asMat#, add_images

from src.helpers.paths import positioning_error_dir
from src.helpers.filetools import unique_path
from detector import Detector

DEVX = random.randint(-10, 10)
DEVY = random.randint(-10, 10)
DEVX = 0
DEVY = 0
CX = 2
CY = -2


class Target(object):
    centroid_value = None
    poly_points = None
    bounding_rect = None
    threshold = None

    @property
    def dev_centroid(self):
        return ((self.origin[0] - self.centroid_value[0]),
                (self.origin[1] - self.centroid_value[1]))

    @property
    def dev_br(self):
        return ((self.origin[0] - self.bounding_rect[0]),
                (self.origin[1] - self.bounding_rect[1]))

    @property
    def aspect_ratio(self):
        return self.bounding_rect.width / float(self.bounding_rect.height)

    @property
    def area(self):
        return self.bounding_rect.width * self.bounding_rect.height


class HoleDetector(Detector):

    _debug = False

    radius_mm = Float(1.5)

    _hole_radius = None

    cropwidth = Float(5)
    cropheight = Float(5)
    crop_expansion_scalar = Float(0.5)
    crosshairs_offsetx = 0
    crosshairs_offsety = 0

    save_positioning_error = Bool(False)
    use_histogram = Bool(True)
#    use_smoothing = Bool(True)
    use_crop = Bool(True)
#    use_dilation = Bool(False)
    _dilation_value = 1
#    use_contrast_equalization = Bool(True)

    segmentation_style = Enum('region', 'edge', 'threshold', 'edge', 'region')
#    segmentation_style = Enum('edge', 'threshold', 'edge', 'region')

    start_threshold_search_value = Int(80)
    threshold_search_width = Int(20)
    crop_tries = Range(0, 102, 1)  # > 101 makes it a spinner
    threshold_tries = Range(0, 102, 2)
    threshold_expansion_scalar = Int(5)

#    def close_image(self):
#        pass
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

    def _edge_segmentation(self, src, **kw):
        from scipy import ndimage
        from skimage.filter import canny

        ndsrc = src.ndarray / 255.
        edges = canny(ndsrc, sigma=2)
        filled = ndimage.binary_fill_holes(edges)

        label_objects, _ = ndimage.label(filled)
        sizes = bincount(label_objects.ravel())

        mask_sizes = sizes > 20
        mask_sizes[0] = 0
        cleaned = mask_sizes[label_objects]
        kw['convextest'] = False
        return self._locate_helper(cleaned, **kw)

    def _region_segmentation(self, src, tlow=100, thigh=150, **kw):
        from skimage.filter import sobel
        from skimage.morphology import watershed

        ndsrc = src.ndarray[:]

        markers = zeros_like(ndsrc)
        markers[ndsrc < tlow] = 1
        markers[ndsrc > thigh] = 255

        el_map = sobel(ndsrc)
        wsrc = watershed(el_map, markers)
        kw['convextest'] = False
        return self._locate_helper(invert(wsrc))

    def _threshold_segmentation(self, src, **kw):
        start = self.start_threshold_search_value
        end = start + self.threshold_search_width
        expand_value = self.threshold_expansion_scalar
        for i in range(self.threshold_tries):
            s = start - i * expand_value
            e = end + i * expand_value
            self.info('searching... thresholding image {} - {}'.format(s,
                                                                       e))
            targets = []
            for ti in range(s, e):
                tsrc = threshold(src, ti)

                ts = self._locate_targets(tsrc, convextest=False)
                if ts:
                    targets += ts

            return targets

    def _locate_helper(self, src, *args, **kw):

        src = asMat(asarray(src, 'uint8'))
        if not 'hole' in kw:
            kw['hole'] = False
        t = self._locate_targets(src, **kw)
        return t


    def _locate_targets(self, src, **kw):
#        dsrc = self.working_image.frames[0]
        contours, hieararchy = contour(src)
#        draw_contour_list(dsrc, contours, hieararchy)
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
#            try:
#                src = self.working_image.frames[0]
#                draw_polygons(src, [pi], thickness=2, color=(255, 255, 0))
#            except IndexError:
#                pass
            if len(pi) < 4:
                continue

            cx, cy = centroid(pi)
            use_radius_filter = False
            if use_radius_filter:
                cx, cy = self._radius_filter(pi, cx, cy)

            tr = Target()
            tr.origin = self._get_true_xy(src)
            tr.centroid_value = cx, cy
            tr.poly_points = pi
            tr.bounding_rect = br

#            if 'thresh' in kw:
#                tr.threshold = kw['thresh']

            targets.append(tr)

#        self.info('found {} targets'.format(len(targets)))
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

        dymm = (dy + 1) / float(self.pxpermm)
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
        src = grayspace(self.target_image.source_frame)
        self.target_image.set_frame(0, colorspace(crop(src, *self.croprect)))
#        self.image.frames[0] = colorspace(crop(src, *self.croprect))
        self._draw_markup(targets, dev=(dx, dy))

        self.parent._nominal_position = cx, cy
        self.parent._corrected_position = nx, ny

        args = cx, cy, nx, ny, dxmm, dymm, round(dx), round(dy)#int(dx), int(dy)

        self.info('current pos: {:0.3f},{:0.3f} calculated pos: {:0.3f}, {:0.3f} dev: {:0.3f},{:0.3f} ({:n},{:n})'.format(*args))

        if self.save_positioning_error and holenum:
            self._save_(holenum, cx, cy, nx, ny, dxmm, dymm)

        return nx, ny


    def _save_(self, holenum, cx, cy, nx, ny, dxmm, dymm):
        path, _ = unique_path(positioning_error_dir,
                              'positioning_error{:03n}_'.format(int(holenum)), filetype='jpg')
        self.target_image.save(path)
        #save an associated text file with some metadata
        head, _ = os.path.splitext(path)
        with open(head + '.txt', 'w') as f:
            f.write('hole={}\n'.format(holenum))
            f.write('nominal pos=   {:5f}, {:5f}\n'.format(cx, cy))
            f.write('corrected pos= {:5f}, {:5f}\n'.format(nx, ny))
            f.write('deviation=     {:5f}, {:5f}'.format(dxmm, dymm))

    def _draw_center_indicator(self, src, color=(0, 0, 255), size=10):
#        w, h = get_size(src)
#        x = float(w / 2)
#        y = float(h / 2)
#        self._draw_indicator(src, new_point(x, y), shape='crosshairs', color=color, size=size)
        self._draw_indicator(src, new_point(*self._get_true_xy(src)),
                             shape='crosshairs',
                             color=(0, 0, 255),
                             size=10)

    def _draw_result(self, src, result, with_br=False, thickness=1, color=(255, 0, 0)):
        self._draw_indicator(src, new_point(*result.centroid_value), shape='crosshairs')
        draw_polygons(src, [result.poly_points])
        if with_br:
            draw_rectangle(src, result.bounding_rect.x,
                                result.bounding_rect.y,
                                result.bounding_rect.width,
                                result.bounding_rect.height,
                                thickness=thickness,
                                color=color
                                )

    def _draw_markup(self, results, dev=None):
        #add to indicators to ensure the indicator is drawn on top
        indicators = []
        for pi in results:

            f0 = self.target_image.get_frame(0)

            draw_polygons(f0, [pi.poly_points], color=(255, 255, 0), thickness=1)

#            f1 = self.working_image.frames[0]
#            draw_contour_list(f1, pi.contours, hierarchy=pi.hierarchy)


            #draw the centroid in blue
            centroid_center = new_point(*pi.centroid_value)
#            indicators.append((f1, centroid_center , (0, 255, 0), 'rect', 2))

            #calculate bounding rect and bounding square for polygon
            r = pi.bounding_rect
#            draw_rectangle(f1, r.x, r.y, r.width, r.height)

            br_center = new_point(r.x + r.width / 2, r.y + r.height / 2)
#            indicators.append((f1,
#                               br_center,
#                               (255, 0, 0), 'rect', 2))

#                #if % diff in w and h greater than 20% than use the centroid as the calculated center
#                #otherwise use the bounding rect center            
#                dwh = abs(r.width - r.height) / float(max(r.width, r.height))
#                if dwh > 0.2:
#                    calc_center = centroid_center
#                else:
#                    calc_center = br_center

            calc_center = centroid_center
            #indicate which center is chosen                
            #indicators.append((f0, calc_center, (0, 255, 255), 'crosshairs', 4))
#            indicators.append((f1, calc_center, (0, 255, 255), 'crosshairs', 1))

            pi.center = calc_center

        #draw the center of the image
        true_cx, true_cy = self._get_true_xy(f0)

#        l = 1.5 * self.pxpermm / 2.0
        #self._draw_indicator(f0, new_point(true_cx, true_cy), (0, 0, 255), 'crosshairs', l)
        #self._draw_indicator(f1, new_point(true_cx, true_cy), (0, 0, 255), 'crosshairs', l)
        self._draw_center_indicator(f0)
#        self._draw_center_indicator(f1)

        for i in indicators:
            self._draw_indicator(*i)

#        #draw the calculated center
        if dev:
            self._draw_indicator(f0, new_point(true_cx - dev[0],
                                               true_cy - dev[1]), (255, 255, 0), 'crosshairs')
    def _draw_indicator(self, src, center, color=(255, 0, 0), shape='circle', size=4, thickness= -1):
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
        tol = 1.3 * self.pxpermm * self.radius_mm
        disp = lambda p:((p.x - cx) ** 2 + (p.y - cy) ** 2) ** 0.5
        disps = map(disp, pi)

        #filter by tol
        fpi = filter(lambda p:p[1] < tol, zip(pi, disps))
        if fpi:
            pii, disps = zip(*fpi)
        else:
            pii = pi
        # 3. recalc centroid
        return centroid(pii)
    def _get_center(self):
        cx = self.croppixels[0] / 2.0
        cy = self.croppixels[1] / 2.0
        return cx, cy

    def _near_center(self, x, y, tol=0.9):
        cx, cy = self._get_center()

        tol *= self.pxpermm
#        print x, y, cx, cy, abs(x - cx) < tol and abs(y - cy) < tol
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
        xo = 0
        yo = 0
        cw_px = int(cw * self.pxpermm)
        ch_px = int(ch * self.pxpermm)
        w, h = get_size(src)
        x = int((w - cw_px) / 2 + xo)
        y = int((h - ch_px) / 2 + yo)
        self.croppixels = (cw_px, ch_px)

        self.croprect = (x, y, cw_px, ch_px)
        src = crop(src, x, y, cw_px, ch_px)

        if image:
#            im = getattr(self.parent, update)
#            image.frames[0] = colorspace(src.clone())

            image.set_frame(0, colorspace(src.clone()))
#            self.image.frames[0] = colorspace(src.clone())
#            self.working_image.frames[0] = colorspace(src.clone())

        return src

    def traits_view(self):
        search_grp = Group(Item('start_threshold_search_value'),
                            Item('threshold_search_width'),
                            Item('threshold_expansion_scalar'),
                            Item('threshold_tries'),
                            Item('crop_tries'),
                            Item('crop_expansion_scalar'),
                            show_border=True,
                           label='Search',
                           )

        process_grp = Group(
                            Item('use_smoothing'),
                            Item('use_dilation'),
                            Item('use_histogram'),
                            Item('use_contrast_equalization'),
                            show_border=True,
                           label='Process')
        return View(Item('segmentation_style'),
                    VGroup(search_grp, process_grp),
                           Item('save_positioning_error'),
                            )
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


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
from traits.api import Float
from pyface.timer.do_later import do_later

# from src.geometry.centroid import centroid
#============= standard library imports ========================
import time
from numpy import array, histogram, argmax, zeros, asarray, delete, ones_like, invert
from skimage.morphology.watershed import is_local_maximum
from skimage.morphology import watershed
from skimage.draw import polygon
from scipy import ndimage
#============= local library imports  ==========================
# from src.geometry.centroid.calculate_centroid import calculate_centroid
from src.loggable import Loggable
from src.mv.segment.region import RegionSegmenter
from src.image.cv_wrapper import grayspace, draw_contour_list, contour, asMat, \
    colorspace, get_polygons, get_size, new_point, draw_circle, draw_rectangle, draw_lines, \
    draw_polygons
from src.mv.target import Target
# from src.image.image import StandAloneImage
from src.geometry.geometry import sort_clockwise, approximate_polygon_center, \
    calc_length
from src.geometry.convex_hull import convex_hull
import math


class Locator(Loggable):
    pxpermm = Float
    use_histogram = False
    use_circle_minimization = False
    def find(self, image, frame, dim):
        '''
            image is a stand alone image
            dim = float. radius or half length of a square in pixels
             
            find the hole in the image
            
            return the offset from the center of the image
            
            0. image is alredy cropped
            1. find polygons
            
        '''
        dx, dy = None, None

        targets = self._find_targets(image, frame, dim, step=2,
                                     preprocess=True,
                                     filter_targets=True)
#
        if targets:
            self.info('found {} potential targets'.format(len(targets)))

            # draw center indicator
#            src = image.get_frame(0)
            src = image.source_frame
            self._draw_center_indicator(src, size=2, shape='rect', radius=int(dim))

            # draw targets
            self._draw_targets(src, targets)


            if self.use_circle_minimization:

#                # calculate circle_minimization position
                dx, dy = self._circle_minimization(src, targets[0], dim)
#                dx, dy = self._calculate_error(targets)
            else:
#                # calculate error
                dx, dy = self._calculate_error(targets)

            # force repaint
            image.source_frame = src[:]

        return dx, dy

    def _circle_minimization(self, src, target, dim):
        '''
            find cx,cy of a circle with r radius using the arc center method
    
            only preform if target has high convexity 
            convexity is simply defined as ratio of area to convex hull area
            
        '''
        tol = 0.98
        if target.convexity < tol:
            tx, ty = self._get_frame_center(src)
            pts = target.poly_points
            pts[:, 1] = pts[:, 1] - ty
            pts[:, 0] = pts[:, 0] - tx
            cx, cy = approximate_polygon_center(pts, dim)
            cx, cy = cx + tx, cy + ty
            self._draw_indicator(src, (cx, cy), color=(255, 0, 128), shape='rect')
            draw_circle(src, (cx, cy), int(dim), color=(255, 0, 128),)

        else:
            cx, cy = self._calculate_error([target])

        return cx, cy

    def _calculate_error(self, targets):
        '''
            calculate the dx,dy 
            deviation of the targets centroid from the center of the image
        '''
        def hist(d):
            f, v = histogram(array(d))
            i = len(f)  if argmax(f) == len(f) - 1 else argmax(f)
            return v[i]

        devxs, devys = zip(*[r.dev_centroid for r in targets])
        if len(targets) > 2 and self.use_histogram:
                dx = hist(devxs)
                dy = hist(devys)
        else:
            avg = lambda s: sum(s) / len(s)
            dx = avg(devxs)
            dy = avg(devys)

        devxs, devys = zip(*[r.dev_centroid for r in targets])
        return -dx, dy

    def _find_targets(self, image, frame, dim, n=20, w=10, start=None, step=1,
                      preprocess=False, filter_targets=True, depth=0, set_image=True):
        '''
            use a segmentor to segment the image
        '''

        if preprocess:
            src = self._preprocess(frame)
        else:
            src = grayspace(frame)
#            image.set_frame(0, src)
#        image.set_frame(0, src)
#        return
        seg = RegionSegmenter(use_adaptive_threshold=False)
#        if seg.use_adaptive_threshold:
#            n = 1
        if start is None:
#            start = int(src.ndarray.mean()) - 3 * w
            start = int(asarray(src).mean()) - 3 * w

        fa = self._get_filter_target_area(dim)

        for i in range(n):
#            print i, start + i - w, start + i + w
            seg.threshold_low = start + i * step - w
            seg.threshold_high = start + i * step + w
            seg.block_size += 5
            nsrc = seg.segment(src)
#            print seg.threshold_low, seg.threshold_high, src.ndarray.mean()

            # convert to Mat
#            nsrc = asMat(nsrc)
#            nsrc = asarray(nsrc)

            nf = asarray(colorspace(nsrc))

            # find the contours
            contours, hieararchy = contour(nsrc)
            # convert to color for display

            # draw contours
            draw_contour_list(nf, contours, hieararchy)

            if set_image:
                # update the image
                image.set_frame(0, nf)
#            time.sleep(0.1)

#            return
            # do polygon approximation
            origin = self._get_frame_center(nsrc)
#            print origin
            pargs = get_polygons(nsrc, contours, hieararchy)
            targets = self._make_targets(pargs, origin)

#            continue
            # filter targets
            if filter_targets:
                targets = self._filter_targets(image, frame, dim, targets, fa)

            if targets:
                return targets

    def _make_targets(self, pargs, origin):
        '''
         convenience function for assembling target list
        '''
        targets = []
        for pi, ai, co, ci in zip(*pargs):
            if len(pi) < 4:
                continue

            tr = Target()
            tr.origin = origin
            tr.poly_points = pi
#            tr.bounding_rect = br
            tr.area = ai
            tr.min_enclose_area = co
            tr.centroid = ci

            targets.append(tr)

        return targets

    def _get_frame_center(self, src):
        '''
            convenience function for geting center of image in c,r from
        '''
        w, h = get_size(src)
        x = float(w / 2)
        y = float(h / 2)

        return x, y
#===============================================================================
# filter
#===============================================================================
    def _filter_targets(self, image, frame, dim, targets, fa, threshold=0.5):
        '''
            filter targets using the _filter_test function
            
            return list of Targets that pass _filter_test
        '''
#        import time
        test_target = self._filter_test
        ts = [test_target(image, frame, ti, dim, threshold, fa[0], fa[1]) for ti in targets]
        return [ta[0] for ta in ts if ta[1]]
#        ts = []
#        for i, ti in enumerate(targets):
#            ta = self._filter_test(image, frame, ti, dim, threshold, fa[0], fa[1])
#            if ta[1]:
#                ts.append(ta[0])
#
#        return ts

    def _near_center(self, xy, frame, tol=0.75):
        '''
            is the point xy within tol distance of the center
        '''
#        cx, cy = self._get_frame_center(frame)
#        x, y = xy
#        tol *= self.pxpermm
#        return abs(x - cx) < tol and abs(y - cy) < tol
#        from scipy.spatial.distance import cdist
        cxy = self._get_frame_center(frame)
        d = calc_length(xy, cxy)
        tol *= self.pxpermm
#        print 'dddddd', d, xy, cxy
        return d < tol


    def _get_filter_target_area(self, dim):
        '''
            calculate min and max bounds of valid polygon areas
        '''

        miholedim = 0.5 * dim
        maholedim = 1.25 * dim
        mi = miholedim ** 2 * 3.1415
        ma = maholedim ** 2 * 3.1415
        return mi, ma

    def _filter_test(self, image, frame, target, dim, cthreshold, mi, ma):
        '''
            if the convexity of the target is <threshold try to do a watershed segmentation
            
            make black image with white polygon
            do watershed segmentation
            find polygon center
            
        '''
        def test(ti):
            ctest = ti.convexity > cthreshold
            centtest = self._near_center(ti.centroid, frame)
            atest = ma > ti.area > mi
#            print ma, ti.area, mi, ti.convexity > cthreshold
#            print ti.convexity , cthreshold
#            print ctest, centtest, atest
            return ctest, centtest, atest

        # find the label with the max area ie max of histogram
        def get_limits(values, bins, width=1):
            ind = argmax(values)
            if ind == 0:
                bil = bins[ind]
                biu = bins[ind + width]
            elif ind == len(bins) - width:
                bil = bins[ind - width]
                biu = bins[ind]
            else:
                bil = bins[ind - width]
                biu = bins[ind + width]

            return bil, biu, ind

        ctest, centtest, atest = test(target)
#        print not ctest and (atest and centtest)
        if not ctest and (atest and centtest):
            src = image.source_frame[:]

 #            return
 #            src = image.get_frame(0)
 #            draw_polygons(src, [target.poly_points], color=(0, 255, 255))

            wh = get_size(src)
            # make image with polygon
            im = zeros(wh)
            points = asarray(target.poly_points)
            rr, cc = polygon(*points.T)

 #            points = asarray([(pi.x, pi.y) for pi in points])
 #            rr, cc = polygon(points[:, 0], points[:, 1])

            im[cc, rr] = 255

            # do watershedding
            distance = ndimage.distance_transform_edt(im)
            local_maxi = is_local_maximum(distance, im)
            markers, ns = ndimage.label(local_maxi)
            wsrc = watershed(-distance, markers,
                              mask=im
                             )

            # bins = 3 * number of labels. this allows you to precisely pick the value of the max area
            values, bins = histogram(wsrc, bins=ns * 3)
            bil, biu, ind = get_limits(values, bins)

            if not bil:
                values = delete(values, ind)
                bins = delete(bins, (ind, ind + 1))
                bil, biu, ind = get_limits(values, bins)

            nimage = ones_like(wsrc, dtype='uint8') * 255
            nimage[wsrc < bil] = 0
            nimage[wsrc > biu] = 0

            nimage = invert(nimage)
            img = nimage
 #            img = asMat(nimage)
            # locate new polygon from the segmented image
            tars = self._find_targets(image, img, dim, start=10, w=4, n=2, set_image=False)
#            tars = None
 #                do_later(lambda: self.debug_show(im, distance, wsrc, nimage))
            if tars:
                target = tars[0]
                ctest, centtest, atest = test(target)
            else:
                return None, False
#        print ctest, atest, centtest
        return target, ctest and atest and centtest

#===============================================================================
# drawing
#===============================================================================
    def _draw_targets(self, src, targets):
        '''
            draw a crosshairs indicator and the target's polygon
        '''

        for ta in targets:
            pt = new_point(*ta.centroid)
            self._draw_indicator(src, pt,
                                 color=(0, 255, 0),
                                 size=10,
                                 shape='crosshairs')
            draw_polygons(src, [ta.poly_points])

    def _draw_center_indicator(self, src, color=(0, 0, 255), shape='crosshairs',
                               size=10, radius=1):
        '''
            draw indicator at center of frame
        '''
        cpt = self._get_frame_center(src)
        self._draw_indicator(src, new_point(*cpt),
#                             shape='crosshairs',
                             shape=shape,
                             color=color,
                             size=size)

        draw_circle(src, cpt, radius, color=color, thickness=1)

    def _draw_indicator(self, src, center, color=(255, 0, 0), shape='circle', size=4, thickness=-1):
        '''
            convenience function for drawing indicators
        '''
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

#===============================================================================
# preprocessing
#===============================================================================
    def _preprocess(self, frame,
                    contrast=True, denoise=10, display=False):
        '''
            1. convert frame to grayscale
            2. remove noise from frame. increase denoise value for move noise filtering
            3. stretch contrast
        '''
#        if display:
#            # open original crop
#            im = StandAloneImage()
#            im.load(colorspace(frame))
#            do_later(im.edit_traits)
#        print type(frame), frame.shape
        frm = grayspace(frame)
#        print frm
#        if display:
#            # open original grayscale crop
#            im = StandAloneImage()
#            im.load(colorspace(frm))
#            do_later(im.edit_traits)
#        src = frm
#        print src
#        src = frm.ndarray[:]
#        src = asarray(frm[:, :])
#        denoise = 0
        # preprocess
        if denoise:
            frm = self._denoise(frm, weight=denoise)
#        contrast = False
        if contrast:
            frm = self._contrast_equalization(frm)

#        frm = asMat(src)
#        frm = asMat(src)
#        if display:
#            # open preprocessed
#            vim = StandAloneImage()
#            vim.load(colorspace(frm))
#            do_later(vim.edit_traits)
#        image.set_frame(0, frm)
#        image.source_frame = asarray(colorspace(frm))
        return frm

    def _denoise(self, img, weight):
        '''
            use TV-denoise to remove noise
            
            http://scipy-lectures.github.com/advanced/image_processing/
            http://en.wikipedia.org/wiki/Total_variation_denoising
        '''
        from skimage.filter import tv_denoise

        return tv_denoise(asarray(img), weight=weight).astype('uint8')

    def _contrast_equalization(self, img):
        '''
            rescale intensities to maximize contrast
        '''
        from skimage.exposure.exposure import rescale_intensity
#        from numpy import percentile
        # Contrast stretching
#        p2 = percentile(img, 2)
#        p98 = percentile(img, 98)
        return rescale_intensity(img).astype('uint8')


#============= EOF =============================================
#        from numpy import linspace, pi, cos, sin, radians
#        from math import atan2
#        from scipy.optimize import fmin
# #        dx, dy = None, None
# #        for ta in targets:
#        pts = array([(p.x, p.y) for p in target.poly_points], dtype=float)
#        pts = sort_clockwise(pts, pts)
#        pts = convex_hull(pts)
#        cx, cy = target.centroid
#        px, py = pts.T
#
#        tx, ty = self._get_frame_center(src)
#        px -= cx
#        py -= cy
#
#        r = dim * 0.5
#        ts = array([atan2(p[1] - cx, p[0] - cy) for p in pts])
# #        ts += 180
#        n = len(ts)
#        hidx = n / 2
#        h1 = ts[:hidx]
#
#        offset = 0 if n % 2 == 0 else 1
#
# #        h1 = array([ti for ti in ts if ti < 180])
# #        h1 = radians(h1)
# #        hidx = len(h1)
# #        print len(ts), hidx
# #        offset = 0
#        def cost(p0):
#            '''
#                cost function
#
#                A-D: chord of the polygon
#                B-C: radius of fit circle
#
#                A  B             C  D
#
#                try to minimize difference fit circle and polygon approx
#                cost=dist(A,B)+dist(C,D)
#            '''
# #            r = p0[2]
#            # northern hemicircle
#            cix1, ciy1 = p0[0] - cx + r * cos(h1), p0[1] - cy + r * sin(h1)
#
#            # southern hemicircle
#            cix2, ciy2 = p0[0] - cx + r * cos(h1 + pi), p0[1] - cy + r * sin(h1 + pi)
#
#            dx, dy = px[:hidx] - cix1, py[:hidx] - ciy1
#            p1 = (dx ** 2 + dy ** 2) ** 0.5
#
# #            dx, dy = cix2 - px[hidx + offset:], ciy2 - py[hidx + offset:]
#            dx, dy = px[hidx + offset:] - cix2, py[hidx + offset:] - ciy2
#            p2 = (dx ** 2 + dy ** 2) ** 0.5
# #            print 'p1', p1
# #            print 'p2', p2
#            return ((p2 - p1) ** 2).sum()
# #            return (p1 + p2).mean()
# #            return p2.sum() + p1.sum()
#
#        # minimize the cost function
#        dx, dy = fmin(cost, x0=[0, 0], disp=False)  # - ta.centroid
#        print dx, dy, ty, cy
# #        dy -= cy
# #        dx -= cx
#
# #        print ty + cy, dy
#        self._draw_indicator(src, (dx, dy), shape='rect')
#        draw_circle(src, (dx, dy), int(r))
#
#        return dx - target.origin[0], dy - target.origin[1]
# def debug_show(image, distance, wsrc, nimage):
#
#    import matplotlib.pyplot as plt
#    fig, axes = plt.subplots(ncols=4, figsize=(8, 2.7))
#    ax0, ax1, ax2, ax3 = axes
#
#    ax0.imshow(image, cmap=plt.cm.gray, interpolation='nearest')
#    ax1.imshow(-distance, cmap=plt.cm.jet, interpolation='nearest')
#    ax2.imshow(wsrc, cmap=plt.cm.jet, interpolation='nearest')
#    ax3.imshow(nimage, cmap=plt.cm.jet, interpolation='nearest')
#
#    for ax in axes:
#        ax.axis('off')
#
#    plt.subplots_adjust(hspace=0.01, wspace=0.01, top=1, bottom=0, left=0,
#                    right=1)
#    plt.show()

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
from traits.api import HasTraits, Int, Float
from traitsui.api import View, Item, TableEditor
from pyface.timer.do_later import do_later

# from src.geometry.centroid import centroid
#============= standard library imports ========================
import time
from numpy import array, histogram, argmax, zeros, asarray, delete, ones_like, invert, \
    interp
from skimage.morphology.watershed import is_local_maximum
from skimage.morphology import watershed
from skimage.draw import polygon
from scipy import ndimage
#============= local library imports  ==========================
# from src.geometry.centroid.calculate_centroid import calculate_centroid
from src.loggable import Loggable
from src.mv.segment.region import RegionSegmenter
from src.image.cvwrapper import grayspace, draw_contour_list, contour, asMat, \
    colorspace, get_polygons, get_size, new_point, draw_circle, draw_rectangle, draw_lines, \
    draw_polygons
from src.mv.target import Target
from src.image.image import StandAloneImage

class Locator(Loggable):
#    cropwidth = Int(3)
#    cropheight = Int(3)
    pxpermm = Float
    use_histogram = False
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
        if targets:
            self.info('found {} potential targets'.format(len(targets)))

            # calculate error
            dx, dy = self._calculate_error(targets)

            # draw center indicator
            src = image.get_frame(0)
            self._draw_center_indicator(src, size=2, shape='rect')

            # draw targets
            self._draw_targets(src, targets)

        return dx, dy

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
                      preprocess=False, filter_targets=True, depth=0):
        '''
            use a segmentor to segment the image
        '''
        if preprocess:
            src = self._preprocess(image, frame)
        else:
            src = grayspace(frame)
            image.set_frame(0, src)


        seg = RegionSegmenter(use_adaptive_threshold=False)
#        if seg.use_adaptive_threshold:
#            n = 1

        if start is None:
            start = int(src.ndarray.mean()) - 3 * w

        fa = self._get_filter_target_area(dim)
#        print '----------------------'
        for i in range(n):
#            print i, start + i - w, start + i + w
            seg.threshold_low = start + i * step - w
            seg.threshold_high = start + i * step + w
            seg.block_size += 5
            nsrc = seg.segment(src)
#            print seg.threshold_low, seg.threshold_high, src.ndarray.mean()

            # convert to Mat
            nsrc = asMat(nsrc)

            # find the contours
            contours, hieararchy = contour(nsrc)

            # convert to color for display
            nsrc = colorspace(nsrc)

            # draw contours
            draw_contour_list(nsrc, contours, hieararchy)

            # update the image
            image.set_frame(0, nsrc)

            # do polygon approximation
            origin = self._get_frame_center(nsrc)
            pargs = get_polygons(contours, hieararchy)
            targets = self._make_targets(pargs, origin)

#            print 'i=', i, len(targets)
            # filter targets
            if filter_targets:
                targets = self._filter_targets(image, frame, dim, targets, fa)

#            time.sleep(0.5)
            if targets:
#                print 'would return'
                return targets

    def _make_targets(self, pargs, origin):
        targets = []
        for pi, br, ai in zip(*pargs):
            if len(pi) < 4:
                continue

#            pts = array([(pt.x, pt.y) for pt in pi], dtype=float)
#            cx, cy = calculate_centroid(pts)

            tr = Target()
            tr.origin = origin
#            tr.centroid_value = cx, cy
            tr.poly_points = pi
            tr.bounding_rect = br
            tr.area = ai

            targets.append(tr)

        return targets

    def _get_frame_center(self, src):
        w, h = get_size(src)
        x = float(w / 2)
        y = float(h / 2)

        return x, y
#===============================================================================
# filter
#===============================================================================
    def _filter_targets(self, image, frame, dim, targets, fa, threshold=0.8):
        test_target = self._filter_test
        ts = [test_target(image, frame, ti, dim, threshold, fa[0], fa[1]) for ti in targets]
        return [ta[0] for ta in ts if ta[1]]

    def _near_center(self, xy, frame, tol=0.75):
        cx, cy = self._get_frame_center(frame)
        x, y = xy
        tol *= self.pxpermm
        return abs(x - cx) < tol and abs(y - cy) < tol

    def _get_filter_target_area(self, dim):
        miholedim = 0.6 * dim
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
#                print fa[1], ti.area, fa[0]
#                print ctest, centtest, atest
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
        if not ctest and (atest and centtest):
            src = image.get_frame(0)
            draw_polygons(src, [target.poly_points], color=(0, 255, 255))

            wh = get_size(src)
            # make image with polygon
            im = zeros(wh)
            points = asarray(target.poly_points)

            points = asarray([(pi.x, pi.y) for pi in points])
            rr, cc = polygon(points[:, 0], points[:, 1])

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
            img = asMat(nimage)
            # locate new polygon from the segmented image
            tars = self._find_targets(image, img, dim, start=10, w=4, n=2)
#                do_later(lambda: self.debug_show(im, distance, wsrc, nimage))

            if tars:
                target = tars[0]
                ctest, centtest, atest = test(target)
            else:
                return None, False

        return target, ctest and atest and centtest

#===============================================================================
# drawing
#===============================================================================
    def _draw_targets(self, src, targets):
        for ta in targets:
            self._draw_indicator(src, new_point(*ta.centroid),
                                 color=(0, 255, 0),
                                 size=10,
                                 shape='crosshairs')
            draw_polygons(src, [ta.poly_points])

    def _draw_center_indicator(self, src, color=(0, 0, 255), shape='crosshairs', size=10):
        self._draw_indicator(src, new_point(*self._get_frame_center(src)),
#                             shape='crosshairs',
                             shape=shape,
                             color=color,
                             size=size)

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

#===============================================================================
# preprocessing
#===============================================================================
    def _preprocess(self, image, frame,
                    contrast=True, denoise=10, display=False):
        '''
            1. convert frame to grayscale
            2. remove noise from frame. increase denoise value for move noise filtering
            3. stretch contrast
        '''
        if display:
            # open original crop
            im = StandAloneImage()
            im.load(colorspace(frame))
            do_later(im.edit_traits)

        frm = grayspace(frame)

        if display:
            # open original grayscale crop
            im = StandAloneImage()
            im.load(colorspace(frm))
            do_later(im.edit_traits)

        src = frm.ndarray[:]

        # preprocess
        if denoise:
            src = self._denoise(src, weight=denoise)
        if contrast:
            src = self._contrast_equalization(src)

        frm = asMat(src[:])

        if display:
            # open preprocessed
            vim = StandAloneImage()
            vim.load(colorspace(frm))
            do_later(vim.edit_traits)

        image.set_frame(0, frm)
        return frm

    def _denoise(self, img, weight):
        from skimage.filter import tv_denoise
        return tv_denoise(img, weight=weight).astype('uint8')

    def _contrast_equalization(self, img):
#        from numpy import percentile
        from skimage.exposure.exposure import rescale_intensity
        # Contrast stretching
#        p2 = percentile(img, 2)
#        p98 = percentile(img, 98)
        return rescale_intensity(img,
#                                 in_range=(p2, p98)
                                 )


#============= EOF =============================================
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

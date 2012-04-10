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
#=============enthought library imports=======================
from traits.api import Any
#============= standard library imports ========================
import numpy as np
#============= local library imports  ==========================
from hole_detector import HoleDetector
from src.image.cvwrapper import colorspace, grayspace, draw_rectangle, \
    new_point, asMat, erode, dilate
import time
from pyface.timer.do_later import do_later
#from src.image.pyopencv_image_helper import asMat

class TrayMapper(HoleDetector):
#    style = 'co2_mapper'
#    center_mx = 0
#    center_my = 0
#
    image_width = 640
    image_height = 480
    stage_map = Any

    correction_dict = None

    def _get_non_corrected(self):
        nholes = len(self.stage_map.sample_holes)
        set(range(1, nholes + 1)) - set(map(int, self.correction_dict.keys()))

    def _add_correction(self, key, val):
        '''
            returns true if this is the first correction for this hole
        '''
        try:
            self.correction_dict[key].append(val)
        except KeyError:
            self.correction_dict[key] = [val]
            return True

    def _get_origin(self):
        pp = 2.0 * self.pxpermm
        ox = self.center_mx - self.image_width / pp
        oy = self.center_my - self.image_height / pp
        return ox, oy

    def map_mm(self, x, y):
        ox, oy = self._get_origin()
        y = self.image_height - y
#        print ox, oy, x, y
        mx = x / float(self.pxpermm) + ox
        my = y / float(self.pxpermm) + oy

        return mx, my

    def map_screen(self, x, y):

        cx = self.center_mx
        cy = self.center_my
        sx = (x - cx) * self.pxpermm + self.image_width / 2

        sy = (cy - y) * self.pxpermm + self.image_height / 2
        return sx, sy

    def map_holes(self):
        self.parent.show_image()

        self.correction_dict = dict()
        regions = [(0, 0)]
        mapped_holes = 0
        n = len(self.stage_map.sample_holes)
        for r in regions:
            mapped_holes += self.map_holes_in_region(r)
            self.info('mapped {} of {} holes ({:0.1f}%)'.format(mapped_holes,
                                            n, mapped_holes / float(n) * 100))

        non_cor = self._get_non_corrected()
        if non_cor:
            self.info('no correction found for {}'.format(
                                ' '.join(map(str, non_cor))))
            for ni in non_cor:
                mx, my = self.stage_map.get_hole_pos(str(ni))
                w, h = 20
#                draw_rectangle(self.image.frames[1], mx - w / 2, my - h / 2,
#                         w, h, color=(255, 255, 0), thickness=2)

#    def _region_segmentation(self, src):
#        ndsrc = src.ndarray
#        from scipy import ndimage
#
#        bins, edges = np.histogram(ndsrc.ravel(), bins=np.arange(0, 256))
##        cen = np.argmax(bins)
#
##        tlow = edges[max(0, cen - 1)]
##        thigh = edges[min(len(edges), cen + 1)]
#
##        from pylab import show, hist
##        hist(ndsrc.ravel(), bins=np.arange(0, 256))
##        do_later(show)
#        tlow = 80
#        thigh = 130
#        markers = np.zeros_like(ndsrc)
#        markers[ndsrc < tlow] = 1
#        markers[ndsrc > thigh] = 255
#
#        from skimage.filter import sobel
#        from skimage.morphology import watershed
#        el_map = sobel(ndsrc)
##        el_map = ndimage.binary_opening(el_map)
##        el_map = ndimage.binary_closing(el_map)
##        print el_map * 255
#        segm = watershed(el_map, markers)
#        segm = np.invert(segm)
#
##        ndsrc = ndimage.binary_fill_holes(ndsrc)
##        print 'ddd', segm
#
##        import matplotlib.pyplot as plt
##        plt.imshow(segm, interpolation='nearest')
##        plt.imshow(markers, cmap=plt.cm.spectral, interpolation='nearest')
##        plt.show()
#        return asMat(np.asarray(segm, 'uint8'))
##        return asMat(np.asarray(el_map * 255, 'uint8'))



    def map_holes_in_region(self, region):
#        self.image.contrast_equalize()
#        self.image.smooth()

#        self.use_dilation = False
#        self.use_erosion = False
        src = self.image.source_frame
        gsrc = grayspace(src)

        self.image.frames[0] = colorspace(gsrc)
        self.working_image.frames = [colorspace(gsrc)]
        t_s = 75
        t_e = t_s + 10
        tol = 0.07
        a = 1800
        atol = 500
        mapped_holes = 0
#        r = 50
        m = 100
#        for ti in range(t_s, t_e + 1):
        osrc = gsrc.clone()
#        for ti in range(2, 40, 1):
#            time.sleep(0.5)

        osrc = dilate(osrc, 1)
        osrc = erode(osrc, 1)
        results = self._region_segmentation(osrc,
                                            min_area=1000,
                                            max_area=a,
                                            convextest=False
                                            )


#            gsrc = self._edge_segmentation(gsrc)
#        results = self._calc_sample_hole_position(gsrc, 0,
#                                        0, 0,
#                                        max_area=2000,
#                                        convextest=False,
#                                        hole=False
#                                        )
        if results:
            self.info('calculated n results {}'.format(len(results)))
            c = 0

            for r in results:
                if (abs(r.aspect_ratio - 1) < tol
                    and abs(r.area - a) < atol):
#                        self._draw_result(self.image.frames[1],
#                                 r, with_br=True, thickness=2)
                    c += 1

                    # convert centroid into mm
                    cargs = self.map_mm(*r.centroid_value)
                    cpos = self.calibrated_center
                    rot = self.calibrated_rotation

                    mmx, mmy = self.stage_map.map_to_calibration(cargs,
                                                                cpos, rot)

                    #check for a match to the stage map
                    hole = self.stage_map._get_hole_by_position(mmx, mmy)
                    if hole is not None:
                        if self._add_correction(hole.id, (mmx, mmy)):
                            self._draw_result(self.image.frames[0], r,
                                               with_br=False, thickness=2)

                            tx = hole.x
                            ty = hole.y

                            #map to calibrated space
                            pos = (tx, ty)
#                                print rot
#                                rot = 0

                            pos = self.stage_map.map_to_uncalibration(pos,
                                                                cpos, rot)

                            #map to screen
                            pos = self.map_screen(*pos)

#                                self._draw_indicator(self.image.frames[0],
#                                        new_point(*pos), color=(255, 255, 0))

                            mapped_holes += 1
#                                print mapped_holes, hole.id
#                        else:
#                            print 'not locating ', mmx, mmy
#                raw_input(' ...')

#                    else:
#                        self._draw_result(self.image.frames[1], r, with_br=True, thickness=2, color=(255, 255, 0))
#                        print 'ar', abs(r.aspect_ratio - 1) < tol, 'area', abs(r.area - a) < atol
#                        time.sleep(0.5)
#                        print r.aspect_ratio, r.area

#                print len(results), 'acceptable', c
#            time.sleep(1)
        return mapped_holes

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('machine_visionasfd')
    t = TrayMapper(center_mx=3.596,
                   center_my= -13.321,
                   pxpermm=23)
    x = 0
    y = -15.9521
    x = 4.596
    y = -13.321
    x, y = -0.536197606705, -14.7107613114
    t.map_screen(x, y)

#============= EOF =====================================

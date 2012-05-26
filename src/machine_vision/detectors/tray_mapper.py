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
from traits.api import Any
#============= standard library imports ========================
import numpy as np
#============= local library imports  ==========================
from hole_detector import HoleDetector
from src.image.cvwrapper import colorspace, grayspace, draw_rectangle, \
    new_point, asMat, erode, dilate
import time
from pyface.timer.do_later import do_later
from co2_detector import CO2HoleDetector
#from src.image.pyopencv_image_helper import asMat

class TrayMapper(CO2HoleDetector):
    center_mx = 0
    center_my = 0
#
    image_width = 640
    image_height = 480
    stage_map = Any
    use_crop = False
    correction_dict = None

    def _segmentation_style_hook(self):
        self.map_holes()

    def _get_non_corrected(self):
        nholes = len(self.stage_map.sample_holes)
        return list(set(range(1, nholes + 1)) - \
                    set(map(int, self.correction_dict.keys())))

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

    def map_holes(self,):
        self.parent.show_image()

        self.correction_dict = dict()
#        regions = [(0, 0)]
        mapped_holes = 0
        n = len(self.stage_map.sample_holes)
#        for r in regions:
        mapped_holes += self.map_holes_in_region()
        self.info('mapped {} of {} holes ({:0.1f}%)'.format(mapped_holes,
                                        n, mapped_holes / float(n) * 100))

#        non_cor = self._get_non_corrected()
#        print non_cor
#        if non_cor:
#            self.info('no correction found for {} holes'.format(len(non_cor)))
##            self.info('no correction found for {}'.format(
##                                ' '.join(map(str, non_cor))))
#            for ni in non_cor:
#                mx, my = self.stage_map.get_hole_pos(str(ni))
#
#                cpos = self.calibrated_center
#                rot = self.calibrated_rotation
#
#                cx, cy = self.stage_map.map_to_uncalibration((mx, my), cpos, rot)
##                cx, cy = self.map_screen(cx, cy)
#
#                mx, my = self.map_screen(cx, cy)
#                w, h = 20, 20
#                draw_rectangle(self.image.frames[0], mx - w / 2, my - h / 2,
#                         w, h, color=(255, 255, 0), thickness=2)


    def map_holes_in_region(self):
        src = self.image.source_frame
        gsrc = grayspace(src)

        self.image.frames[0] = colorspace(gsrc)
        self.working_image.frames = [colorspace(gsrc)]
        tol = 0.07
        a = 2000
        atol = 500
        mapped_holes = 0
        osrc = gsrc.clone()

        osrc = self.contrast_equalization(osrc)
        osrc = self.smooth(osrc)

#        func = getattr(self, '_{}_segmentation'.format(self.segmentation_style))
#        results = func(osrc, min_area=1000, max_area=a,
#                       convextest=False)

        func = self._region_segmentation
        rresults = func(osrc, min_area=1000, max_area=a,
                       convextest=False)
#        rresults = []
        func = self._edge_segmentation
        eresults = func(osrc, min_area=1000, max_area=a,
                       convextest=False)

        if rresults is None:
            rresults = []
        if eresults is None:
            eresults = []

        results = rresults + eresults
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

#                            tx = hole.x
#                            ty = hole.y

                            #map to calibrated space
#                            pos = (tx, ty)
#                            pos = self.stage_map.map_to_uncalibration(pos,
#                                                                cpos, rot)
#
##                            #map to screen
#                            pos = self.map_screen(*pos)
#
#                            self._draw_indicator(self.image.frames[0],
#                                    new_point(*pos), color=(255, 255, 0))

                            mapped_holes += 1

            for k, v in self.correction_dict.iteritems():
                xs, ys = zip(*v)
                cx = sum(xs) / len(xs)
                cy = sum(ys) / len(ys)
                self.stage_map.set_hole_correction(k, cx, cy)

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

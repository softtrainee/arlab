#'''
#Copyright 2011 Jake Ross
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#'''
##============= enthought library imports =======================
##============= standard library imports ========================
#
##from numpy import array
##============= local library imports  ==========================
#from image_helper import erode, dilate, draw_squares, draw_rectangle, \
#    new_dst, new_size, new_point, new_mask, new_rect, grayspace, colorspace, threshold, contour, draw_contour_list, \
#    clone, new_seq, avg, rotate, get_polygons, draw_polygons, subsample, \
#    avg_std, get_min_max_location, draw_point, convert_seq, equalize
#
#
#from image import Image
#from src.data_processing.centroid.centroid import centroid
#
#class TargetImage(Image):
#    '''
#    '''
#
#    def process(self, thresh, angle, erode=False, dilate=False):
#        '''
#   
#        '''
#        ta = None
#        self.frames = []
#
#        #display original
#        timg = rotate(clone(self.source_frame), angle)
#        self.frames.append(timg)
#
#        #preprocess and get a thresholded source
#        tsrc = self.preprocess(timg, erode, dilate, thresh)
#
#        #locate the target and return the boundng rect
#        try:
#            br, polygons = self.locate_target(tsrc)
#        except:
#            pass
##        if br:
##            #a bounding rect has been calculated 
##            #calculate the targets pixel values
##            ta, p1, p2, minpt, maxpt = self.calculate_target_value(self.source_frame, br)
##
##            for f in self.frames:
##                draw_point(f, minpt, color = (0, 255, 0))
##                draw_point(f, maxpt, color = (0, 255, 255))
##
##                #draw_rectangle(f, p1, p2)
##
##                for po in polygons[:1]:
##                    data = convert_seq(po)
##                    datap = []
##                    for d in data:
##                        draw_point(f, d)
##                        datap.append((float(d.x), float(d.y)))
##
##
##
##                    draw_point(f, centroid(array(datap)))
#
#
#        return ta
#
#    def preprocess(self, src, erode_value, dilate_value, thresh):
#        '''
#        '''
#        #display original gray scaled
#        gsrc = grayspace(src)
#        cgsrc = colorspace(gsrc)
#        gsrc = equalize(gsrc)
#
#        self.frames.append(cgsrc)
#
#        if erode_value:
#            #display an eroded gray scale
#            edst = erode(gsrc, erode_value)
#            #edst=clone(gsrc)
#            #cvErode(edst,edst,0,erode)
#            self.frames.append(colorspace(edst))
#            gsrc = edst
#
#        if dilate_value:
#            #display a dilated gray scale
#            #ddst=clone(gsrc)
#            ddst = dilate(gsrc, dilate_value)
#            self.frames.append(colorspace(ddst))
#            gsrc = ddst
#
#        #threshold and display the gray scale
#        tsrc = threshold(gsrc, thresh)
#
#        self.frames.append(colorspace(tsrc))
#
#        return tsrc
#
#    def calculate_target_value(self, src, bounding_rect):
#        '''
#            @type src: C{str}
#            @param src:
#
#            @type bounding_rect: C{str}
#            @param bounding_rect:
#        '''
#
#        x0 = bounding_rect.x
#        y0 = bounding_rect.y
#        w = bounding_rect.width
#        h = bounding_rect.height
#
#        x2 = x0 + w
#        y2 = y0 + h
#        o0 = 0#55
#        o2 = 0#55
#
#        nw, nh = abs(w - o0 - o2), abs(h - o0 - o2)
#        subrect = subsample(src, x0 + o0, y0 + o0, nw, nh)
#
##        ta = avg_std(subrect)
#        ta = avg(subrect)
#
#        mask = new_mask(src, x0 + o0, y0 + o0, nw, nh)
#        _minval, _maxval, minpt, maxpt = get_min_max_location(src, mask)
#
#
#
#        return ta, new_point(x0 + o0, y0 + o0), new_point(x2 - o2, y2 - o2), minpt, maxpt
#
#    def locate_target(self, tsrc):
#        '''
#            
#        '''
#
#        #contour the threshold source
#        _nc, contours = contour(tsrc)
#        if contours:
#            #display the contours 
#            csrc = clone(colorspace(tsrc))
#            #draw_contour_list(csrc, contours)
#
#            #approximate and draw polygons from contours
#            polygons, br = get_polygons(contours)
#            draw_polygons(csrc, polygons)
#            self.frames.append(csrc)
#            return br, polygons
#
#
#
#
#
#
##============= EOF ====================================

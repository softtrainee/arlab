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
from traits.api import HasTraits, Any, List, Int, Bool

#=============standard library imports ========================
import wx
#=============local library imports  ==========================

from ctypes_opencv import cvConvertImage, cvCloneImage, \
    cvResize, cvFlip, \
    CV_CVTIMG_SWAP_RB
from image_helper import load_image, new_dst, grayspace, clone
#from src.image.image_helper import threshold, colorspace, contour, get_polygons, \
#    draw_polygons, find_circles, find_ellipses, clone, crop, draw_contour_list, \
#    centroid, erode
#from ctypes_opencv.cxcore import CvPoint, cvRound, cvCircle



class Image(HasTraits):
    '''
    '''
    frames = List
    source_frame = Any
    width = Int
    height = Int
    _bitmap = None
    _frame = None

#    def load(self, img, swap_rb=True):
    def load(self, img):
        if isinstance(img, str):
            img = load_image(img)

#        if swap_rb:
#            cvConvertImage(img, img, CV_CVTIMG_SWAP_RB)

        self.source_frame = img
        self.frames = [clone(img)]

    def update_bounds(self, obj, name, old, new):
        if new:
            self.width = new[0]
            self.height = new[1]

    def _get_frame(self):
        return self.source_frame

    def get_frame(self, flip=False, mirror=False, gray=False, swap_rb=True, clone=False):


        rframe = self._get_frame()
        if rframe is not None:



            if swap_rb:
                cvConvertImage(rframe, rframe, CV_CVTIMG_SWAP_RB)

            frame = new_dst(rframe, width=self.width,
                              height=self.height)

            cvResize(rframe, frame)
            if clone:
                frame = cvCloneImage(frame)

            if flip and mirror:
                cvFlip(frame, flip_mode=2)
            elif mirror:
                cvFlip(frame, flip_mode=1)
            elif flip:
                cvFlip(frame)

            if gray:
                frame = grayspace(frame)

            return frame

    def get_bitmap(self, **kw):#flip = False, swap_rb = False, mirror = True):
        '''

        '''
#        kw = dict()
#        if swap_rb:
#            kw['flag'] = CV_CVTIMG_SWAP_RB

        frame = self.get_frame(**kw)

        if frame is not None:
            self._frame = frame
            self._bitmap = wx.BitmapFromBuffer(frame.width,
                                       frame.height,
                                       frame.data_as_string()
                                        )
            return self._bitmap
#            return cvIplImageAsBitmap(frame, flip = flip, swap = swap_rb)
#
#            data = ctypes.string_at(frame.imageData, frame.width * frame.height * 4)
#            #print data
#
#            if self._bitmap is None:
#                self._bitmap = wx.BitmapFromBuffer(frame.width,
#                                                 frame.height,
#                                                 frame.data_as_string()
#                                                 )
#
#            else:
#                self._bitmap.CopyFromBuffer(frame.data_as_string())
#                
##
#            return self._bitmap





#    def _source_frame_changed(self):
#        '''
#        '''
#        self.frames = [self.source_frame]
#    sources=List
#    source=String
#    sources=['/Users/Ross/Desktop/calibration_chamber.png']
#    
#    frames=List
#    frame=Any
#    
#    low_threshold=Float(50)
#    high_threshold=Float(120)
#    
#    low_low=Float(0)
#    low_high=Float(50)
#    
#    high_low=Float(0)
#    high_high=Float(255)
#    
#    #control=Any
#    center=Tuple
#    def get_avg(self,frame=None):
#        if frame is None:
#            frame=self.frame
#        
#        return cvAvg(frame)#,cvAvgSdv(frame),cvSum(frame)
#    def _low_threshold_changed(self):
#        if self.frame:
#            self.process(self.frame)
#            
#    def _high_threshold_changed(self):
#        
#        if self.frame:
#            self.low_high=self.high_threshold
#            self.process(self.frame)
#            
#    def save(self,root, path=None):
#        return save_image(self.frame, root, path=path)
#         
#    def process(self,frame=None):
#        
#        if frame is None:
#            frame=cvLoadImage(self.sources[0])
#        
#        self.frame=frame=cvCloneImage(frame)
#        
#        gray_frame=grayspace(frame)
#        thresh_g,cont_frame=contour(gray_frame,threshold=self.high_threshold)

#        center=(100,100)
#        subframe=subsample(frame,
#                           add_rect=True,
#                           width=640,height=480,
#                           center=center)
#
#        g_subframe=grayspace(subframe)
#
#        cframe=canny(g_subframe,self.low_threshold,self.high_threshold)
#
#        line_frame=lines(cframe)
#        histframe=histogram(frame)

#        self.frames=[
#                     frame,
#                     colorspace(thresh_g),
#                     cont_frame
#                     ]

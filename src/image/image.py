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
from numpy import asarray, flipud, ndarray
#=============local library imports  ==========================

from ctypes_opencv import cvConvertImage, cvCloneImage, \
    cvResize, cvFlip, \
    CV_CVTIMG_SWAP_RB, cvCreateImageFromNumpyArray
from image_helper import load_image, new_dst, grayspace, clone
from src.image.image_helper import crop, draw_lines, save_image, threshold, \
    colorspace, subsample
from ctypes_opencv.interfaces import cvCreateMatNDFromNumpyArray, pil_to_ipl
from ctypes_opencv.cxcore import cvCreateImage, cvGetImage, CvSize, cvZero, \
    cvAddS, CvScalar, CvRect, cvSetImageROI, cvResetImageROI, \
    cvCreateImageHeader, cvSize, cvSetData, IPL_DEPTH_8U
from Image import fromarray
import math
from ctypes import cast, c_byte, POINTER
#from ctypes_opencv.cv import cvCvtColor
#from ctypes_opencv.interfaces import ipl_to_pil
#from src.image.image_helper import threshold, colorspace, contour, get_polygons, \
#    draw_polygons, find_circles, find_ellipses, clone, crop, draw_contour_list, \
#    centroid, erode
#from ctypes_opencv.cxcore import CvPoint, cvRound, cvCircle
def my_pil_to_ipl(im_pil, nc):
        im_ipl = cvCreateImageHeader(cvSize(im_pil.size[0], im_pil.size[1]),
IPL_DEPTH_8U, nc)
        data = im_pil.tostring('raw', 'L', im_pil.size[0] * nc)
        cvSetData(im_ipl, cast(data, POINTER(c_byte)), im_pil.size[0] * nc)
#        cvCvtColor(im_ipl, im_ipl, CV_RGB2BGR)
        im_ipl._depends = (data,)
        return im_ipl
class GraphicsContainer(object):

    _lines = None

    def add_line(self, l):
        if self._lines is None:
            self._lines = [l]
        else:
            self._lines.append(l)

    @property
    def lines(self):
        return self._lines

class Image(HasTraits):
    '''
    '''
    frames = List
    source_frame = Any
    width = Int
    height = Int
    _bitmap = None
    _frame = None

    graphics_container = None

    swap_rb = Bool(False)
    flip = Bool(False)
    panel_size = Int(300)
    def new_graphics_container(self):
        self.graphics_container = GraphicsContainer()

#    def load(self, img, swap_rb=True):
#    def swap_rb(self):
#        cvConvertImage(self.source_frame, self.source_frame, CV_CVTIMG_SWAP_RB)
#        self.frames[0] = self.source_frame

    def load(self, img, swap_rb=False, nchannels=3):
        if isinstance(img, str):
            img = load_image(img, swap_rb)

        elif isinstance(img, ndarray):
#            img = cvCreateImageFromNumpyArray(img)
#            print fromarray(img)
            if nchannels < 3:
                img = my_pil_to_ipl(fromarray(img), nchannels)
                img = colorspace(img)
            else:
                img = pil_to_ipl(fromarray(img))
#            mat = cvCreateMatNDFromNumpyArray(img)
#            img = cvGetImage(mat)

#            FromNumpyArray(img)
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

    def get_array(self, swap_rb=True, cropbounds=None):
        f = self.source_frame
        if swap_rb:
            f = clone(self.source_frame)
            cvConvertImage(f, f, CV_CVTIMG_SWAP_RB)


        a = f.as_numpy_array()
        if cropbounds:
            a = a[
                cropbounds[0]:cropbounds[1],
                cropbounds[2]:cropbounds[3]
                ]

        return flipud(a)#[lx / 4:-lx / 4, ly / 4:-ly / 4]

    def get_frame(self, flip=None, mirror=False, gray=False, swap_rb=None, clone=False, croprect=None):
        rframe = self._get_frame()
        if rframe is not None:
#            if raw:
#                frame = rframe
#            else:
#                frame = new_dst(rframe, width=self.width,
#                              height=self.height)
            frame = new_dst(rframe, width=self.width,
                          height=self.height)

            if swap_rb is None:
                swap_rb = self.swap_rb

            self.swap_rb = swap_rb

            if swap_rb:
                #cool fractal display
#                cvConvertImage(frame, rframe, CV_CVTIMG_SWAP_RB)
                cvConvertImage(rframe, rframe, CV_CVTIMG_SWAP_RB)

            cvResize(rframe, frame)
            rframe = frame
            if clone:
                frame = cvCloneImage(frame)

            if flip is None:
                flip = self.flip

            if flip and mirror:
                cvFlip(rframe, flip_mode=2)
            elif mirror:
                cvFlip(rframe, flip_mode=1)
            elif flip:
                cvFlip(rframe)

            if gray:
                frame = grayspace(rframe)

#                frame = threshold(frame, 255)

            if self.graphics_container:
                draw_lines(rframe, self.graphics_container.lines)

            if croprect:

                if len(croprect) == 2: # assume w, h
#                    args = (frame, (frame.width - croprect[0]) / 2, (frame.height - croprect[1]) / 2, croprect[0], croprect[1])
                    croprect = (frame.width - croprect[0]) / 2, (frame.height - croprect[1]) / 2, croprect[0], croprect[1]
                else:
                    pass
#                    args = (frame,) + croprect
                d = frame.as_numpy_array()
                rs = croprect[0]
                re = croprect[0] + croprect[2]
                cs = croprect[1]
                ce = croprect[1] + croprect[3]
                d = d[cs:ce, rs:re]

                frame = pil_to_ipl(fromarray(d))

#                crop(*args)
#                frame = subsample(*args)
                #pixelcrop(*args)
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

    def render_images(self, src):
        nsrc = len(src)
        rows = math.floor(math.sqrt(nsrc))
        cols = rows
        if rows * rows < nsrc:
            cols = rows + 1
            if cols * rows < nsrc:
                rows += 1

#        size = 300
        size = self.panel_size
        #create display image
        w = self.width
        h = self.height

        display = cvCreateImage(CvSize(w, h), 8, 3)

        cvZero(display)
        cvAddS(display, CvScalar(200, 200, 200), display)
        padding = 12
        m = padding
        n = padding
        for i, s in enumerate(src):
            x = s.width
            y = s.height
            ma = float(max(x, y))
            scale = ma / size
            if i % cols == 0 and m != padding:
                m = padding
                n += size + padding

            cvSetImageROI(display, CvRect(int(m), int(n), int(x / scale), int(y / scale)))
            cvResize(s, display)
            cvResetImageROI(display)
            m += (padding + size)
        return display

    def save(self, path):
        src = self.render_images(self.frames)
        cvConvertImage(src, src, CV_CVTIMG_SWAP_RB)
        save_image(src, path)

    def _draw_crosshairs(self, src):
        r = 10
        pts = [[(src.width / 2, 0), (src.width / 2, src.height / 2 - r)],
               [(src.width / 2, src.height / 2 + r), (src.width / 2, src.height)],
               [(0, src.height / 2), (src.width / 2 - r, src.height / 2)],
               [(src.width / 2 + r, src.height / 2), (src.width , src.height / 2)],
               ]
        draw_lines(src, pts, color=(0, 255, 255), thickness=1)

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

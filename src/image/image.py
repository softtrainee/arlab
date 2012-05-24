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
from traits.api import HasTraits, Any, List, Int, Bool

#=============standard library imports ========================
import wx
from numpy import asarray, flipud, ndarray, hstack, array, ones, vstack, zeros, \
    percentile
#=============local library imports  ==========================
from cvwrapper import swapRB, grayspace, cvFlip, \
    draw_lines, add_scalar, new_dst, \
    resize, asMat, frompil, save_image, load_image, \
    get_size, smooth, denoise#, setImageROI, resetImageROI
    #cvSetImageROI, cvResetImageROI

#class GraphicsContainer(object):
#
#    _lines = None
#
#    def add_line(self, l):
#        if self._lines is None:
#            self._lines = [l]
#        else:
#            self._lines.append(l)
#
#    @property
#    def lines(self):
#        return self._lines
#from numpy.core.numeric import zeros
import Image as PILImage
from pyface.timer.do_later import do_later, do_after


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

#    def new_graphics_container(self):
#        self.graphics_container = GraphicsContainer()

#    def load(self, img, swap_rb=True):
#    def swap_rb(self):
#        cvConvertImage(self.source_frame, self.source_frame, CV_CVTIMG_SWAP_RB)
#        self.frames[0] = self.source_frame

    def load(self, img, swap_rb=False, nchannels=3):
        if isinstance(img, (str, unicode)):
            img = load_image(img, swap_rb)

        elif isinstance(img, ndarray):
#            img = cvCreateImageFromNumpyArray(img)
#            print fromarray(img)
#            if nchannels < 3:
#                img = my_pil_to_ipl(fromarray(img), nchannels)
#                img = colorspace(img)
#            else:
#                img = pil_to_ipl(fromarray(img))
#            mat = cvCreateMatNDFromNumpyArray(img)
#            img = cvGetImage(mat)
            pass
#            FromNumpyArray(img)
#        if swap_rb:
#            cvConvertImage(img, img, CV_CVTIMG_SWAP_RB)

        self.source_frame = img

#        self.frames = [clone(img)]
        self.frames = [img.clone()]

    def update_bounds(self, obj, name, old, new):
        if new:
            self.width = new[0]
            self.height = new[1]

    def _get_frame(self, **kw):
        return self.source_frame

    def get_array(self, swap_rb=True, cropbounds=None):
        f = self.source_frame
        if swap_rb:
            f = self.source_frame.clone()
            f = swapRB(f)
#            f = clone(self.source_frame)
#            cv.convertImage(f, f, CV_CVTIMG_SWAP_RB)

        a = f.as_numpy_array()
        if cropbounds:
            a = a[
                cropbounds[0]:cropbounds[1],
                cropbounds[2]:cropbounds[3]
                ]

        return flipud(a)#[lx / 4:-lx / 4, ly / 4:-ly / 4]

    def get_frame(self, flip=None, mirror=False, gray=False, swap_rb=None,
                  clone=False, croprect=None, size=None, **kw):
        frame = self._get_frame(**kw)
        if frame is not None:
#            if raw:
#                frame = rframe
#            else:
#                frame = new_dst(rframe, width=self.width,
#                              height=self.height)
#            frame = new_dst(rframe, width=self.width,
#                          height=self.height)

            if swap_rb is None:
                swap_rb = self.swap_rb

            self.swap_rb = swap_rb

            if swap_rb:
                #cool fractal display
#                cvConvertImage(frame, rframe, CV_CVTIMG_SWAP_RB)
#                cvConvertImage(rframe, rframe, CV_CVTIMG_SWAP_RB)
#                rframe = swapRB(rframe)
                frame = swapRB(frame)

#            cvResize(rframe, frame)
#            rframe = frame
            if clone:
#                frame = cvCloneImage(frame)
                frame = frame.clone()

            if flip is None:
                flip = self.flip

            if flip and mirror:
                cvFlip(frame, flip_mode=2)
            elif mirror:
                cvFlip(frame, flip_mode=1)
            elif flip:
                cvFlip(frame, 0)

            if gray:
                frame = grayspace(frame)

#                frame = threshold(frame, 255)

#            if self.graphics_container:
#                draw_lines(rframe, self.graphics_container.lines)

            if croprect:

                if len(croprect) == 2: # assume w, h
#                    args = (frame, (frame.width - croprect[0]) / 2, (frame.height - croprect[1]) / 2, croprect[0], croprect[1])

                    w, h = get_size(frame)
                    croprect = (w - croprect[0]) / 2, (h - croprect[1]) / 2, croprect[0], croprect[1]
                else:
                    pass
#                    args = (frame,) + croprect
                #d = frame.as_numpy_array()
                d = frame.ndarray
                rs = croprect[0]
                re = croprect[0] + croprect[2]
                cs = croprect[1]
                ce = croprect[1] + croprect[3]
                d = d[cs:ce, rs:re]
                frame = asMat(d)
#                frame = pil_to_ipl(fromarray(d))

#                crop(*args)
#                frame = subsample(*args)
                #pixelcrop(*args)

            if size:
                frame = resize(frame, *size)

            return frame

    def get_bitmap(self, **kw):#flip = False, swap_rb = False, mirror = True):
        '''

        '''
#        kw = dict()
#        if swap_rb:
#            kw['flag'] = CV_CVTIMG_SWAP_RB
        frame = self.get_frame(**kw)
        try:
            return frame.to_wx_bitmap()
        except AttributeError:
            if frame is not None:
                self._frame = frame
                return wx.BitmapFromBuffer(frame.width,
                                       frame.height,
                                       frame.data_as_string()
                                        )

    def render_images(self, src):

#        w = sum([s.size()[0] for s in src])
#        h = sum([s.size()[1] for s in src])
        w = 600
        h = 600
        display = new_dst(w, h, 3)
        try:
            s1 = src[0].ndarray
            s2 = src[1].ndarray
        except IndexError:
            resize(src[0], w, h, dst=display)
            return display
        except (TypeError, AttributeError):
            return

        try:
            s1 = src[0].ndarray
            s2 = src[1].ndarray

            npad = 2
            pad = asMat(zeros((s1.shape[0], npad, s1.shape[2]), 'uint8'))
            add_scalar(pad, (255, 0, 255))

            s1 = hstack((pad.ndarray, s1))
            s1 = hstack((s1, pad.ndarray))
            s1 = hstack((s1, s2))
            da = hstack((s1, pad.ndarray))

            vpad = asMat(zeros((npad, da.shape[1], da.shape[2]), 'uint8'))
            add_scalar(vpad, (0, 255, 255))
            da = vstack((vpad.ndarray, da))
            da = vstack((da, vpad.ndarray))

            i1 = PILImage.fromarray(da)
            composite = frompil(i1)

            resize(composite, w, h, dst=display)
        except TypeError:
            pass

        return display

    def save(self, path, src=None):
        if src is None:
            src = self.render_images(self.frames)
        display = new_dst(640, 480, 3)
        resize(src, 640, 480, dst=display)
#        cvConvertImage(src, src, CV_CVTIMG_SWAP_RB)
#        src = swapRB(src)
        save_image(display, path)

    def _draw_crosshairs(self, src):
        r = 10

        w, h = map(int, get_size(src))
        pts = [[(w / 2, 0), (w / 2, h / 2 - r)],
               [(w / 2, h / 2 + r), (w / 2, h)],
               [(0, h / 2), (w / 2 - r, h / 2)],
               [(w / 2 + r, h / 2), (w, h / 2)],
               ]
        draw_lines(src, pts, color=(0, 255, 255), thickness=1)

from traits.api import Instance
from traitsui.api import View, Item, Handler
from src.image.image_editor import ImageEditor

class StandAloneImage(HasTraits):
    _image = Instance(Image, ())
    width = Int(600)
    height = Int(600)
    view_identifier = None
    title = None
    ui = Any
    def __image_default(self):
        return Image(width=self.width, height=self.height)

#    def __getattr__(self, attr):
#        if hasattr(self._image, attr):
#            return getattr(self._image, attr)
#        else:
#            pass
    def show(self):
        do_after(1, self.edit_traits)

    def close(self):
        if self.ui is not None:
            do_later(self.ui.dispose)
        self.ui = None

    def load(self, src):
        self._image.load(src)

    @property
    def source_frame(self):
        return self._image.source_frame

    def set_frames(self, fs):
        self._image.frames = fs

    def set_frame(self, i, src):
        self._image.frames[i] = src
        return self._image.source_frame

    def get_frame(self, i):
        return self._image.frames[i]

    def save(self, path):
        self._image.save(path)

    def traits_view(self):

        imgrp = Item('_image', show_label=False, editor=ImageEditor(),
                      width=self.width,
                      height=self.height,
                      style='custom'
                      )

        v = View(imgrp,
                 handler=ImageHandler,
                 x=0.55,
                 y=35,
                 width=self.width,
                 height=self.height + 22,
#                 resizable=True
                 )

        if self.title is not None:
            v.title = self.title

        if self.view_identifier is not None:
            v.id = self.view_identifier

        return v

class ImageHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui



if __name__ == '__main__':
    src = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321-an4.tiff'
    im = StandAloneImage()
    im.load(src)
    im.configure_traits()

#======== EOF ================================
#    def render_images1(self, src):
#        nsrc = len(src)
#        rows = math.floor(math.sqrt(nsrc))
#        cols = rows
#        if rows * rows < nsrc:
#            cols = rows + 1
#            if cols * rows < nsrc:
#                rows += 1
#
##        size = 300
#        size = self.panel_size
#        #create display image
#        w = self.width
#        h = self.height
#
##        display = cvCreateImage(CvSize(w, h), 8, 3)
##        display = cvCreateImage(CvSize(w, h), 8, 3)
##        display = new_color_dst(w, h)
#        display = new_dst(w, h, 3)
##        zero(display)
#        add_scalar(display, 100)
#        #cvAddS(display, CvScalar(200, 200, 200), display)
#        padding = 12
#        m = padding
#        n = padding
#        for i, s in enumerate(src[:0]):
#
##            x = s.width
##            y = s.height
#            x, y = get_size(s)
#
#            ma = float(max(x, y))
#            scale = ma / size
#            if i % cols == 0 and m != padding:
#                m = padding
#                n += size + padding
#            display.adjustROI(m, n, int(x / scale), int(y / scale))
#
##            setImageROI(display, new_rect(int(m), int(n), int(x / scale),
##                                            int(y / scale)))
#            resize(s, 640, 480, dst=display)
#            display.adjustROI(0, 0, w, h)
##            resetImageROI(display)
#            m += (padding + size)
#
#        return display
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

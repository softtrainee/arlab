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
from traits.api import HasTraits, Any, List, Int, Bool, on_trait_change

#=============standard library imports ========================
import wx
from numpy import asarray, flipud, ndarray
from globals import globalv
from src.image.pyopencv_image_helper import colorspace
#=============local library imports  ==========================
try:
    from cvwrapper import swapRB, grayspace, cvFlip, \
    draw_lines, new_dst, \
    resize, asMat, save_image, load_image, \
    get_size, cv_swap_rb
except ImportError:
    pass
# class GraphicsContainer(object):
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
# from numpy.core.numeric import zeros
# import Image as PILImage
from pyface.timer.do_later import do_later, do_after

# from src.helpers.memo import memoized
class Image(HasTraits):
    '''
    '''
    frames = List
    source_frame = Any
#    current_frame = Any
    width = Int
    height = Int
    _bitmap = None
    _frame = None

    graphics_container = None

    swap_rb = Bool(False)
    hflip = Bool(False)
    vflip = Bool(False)
#    mirror = Bool(False)
    panel_size = Int(300)

    @classmethod
    def new_frame(cls, img, swap_rb=False):
        if isinstance(img, (str, unicode)):
            img = load_image(img, swap_rb)

        elif isinstance(img, ndarray):
            img = asMat(asarray(img, dtype='uint8'))

        if swap_rb:
            cv_swap_rb(img)

        return img

    def load(self, img, swap_rb=False, nchannels=3):
#        if isinstance(img, (str, unicode)):
#            img = load_image(img, swap_rb)
#
#        elif isinstance(img, ndarray):
#            img = asMat(asarray(img, dtype='uint8'))
#            img = colorspace(img)
#            img = cvCreateImageFromNumpyArray(img)
#            print fromarray(img)
#            if nchannels < 3:
#                img = my_pil_to_ipl(fromarray(img), nchannels)
#                img = colorspace(img)
#            else:
#                img = pil_to_ipl(fromarray(img))
#            mat = cvCreateMatNDFromNumpyArray(img)
#            img = cvGetImage(mat)
#            pass
#            FromNumpyArray(img)
#        if swap_rb:
#            cvConvertImage(img, img, CV_CVTIMG_SWAP_RB)
#        print img
#        if swap_rb:
#            cv_swap_rb(img)
#        print img.reshape(960, 960)

        img = self.new_frame(img, swap_rb)
        self.source_frame = img
#        self.current_frame = img.clone()
        self.frames = [img.clone()]

#        self.frames = [clone(img)]

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

        return flipud(a)  # [lx / 4:-lx / 4, ly / 4:-ly / 4]

    def get_frame(self, **kw):
#        try:
#            del self._frame
#        except AttributeError:
#            pass

        frame = self._get_frame(**kw)
        frame = self.modify_frame(frame, **kw)
        return frame

    def get_image(self, **kw):
        frame = self.get_frame(**kw)
        return frame.to_pil_image()


    def get_bitmap(self, **kw):  # flip = False, swap_rb = False, mirror = True):
        '''

        '''
#        kw = dict()
#        if swap_rb:
#            kw['flag'] = CV_CVTIMG_SWAP_RB
#        print kw
        frame = self.get_frame(**kw)
        try:
            return frame.to_wx_bitmap()
        except AttributeError:
            if frame is not None:
#                self._frame = frame
                return wx.BitmapFromBuffer(frame.width,
                                       frame.height,
                                       frame.data_as_string()
                                        )

    def modify_frame(self, frame, vflip=None, hflip=None , gray=False, swap_rb=None,
                  clone=False, croprect=None, size=None):
        if frame is not None:
            def _get_param(param, p):
                if param is None:
                    return getattr(self, p)
                else:
#                    setattr(self, p, param)
                    return param
            swap_rb = _get_param(swap_rb, 'swap_rb')
            vflip = _get_param(vflip, 'vflip')
            hflip = _get_param(hflip, 'hflip')

            if clone:
                frame = frame.clone()

            if swap_rb:
                frame = swapRB(frame)

            if gray:
                frame = grayspace(frame)

            if croprect:
                if len(croprect) == 2:  # assume w, h
                    w, h = get_size(frame)
                    croprect = (w - croprect[0]) / 2, (h - croprect[1]) / 2, croprect[0], croprect[1]
                else:
                    pass

                rs = croprect[0]
                re = croprect[0] + croprect[2]
                cs = croprect[1]
                ce = croprect[1] + croprect[3]

                frame = asMat(frame.ndarray[cs:ce, rs:re])

            if size:
                resize(frame, *size)

            if not globalv.video_test:
                if vflip:
                    if hflip:
                        cvFlip(frame, -1)
                    else:
                        cvFlip(frame, 0)
                elif hflip:
                    cvFlip(frame, 1)

        return frame

#    @memoized
#    def render_images(self, src):
    def render(self):

#        w = sum([s.size()[0] for s in src])
#        h = sum([s.size()[1] for s in src])
#        print w,h, src[0].size()
        w = self.width
        h = self.height - 15
#        display =
        try:
            return resize(self.frames[0], w, h, dst=new_dst(w, h, 3))
        except IndexError:
            pass
#        return display

#        try:
#            s1 = src[0].ndarray
#            s2 = src[1].ndarray
#        except IndexError:
#            resize(src[0], w, h, dst=display)
#            return display
#        except (TypeError, AttributeError):
#            return
#
#        try:
#            s1 = src[0].ndarray
#            s2 = src[1].ndarray
#
#            npad = 2
#            pad = asMat(zeros((s1.shape[0], npad, s1.shape[2]), 'uint8'))
#            add_scalar(pad, (255, 0, 255))
#
#            s1 = hstack((pad.ndarray, s1))
#            s1 = hstack((s1, pad.ndarray))
#            s1 = hstack((s1, s2))
#            da = hstack((s1, pad.ndarray))
#
#            vpad = asMat(zeros((npad, da.shape[1], da.shape[2]), 'uint8'))
#            add_scalar(vpad, (0, 255, 255))
#            da = vstack((vpad.ndarray, da))
#            da = vstack((da, vpad.ndarray))
#
#            i1 = PILImage.fromarray(da)
#            composite = frompil(i1)
#
#            resize(composite, w, h, dst=display)
#        except TypeError:
#            pass


    def save(self, path, src=None, width=640, height=480):
        if src is None:
            src = self.render()
#            src = self.render_images(self.frames)
#        display =

#        cvConvertImage(src, src, CV_CVTIMG_SWAP_RB)
#        src = swapRB(src)
        save_image(resize(src, width, height, dst=new_dst(width, height, 3)), path)

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
    width = Int(300)
    height = Int(300)
    view_identifier = None
    title = None
    ui = Any
#    thresholdv = Int
#    osrc = None
#    def _thresholdv_changed(self):
#        if self.osrc is None:
#            self.osrc = grayspace(self._image.get_frame(0))
#            self.osrc = crop(self.osrc, 640 / 2, 480 / 2, 200, 200)

#        print 'fff'
#        im = self.get_frame(0)
#        tim = threshold(im, self.thresholdv)
#        self.source_frame = tim
#        self.set_frame(0, None)
#        self.load(self.source_frame)
#        self.set_frame(0, self.source_frame)
#        print self._image.frames[0] == self.source_frame
#        sc = self._image.source_frame
#        tim = threshold(self.osrc, self.thresholdv)
# #        self._image = Image(width=self.width, height=self.height)
# #        self.load(colorspace(tim))
#        self.set_frame(0, colorspace(tim))
#
    def __image_default(self):
        return Image(width=self.width, height=self.height)

#    def __getattr__(self, attr):
#        if hasattr(self._image, attr):
#            return getattr(self._image, attr)
#        else:
#            pass
    @on_trait_change('width, height')
    def wh_update(self, obj, name, old, new):
        setattr(self._image, name, getattr(self, name))

    def show(self):
        do_after(1, self.edit_traits)

    def close(self):
        if self.ui is not None:
            do_later(self.ui.dispose)
        self.ui = None

    def load(self, src, **kw):
        self._image.load(src, **kw)

    @property
    def source_frame(self):
        return self._image.source_frame

    def set_frames(self, fs):
        self._image.frames = fs

    def set_frame(self, i, src):
        if isinstance(src, ndarray):
            src = asMat(src)
        self._image.frames[i] = colorspace(src)

    def get_frame(self, i):
        return self._image.frames[i]

    def save(self, *args, **kw):
        self._image.save(*args, **kw)

    def traits_view(self):

        imgrp = Item('_image', show_label=False, editor=ImageEditor(),
                      width=self.width,
                      height=self.height,
                      style='custom'
                      )

        v = View(
#                 Item('thresholdv'),
                 imgrp,
                 handler=ImageHandler,
                 x=0.55,
                 y=35,
                 width=self.width,
                 height=self.height + 22,
                 resizable=True
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
# #        size = 300
#        size = self.panel_size
#        #create display image
#        w = self.width
#        h = self.height
#
# #        display = cvCreateImage(CvSize(w, h), 8, 3)
# #        display = cvCreateImage(CvSize(w, h), 8, 3)
# #        display = new_color_dst(w, h)
#        display = new_dst(w, h, 3)
# #        zero(display)
#        add_scalar(display, 100)
#        #cvAddS(display, CvScalar(200, 200, 200), display)
#        padding = 12
#        m = padding
#        n = padding
#        for i, s in enumerate(src[:0]):
#
# #            x = s.width
# #            y = s.height
#            x, y = get_size(s)
#
#            ma = float(max(x, y))
#            scale = ma / size
#            if i % cols == 0 and m != padding:
#                m = padding
#                n += size + padding
#            display.adjustROI(m, n, int(x / scale), int(y / scale))
#
# #            setImageROI(display, new_rect(int(m), int(n), int(x / scale),
# #                                            int(y / scale)))
#            resize(s, 640, 480, dst=display)
#            display.adjustROI(0, 0, w, h)
# #            resetImageROI(display)
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
# #
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

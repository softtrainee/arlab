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
from traits.api import  Any, Bool, Float, List, Int
#=============standard library imports ========================
from threading import Thread

#=============local library imports ===========================
from ctypes_opencv import cvCreateCameraCapture, cvQueryFrame, cvWriteFrame
#    cvIplImageAsBitmap, \
#    cvConvertImage, cvCloneImage, \
#    cvResize, cvWriteFrame, \
#    CV_CVTIMG_SWAP_RB

from image_helper import clone, save_image, new_video_writer
from image_helper import crop as icrop
import time
from src.image.image import Image

class Video(Image):
    '''
    '''
    cap = Any
    track_mouse = Bool
    mouse_x = Float
    mouse_y = Float
#    snapshot = Button
#    data_directory = Any

    users = List

    _recording = Bool(False)

    def open(self, user=None):
        '''

        '''
        if self.cap is None:
            try:
                self.cap = cvCreateCameraCapture(0)
                self.width = 640
                self.height = 480

            except:
                self.cap = None

        if not user in self.users:
            self.users.append(user)

    def shutdown(self):
        self.users = []
        del(self.cap)

    def close(self, user=None, force=False):
        '''
  
        '''
#        i = self.users.index(user)
        if user in self.users:
            i = self.users.index(user)
            self.users.pop(i)
            if not self.users:

                del(self.cap)

#    def update_bounds(self, obj, name, old, new):
#        if new:
#            self.width = new[0]
#            self.height = new[1]
#
#    def get_frame(self, gray = False, flag = None, clone = False):
#        '''
#
#        '''
    def _get_frame(self):
        if self.cap is not None:

            return  cvQueryFrame(self.cap)


#
#            frame = new_dst(rframe, width = self.width,
#                          height = self.height)
#
#            cvResize(rframe, frame)
#            if flag is not None:
#                cvConvertImage(frame, frame, flag)
#            if clone:
#                frame = cvCloneImage(frame)
#
#            if gray:
#                frame = grayspace(frame)
#            return frame
#
#    def get_bitmap(self, flip = False, swap_rb = False):
#        '''
#
#        '''
#        kw = dict()
#        if swap_rb:
#            kw['flag'] = CV_CVTIMG_SWAP_RB
#
#        frame = self.get_frame(**kw)
#        if frame is not None:
#            return cvIplImageAsBitmap(frame, flip = flip)

    def start_recording(self, path):
        fps = 5.0
        def __record():
            if self.cap is not None:
                #fps = cvGetCaptureProperty(self.cap, CV_CAP_PROP_FPS)
                self._recording = True
                writer = new_video_writer(path)
                while self._recording:
                    st = time.time()
                    img = cvQueryFrame(self.cap)
                    cvWriteFrame(writer, img)
                    d = 1 / fps - (time.time() - st)
                    if d >= 0:
                        time.sleep(d)

        t = Thread(target=__record)
        t.start()

    def stop_recording(self):
        '''
        '''
        self._recording = False

    def record_frame(self, path, crop=None):
        '''
        '''

        src = self.get_frame()
        if src is not None:

            if crop:
                icrop(*((src,) + crop))
            save_image(src, path)

        return clone(src)


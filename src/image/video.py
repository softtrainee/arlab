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
from traits.api import  Any, Bool, Float, List
#=============standard library imports ========================
from threading import Thread, Lock

#=============local library imports ===========================
#from ctypes_opencv import cvCreateCameraCapture, cvQueryFrame, cvWriteFrame
#    cvIplImageAsBitmap, \
#    cvConvertImage, cvCloneImage, \
#    cvResize, cvWriteFrame, \
#    CV_CVTIMG_SWAP_RB

#from image_helper import clone, save_image, new_video_writer
#from image_helper import crop as icrop

import time
from src.image.image import Image
#from src.image.image_helper import load_image
#from multiprocessing.process import Process
from cvwrapper import get_capture_device, query_frame, write_frame, \
    load_image, new_video_writer, grayspace

DEBUG = False
#DEBUG = True


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
    _lock = None

    def open(self, user=None, identifier=0):
        '''

        '''
        self._lock = Lock()
        self.width = 640
        self.height = 480
        if self.cap is None:

            #ideally an identifier is passed in 
            try:
                if DEBUG:
                    self.cap = 1
                else:
#                    self.cap = cvCreateCameraCapture(0)
                    self.cap = get_capture_device(identifier)
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
        if user in self.users:
            i = self.users.index(user)
            self.users.pop(i)
            if not self.users:
                del(self.cap)

    def _get_frame(self, **kw):
        if self.cap is not None:
            with self._lock:
                if DEBUG:
#                    src = '/Users/ross/Sandbox/tray_screen_shot3.tiff'
                    src = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321-an4.tiff'
                    return load_image(src)

                self._frame = query_frame(self.cap)
            return self._frame

#                return  cvQueryFrame(self.cap)

    def start_recording(self, path, user=None):
        fps = 1 / 8.
        size = 640 / 2, 480 / 2

        def __record():
            if self.cap is None:
                self.open(user=user)

            if self.cap is not None:
                self._recording = True

                writer = new_video_writer(path, 1 / fps,
                                          size
                                          )

                while self._recording:
                    st = time.time()
                    src = self._frame

                    if src is None:
                        src = self.get_frame(clone=True)
                    self._draw_crosshairs(src)
                    write_frame(writer, grayspace(src))

                    d = fps - (time.time() - st)
                    if d >= 0:
                        time.sleep(d)

        t = Thread(target=__record)
        t.start()

    def stop_recording(self):
        '''
        '''
        self._recording = False

    def record_frame(self, path, crop=None, **kw):
        '''
        '''
        src = self.get_frame(**kw)
        if src is not None:

#            if crop:
#                icrop(*((src,) + crop))
            self.save(path, src=src)

        return src.clone()

#=================== EOF =================================================

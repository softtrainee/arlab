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
from traits.api import  Any, Bool, Float, List
#=============standard library imports ========================
from threading import Thread, Lock, Event
import time
#from numpy import array, hsplit, array_split, asarray, transpose, hstack, rot90, swapaxes
#from matplotlib import cm
#=============local library imports ===========================
from src.image.image import Image
from cvwrapper import get_capture_device, query_frame, write_frame, \
    new_video_writer, grayspace, get_nframes, \
    set_frame_index, get_fps, set_video_pos, crop
from globals import globalv


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
    _prev_frame = None
    _stop_recording_event = None
    _last_get = None
    def open(self, user=None, identifier= -1, force=False):
        '''

        '''
        self._lock = Lock()
        self.width = 640
        self.height = 480
        if self.cap is None or force:

            if globalv.video_test:
                self.cap = 1
            else:
                #ideally an identifier is passed in 
                try:
                    self.cap = get_capture_device(identifier)
                except Exception, e:
                    print 'video.open', e
                    self.cap = None

        if not user in self.users:
            self.users.append(user)

    def shutdown(self):
        self.users = []
        del(self.cap)

    def get_nframes(self):
        if self.cap is not None:
            return get_nframes(self.cap)

    def get_fps(self):
        if self.cap is not None:
            return get_fps(self.cap)

    def set_video_pos(self, pos):
        if self.cap is not None:
            set_video_pos(self.cap, pos)

    def close(self, user=None, force=False):
        '''
  
        '''
        if force:
            del(self.cap)
            return

        if user in self.users:
            i = self.users.index(user)
            self.users.pop(i)
            if not self.users:
                del(self.cap)


    def set_frame_index(self, ind):
        cap = self.cap
        if cap:
            set_frame_index(cap, ind)

    def _get_frame(self, lock=True, **kw):
        cap = self.cap
        if cap is not None:
#            if lock:
            with self._lock:
#            with self._lock:
                if globalv.video_test:
                    if self.source_frame is None:
                        p = globalv.video_test_path
                        self.load(p)

                    f = self.source_frame.clone()
                    return f
#                f = self.current_frame.clone()
                else:
                    self.source_frame = query_frame(cap, frame=self.source_frame)
                    return self.source_frame

    def get_image_data(self, cmap=None, **kw):
        return self.get_frame(**kw).ndarray
##        print arr.shape
#        if cmap is not None:
#            _, _, colors = transpose(arr)
#            cmap = cm.get_cmap(cmap)
#            arr = cmap(colors) * 255
#            arr = asarray(arr, dtype='uint8')
#            arr = swapaxes(arr, 0, 1)
#
#        return arr


#        if not self._last_get:
#            self._frame = self.get_frame(**kw).ndarray
#            self._last_get = time.clock()
#        else:
##            print time.clock() - self._last_get
#            if time.clock() - self._last_get > 1 / 25.:
#                self._frame = self.get_frame(**kw).ndarray
#                self._last_get = time.clock()

#        return self._frame

#        return query_frame(self.cap).ndarray

    def start_recording(self, path, user=None):
        self._stop_recording_event = Event()
        def __record():
            fps = 1 / 8.
            if self.cap is None:
                self.open(user=user)

            if self.cap is not None:
                self._recording = True
                if self._frame is None:
                    self.get_frame()

#                size = map(int, self._frame.size())
                w = 200
                h = 200
                size = (w, h)
                writer = new_video_writer(path, 1 / fps,
                                          size
                                          )
                sleep = time.sleep
                ctime = time.time

                stop = self._stop_recording_event.isSet

                fsize = self._frame.size()
                x = (fsize[0] - size[0]) / 2
                y = (fsize[1] - size[1]) / 2

                while not stop():
                    st = ctime()
                    f = crop(self._frame.clone(), x, y, w, h)
                    write_frame(writer, grayspace(f))
                    dur = ctime() - st
                    sleep(max(0.001, fps - dur))

        t = Thread(target=__record)
        t.start()

    def stop_recording(self):
        '''
        '''
        if self._stop_recording_event is not None:
            self._stop_recording_event.set()
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

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
from traits.api import  Any, Bool, Float, List, Str
#=============standard library imports ========================
from threading import Thread, Lock, Event
import time
import os
import shutil
from numpy import asarray
#=============local library imports ===========================
from src.image.image import Image
# from src.image.pyopencv_image_helper import swapRB
from cv_wrapper import get_capture_device
from cv_wrapper import swap_rb as cv_swap_rb
# query_frame, write_frame, \
#    new_video_writer, grayspace, get_nframes, \
#    set_frame_index, get_fps, set_video_pos, crop, swapRB
#

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
    _save_ok_event = None
    _last_get = None

    output_path = Str
    output_mode = Str('MPEG')
    ffmpeg_path = Str

    def is_open(self):
        return self.cap is not None

    def open(self, user=None, identifier=0, force=False):
        '''

        '''
        self._lock = Lock()
        self.width = 640
        self.height = 480
        if self.cap is None or force:

            if globalv.video_test:
                self.cap = 1
            else:
                # ideally an identifier is passed in
                try:
                    self.cap = get_capture_device()
                    self.cap.open(identifier)
                except Exception, e:
                    print 'video.open', e
                    self.cap = None

        if not user in self.users:
            self.users.append(user)

#    def shutdown(self):
#        self.users = []
#        del(self.cap)
#
#    def get_nframes(self):
#        if self.cap is not None:
#            return get_nframes(self.cap)
#
#    def get_fps(self):
#        if self.cap is not None:
#            return get_fps(self.cap)
#
#    def set_video_pos(self, pos):
#        if self.cap is not None:
#            set_video_pos(self.cap, pos)

    def close(self, user=None, force=False):
        '''
  
        '''
        if force:
            self.cap.release()
            self.cap = None
            return

        if user in self.users:
            i = self.users.index(user)
            self.users.pop(i)
            if not self.users:
                self.cap.release()
                self.cap = None

#    def set_frame_index(self, ind):
#        cap = self.cap
#        if cap:
#            set_frame_index(cap, ind)

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
                    s, img = self.cap.read()
                    if s:
                        return img
#                    return self.cap.read()
#                    return query_frame(cap)
#                    pass
#                    self.source_frame = query_frame(cap, frame=self.source_frame)
#                    return self.source_frame

    def get_image_data(self, cmap=None, **kw):
        frame = self.get_frame(**kw)
        if frame is not None:
            return asarray(frame[:, :])

            return frame.ndarray
# #        print arr.shape
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
# #            print time.clock() - self._last_get
#            if time.clock() - self._last_get > 1 / 25.:
#                self._frame = self.get_frame(**kw).ndarray
#                self._last_get = time.clock()

#        return self._frame

#        return query_frame(self.cap).ndarray

    def start_recording(self, path, renderer=None):
        self._stop_recording_event = Event()
        self.output_path = path

        if self.output_mode == 'MPEG':
            func = self._ffmpeg_record
        else:
            func = self._cv_record

        fps = 8.
        if self.cap is None:
            self.open()

        if self.cap is not None:
            self._recording = True

            t = Thread(target=func, args=(path, self._stop_recording_event, fps, renderer))
            t.start()

    def _ready_to_save(self):
        if self._save_ok_event:
            while not self._save_ok_event.is_set():
                time.sleep(0.5)
            return True

    def stop_recording(self, wait=False):
        '''
        '''
        if self._stop_recording_event is not None:
            self._stop_recording_event.set()
        self._recording = False
        if wait:
            self._save_ok_event = Event()
            return self._ready_to_save()

    def record_frame(self, path, crop=None, **kw):
        '''
        '''
        src = self.get_frame(**kw)
        if src is not None:

#            if crop:
#                icrop(*((src,) + crop))
            self.save(path, src=src)

        return src.clone()

    def _ffmpeg_record(self, path, stop, fps, renderer=None):
        '''
            use ffmpeg to stitch a directory of jpegs into a video
            
        '''
        remove_images = True
        root = os.path.dirname(path)
        name = os.path.basename(path)
        name, _ext = os.path.splitext(name)

        image_dir = os.path.join(root, '{}-images'.format(name))
        cnt = 0
        while os.path.exists(image_dir):
            image_dir = os.path.join(root, '{}-images-{:03n}'.format(name, cnt))
            cnt += 1

        os.mkdir(image_dir)

        cnt = 0
#        new_frame = lambda : self.get_frame(swap_rb=False)
#        frame = self.get_frame(swap_rb=False)

        if renderer is None:
            frame = self.get_frame()
            save = lambda x: self.save(x, src=cv_swap_rb(frame))
        else:
            save = lambda x:renderer(x)

        while not stop.is_set():
            st = time.time()
            pn = os.path.join(image_dir, 'image_{:05n}.jpg'.format(cnt))
            save(pn)
            cnt += 1
            time.sleep(max(0.001, 1 / fps - (time.time() - st)))

        self._convert_to_video(image_dir, fps, name_filter='image_%05d.jpg', output=path)

        if remove_images:
            shutil.rmtree(image_dir)

        if self._save_ok_event:
            self._save_ok_event.set()

    def _convert_to_video(self, path, fps, name_filter='snapshot%03d.jpg', output=None):
        '''
            path: path to directory containing list of images 
            
            commandline
            $ ffmpeg -r 25 -codec x264 -i /snapshot%03d.jpg -o output.avi
            
            
        '''
        import subprocess
        if output is None:
            output = os.path.join(path, '{}.avi'.format(path))

        if os.path.exists(output):
            return

        frame_rate = '{}'.format(fps)
        codec = '{}'.format('x264')  # H.264
        path = '{}'.format(os.path.join(path, name_filter))

        ffmpeg = '/usr/local/bin/ffmpeg'
        if self.ffmpeg_path:
            ffmpeg = self.ffmpeg_path

        subprocess.call([ffmpeg, '-r', frame_rate, '-i', path, output, '-codec', codec])

    def _cv_record(self, path, stop, fps, renderer=None):
        '''
            use OpenCV VideoWriter to save video file
            !!on mac seems only raw video can saved. playable avi file but
            bad internally. No format
        '''
#        fps = 1 / 8.
#        if self.cap is None:
#            self.open()
#
#        if self.cap is not None:
#            self._recording = True
# #                if self._frame is None:
        frame = self.get_frame()

#                size = map(int, self._frame.size())
        w = 300
        h = 300
        size = (w, h)

        '''
            @todo: change video writing scheme
            
            create a new directory
            save jpegs into directory
            use ffmpeg to stitch into a video
        '''
        writer = new_video_writer(path, fps,
                                  size
                                  )
        sleep = time.sleep
        ctime = time.time

        fsize = frame.size()
        x = (fsize[0] - size[0]) / 2
        y = (fsize[1] - size[1]) / 2

        while not stop.is_set():
            st = ctime()
            f = crop(frame.clone(), x, y, w, h)
#                    write_frame(writer, grayspace(f))
            write_frame(writer, f)
            dur = ctime() - st
            sleep(max(0.001, 1 / fps - dur))
#=================== EOF =================================================

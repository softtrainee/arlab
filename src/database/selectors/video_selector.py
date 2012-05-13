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

#============= enthought library imports =======================
from traits.api import String, Float, Instance, Button, Int, Bool, Property
from traitsui.api import View, Item, VGroup, HGroup, spring, RangeEditor
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector, DBResult
from src.database.orms.video_orm import VideoTable
from src.image.image_editor import ImageEditor
from src.image.image import Image
from src.image.video import Video
from pyface.timer.do_later import do_after
from threading import Thread, Event
import time

class VideoResult(DBResult):
    title_str = 'VideoRecord'
    video_image = Instance(Image, ())
    video = Instance(Video, ())

    play = Button
    stop = Button
    pause = Button
    _current_frame_id = 0
    _playing = Bool(False)
    _stepping = Bool(False)

#    frame = Property(depends_on='frame')
#    frame = Int(1)
    frame = Int(1)

    nframes = Int(100)
    step_len = Int(3)

    bstep = Button('<<<')
    fstep = Button('>>>')

    play_flag = None
    step_flag = None

#    _paused = False

#    def _get_frame(self):
#        return self.frame
#
#    def _set_frame(self, v):
##        print v / float(self.nframes)
#        def _sf():
#            self.video.set_video_pos(v / float(self.nframes))
#            f = self.video.get_frame()
#            do_after(1, self.video_image.load, f)
#        t = Thread(target=_sf)
#        t.start()
##        self.video_image.load()

    def _fstep_fired(self):
        self._flag_factory()
        self.step_flag.set()
        self._play_video()

    def _bstep_fired(self):

        self._flag_factory()
        self.step_flag.set()
        self._play_video(rewind=True)

    def _stop_fired(self):
        self._playing = False

        self.play_flag.set()
        self.step_flag.set()

        time.sleep(0.1)
        self._current_frame_id = 0
        self.frame = 1
        self._load_hook(self._db_result)

    def _pause_fired(self):
        self.play_flag.set()
        self._playing = False
        self._stepping = True
#        self._paused = True

    def _play_fired(self):
        if not self._playing:
#            if not self._paused:
#                self.video.set_video_pos(0)

#            self._paused = False
            self._stepping = False
            self._playing = True
            self._flag_factory()
            self._play_video()

    def _flag_factory(self):
        self.play_flag = Event()
        self.step_flag = Event()

    def _play_video(self, rewind=False):
        func = self._play

        t = Thread(name='video', target=func, args=(self.play_flag,
                                                          self.step_flag, rewind))
        t.start()

    def _play(self, play_flag, step_flag, rewind):
        vid = self.video
        fps = vid.get_fps()
        try:
#            self.nframes = nframes = int(self.video.get_nframes())
            step = 1
            end = self.nframes
            if rewind:
                step = -1
                end = 0

            for i, fi in enumerate(range(self._current_frame_id, end, step)):
                self._current_frame_id = fi
                if play_flag.isSet():
                    break

                if rewind:
                    vid.set_frame_index(fi)

                f = vid.get_frame()
                do_after(1, self.video_image.load, f)
                time.sleep(1 / fps)
                if step_flag.isSet():
                    if i >= self.step_len:
                        break
                    self.frame += step
                else:
                    self.frame = fi + 1
                self._current_frame_id = self.frame
            else:
                self._playing = False
                play_flag.clear()
                self._current_frame_id = 0
                self.frame = 1

        except Exception, e:
            print e

    def _load_hook(self, dbr):

        src = os.path.join(self.directory, self.filename)
        vid = self.video
        vid.open(identifier=src, force=True)
        self.video_image.load(vid.get_frame())
        self.nframes = int(self.video.get_nframes())

    def _get_additional_tabs(self):
        controls = VGroup(HGroup(
                          Item('play', show_label=False),
                          Item('stop', show_label=False, enabled_when='_playing'),
                          Item('pause', show_label=False, enabled_when='_playing'),
                          Item('bstep',
                               show_label=False,
                               enabled_when='_stepping or not _playing and frame>=1+step_len'),
                          Item('fstep',
                               show_label=False, enabled_when='_stepping or not _playing'),
                          Item('step_len', show_label=False),
                          ),
                    Item('frame',
                         enabled_when='0',
                         editor=RangeEditor(low=1, high_name='nframes',
                                                     mode='slider'
                                                     ))
                    )
        vtab = VGroup(controls,
                     Item('video_image', style='custom',
                    show_label=False,
                    width=640, height=480,
                    editor=ImageEditor()))
        return [vtab]

class VideoSelector(DBSelector):
    parameter = String('VideoTable.rundate')
    date_str = 'rundate'
    query_table = 'VideoTable'
    result_klass = VideoResult

    def _get__parameters(self):

        b = VideoTable

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = f(b)
        return list(params)

    def _get_selector_records(self, *args, **kw):
        return self._db.get_video_records(*args, **kw)



#============= EOF =============================================

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
from traits.api import String, Float, Instance, Button, Int
from traitsui.api import View, Item, VGroup, HGroup, spring, RangeEditor
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector, DBResult
from src.database.orms.video_orm import VideoTable
from src.graph.graph import Graph
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.image.image_editor import ImageEditor
from src.image.image import Image
from src.image.video import Video
from pyface.timer.do_later import do_later
from threading import Thread
import time

class VideoResult(DBResult):
    title_str = 'VideoRecord'
    video_image = Instance(Image, ())
    video = Instance(Video, ())

    play = Button
    stop = Button
    pause = Button
    _playing = False
    _current_frame_id = 0
    _pause = False

    frame = Int
    nframes = Int(100)

    step = Button
    _step = False

    def _step_fired(self):
        self._step = True
        self._playing = True
        self._pause = False
        self._play_video()

    def _stop_fired(self):

        self._playing = False
        self._current_frame_id = 0
        self.frame = 0
        self._step = False
        self._load_hook(self._db_result)

    def _pause_fired(self):
        self._pause = True
        self._playing = False

    def _play_fired(self):
        if not self._playing:
            self._playing = True
            self._pause = False
            self._step = False

            self._play_video()

    def _play_video(self):
        t = Thread(name='video', target=self._play)
        t.start()

    def _play(self):
        vid = self.video
        try:
            self.nframes = nframes = int(self.video.get_nframes())
            for fi in range(self._current_frame_id, nframes, 1):
                self._current_frame_id = fi
                if not self._playing:
                    break
                if self._pause:
                    break

                f = vid.get_frame()
                do_later(self.video_image.load, f)
                time.sleep(1 / 8.)
                if self._step:
                    self.frame += 1
                    self._step = False
                    self._current_frame_id = self.frame

                    break
                else:
                    self.frame = fi + 1

        except Exception, e:
            print e
        finally:
            self._playing = False


    def _load_hook(self, dbr):

        src = os.path.join(self.directory, self.filename)
        vid = self.video
        vid.open(identifier=src, force=True)
        self.video_image.load(vid.get_frame())

    def _get_additional_tabs(self):
        controls = VGroup(HGroup(
                          Item('play', show_label=False),
                          Item('stop', show_label=False),
                          Item('pause', show_label=False),
                          Item('step', show_label=False)
                          ),
                    Item('frame',
                         enabled_when='0',
                         editor=RangeEditor(low=0, high_name='nframes',
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

    def _get_selector_records(self, **kw):
        return self._db.get_video_records(**kw)



#============= EOF =============================================

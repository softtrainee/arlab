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
#============= standard library imports ========================
#============= local library imports  ==========================
from src.canvas.canvas2D.base_data_canvas import BaseDataCanvas
from src.canvas.canvas2D.video_underlay import VideoUnderlay


class VideoCanvas(BaseDataCanvas):
    video = None
    camera = None
    padding = 0

    def __init__(self, *args, **kw):
        '''

        '''
        super(VideoCanvas, self).__init__(*args, **kw)

        self.video_underlay = VideoUnderlay(component=self, video=self.video)

        self.underlays.insert(0, self.video_underlay)

        for key, d in [('x_grid', dict(line_color=(1, 1, 0),
                                     line_width=1,
                                     line_style='dash',
                                     visible=self.show_grids)
                                     ),
                       ('y_grid', dict(line_color=(1, 1, 0),
                                      line_width=1,
                                      line_style='dash',
                                      visible=self.show_grids))]:
            o = getattr(self, key)
            o.trait_set(**d)


        if self.video:
            self.on_trait_change(self.video.update_bounds, 'bounds')


#============= EOF ====================================

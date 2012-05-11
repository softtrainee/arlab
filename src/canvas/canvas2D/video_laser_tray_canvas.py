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
from traits.api import on_trait_change
#============= standard library imports ========================
#============= local library imports  ==========================
from src.canvas.canvas2D.video_canvas import VideoCanvas
from src.canvas.canvas2D.markup.markup_items import Rectangle
from laser_tray_canvas import LaserTrayCanvas


class VideoLaserTrayCanvas(LaserTrayCanvas, VideoCanvas):
    '''
    '''

    @on_trait_change('parent:parent:zoom')
    def zoom_update(self, obj, name, old, new):
        if new is not None:
            self.camera.set_limits_by_zoom(new)

    @on_trait_change('calibrate')
    def _update_(self, new):
        self.pause = new

    def set_stage_position(self, x, y):
        '''
        '''
        super(VideoLaserTrayCanvas, self).set_stage_position(x, y)
        self.adjust_limits('x', x)
        self.adjust_limits('y', y)
        if self.use_camera:
            self.camera.current_position = (x, y)

    def add_markup_rect(self, x, y, w, h):
        self.markupcontainer['croprect'] = Rectangle(x=x, y=y, width=w, height=h)

#============= EOF ====================================

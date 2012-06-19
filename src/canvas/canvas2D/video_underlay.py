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
from traits.api import Instance
from chaco.api import AbstractOverlay
#============= standard library imports ========================

#============= local library imports  ==========================
from src.image.video import Video
from src.helpers.memo import memoized


class VideoUnderlay(AbstractOverlay):
    '''
    '''
    video = Instance(Video)
#    swap_rb = True
#    mirror = False
#    flip = False

#    @memoized
    def overlay(self, component, gc, *args, **kw):
        '''

        '''
        try:
            gc.save_state()
            img = self.video.get_frame(
#                                       flip=not self.flip,
                                         #swap_rb=self.swap_rb,
#                                         mirror=self.mirror,
                                         size=map(int, (component.width, component.height)))
            gc.clip_to_rect(component.x, component.y,
                            component.width, component.height)
            gc.draw_image(img.ndarray)

        except (AttributeError, UnboundLocalError), e:
            print e
        finally:
            gc.restore_state()




#============= EOF ====================================

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
from src.image.image import Image

class ImageUnderlay(AbstractOverlay):
    '''
    '''
    image = Instance(Image)
    swap_rb = True

    def overlay(self, component, gc, *args, **kw):
        '''

        '''
        gc.save_state()
        try:

            data = self.image.get_array()
            #data should be a numpy ndarray

            gc.draw_image(data, rect=(0, 0, component.width, component.height))
#            dc = component._window.dc

           # dc = wx.PaintDC()
            #print dc
#            bitmap = self.image.get_bitmap(flip=True,
#                                         swap_rb=self.swap_rb
#                                         )

#            if bitmap:
#                x = component.x
#                y = component.y
#                gc.draw_image(bitmap)
#                dc.DrawBitmap(bitmap, x, y, False)

        except (AttributeError, UnboundLocalError), e:
            print e
        finally:
            gc.restore_state()




#============= EOF ====================================

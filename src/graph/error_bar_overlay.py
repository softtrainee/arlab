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
from chaco.api import AbstractOverlay
import wx

#============= standard library imports ========================

#============= local library imports  ==========================


class ErrorBarOverlay(AbstractOverlay):
    def overlay(self, component, gc, view_bounds=None, mode='normal'):
        '''
            
        '''
        gc.save_state()
        gc.clip_to_rect(component.x, component.y, component.width, component.height)

        x = component.index.get_data()
        y = component.value.get_data()
        xer = component.xerror.get_data()

        args1 = component.map_screen(zip(x - xer, y))
        args2 = component.map_screen(zip(x + xer, y))

        color = component.color
        if isinstance(color, str):
            color = wx.Color()
            color.SetFromName(component.color)

        gc.set_stroke_color(color)
        for (x1, y1), (x2, y2) in zip(args1, args2):
            gc.move_to(x1, y1)
            gc.line_to(x2, y2)
            gc.stroke_path()

        gc.restore_state()
        #============= EOF =====================================

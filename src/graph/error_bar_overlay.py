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
from traits.api import Int, Enum
from chaco.api import AbstractOverlay
#============= standard library imports ========================
import wx

#============= local library imports  ==========================


class ErrorBarOverlay(AbstractOverlay):
    orientation = Enum('x', 'y')

    draw_layer = 'underlay'
    nsigma = 1

    def overlay(self, comp, gc, view_bounds=None, mode='normal'):
        '''
            
        '''
        component = self.component
        with gc:
            gc.clip_to_rect(comp.x, comp.y, comp.width, comp.height)
            gc.set_line_width(2)

            x = component.index.get_data()
            y = component.value.get_data()

            if self.orientation == 'x':
                xer = component.xerror.get_data()

                xer_sigma = xer * self.nsigma

                args1 = component.map_screen(zip(x - xer_sigma, y))
                args2 = component.map_screen(zip(x + xer_sigma, y))
            else:
                yer = component.yerror.get_data()

                yer_sigma = yer * self.nsigma
                args1 = component.map_screen(zip(x, y - yer_sigma))
                args2 = component.map_screen(zip(x, y + yer_sigma))

            sel = component.index.metadata['selections']

            color = component.color
            if isinstance(color, str):
                color = wx.Color()
                color.SetFromName(component.color)
#                r, g, b = color.Red() / 255., color.Green() / 255., color.Blue() / 255.
#                print component.color, r, g, b
#                rgb = map(lambda x: x / 255. , color.GetRGB())
#                color.Set(r, g, b)
            sels = (a for i, a in enumerate(zip(args1, args2)) if i in sel)
            nonsels = (a for i, a in enumerate(zip(args1, args2)) if i not in sel)

            gc.set_stroke_color((1, 0, 0.5))
            gc.set_fill_color((1, 0, 0.5))
            for ((x1, y1), (x2, y2)) in sels:
                gc.move_to(x1, y1)
                gc.line_to(x2, y2)
            gc.draw_path()

            rgb = color.red / 100., color.green / 100., color.blue / 100.
            gc.set_stroke_color(rgb)
            gc.set_fill_color(rgb)
            for ((x1, y1), (x2, y2)) in nonsels:
                gc.move_to(x1, y1)
                gc.line_to(x2, y2)
            gc.draw_path()


#            for i, ((x1, y1), (x2, y2)) in enumerate(zip(args1, args2)):
#                if i in sel:
#                    gc.set_stroke_color((255, 0, 122))
#                else:
#                    print (color.red, color.green, color.blue)
#                    gc.set_stroke_color((255, color.green, color.blue))
# #                    gc.set_stroke_color((color.red / 255., color.green / 255., color.blue / 255.))
# #                    gc.set_stroke_color((255, 0, 0))
#                gc.move_to(x1, y1)
#                gc.line_to(x2, y2)
#                gc.stroke_path()

#============= EOF =====================================

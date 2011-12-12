'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================
from traits.api import HasTraits
from traitsui.api import View, Item
from chaco.api import AbstractOverlay

#============= standard library imports ========================

#============= local library imports  ==========================
class ErrorBarOverlay(AbstractOverlay):
    def overlay(self, component, gc, view_bounds=None, mode='normal'):
        '''
            
        '''
        gc.clip_to_rect(component.x, component.y, component.width, component.height)

        x = component.index.get_data()
        y = component.value.get_data()
        xer = component.xerror.get_data()
#        yer = component.yerror.get_data()
#        nx, ny = component.map_screen([(x, y)])[0][0]
        nx1, nye = component.map_screen([(x - xer, y)])[0][0]
        nx2, nye = component.map_screen([(x + xer, y)])[0][0]
#        print nx, nxe
        gc.move_to(nx1, nye - 10)
        gc.line_to(nx1, nye + 10)
        gc.stroke_path()
        gc.move_to(nx2, nye - 10)
        gc.line_to(nx2, nye + 10)
        gc.stroke_path()
        
        gc.save_state()     
        gc.move_to(nx1, nye)
        gc.line_to(nx2, nye)
        gc.stroke_path()
        gc.restore_state()
        #============= EOF =====================================

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
#=============enthought library imports========================
#from traits.api import Any
#=============standard library imports ========================

#=============local library imports  ==========================
from base_data_canvas import BaseDataCanvas
class InteractionCanvas(BaseDataCanvas):
    '''
    '''
    def __init__(self, *args, **kw):
        '''
            
        '''
        super(InteractionCanvas, self).__init__(*args, **kw)
        self.component_groups = []
        self.cur_pos = [0, 0]


    def normal_mouse_move(self, event):
        '''
        '''
        self.cur_pos = [event.x, event.y]

        for compdict in self.component_groups:

            if self._over_components(event, compdict):
                self.event_state = 'select'
                event.window.set_pointer(self.select_pointer)

                break
            else:
                self.draw_info = False
                self.event_state = 'normal'
                event.window.set_pointer(self.normal_pointer)
        self.request_redraw()
        event.handled = True

    def select_mouse_move(self, event):
        '''
        '''
        self.normal_mouse_move(event)

    def select_left_down(self, event):
        '''
        '''
        event.handled = True
        for compdict in self.component_groups:
            c = self._over_components(event, compdict)
            if not c == None:
                return c

    def _over_components(self, event, compdict):
        '''
        '''
        x = event.x
        y = event.y
        for ck in compdict.explanable_items:
            c = compdict.explanable_items[ck]

            dx, dy, = self.map_screen([(c.x, c.y)])[0]
            oo, wh = self.map_screen([(0, 0), (c.width, c.height)])

            w = abs(oo[0] - wh[0])
            h = abs(oo[1] - wh[1])

            dx += w / 2.0
            dy += h / 2.0

            if abs(dx - x) < w and abs(dy - y) < h:

                return c

        return

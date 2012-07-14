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
from chaco.tools.api import PanTool
from enable.base_tool import BaseTool
#============= standard library imports ========================

#============= local library imports  ==========================


class MyPanTool(PanTool):
    '''
    '''
    active = False

    def normal_key_pressed(self, event):
        '''

        '''
#        print event.character
        #print self.component
        if event.character == 'p':
            self.active = not self.active

            #disable the other tools
            bc = self.component.tools[0]
            for t in bc.tools:
                if t is not self:
                    t.active = not self.active
            if self.active:
                event.window.set_pointer('hand')
            else:
                event.window.set_pointer('arrow')

        elif event.character == 'Esc':
            c = self.component
            for r in ['index', 'value']:
                ra = getattr(c, '%s_range' % r)
                for s in ['low', 'high']:
                    ra.trait_set(**{'%s_setting' % s: 'auto'})

        event.handled = True

    def normal_left_down(self, event):
        '''
        '''

        if self.active:
            PanTool.normal_left_down(self, event)
#            event.handled = True

#    def normal_left_up(self, event):
#        '''
#        '''
#        if self.active:
#            PanTool.normal_left_up(self, event)
##            event.handled = False
#        print event.handled, 'panup'

#    def panning_left_up(self, event):
#        print 'panup', event
#        if self._auto_constrain:
#            self.constrain = False
#            self.constrain_direction = None
#        self.event_state = "normal"
#        event.window.set_pointer("arrow")
#        if event.window.mouse_owner == self:
#            event.window.set_mouse_owner(None)

#        PanTool.panning_left_up(self, event)
#        event.handled = False
#        self.normal_left_up(event)
#============= EOF ====================================

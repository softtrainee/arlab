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
#============= enthought library imports =======================
from chaco.tools.api import PanTool
#============= standard library imports ========================

#============= local library imports  ==========================


class MyPanTool(PanTool):
    '''
    '''
    active = False

    def normal_key_pressed(self, event):
        '''

        '''
        #print self.component
        if event.character == 'p':
            self.active = not self.active

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
#============= EOF ====================================

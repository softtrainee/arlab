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
'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import Any, Int
from chaco.tools.api import ScatterInspector

#=============standard library imports ========================

#=============local library imports  ==========================
class ScatterTool(ScatterInspector):
    '''
        G{classtree}
    '''
    parent = Any
    plotid = Int(0)
    def normal_mouse_move(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        #self.parent.selected_plotid = self.plotid
        #super(ScatterTool, self).normal_mouse_move(event)
        ScatterInspector.normal_mouse_move(self, event)
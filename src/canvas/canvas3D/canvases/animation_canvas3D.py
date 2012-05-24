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

#=============standard library imports ========================
#from OpenGL.GL import *
#from OpenGL.GLU import *
#from wx import Timer, EVT_TIMER
#=============local library imports  ==========================

from canvas3D import Canvas3D


class AnimationCanvas3D(Canvas3D):
    '''
    '''

    def __init__(self, panel):
        '''
        '''
        super(AnimationCanvas3D, self).__init__(panel)
        #self.Bind(EVT_TIMER, self.OnTimer)
        #self.t1 = Timer(self)
        #t = 1000.0 / 24
        #self.t1.Start(t)

    def OnTimer(self, event):
        '''
        '''
        self.scene_graph.increment_animation_counter()
#        if self.scene_graph.animate_cnt>100:
#            self.scene_graph.animate_cnt=0
#        
        self.Refresh()

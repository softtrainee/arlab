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
from wx import EVT_PAINT, EVT_SIZE
import wx.glcanvas
from OpenGL.GL import glClear, glClearDepth, glClearColor, glMatrixMode, glLoadIdentity, glOrtho, \
    glBlendFunc, glEnable, glLineWidth, glLightfv, glViewport, \
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, GL_PROJECTION, \
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_BLEND, GL_LINE_SMOOTH, GL_DEPTH_TEST, \
    GL_LIGHTING, GL_LIGHT0, GL_LIGHT1, GL_POSITION, GL_AMBIENT, GL_SPECULAR, GL_DIFFUSE, GL_COLOR_MATERIAL, GL_AMBIENT_AND_DIFFUSE
#=============local library imports  ==========================
from src.canvas.canvas3D.scene_graph import SceneGraph

class Canvas3D(wx.glcanvas.GLCanvas):
    '''
    '''
    scene_graph = None
    #draw = True
    def __init__(self, panel):
        '''
        '''
        super(Canvas3D, self).__init__(panel)
        EVT_PAINT(self, self.OnPaint)
        EVT_SIZE(self, self.OnSize)
        self.scene_graph = self.scene_graph_factory()
        self.init = False

#    def OnSize(self, event):
#        w = event.GetSize().GetWidth()
#        h = event.GetSize().GetHeight()
#        #glViewport(0,0,w/10,h/10)
        #
        #self.Update()
        #self.Refresh()
    def draw(self, offscreen=False):
        '''
        '''
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if self.draw:
            self.scene_graph.render(offscreen)

        if not offscreen:
            self.SwapBuffers()
        return

    def OnPaint(self, event):
        '''
        '''
        if not self.init:
            self._init_GL()
            self.init = True

        self.draw()
        return

    def OnSize(self, event):
        '''
        '''
        pass

    def set_background_color(self, color):
        '''
        '''
        if len(color) == 3:
            color += (1,)

        glClearColor(*color)

    def _init_GL(self):
        '''
        '''
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glEnable(GL_LINE_SMOOTH)
        glLineWidth(2.0)
        glEnable(GL_DEPTH_TEST)

        #glEnable(GL_TEXTURE_2D)

        #set the lighting
        self._set_lighting()


        # set the background color 
        #glClearColor(0.15, 0.15, 0.15, 1)
        glClearDepth(1.0)

        # set the camera
        glMatrixMode(GL_PROJECTION)
        #glPushMatrix()
        glLoadIdentity()
        self._set_view_volume()

        glMatrixMode(GL_MODELVIEW)
        return

    def _set_lighting(self):
        '''
        '''
        glEnable(GL_LIGHTING)
        lights = [(GL_LIGHT0, [(GL_POSITION, [1, 1, 0, 0]),
                            (GL_AMBIENT, [0.1, 0.1, 0.1, 1]),
                            (GL_SPECULAR, [1, 1, 1, 1]),
                            (GL_DIFFUSE, [1, 1, 1, 1])
                            ]),
#                  (GL_LIGHT1, [(GL_POSITION, [0, 0, 1, 0]),
#                            (GL_AMBIENT, [0.1, 0.1, 0.1, 1]),
#                            (GL_SPECULAR, [1, 1, 1, 1]),
#                            (GL_DIFFUSE, [1, 1, 1, 1])
#                            ]
#                   ),
                ]
        for l, params in lights:
            glEnable(l)
            for pa, args in params:
                glLightfv(l, pa, args)
#            
                #glLightfv(GL_LIGHT0, GL_POSITION, [10, 0, 0, 0])
#        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1])
#        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
#        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
#        
#        glLightfv(GL_LIGHT0,GL_SPOT_CUTOFF,30)
#        
#        glLightfv(GL_LIGHT0,GL_SPOT_DIRECTION,[-1,0,0,0])
#        



        glEnable(GL_COLOR_MATERIAL, GL_AMBIENT_AND_DIFFUSE)
    def _set_view_volume(self):
        '''
        '''

        glOrtho(-20, 20, -20, 20, 50, -50)

        size = self.GetSize()
        glViewport(0, 0, size.width, size.height)

    def scene_graph_factory(self):
        '''
        '''
        return SceneGraph(self)

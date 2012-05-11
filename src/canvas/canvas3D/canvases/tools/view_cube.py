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
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup
from src.canvas.canvas3D.elements.object3D import Transform
#from OpenGL.GL import glBegin, (, glVertex3f, GL_QUADS, glEnd, glGenTextures, \
#    glBindTexture, GL_TEXTURE_2D, glPixelStorei, GL_UNPACK_ALIGNMENT, GL_RGBA, GL_UNSIGNED_BYTE, \
#    glTexImage2D
from OpenGL.GL import glBegin, glEnd, glColor3f, glVertex3f, GL_QUADS

#============= standard library imports ========================

#============= local library imports  ==========================
#from PIL import Image
#import Image
class ViewCube(Transform):
    offscreen = False
#    textures = None
#    def __init__(self, *args, **kw):
#        Transform.__init__(self, *args, **kw)
#        self.load_textures()

    def render(self):
#        if self.offscreen:
        self.id = 1
        Transform.render(self)
#        self._set_material((255, 0, 255))

#        self._cube_(radius = 4)
#        glPushAttrib(GL_CURRENT_BIT)
#        self.cube()
        self.cube()
        #print 'id', self.id
#        if self.offscreen:
#            self.cube()
#        else:
#            self._cube_()
        #glPopAttrib(GL_CURRENT_BIT)
    def set_face(self, face_color):
        #print face_color
        pass

    def cube(self):
        glBegin(GL_QUADS)            # Start Drawing The Cube
        glColor3f(0.0, 1.0, 0.0)            # Set The Color To Blue
        glVertex3f(1.0, 1.0, -1.0)        # Top Right Of The Quad (Top)
        glVertex3f(-1.0, 1.0, -1.0)        # Top Left Of The Quad (Top)
        glVertex3f(-1.0, 1.0, 1.0)        # Bottom Left Of The Quad (Top)
        glVertex3f(1.0, 1.0, 1.0)        # Bottom Right Of The Quad (Top)

        glColor3f(1.0, 0.5, 0.0)            # Set The Color To Orange
        glVertex3f(1.0, -1.0, 1.0)        # Top Right Of The Quad (Bottom)
        glVertex3f(-1.0, -1.0, 1.0)        # Top Left Of The Quad (Bottom)
        glVertex3f(-1.0, -1.0, -1.0)        # Bottom Left Of The Quad (Bottom)
        glVertex3f(1.0, -1.0, -1.0)        # Bottom Right Of The Quad (Bottom)

        glColor3f(1.0, 0.0, 0.0)            # Set The Color To Red
        glVertex3f(1.0, 1.0, 1.0)        # Top Right Of The Quad (Front)
        glVertex3f(-1.0, 1.0, 1.0)        # Top Left Of The Quad (Front)
        glVertex3f(-1.0, -1.0, 1.0)        # Bottom Left Of The Quad (Front)
        glVertex3f(1.0, -1.0, 1.0)        # Bottom Right Of The Quad (Front)

        glColor3f(1.0, 1.0, 0.0)            # Set The Color To Yellow
        glVertex3f(1.0, -1.0, -1.0)        # Bottom Left Of The Quad (Back)
        glVertex3f(-1.0, -1.0, -1.0)        # Bottom Right Of The Quad (Back)
        glVertex3f(-1.0, 1.0, -1.0)        # Top Right Of The Quad (Back)
        glVertex3f(1.0, 1.0, -1.0)        # Top Left Of The Quad (Back)

        glColor3f(0.0, 0.0, 1.0)            # Set The Color To Blue
        glVertex3f(-1.0, 1.0, 1.0)        # Top Right Of The Quad (Left)
        glVertex3f(-1.0, 1.0, -1.0)        # Top Left Of The Quad (Left)
        glVertex3f(-1.0, -1.0, -1.0)        # Bottom Left Of The Quad (Left)
        glVertex3f(-1.0, -1.0, 1.0)        # Bottom Right Of The Quad (Left)

        glColor3f(1.0, 0.0, 1.0)            # Set The Color To Violet
        glVertex3f(1.0, 1.0, -1.0)        # Top Right Of The Quad (Right)
        glVertex3f(1.0, 1.0, 1.0)        # Top Left Of The Quad (Right)
        glVertex3f(1.0, -1.0, 1.0)        # Bottom Left Of The Quad (Right)
        glVertex3f(1.0, -1.0, -1.0)        # Bottom Right Of The Quad (Right)
        glEnd()                # Done Drawing The Quad


#============= EOF =============================================
#    def load_textures(self):
#        '''
#        '''
#        tnames = ['red', 'green', 'blue', 'red', 'green', 'blue']
#        self.textures = texs = glGenTextures(len(tnames))
#        i = 0
#        for tname, tex in zip(tnames, texs):
#            img = Image.Image()
##            p = ghome + '/images/font/%s.bmp' % tlist[i]
#            p = '/Users/Ross/Desktop/test/{}.bmp'.format(tname)
#            timg = Image.open(p)
#            img.sizeX = timg.size[0]
#            img.sizeY = timg.size[1]
##            img.data = timg.tostring()
#            img.data = timg.tostring('raw', 'RGBX', 0, -1)
#            glBindTexture(GL_TEXTURE_2D, tex)
#            #i += 1
##            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
##            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
#            glTexImage2D(GL_TEXTURE_2D, 0, 4, img.sizeX, img.sizeY, 0,
#                         GL_RGBA, GL_UNSIGNED_BYTE, img.data)
#
#        #return texs
#    def tcube(self):
#        def face(t, pts):
##            glBindTexture(GL_TEXTURE_2D, self.textures[t])
#            glBindTexture(GL_TEXTURE_2D, t + 1)
#
#            glBegin(GL_QUADS)
#            for a, b in pts:
#                glTexCoord2f(*a)
#                glVertex3f(*b)
#            glEnd()
#
#        glDisable(GL_DEPTH_TEST)
#        glEnable(GL_TEXTURE_2D)
#        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
#        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
#        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
#        glDisable(GL_LIGHTING)
#        r = 2
#        faces = [
##                (0, [((0.0, 0.0), (-1.0, -1.0, 1.0)), #back
##                ((1.0, 0.0), (1.0, -1.0, 1.0)),
##                ((1.0, 1.0), (1.0, 1.0, 1.0)),
##                ((0.0, 1.0), (-1.0, 1.0, 1.0))]),
#                (0, [((0, 0), (r, r, -r)),
#                     ((1, 0), (-r, r, -r)),
#                     ((1, 1), (-r, r, r)),
#                     ((0, 1), (r, r, r)),
#                     ]),
#                (2, [((1, 0), (r, -r, r)),
#                     ((1, 1), (-r, -r, r)),
#                     ((0, 1), (-r, -r, -r)),
#                     ((0, 0), (r, -r, -r)),
#                     ]),
##                (3, [((0, 1), (r, r, r)),
##                     ((0, 0), (-r, r, r)),
##                     ((1, 0), (-r, -r, r)),
##                     ((1, 1), (r, -r, r)),
##                     ]),
#                (2, [((1, 0), (r, -r, r)),
#                     ((1, 1), (-r, -r, r)),
#                     ((0, 1), (-r, -r, -r)),
#                     ((0, 0), (r, -r, -r)),
#                     ]),


#                (2, [((1.0, 0.0), (-1.0, -1.0, -1.0)), #front
#                ((1.0, 1.0), (-1.0, 1.0, -1.0)),
#                ((0.0, 1.0), (1.0, 1.0, -1.0)),
#                ((0.0, 0.0), (1.0, -1.0, -1.0))]),
##
#                (1, [((0.0, 1.0), (-1.0, 1.0, -1.0)), #top
#                ((0.0, 0.0), (-1.0, 1.0, 1.0)),
#                ((1.0, 0.0), (1.0, 1.0, 1.0)),
#                ((1.0, 1.0), (1.0, 1.0, -1.0))]),
#
#                (3, [((1.0, 1.0), (-1.0, -1.0, -1.0)),
#                ((0.0, 1.0), (1.0, -1.0, -1.0)),
#                ((0.0, 0.0), (1.0, -1.0, 1.0)),
#                ((1.0, 0.0), (-1.0, -1.0, 1.0))]),

#                ((1.0, 0.0), (1.0, -1.0, -1.0)),
#                ((1.0, 1.0), (1.0, 1.0, -1.0)),
#                ((0.0, 1.0), (1.0, 1.0, 1.0)),
#                ((0.0, 0.0), (1.0, -1.0, 1.0)),
#
#                ((0.0, 0.0), (-1.0, -1.0, -1.0)),
#                ((1.0, 0.0), (-1.0, -1.0, 1.0)),
#                ((1.0, 1.0), (-1.0, 1.0, 1.0)),
#                ((0.0, 1.0), (-1.0, 1.0, -1.0))
#
#                ]
#
#        for f in faces:
#            face(*f)
#        glEnable(GL_LIGHTING)
#        glDisable(GL_TEXTURE_2D)
#        glEnable(GL_DEPTH_TEST)




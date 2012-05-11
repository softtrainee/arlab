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



#'''
#@author: Jake Ross
#@copyright: 2009
#@license: Educational Community License 1.0
#'''
##=============enthought library imports=======================
#
##=============standard library imports ========================
#from OpenGL.GL import *
#import os
##=============local library imports  ==========================
##from globals import ghome
#
#from filetools import *
#import Image
#def load_textures(tlist):
#    '''
#    '''
#    texs = glGenTextures(len(tlist))
#    i = 0
#    for tex in texs:
#        img = Imaged()
#        p = ghome + '/images/font/%s.bmp' % tlist[i]
#        timg = Image.open(p)
#        img.sizeX = timg.size[0]
#        img.sizeY = timg.size[1]
#        img.data = timg.tostring('raw', 'RGBX', 0, -1)
#        glBindTexture(GL_TEXTURE_2D, tex)
#        i += 1
#        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
#        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
#        glTexImage2D(GL_TEXTURE_2D, 0, 4, img.sizeX, img.sizeY, 0,
#                     GL_RGBA, GL_UNSIGNED_BYTE, img.data)
#    return texs
#def load_texture():
#    '''
#    '''
#    img = Imaged()
#    p = ghome + '/images/env1.bmp'
#    #p=ghome+'/images/base1.jpg'
#    poo = Image.open(p)
#    img.sizeX = poo.size[0]
#    img.sizeY = poo.size[1]
#    img.data = poo.tostring('raw', 'RGBX', 0, -1)
#
#    tex = glGenTextures(1)
#
#    glBindTexture(GL_TEXTURE_2D, tex)
#    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
#    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
#    glTexImage2D(GL_TEXTURE_2D, 0, 4, img.sizeX, img.sizeY, 0,
#                 GL_RGBA, GL_UNSIGNED_BYTE, img.data)
#    return tex
#class Imaged:
#    '''
#        G{classtree}
#    '''
#    sizeX = 0.0
#    sizeY = 0.0
#    data = None
#class Triangle:
#    '''
#        G{classtree}
#    '''
#    name = 'triangle'
#    id = 0
#    def __init__(self, v1, v2, v3, t = None, color = None):
#        '''
#            @type v1: C{str}
#            @param v1:
#
#            @type v2: C{str}
#            @param v2:
#
#            @type v3: C{str}
#            @param v3:
#
#            @type t: C{str}
#            @param t:
#
#            @type color: C{str}
#            @param color:
#        '''
#        self.vertices = [v1, v2, v3]
#        self.texture = t
#        self.color = color
#
#    def render(self):
#        '''
#        '''
#        #glColor3f(1,1,1)
#        if self.color is not None:
#            c = self.color
#            glColor3f(c[0], c[1], c[2])
#        if self.texture is not None:
#            glBindTexture(GL_TEXTURE_2D, self.texture)
#        glBegin(GL_TRIANGLES)
#        glNormal3f(0.0, 0.0, 1.0)
#        for i in range(3):
#            x = self.vertices[i][0]
#            y = self.vertices[i][1]
#            z = self.vertices[i][2]
#
#            if self.texture is not None:
#                u = self.vertices[i][3]
#                v = self.vertices[i][4]
#                glTexCoord2f(float(u), float(v))
#            glVertex3f(float(x), float(y), float(z))
#        glEnd()
#
#def load_environment(sg):
#    '''
#    '''
#
#    p = os.path.join(ghome, 'setupfiles', 'environments', 'env1.txt')
#    lines = parse_setupfile(p)
#    t = load_texture()
#    cdict = {'0':(0, 0, 0), '3':(0, 0, 0), '6':(0, 0, 1), '9':(0, 0, 1), '12':(0, 0, 1), '15':(0, 0, 1)}
#    for i in range(0, len(lines), 3):
#        a = lines[i]
#        b = lines[i + 1]
#        c = lines[i + 2]
#
#        cc = cdict[str(i)]
#        triangle = Triangle(a, b, c, color = cc)
#        sg.add_object(triangle)

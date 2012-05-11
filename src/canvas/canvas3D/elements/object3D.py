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



'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
#=============standard library imports ========================
from OpenGL.GLUT import glutSolidSphere, glutSolidCube, glutSolidTorus, \
    glutStrokeCharacter, glutStrokeWidth, glutBitmapCharacter, \
    GLUT_STROKE_ROMAN, GLUT_BITMAP_HELVETICA_18


from OpenGL.GL import glTranslatef, glRotatef, glLoadName, \
    glColor3f, glColor4f, glPushMatrix, glPopMatrix, glRasterPos2f, \
    glEnable, glDisable, GL_LIGHTING, glBegin, glEnd, glVertex2f, glVertex3f, GL_LINES, GL_LINE_LOOP, \
    glMultMatrixf

from OpenGL.GLU import gluNewQuadric, gluCylinder, gluDisk, gluPartialDisk
from OpenGL.GLE import glePolyCylinder
import math

#=============local library imports  ==========================
from src.helpers.color_generators import colors1f as colors

xseg = yseg = 10
from node import Node
class Object3D(Node):
    '''
        G{classtree}
    '''

    color = colors['gray']
    state = False
    identify = False
    rotation_points = None
    def __init__(self, *args, **kw):
        '''
        '''
        super(Object3D, self).__init__(*args)
        self.translate = (0, 0, 0)
        self.rotate = (0, 0, 0, 0)
        self.scale = (1.0, 1.0, 1.0)


        for k in kw:
            setattr(self, k, kw[k])

    def render(self):
        '''
        '''
        if self.id:
            glLoadName(self.id)
            self._set_material()


    def toggle_identify(self):
        '''
        '''
        self.identify = not self.identify
        self.refresh()


    def _chart_(self, graphinfo, data):
        '''

        '''
        xax1, xax2 = graphinfo[0]
        yax1, yax2 = graphinfo[1]
        self._line2D_(xax1, xax2)
        self._line2D_(yax1, yax2)

    def _line3D_(self, pt1, pt2):
        '''
        '''
        self.__line__(glVertex3f, pt1, pt2)

    def _line2D_(self, pt1, pt2):
        '''
        '''
        self.__line__(glVertex2f, pt1, pt2)

    def __line__(self, vfactory, pt1, pt2, *args, **kw):
        '''
        '''
        glDisable(GL_LIGHTING)

        glBegin(GL_LINES)
        vfactory(*pt1)
        vfactory(*pt2)
        glEnd()

        glEnable(GL_LIGHTING)

    def _rect2D_(self, x, y, w, h):
        '''
        '''
        glDisable(GL_LIGHTING)

        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        glEnable(GL_LIGHTING)

    def _text_(self, text, offs, stroke=False, color=None):
        '''
        '''

        if stroke:
            font = GLUT_STROKE_ROMAN

            glutStrokeWidth(font, 50)
            for c in text:
                glutStrokeCharacter(font, ord(c))
        else:
            glDisable(GL_LIGHTING)
            co = color if (color and (isinstance(color, tuple) or isinstance(color, list))) else (0, 1, 0)

            glColor3f(*co)
            font = GLUT_BITMAP_HELVETICA_18
            glRasterPos2f(*offs)
            for c in text:
                glutBitmapCharacter(font, ord(c))
            glEnable(GL_LIGHTING)

    def _cylinder_(self, r, h, rotate=True):
        '''
        '''
        if rotate:
            glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), r, r, h, xseg, yseg)

    def _sphere_(self, radius=1):
        '''
        '''

        glutSolidSphere(radius, xseg, yseg)

    def _cube_(self, radius=1):
        '''
        '''
        glutSolidCube(radius)

    def _tube_(self, points, colors, radius=1):
        '''
        '''
        if len(colors) == 4:
            colors = colors[:3]
        c = [colors] * len(points)

        glePolyCylinder(points, c, radius)
    def _elbow_(self, bend_radius, tube_radius):
        '''
        '''
        glPushMatrix()
        points = [(0, 0, 0), (0, 0, 0),
                (0, bend_radius, 0),
                (math.cos(bend_radius), bend_radius + math.sin(bend_radius), 0), (math.cos(bend_radius), bend_radius + math.sin(bend_radius), 0),
                (bend_radius, 2 * bend_radius, 0),
                (2 * bend_radius, 2 * bend_radius, 0), (2 * bend_radius, 2 * bend_radius, 0)]


        self._tube_(points, self.color, radius=tube_radius)

        glPushMatrix()
        glTranslatef(0, 0.5, 0)
        self._can_(0.66, 0.5)
        glPopMatrix()

        glTranslatef(2 * bend_radius - 0.5, 2 * bend_radius, 0)
        glRotatef(90, 0, 0, 1)
        self._can_(0.66, 0.5)
        glPopMatrix()

    def _nipple_(self, trans, rot, rh, flange='mini'):
        '''
        '''
        if flange == 'mini':
            frh = (0.66, 0.5)

        glPushMatrix()

        glTranslatef(*trans)
        glRotatef(*rot)
        self._can_(*rh)

        glPushMatrix()
        self._can_(*frh)
        glTranslatef(0, -rh[1] + frh[1], 0)
        self._can_(*frh)
        glPopMatrix()

        glPopMatrix()

    def _can_(self, radius=1, height=1):
        '''
        '''
        glPushMatrix()

        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        self._disk_(radius=radius)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -height, 0)
        glRotatef(90, 1, 0, 0)
        self._disk_(radius=radius)
        glPopMatrix()

        self._cylinder_(radius, height)

        glPopMatrix()

    def _fan_(self):
        '''
        '''
        i_r = 0
        o_r = 1
        glPushMatrix()

        glRotatef(90, 1, 0, 0)
        #blades=[-15,-15+45,-15+90]

        sweep = 30
        nblades = 8
        for start in [-15] * nblades:
            glRotatef(-360.0 / nblades, 0, 0, 1)
            glPushMatrix()
            glRotatef(25, 0 + math.cos(start), 1, 0)
            #glRotatef(5,math.sin(start),math.cos(start),0)

            gluPartialDisk(gluNewQuadric(), i_r, o_r, xseg, yseg,
                           start, sweep
                           )
            glPopMatrix()
        glPopMatrix()

    def _disk_(self, radius=1, inner_radius=0):
        '''
        '''
        gluDisk(gluNewQuadric(), inner_radius, radius, xseg, yseg)

    def _torus_(self, radius=1, inner_radius=0, xs=None, ys=None):
        '''
        '''
        if xs is None:
            xs = xseg

        if ys is None:
            ys = yseg

        glutSolidTorus(inner_radius, radius, xs, ys)

    def _set_material(self, color=None, alpha=None):
        '''
        '''
        c = color
        if c is None:
            c = self.color

        if c is None:
            c = (1, 0, 0)

        if alpha:
            if isinstance(c, tuple):
                c += (alpha,)
            else:
                c.append(alpha)

        if len(c) == 3:
            glColor3f(*c)
        else:
            glColor4f(*c)

    def update(self):
        '''
        '''
        if self.canvas is not None:
            self.canvas.Update()

    def refresh(self):
        '''
        '''
        if self.canvas is not None:
            self.canvas.Refresh()

#state_color_map = dict(static = colors['gray'],
#                     dynamic = colors['blue'],
#                     gettering = colors['green'],
#                     measuring_sample = colors['yellow'],
#                     measuring_air = colors['purple'],
#                     measuring_quad = colors['navy'])
class SetStateObject3D(Object3D):
    '''
        G{classtree}
    '''
    pass

class MultiStateObject3D(Object3D):
    '''
        G{classtree}
    '''
    #always_on=False
    precedence = 0
    precedence_stack = None
    state_stack = None
    test = ''

    def __init__(self, *args, **kw):
        '''

        '''
        super(MultiStateObject3D, self).__init__(*args, **kw)
        self.dependencies = []
        self.state_stack = []
        self.precedence_stack = []
#        if self.always_on:
#            pass
            #self.state=True
            #self.color=colors['green']

#    def _set_material(self, **kw):
#        '''
#            @type **kw: C{str}
#            @param **kw:
#        '''
#
##        if self.always_on:
##            kw['color']=None
#
#        super(MultiStateObject3D, self)._set_material(**kw)


#    def set_state(self, state, calling_valve):
#        '''
#            @type state: C{str}
#            @param state:
#
#            @type calling_valve: C{str}
#            @param calling_valve:
#        '''
#
#
#        if not self.check_dependencies(calling_valve):
#            return
#
#        if isinstance(state, bool):
#            self.color = colors['green'] if state else colors['gray']
#
#        if state in state_color_map.keys():
#            self.color = state_color_map[state]
#            self.state = state
#
#        for b in self.branches:
#            if not isinstance(b, SetStateObject3D):
#                b.set_state(state, calling_valve)
#            else:
#                if b.low_side:
#                    b.low_side.set_state(state, calling_valve)
#
#                if b.state:
#                    if b.high_side:
#                        b.high_side.set_state(state, calling_valve)
#
#                    for bb in b.branches:
#                        bb.set_state(state, calling_valve)
#
#    def check_dependencies(self, cv):
#        '''
#        '''
#        passed = True
#        for d in self.dependencies:
#            #d=self.canvas.scene_graph.get_object_by_name(d)
#            if d.state and d.name != cv:
#                return False
#
#        return passed


class Transform(Object3D):
    '''
        G{classtree}
    '''
    matrix = None
    def render(self):
        '''

        '''
        Object3D.render(self)
        if self.matrix is not None:
            glMultMatrixf(self.matrix)

#class ActiveObject3D(Object3D):
#    pass


#====================== EOF =====================
#        if self.inlet and not self.inlet.state:
#            #return s,self.precedence
#            if action:
#                self.state_stack.insert(0,s)
#                self.precedence_stack.insert(0,precedence)
##                
#                self.precedence=precedence
##                #return s,self.precedence
#                pass
#            else:
#                if self.state_stack:
#                    set_color(s)#self.state_stack[-1:][0])
#                    self.state_stack.pop()
#                    self.precedence_stack.pop()
#                else:
#                    self.precedence=0
#            return s,self.precedence
#        
#        if precedence>=self.precedence:
#            if action:
#                #if not self.state_stack:
#                self.state_stack.insert(0,s)
#                self.precedence_stack.insert(0,precedence)
#                self.precedence=precedence
#            elif self.state_stack:
#                state=self.state_stack.pop(0)
#                p=self.precedence_stack.pop(0)
#                if self.state_stack:
#                    s=self.state_stack[-1:][0]
#                    self.precedence=self.precedence_stack[-1:][0]
#                else:
#                    self.precedence=0  
#           
#            set_color(s)
#        else:
#            if action:
##                max_state=None
##                for s,p in zip(self.state_stack,
##                               self.precedence_stack):
##                    if p>=self.precedence:
##                        max_state=s
##               
##                if max_state:
##                    set_color(max_state)
#                    #self.precedence=p
#               # else:  
#                self.state_stack.append(s)
#                self.precedence_stack.append(precedence)
#                
#                #set to highest precedence
#                
#            else:
#                if self.state_stack:
#                    self.state_stack.pop()
#                    self.precedence_stack.pop()
#                    
##    
##            
#        if self.name=='Argus':
#            print s,action,precedence,self.precedence,self.state_stack,self.precedence_stack
#        return s,self.precedence
##    #

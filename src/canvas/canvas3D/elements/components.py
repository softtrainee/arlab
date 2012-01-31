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

#=============standard library imports ========================

from OpenGL.GL import glScalef, glTranslatef, glRotatef, \
     glPushAttrib, glPopAttrib, glPushMatrix, glPopMatrix, \
     glEnable, glDisable, glLoadIdentity, \
     GL_CURRENT_BIT, GL_DEPTH_TEST

#=============local library imports  ==========================
from object3D import MultiStateObject3D, Object3D, SetStateObject3D
from src.helpers.color_generators import colors1f as colors
animate = False
class Grid(Object3D):
    def render(self):
        n = 10
        i = 2
        yl = n
        xl = n
        for x in range(-n, n + 1, i):
            self._set_material()
            self._line2D_((x, -n), (x, n))  # vertical lines    
            self._line2D_((-n, x), (n, x)) # horizontal lines

            self._set_material(color=(0, 1, 1))
            self._line3D_((x, 0, n), (x, 0, -n))

#            self._set_material(color=(0,1,0))
            self._line3D_((n, 0, x), (-n, 0, x))


class Origin(Object3D):
    '''
    '''

    def render(self):
        '''
           
        '''

        self._set_material()
        points = [([0, 0, 0], [10, 0, 0]),
                ([0, 0, 0], [0, 10, 0]),
                ([0, 0, 0], [0, 0, 10])
                ]
        for p1, p2 in points:
            self._line3D_(p1, p2)

class Turbo(MultiStateObject3D):
    '''
    '''
    def render(self):
        '''

        '''
        super(Turbo, self).render()
        if self.identify:
            tag = self.name.split('_')
            tag = ' '.join([i.capitalize() for i in tag])
            self._text_(tag, [-2, 2])


        glPushAttrib(GL_CURRENT_BIT)

        glPushMatrix()
        self._set_material(color=[0, 0, 0])
        glTranslatef(0, 0.5, 0)

        ac = 1
        glPushMatrix()
        glRotatef(ac * 5, 0, 1, 0)
        self._fan_()
        glPopMatrix()

        glPushMatrix()
        glRotatef(-ac * 5, 0, 1, 0)
        glTranslatef(0, 0.5, 0)
        self._fan_()
        glPopMatrix()

        glPushMatrix()
        glRotatef(ac * 5, 0, 1, 0)
        glTranslatef(0, 1, 0)
        self._fan_()
        glPopMatrix()

        glPopMatrix()
        glPopAttrib()
        #self._set_material()
        #draw main body

        glPushAttrib(GL_CURRENT_BIT)
        for r, h, alpha in [(1, 3, 0.5), (1.5, 0.5, False)]:
            self._set_material(alpha=alpha)
            glTranslatef(0, h, 0)
            self._can_(radius=r, height=h)
        glPopAttrib()

class SixWayCross(MultiStateObject3D):
    '''
    '''

    def render(self):
        '''
        '''
        super(SixWayCross, self).render()

        glPushMatrix()
        h = 3
        r = 0.5
        for trans, rot, rh in [
                             [(0, h, 0), (0, 0, 0, 0), (r, h)],
                          [(0, h / 2.0, h / 2.0), (90, 1, 0, 0), (r, h)],
                          [(-h / 2.0, h / 2.0, 0), (90, 0, 0, 1), (r, h)]
                          ]:
            self._nipple_(trans, rot, rh)
        glPopMatrix()

class Elbow(MultiStateObject3D):
    '''
        
    '''

    def render(self):
        '''
        '''
        super(Elbow, self).render()
        self._elbow_(1, 0.5)

class Bellows(MultiStateObject3D):
    '''
    '''
    straight = True
    radius = 0.5
    height = 2
    points = None
    def render(self):
        '''
        '''
        super(Bellows, self).render()
        if self.straight:
            trans = [0, 0, 0]
            rot = [0, 0, 0, 0]
            rh = [self.radius, self.height]
            self._nipple_(trans, rot, rh)
        else:
            self._tube_(self.points, self.color, radius=self.radius)

class Flex(Bellows):
    '''
    '''
    straight = False

class IonPump(MultiStateObject3D):
    '''
    '''

    def render(self):
        '''
        '''
        super(IonPump, self).render()
        pumpheight = 3
        pumpwidth = 2
        pumplength = 4

        glPushMatrix()

        self._set_material()

        h = 0.75
        glPushMatrix()
        glTranslatef(pumpwidth / 4.0, pumpheight / 2.0 + h, 0)
        self._cylinder_(0.5, h)
        glPopMatrix()

        h = 0.5
        glPushMatrix()
        glTranslatef(pumpwidth / 4.0, pumpheight / 2.0 + 1.5 - h, 0)
        self._can_(radius=0.75, height=h)
        glPopMatrix()

        h = pumpheight / 2.0 + 0.75
        h2 = 10.5
        points = [(pumpwidth / 4.0, h, 0),
                (pumpwidth / 4.0, h, 0),
                (pumpwidth / 4.0, h + 2, 0),
                (0, h2 - 2, 0), (0, h2, 0), (0, h2, 0)]

        self._tube_(points, self.color, radius=0.45)

        glScalef(pumplength, pumpheight, pumpwidth)

        self._cube_()

        glPopMatrix()

class Laser(MultiStateObject3D):
    '''
    '''

    def render(self):
        '''
        '''
        #super(Laser, self).render()
        MultiStateObject3D.render(self)
        glPushAttrib(GL_CURRENT_BIT)
        self._set_material()

        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        self._disk_()

        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -1, 0)
        glRotatef(90, 1, 0, 0)
        self._disk_()
        glPopMatrix()
        self._cylinder_(1, 1)
        glPopAttrib()

    def on(self):
        '''
        '''
        #self.state=True
        self.color = [1, 1, 0]

    def off(self):
        '''
        '''
        #self.state=False
        if self.state:
            self.color = colors['green']
        else:
            self.color = colors['red']

class Quadrupole(MultiStateObject3D):
    '''
    '''
    colorlist = ['black'] * 9 + ['yellow']
    prev_ac = 0
    def render(self):
        '''
        '''
        super(Quadrupole, self).render()
        glPushMatrix()
#        if self.state:
#            glPushMatrix()
#            glRotatef(90, 1, 0, 0)
#
#            import random
#            mod = 60
#            nj = mod / 9
#            revn = 2
#            h = 7
#            for i in [0, 1, 2, 4]:
#                for j in range(nj):
#                    jj = j
#                    j = j / float(nj) * mod - 1
#                    fact = ((ac + j) % mod) / mod
#                    glPushMatrix()
#                    radius = 1.2 * (1 - math.pow(fact, 4))
#                    glTranslatef(radius * math.cos(fact * revn * 2 * math.pi + math.pi / 2.0 * i),
#                             radius * math.sin(fact * revn * 2 * math.pi + math.pi / 2.0 * i),
#                             - fact * h + 4.2)
#
#                    self._set_material(color = [1, fact, 0, 2 * (fact ** 0.5) - 1.8 * fact ** 2])
#                    self._sphere_(radius = 0.2)
#                    glPopMatrix()
#            glPopMatrix()

        self._set_material()
        self._cylinder_(0.75, 4)

        glTranslatef(0, 0, -3)
        glRotatef(-90, 1, 0, 0)
        self._can_(radius=1, height=3)

        glPopMatrix()

class Sector(MultiStateObject3D):
    '''
        
    '''
    start_ac = None
    def render(self):
        '''
        '''
        super(Sector, self).render()

        glPushMatrix()

        glScalef(3, 5, 5)
        self._set_material()
        self._cube_()

        glPopMatrix()

class Shaft(MultiStateObject3D):
    '''
    '''
    #state=F
    prev_ac = 0
    orientation = None
    length = 6
    def render(self):
        '''

        '''
        super(Shaft, self).render()

        glPushAttrib(GL_CURRENT_BIT)
        n = int(self.length)
        lim = n - 1
        if self.orientation in ['down', 'forward', 'backward']:
            lim = 0
        self._set_material()
#        print lim
        for i in range(n):
            glPushMatrix()

            glTranslatef(0, i / 2.0, 0)

            if i == lim:
                self._can_(0.66, 0.5)

            self._cylinder_(0.5, 0.5)

            glPopMatrix()
#        if self.state and animate:
#            if ac % 20 == 0 and self.prev_ac != ac:
#                if self.orientation == 'left' or self.orientation == 'up':
#                    self.colorlist = shift(self.colorlist)
#                else:
#                    self.colorlist = deshift(self.colorlist)
#            self.prev_ac = ac
        glPopAttrib()

def shift(l):
    '''
    '''
    last = l[-1:]
    rl = []
    rl.append(last[0])

    rl += [l[i] for i in range(len(l) - 1)]
    return rl

def deshift(l):
    '''
    '''
    first = l[:-1]
    rl = []
    rl.append(first[0])

    rl += [l[i] for i in range(len(l) - 1)]
    return rl

class Bone(MultiStateObject3D):
    '''
    '''
    length = 1

    def render(self):
        '''
         '''
        super(Bone, self).render()

        glPushAttrib(GL_CURRENT_BIT)

        glPushMatrix()
        self._set_material()
        #glTranslatef(0, 0, 0)
        self._cube_()
        for _i in range(self.length - 1):
            glTranslatef(1, 0, 0)
            self._cube_()
        glPopMatrix()

        glPopAttrib()

class Object2D(Object3D):
    '''
    '''
    def start_render(self):
        '''
        '''
        glDisable(GL_DEPTH_TEST)

        glPushMatrix()
        glLoadIdentity()

        glTranslatef(*self.translate)

    def end_render(self):
        '''
        '''
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)

class TextPanel(Object2D):
    '''
    '''
    fields = None
    title = ''
    def __init__(self, *args, **kw):
        '''
        '''
        super(TextPanel, self).__init__(*args, **kw)

        self.fields = [(0, False, 'pressure'), (0, False, 'pressure'), (0, False, 'pressure'),
                       (0, False, 'pumping_dur'), (0, False, 'idle_dur')]

#    def render(self):
#        '''
#            @type ac: C{str}
#            @param ac:
#        '''
#        self.start_render()
#        h = 14.5 * (1 + 2 / 5.)
#        #super(TextPanel, self).render()
#
#        Object2D.render(self)
#
#        self._text_(self.title, [8, h + 3])
#        for i, f in enumerate(self.fields):
#            _type = f[2]
#            if _type == 'pressure':
#                val = f[0]
#                state = f[1]
#
#                if not state:
#                    val = '----'
#                    fmt = '{}'
#                else:
#                    fmt = '{0.3f}'
#                    if i == 0:
#                        fmt = '%0.2e'
#                text = ('p %i = %s (torr)' % (i, fmt)) % val, [3, h - 5 - (i * 3.5)]
#            elif _type == 'pumping_dur':
#                val = f[0]
##                if f>60:
##                    tunit='min'
#                tunit = 'sec'
#                text = ('p. dur.= %0.1f (%s)' % (val, tunit), [3, h - 5 - (i * 3.5)])
#            elif _type == 'idle_dur':
#                val = f[0]
#                tunit = 'sec'
#                text = ('i. dur.= %0.1f (%s)' % (val, tunit), [3, h - 5 - (i * 3.5)])
#
#            self._text_(*text)
#
#        self._rect2D_(0, 0, 33, h)
#
#        self.end_render()

class Valve(SetStateObject3D):
    '''
    '''
    valve_manager = None

    label_offsets = (0, 3)
    soft_lock = False

    radius = 1
    low_side = None
    high_side = None

    def __init__(self, *args):
        '''
            
        '''
        super(Valve, self).__init__(*args)
        self.connections = []


    def render(self):
        '''

        '''
        #glPushAttrib(GL_CURRENT_BIT)
        super(Valve, self).render()
        #SetStateObject3D.render(self)
        #self._set_material()
        self._sphere_(radius=self.radius)
        #glPopAttrib()

        if self.identify:

            self._text_(self.name, self.label_offsets)

        if self.soft_lock:
            self._draw_soft_locked_identifier()

    def toggle_state(self):
        '''
        '''
        if not self.state:
            self.open()
        else:
            self.close()

    def toggle_lock(self):
        vm = self.valve_manager
        if vm is not None:
            if self.soft_lock:
                vm.unlock(self.name)
            else:
                vm.lock(self.name)
        self.soft_lock = not self.soft_lock

    def sample_valve(self):
        '''
        '''
        self.auto = False
        self.valve_manager.auto_control(self.name, self.auto)

        self.valve_manager.sample(self.name, self)
        self.update()

    def open(self):
        '''
        '''
        s = self.set_state(True)
        self._finish_state_change(True, success=s)
        return s

    def close(self):
        '''
        '''
        s = self.set_state(False)
        self._finish_state_change(False, success=s)
        return s


#    def set_hard_lock(self, lock):
#        '''
#        '''
#        if lock:
#            self.color = colors['yellow']
#            #self.default_color = colors['yellow']
#        else:
#            self._finish_state_change(self.state)
#        self.refresh()

    def set_state(self, state):
        '''
        '''

        if self.valve_manager is not None:
            if state:
                s = self.valve_manager.open_by_name(self.name)
            else:
                s = self.valve_manager.close_by_name(self.name)

            return s

    def _finish_state_change(self, s, success=True):
        '''

        '''
        if isinstance(success, bool) and success:
            self.state = s

            if s:
                self.color = colors['green']
            else:
                self.color = colors['red']

            #required so canvas shows valve state changes
            self.refresh()

    def _draw_soft_locked_identifier(self):
        '''
        '''
        self._draw_orbitals()
        #self._draw_halo()

    def _draw_orbitals(self):
        r = 1.5
        glPushAttrib(GL_CURRENT_BIT)
        self._set_material((0, 0, 1))
        for a in [60, -60, 0]:
            glPushMatrix()
            glRotatef(a, 1, 0, 0)
            glTranslatef(0, 0, -0.25 / 2)
            self._torus_(radius=r, inner_radius=0.15,
                         xs=25, ys=25
                         )
            glPopMatrix()

        glPopAttrib()

    def _draw_halo(self):
        glPushAttrib(GL_CURRENT_BIT)
        self._set_material((0, 0, 1), alpha=0.3)
        self._sphere_(radius=1.5)
        glPopAttrib()

    def _draw_blue_balls(self):
        l = [[1, 0, 0],
           [-1, 0, 0],
           [0, 1, 0],
           [0, -1, 0],
           [0, 0, 1],
           [0, 0, -1]]
        for c in l:
            glPushMatrix()
            glTranslatef(*c)
            self._set_material(color=[0, 0, 1])
            self._sphere_(radius=0.3)
            glPopMatrix()


class PipetteValve(Valve):
    '''
    '''
    radius = 0.75


#=============== EOF ==================
    #def _draw_halo(self):
#        glPushAttrib(GL_CURRENT_BIT)
#        glColor4f(1, 1, 0, 0.5)

        #self._sphere_(radius = 1.3)
        #glPopAttrib()
#        alpha = 'ABCDEFGHIFKLMNOPQRSTUVWXYZ'
#        try:
#            tex = self.textures[alpha.index(self.name)]
#        except:
#            tex = self.textures[0]
#        glBindTexture(GL_TEXTURE_2D, tex)
#        glBegin(GL_TRIANGLES)
#        glNormal3f(0.0, 0.0, 1.0)
#        triangles = [[[0, 0, 0, 0, 0], [0, 1, 0, 0, 1], [1, 0, 0, 1, 0]],
#                  [[1, 1, 0, 1, 1], [1, 0, 0, 1, 0], [0, 1, 0, 0, 1]]]
#        for t in triangles:
#            for v in t:
#
#                uv = [float(v[3]), float(v[4])]
#                glTexCoord2f(*uv)
#                xyz = [float(v[0]), float(v[1]), float(v[2])]
#                glVertex3f(*xyz)
#        glEnd()

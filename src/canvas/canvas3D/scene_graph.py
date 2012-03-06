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
from OpenGL.GL import glRotatef, glTranslatef, glScalef, glPushMatrix, glPopMatrix, \
glLoadIdentity, glGetFloatv, GL_MODELVIEW_MATRIX

from numpy import identity
#=============local library imports  ==========================
from elements.object3D import Object3D
from wx._core import PyDeadObjectError

class SceneGraph(object):
    '''
    Simple scene graph data structure for displaying 3D scene
    On a render class the scene graph traverses its nodes telling each node to render itself
    Actually rendering is handled by the component
    '''

    canvas = None
    root = None
    use_view_cube = False
#    use_view_cube = True

    def __init__(self, canvas, *args, **kw):
        '''


        '''
        super(SceneGraph, self).__init__(*args, **kw)
        self.canvas = canvas
        self.animation_counter = 0

    def increment_animation_counter(self):
        '''
        '''
#        global animation_counter
        self.animation_counter += 1
#        animation_counter += 1
        #reset the animation counter so it doesnt over flow
        if self.animation_counter > 100:
            self.animation_counter = 0

    def get_object_by_name(self, name):
        '''
        '''
        return self.get_object('name', name)

    def get_object_by_id(self, i):
        '''
        '''
        return self.get_object('id', i)

    def get_object(self, t, key):
        '''
        '''
        r = search(None, self.root, t, key)
        return r

    def reset_view(self):
        '''
        '''
        try:
            self.canvas.set_transform(identity(4))
        except PyDeadObjectError:
            pass

    def calc_rotation_matrix(self, x, y, z):
        '''
        '''
        glPushMatrix()
        glLoadIdentity()
        for r in [[x, 1, 0, 0], [y, 0, 1, 0], [z, 0, 0, 1]]:
            glRotatef(*r)
        m = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()

        rot = [[y for j, y in enumerate(x) if j <= 2] for i, x in enumerate(m) if i <= 2]
        return m, rot

    def set_view_cube_rotation(self, m):
        if self.use_view_cube:
            self.root[1].matrix = m

    def set_view_cube_face(self, f):
        if self.use_view_cube:
            self.root[1].set_face(f)

    def render(self, offscreen):
        '''
        '''
        if self.use_view_cube:
            self.root[1].offscreen = offscreen

        traverse(self.root)

def search(rnode, node, searchtype, searchkey):
    '''
    '''
    if node is None:
        return
    nkey = getattr(node, searchtype)
    if nkey == searchkey:
        rnode = node
        return node

    for b in node.branches:
        rnode = search(rnode, b, searchtype, searchkey)

    return rnode

def traverse(node):
    '''
    '''
    def rotate():
        if len(node.rotate) != 4:

            for r in node.rotate:
                glRotatef(*r)
        else:
            glRotatef(*node.rotate)

    glPushMatrix()
    if isinstance(node, Object3D):

        glTranslatef(*node.translate)
        if node.rotation_points is not None:

            glTranslatef(*node.rotation_points[0])
            rotate()
            glTranslatef(*node.rotation_points[1])

        else:
            rotate()

        glScalef(*node.scale)
        node.render()

    for b in node.branches:
        traverse(b)

    glPopMatrix()
#============= EOF ============================================

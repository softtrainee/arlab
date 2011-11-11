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

#=============standard library imports ========================
from wx import EVT_LEFT_DOWN, EVT_RIGHT_DOWN, EVT_KEY_DOWN, EVT_KEY_UP, EVT_MOTION, EVT_LEFT_UP, EVT_MOUSEWHEEL, \
    EVT_ENTER_WINDOW, \
    StockCursor, CURSOR_CROSS, CURSOR_ARROW, CURSOR_SIZING, CURSOR_HAND


from OpenGL.GL import glSelectBuffer, glGetIntegerv, glRenderMode, glInitNames, glPushName, glMatrixMode, \
        glLoadIdentity, glPopMatrix, glPushMatrix, glReadPixels, \
        GL_PROJECTION, GL_MODELVIEW, GL_RENDER, GL_SELECT, GL_VIEWPORT, GL_RGB, GL_UNSIGNED_BYTE
from OpenGL.GLU import gluPickMatrix

import copy
import struct
#=============local library imports  ==========================
from animation_canvas3D import AnimationCanvas3D
from tools.arcball import Matrix3fT, Matrix4fT, ArcBallT, Point2fT, \
    Matrix3fMulMatrix3f, Matrix3fSetRotationFromQuat4f, Matrix4fSetRotationFromMatrix3f
from tools.panner import Panner
from src.canvas.popup_window import PopupWindow

class InteractionCanvas3D(AnimationCanvas3D):
    '''
        G{classtree}
    '''
    _current_pos = (0, 0)
    _hit = None
    def __init__(self, panel):
        '''

        '''
        super(InteractionCanvas3D, self).__init__(panel)
        EVT_LEFT_DOWN(self, self.OnSelect)
        EVT_KEY_DOWN(self, self.OnKeyDown)
        EVT_KEY_UP(self, self.OnKeyUp)
        EVT_MOTION(self, self.OnMotion)
        EVT_LEFT_UP(self, self.OnUnSelect)

        EVT_MOUSEWHEEL(self, self.OnMouseWheel)
        EVT_ENTER_WINDOW(self, self.OnEnter)

        EVT_RIGHT_DOWN(self, self.OnAltSelect)
        self.panner = Panner()

        self.user_views = []
        self.valid_hitids = []

        self.dragging = False
        self.panning = False
        self.lastrotation = Matrix3fT()
        self.thisrotation = Matrix3fT()
        self.transform = Matrix4fT()
        self.translation = (0.0, 0.0, 0.0)

        self.popup = PopupWindow(self)

    def _set_view(self, v):

        self.scene_graph.reset_view()
        self.scene_graph.root[0].translate = [v.x, v.y, v.z]

        m, rot = self.scene_graph.calc_rotation_matrix(v.rx, v.ry, v.rz)
        self.scene_graph.root[0].matrix = m
        self.thisrotation = rot

        self.scene_graph.root[0].scale = (v._zoom,) * 3

    def OnKeyUp(self, event):
        self.panning = False

    def OnKeyDown(self, event):
        '''
        '''
        handled = False
        char_code = event.GetKeyCode()
        if char_code == 32:
            self.panning = True

            handled = True
        elif char_code == 308:#Control
            self._show_popup(event, position=self._current_pos)
            handled = True
            self.Refresh()
        else:
            #check for user views
            for v in self.user_views:
                if char_code == ord(v.key.upper()):
                    handled = True
                    self._set_view(v)
                    break
            self.Refresh()

        if not handled:
            self._on_key_hook(event)

    def _on_key_hook(self, event):
        pass

    def OnSize(self, event):
        '''
        '''
        self.arcball = ArcBallT(*event.GetSize())

        self.Refresh()

    def OnEnter(self, event):
        '''
        '''
        self.SetFocus()
        self.Refresh()

    def OnMouseWheel(self, event):
        '''
        '''
        zoom_limit = 0.5
        m = event.m_wheelRotation
        s = self.scene_graph.root[0].scale

        if s[0] + m / 10.0 >= zoom_limit:
            s = [s + m / 10.0 for s in self.scene_graph.root[0].scale]
            self.scene_graph.root[0].scale = s

        self.Refresh()

    def OnMotion(self, event):
        '''
        '''

        x = event.GetX()
        y = event.GetY()

        self._current_pos = (x, y)

        gw, gh = self.GetSize()
        hit = None
        if self.dragging:

            if self.panning:
                self.SetCursor(StockCursor(CURSOR_HAND))
                self.translation = map(lambda gti, ai: gti + ai,
                                       self.translation, self.panner.drag(Point2fT(gw - x, y)))
                self.scene_graph.root[0].translate = self.translation
            else:
                self.SetCursor(StockCursor(CURSOR_SIZING))

                quat = self.arcball.drag(Point2fT(gw - x, gh - y))

                self.thisrotation = Matrix3fMulMatrix3f(self.lastrotation,
                                                        Matrix3fSetRotationFromQuat4f(quat))
                self.transform = Matrix4fSetRotationFromMatrix3f(self.transform,
                                                        self.thisrotation)
                self.scene_graph.root[0].matrix = self.transform
                self.scene_graph.set_view_cube_rotation(self.transform)

        else:
            hit = self._gl_select_(x, y)
            self._show_popup(event, hit=hit)

        self.Refresh()
        return hit

    def _show_popup(self, event, position=None, hit=None):

        if position is not None:
            x, y = position
            hit = self._gl_select_(x, y)

        else:
            x = event.GetX()
            y = event.GetY()
        show = False
        if hit is not None:
            self._popup_hook(hit)
            show = hit in self.valid_hitids

        if show:
            self.popup.SetPosition(self.ClientToScreenXY(x + 5, y + 5))
            self.SetCursor(StockCursor(CURSOR_CROSS))

            if self._hit is hit or event.ControlDown():
                self.popup.Show(True)
            self._hit = hit
        else:
            self.SetCursor(StockCursor(CURSOR_ARROW))
            self.popup.Show(False)

    def _popup_hook(self, hit):
        pass

    def OnUnSelect(self, event):
        '''
        '''
        self.dragging = False
        if self._hit is None:
            self.SetCursor(StockCursor(CURSOR_ARROW))

        self.lastrotation = copy.copy(self.thisrotation)
        self.Refresh()

    def OnAltSelect(self, event):
        x = event.GetX()
        y = event.GetY()
        hit = self._gl_select_(x, y)
        if not (hit is None or hit not in self.valid_hitids or hit == 0):
            return hit

    def OnSelect(self, event):
        '''
        '''
        x = event.GetX()
        y = event.GetY()
        gw, gh = self.GetSize()
        hit = self._gl_select_(x, y)
        if hit is None or hit not in self.valid_hitids or hit == 0:

            self.lastrotation = copy.copy(self.thisrotation)
            self.dragging = True

            if self.panning:
                self.panner.click(Point2fT(gw - x, y))
            else:
                self.arcball.click(Point2fT(gw - x, gh - y))

        return hit


    def set_transform(self, t):
        '''
 
        '''
        self.transform = t
        self.lastrotation = Matrix3fT()
        self.thisrotation = Matrix3fT()
        self.scene_graph.root[0].transform = t


    def _gl_select_(self, x, y):
        '''

        '''
        _gw, gh = self.GetSize()

        self.draw(offscreen=True)
        b = glReadPixels(x, gh - y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE)

        _buff = glSelectBuffer(128)
        view = glGetIntegerv(GL_VIEWPORT)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(0)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPickMatrix(x, gh - y, 1.0, 1.0, view)
        self._set_view_volume()

        glMatrixMode(GL_MODELVIEW)
        self.draw(offscreen=True)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        hits = glRenderMode(GL_RENDER)
        glMatrixMode(GL_MODELVIEW)

        self.scene_graph.set_view_cube_face(struct.unpack('BBB', b))

        #get the top object

        return min([(h.near, h.names[0]) for h in hits])[1] if hits else None

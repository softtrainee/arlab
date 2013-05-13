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
from traits.api import List, Any
from traitsui.qt4.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
from PySide.QtGui import QLabel, QImage, QPixmap
from src.ui.gui import invoke_in_main_thread

#=============standard library imports ========================

# import math
# import wx
# from wx._core import EVT_PAINT
#=============local library imports  ==========================
# from ctypes_opencv import  cvCreateImage, CvSize, cvAddS, CvScalar, \
# CvRect, cvSetImageROI, cvResize, cvResetImageROI
# from ctypes_opencv.cxcore import cvZero

def convert_bitmap(image, width=None):
    s = image.shape
    im = QImage(image.tostring(),
                 s[1], s[0],
                 QImage.Format_RGB888
                 )
    if width:
        im = QImage.scaledToWidth(im, width)
    pix = QPixmap.fromImage(QImage.rgbSwapped(im))

    return pix

class _ImageEditor(Editor):
    def init(self, parent):
        image = self.factory.image
        if image is None:
            image = self.value

        self.control = QLabel()
        print 'pix map init'
        self.control.setPixmap(convert_bitmap(image))

        self.set_tooltip()

    def update_editor(self):
        image = self.factory.image
        if image is None:
            image = self.value

        qsize = self.control.size()
        print 'pix map update editor'
        invoke_in_main_thread(self.set_pixmap, image, qsize.width())
#         self.control.setPixmap(convert_bitmap(image, qsize.width()))

    def set_pixmap(self,image, w):
        self.control.setPixmap(convert_bitmap(image, w))

#    '''
#    '''
#
#    points = List
#    fps = 20
# #    playTimer = Any
#    def init(self, parent):
# #        '''
# #        '''
#        self.control = self._create_control(parent)
#        self.set_tooltip()
#
# #        self.object.on_trait_change(self.update_editor, 'update_needed')
#
#    def update_editor(self):
# #        '''
# #        '''
#        try:
#            frame = self.value.render()
#        except AttributeError:
#            return
#
#        if not frame:
#            return
#
#        qim = QImage(frame.tostring(),
#                     frame.width, frame.height,
#                     QImage.Format_RGB888)
# #        print qim.width()
#        pix = QPixmap.fromImage(qim)
#        self.control.setPixmap(pix)
#        self.control.repaint()
# #        print 'iiiii'
# #        self.control.setPicture()
# #        self.control.update()
#
# #    def get_frames(self):
# #        '''
# #        '''
# #
# #        obj = self.value
# #        try:
# #            if obj.frames:
# #                return obj.frames
# #        except AttributeError:
# #            pass
#
#    def _create_control(self, parent, track_mouse=False):
#        return QLabel()
# #        '''
# #        '''
# #        panel = Panel(parent, -1, style=CLIP_CHILDREN)
# #
# #        self._set_bindings(panel)
# #        return panel
#
#
# #    def _set_bindings(self, panel):
# #        pass
# #        self.playTimer = wx.Timer(panel, 5)
# #        panel.Bind(wx.EVT_TIMER, self.onNextFrame, self.playTimer)
# #        self.playTimer.Start(1000 / self.fps)
#
# #        panel.Bind(EVT_PAINT, self.onPaint)
# #        if track_mouse:
# #            panel.Bind(EVT_MOTION, self.onMotion)
#
# #        panel.Bind(EVT_IDLE, self.onIdle)
# #        panel.Bind(EVT_LEFT_DOWN, self.onLeftDown)
#
# #    def onLeftDown(self, event):
# #        '''
# #        '''
# #        self.value.mouse_x = x = event.GetX()
# #        self.value.mouse_y = y = event.GetY()
# #
# #        if not self.points:
# #            self.points.append((x, y))
# #        else:
# #            self.points[0] = (x, y)
# #
# #        self.control.Refresh()
# #
# #    def onPaint(self, event):
# #        '''
# #
# #        '''
# #        self._draw_(event)
#
# #    def onIdle(self, event):
# #        self._draw_(event)
# #        event.RequestMore()
#
# #    def onNextFrame(self, event):
# # #        src = self.get_frames()
# # #        frames = self.value.frames
# # #        if frames is not None:
# #        try:
# #            frame = self.value.render()
# #        except AttributeError:
# #            return
# #
# #        if not frame:
# #            return
# #        try:
# #            bitmap = frame.to_wx_bitmap()
# # #            for d in dir(src):
# # #                print d
# #        except AttributeError, e:
# #            print e
# #
# #            bitmap = BitmapFromBuffer(frame.width, frame.height,
# #                                           frame.data
# #                                            )
# #        dc = PaintDC(self.control)
# #        dc.DrawBitmap(bitmap, 0, 0, False)
# #    def onMotion(self, event):
# #        '''
# #
# #        '''
# #        #self.value.mouse_x=event.GetX()
# #        #self.value.mouse_y=event.GetY()
# #        pass
#
# #    def _draw(self, src):
# #        '''
# #        '''
# #        if src:
# #            self._display_images(src)
# #
# # #        if self.points:
# # #            self._display_points(dc,self.points)
# #
# #    def _display_image(self, src):
# #        '''
# #        '''
# #
# #        if src is not None:
# #            try:
# #                bitmap = src.to_wx_bitmap()
# #    #            for d in dir(src):
# #    #                print d
# #            except AttributeError, e:
# #                print e
# #
# #                bitmap = BitmapFromBuffer(src.width, src.height,
# #                                               src.data
# #                                                )
# #            dc = PaintDC(self.control)
# #            dc.DrawBitmap(bitmap, 0, 0, False)
#
#
# #    def _display_images(self, src):
# #        '''
# #        '''
# #        display = self.value.render_images(src)
# #        self._display_image(display)
#
# #    def _display_crosshair(self, dc, x, y, pen=None):
# #        '''
# #        '''
# #        if not pen:
# #            pen = RED_PEN
# #        dc.SetPen(pen)
# #        dc.CrossHair(x, y)
# #
# #    def _display_points(self, dc, ptlist, radius=5):
# #        '''
# #        '''
# #        for pt in ptlist:
# #            params = pt + (radius,)
# #
# #            dc.DrawCircle(*params)


class ImageEditor(BasicEditorFactory):
    '''
    '''
    klass = _ImageEditor
    image = Any

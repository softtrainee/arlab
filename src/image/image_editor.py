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
from traits.api import List
from traitsui.wx.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory

#=============standard library imports ========================
from wx import Panel, ClientDC, \
    CLIP_CHILDREN, EVT_MOTION, EVT_LEFT_DOWN, EVT_IDLE, \
    RED_PEN

import math
#=============local library imports  ==========================
from ctypes_opencv import  cvIplImageAsBitmap, cvCreateImage, CvSize, cvAddS, CvScalar, \
 CvRect, cvSetImageROI, cvResize, cvResetImageROI
from ctypes_opencv.cxcore import cvZero


class _ImageEditor(Editor):
    '''
    '''

    points = List
    def init(self, parent):
        '''
        '''
        self.control = self._create_control(parent)
        self.set_tooltip()

    def update_editor(self):
        '''
        '''
        self.control.Refresh()

    def get_frames(self):
        '''
        '''

        obj = self.value

        if obj.frames:
            return obj.frames

    def _create_control(self, parent, track_mouse=False):
        '''
        '''
        panel = Panel(parent, -1, style=CLIP_CHILDREN)


        panel.Bind(EVT_IDLE, self.onIdle)
        if track_mouse:
            panel.Bind(EVT_MOTION, self.onMotion)

        panel.Bind(EVT_LEFT_DOWN, self.onLeftDown)

        return panel

    def onLeftDown(self, event):
        '''
      
        '''
        self.value.mouse_x = x = event.GetX()
        self.value.mouse_y = y = event.GetY()

        if not self.points:
            self.points.append((x, y))
        else:
            self.points[0] = (x, y)

        self.control.Refresh()

    def onPaint(self, event):
        '''

        '''
        self._draw_()

    def onIdle(self, event):
        '''

        '''
        self._draw_()
        event.RequestMore()

    def _draw_(self):
        '''
        '''
        src = self.get_frames()
        if src is not None:
            self._draw(src)

    def onMotion(self, event):
        '''

        '''
        #self.value.mouse_x=event.GetX()
        #self.value.mouse_y=event.GetY()
        pass

    def _draw(self, src):
        '''
        '''
        dc = ClientDC(self.control)
        if src:
            self._display_images(dc, src)

#        if self.points:
#            self._display_points(dc,self.points)

    def _display_image(self, dc, src):
        '''
        '''

        bitmap = cvIplImageAsBitmap(src,
                                    swap=False,
                                    flip=False
                                    )
        dc.DrawBitmap(bitmap, 0, 0, False)

    def _display_crosshair(self, dc, x, y, pen=None):
        '''
        '''
        if not pen:
            pen = RED_PEN
        dc.SetPen(pen)
        dc.CrossHair(x, y)

    def _display_images(self, dc, src):
        '''
        '''
        if isinstance(src, list):
            if len(src) > 1:
                nsrc = len(src)
                rows = math.floor(math.sqrt(nsrc))
                cols = rows
                if rows * rows < nsrc:
                    cols = rows + 1
                    if cols * rows < nsrc:
                        rows += 1

                size = 300

                #create display image
                w = self.value.width
                h = self.value.height

                display = cvCreateImage(CvSize(w, h), 8, 3)

                cvZero(display)
                cvAddS(display, CvScalar(200, 200, 200), display)
                padding = 12
                m = padding
                n = padding
                for i, s in enumerate(src):
                    x = s.width
                    y = s.height
                    ma = float(max(x, y))
                    scale = ma / size
                    if i % cols == 0 and m != padding:
                        m = padding
                        n += size + padding

                    cvSetImageROI(display, CvRect(int(m), int(n), int(x / scale), int(y / scale)))
                    cvResize(s, display)
                    cvResetImageROI(display)
                    m += (padding + size)
            else:
                display = src[0]

        else:
            display = src
        self._display_image(dc, display)

    def _display_points(self, dc, ptlist, radius=5):
        '''
        '''
        for pt in ptlist:
            params = pt + (radius,)

            dc.DrawCircle(*params)

class ImageEditor(BasicEditorFactory):
    '''
    '''
    klass = _ImageEditor
    

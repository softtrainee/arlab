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
from traits.api import HasTraits, Property, Int, Callable
from traitsui.qt4.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
#============= standard library imports ========================
from PySide.QtGui import QImage, QLabel, QColor, QPixmap
#============= local library imports  ==========================
#============= views ===================================
COLORS = ['red', 'yellow', 'green', 'black']
QT_COLORS = [QColor(ci) for ci in COLORS]
# QT_COLORS = [
#             QColor(220, 10, 10),
#             QColor(250, 200, 0),
#             QColor(10, 220, 10),
#             QColor(0, 0, 0),
#             ]

class LED(HasTraits):
    '''
    '''
    shape = 'circle'
    state = Property(depends_on='_state')
    _state = Int
    def _set_state(self, v):
        if isinstance(v, str):
            self._state = COLORS.index(v)
        elif isinstance(v, int):
            self._state = v

        self.trait_property_changed('state', 0)

    def _get_state(self):
        return self._state

class ButtonLED(LED):
    callable = Callable
    def on_action(self):
        self.callable()


def change_intensity(color, fac):
    '''

    '''
    rgb = [color.red(), color.green(), color.blue()]
    for i, intensity in enumerate(rgb):
        rgb[i] = min(int(round(intensity * fac, 0)), 255)

    return QColor(*rgb)

class qtLED(QLabel):
    _state = False

    def __init__(self, parent, obj, state):
        '''

        '''
        super(qtLED, self).__init__()

        self._blink = 0
        self.blink = False


#        self.timer = wx.Timer(self)
#        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

#        self.connect()
#        self.Bind(wx.EVT_PAINT, self.OnPaint, self)
#        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeft, self)

        self._obj = obj
        s = self._obj.shape
        if s == 'circle':
            self.ascii_led = '''
        000000-----000000      
        0000---------0000
        000-----------000
        00-----XXX-----00
        0----XXXXXXX----0
        0---XXXXXXXXX---0
        ----XXXXXXXXX----
        ---XXXXXXXXXXX---
        ---XXXXXXXXXXX---
        ---XXXXXXXXXXX---
        ----XXXXXXXXX----
        0---XXXXXXXXX---0
        0----XXXXXXX----0
        00-----XXX-----00
        000-----------000
        0000---------0000
        000000-----000000
        '''.strip()
        else:
            self.ascii_led = '''
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        XXXXXXXXXXXXXXXXX
        '''.strip()

        self.set_state(state)


#    def OnMotion(self, event):
#        print event
#
#    def OnLeft(self, event):
#        if self._state:
#            self.set_state(0)
#        else:
#            self.set_state(2)
#
#        if self._obj is not None:
#            self._obj.on_action()
#
#    def GetValue(self):
#        return self._state

    def setText(self, v):
        pass

#    def SetValue(self, v):
#        if isinstance(v, int):
#            self._state = v
#
#    def OnTimer(self, event):
#        '''
#
#        '''
#        if self.blink:
#            if self._blink % 3 == 0:
#                self._set_led_color(0, color=change_intensity(WX_COLORS[self._state], 0.5))
#            else:
#                self._set_led_color(self._state)
#
#            self._blink += 1
#            if self._blink >= 100:
#                self._blink = 0

    def set_state(self, s):
        '''

        '''
        self.blink = False
        # use negative values for blinking
        if s < 0:
            self.blink = True
#            self.timer.Start(200)
        else:
            pass
#            self.timer.Stop()

        s = abs(s)

        self._state = s
        self._set_led_color(s)


    def _set_image(self, color1, color2):
        xpm = ['17 17 3 1',  # width height ncolors chars_per_pixel
               '0 c None',
               'X c {}'.format(color1.name()),
               '- c {}'.format(color2.name())
               ]
        xpm += [s.strip() for s in self.ascii_led.splitlines()]

        qim = QImage(xpm)
        pix = QPixmap.fromImage(qim)
        self.setPixmap(pix)

    def _set_led_color(self, state, color=None):
        '''

        '''
        if color is not None:
            color1 = color
            color2 = color
        else:
#            base_color = WX_COLORS[state]
            base_color = QT_COLORS[state]
            color1 = base_color
            color2 = change_intensity(base_color, 0.5)

        self._set_image(color1, color2)


class _LEDEditor(Editor):
    def init(self, parent):
        '''

        '''
        if self.control is None:
            self.control = qtLED(parent, self.value, self.value.state)
#            self.control = self._create_control(parent)
            self.value.on_trait_change(self.update_object, 'state')

    def update_object(self, obj, name, new):
        '''

        '''
        if name == 'state':
            if self.control is not None:
                self.control.set_state(new)

    def update_editor(self, *args, **kw):
        '''
        '''
        if self.control:
            pass
#        self.control = self._create_control(None)
#        self.value.on_trait_change(self.update_object, 'state')

#    def _create_control(self, parent):
#        '''
#
#        '''
#        panel = qtLED(parent, self.value, self.value.state)
#        return panel

class LEDEditor(BasicEditorFactory):
    '''
    '''
    klass = _LEDEditor
#============= EOF ====================================

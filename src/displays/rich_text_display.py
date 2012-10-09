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
from traits.api import HasTraits, List, Float, Str, Button, Int
from traitsui.api import View, Item, CustomEditor, Handler, HGroup, VGroup, spring

#=============standard library imports ========================
import wx
import wx.richtext as rt
from src.helpers.color_generators import colors8i
from pyface.timer.do_later import do_later
from email.mime.base import MIMEBase
from src.paths import paths
#=============local library imports  ==========================

def gui_decorator(func):
    def decorator(*args,**kw):
        do_later(func, *args, **kw)
    return decorator

class DisplayHandler(Handler):
    def closed(self, info, is_ok):
        obj = info.object
        obj.opened = False
        obj.was_closed = True
        return True

    def init(self, info):
        info.object.ui = info.ui
        info.object.opened = True
        info.object.load_text_buffer()

class RichTextDisplay(HasTraits):
    '''
    '''
    _display = None
    title = Str
    ui = None
    width = Float(625)
    height = Float(415)
#    delegated_text = List
    text = List
    editable = False
    ok_to_open = True

    opened = False
    was_closed = False

    default_color = Str('red')
    default_size = Int(9)
#    bg_color = Str('white')
    bg_color = None

    x = Float(10)
    y = Float(20)

    #height of the text panel == height-_hspacer
    _hspacer = 25
    _text_buffer = List
    selectable = False
    id = ''
    def close(self):
        if self.ui is not None:
            self.ui.dispose()

    def traits_view(self):
        '''
        '''
        return View(
#                    VGroup(
                        Item('_display', show_label=False,
                         editor=CustomEditor(factory=self.factory,
                                             ),
                             height=1.0),
#                         )
#                           ),
                     handler=DisplayHandler,
                     title=self.title,
                     resizable=True,
#                     width=self.width,
#                     height=self.height,
                     x=self.x,
                     y=self.y,
                     id=self.id
                     )

    def factory(self, window, editor):
        '''

        '''

        panel = wx.Panel(window,
                       - 1,
                       wx.DefaultPosition,
                       )

        rtc = rt.RichTextCtrl(panel,
                              - 1,
                            size=wx.Size(self.width, self.height - self._hspacer),
                            style=wx.VSCROLL | wx.HSCROLL | wx.TE_READONLY
                            )

#        prevent moving the cursor
        if not self.selectable:
            rtc.Bind(wx.EVT_LEFT_DOWN, lambda x: x)

#        print self.bg_color
#        rtc.SetBackgroundColour(self.bg_color)
        if self.bg_color:
            rtc.SetBackgroundColour(self.bg_color)
#        panel.SetBackgroundColour(self.bg_color)

        rtc.SetEditable(self.editable)
        self._display = rtc
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(rtc, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)

        return panel

    def load_text_buffer(self):
        self.add_text(self._text_buffer)
        self._text_buffer = []

    @gui_decorator
    def clear(self):
        self.text = []
#        self._text_buffer = []
#        del self.text
#        del self._text_buffer
        
        d = self._display
        if d:
#            d.Freeze()
#            for i in range(4):
            d.SelectAll()
#                d.DeleteSelection()
            d.Delete(d.Selection)
            d.SelectNone()
            d.SetInsertionPoint(0)
#            d.Thaw()
            
    def freeze(self):
        if self._display:
            self._display.Freeze()
            
    def thaw(self):
        if self._display:
            self._display.Thaw()
            
    def _add_(self, msg, color=None, size=None,
              bold=False,
              underline=False, **kw):
        '''
            
        '''
        if not isinstance(msg, (str, unicode)):
            #print 'not str or unicode ', msg
            if not isinstance(msg, tuple):
                return
            msg = msg[0]

        d = self._display
        if color is None:
            color = wx.Colour(*colors8i[self.default_color])
        if size is None:
            size = self.default_size

        elif isinstance(color, str):
            if color in colors8i:
                color = wx.Colour(*colors8i[color])
            else:
                color = wx.Colour(*colors8i[self.default_color])
        else:
            color = wx.Colour(*color)

        family = wx.FONTFAMILY_MODERN
        style = wx.FONTSTYLE_NORMAL
        weight = wx.FONTWEIGHT_NORMAL
        font = wx.Font(size, family, style, weight, False, 'Consolas')

#        d.Freeze()

        d.BeginFont(font)
        d.BeginTextColour(color)

        if underline:
            d.BeginUnderline()
        if bold:
            d.BeginBold()

        d.WriteText(msg)

        if underline:
            d.EndUnderline()
        if bold:
            d.EndBold()

        d.EndTextColour()
        d.EndFont()
        d.Newline()

        n = 300
        if len(self.text) >= n:
            pop = self.text.pop
            s = sum(pop(0) for _ in xrange(100))
            d.Remove(0, s)

        lp = d.GetLastPosition()
        self.show_positon(lp + 10)

#        d.Thaw()

    def show_positon(self, ipos):
        try:
            d = self._display
    #        def _ShowPosition(self, ipos):
            line = d.GetVisibleLineForCaretPosition(ipos)
            ppuX, ppuY = d.GetScrollPixelsPerUnit()  #unit = scroll
    #step
            startYUnits = d.GetViewStart()[1]
            sy = d.GetVirtualSize()[1]
    
            if ppuY == 0:
                return False  # since there's no scrolling, hence no
    #adjusting
    
            syUnits = sy / ppuY
            r = line.GetRect()
            ry = r.GetY()
            rh = r.GetHeight()
            csY = d.GetClientSize()[1]
            csY -= d.GetBuffer().GetBottomMargin()
    
    #        if self.center_caret:
            if ry >= startYUnits * ppuY + csY - rh / 2:
                yUnits = startYUnits + csY / ppuY / 2
                d.SetScrollbars(ppuX, ppuY, 0, syUnits, 0, yUnits)
                d.PositionCaret()
        except AttributeError:
            pass
    #                return True
#        return False
    @gui_decorator
    def add_text(self, msg, **kw):
        '''
        '''
        disp = self._display
        if disp:
#            tappend = self.text.append
            if isinstance(msg, (list, tuple)):
                self.text+=[len(mi)+1 for mi in msg]
#                for mi in msg:
#                    tappend(len(mi) + 1)
            else:
                self.text.append(len(msg)+1)
#                tappend(len(msg) + 1)

            if isinstance(msg, (list, tuple)):
                for mi in msg:
                    if isinstance(mi, tuple):
                        if len(mi) == 2:
                            kw = mi[1]
                        mi = mi[0]
                    self._add_(mi, **kw)

#                    print 'add', msg
            else:
                self._add_(msg, **kw)
        else:
#            pass
            self._text_buffer.append((msg, kw))
            
        


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
import smtplib
from threading import Thread
import os
class ErrorDisplay(RichTextDisplay):
    report = Button
    _hspacer = 60
    def _report_fired(self):
        def send_report():
            try:
                msg = MIMEMultipart()
                msg['From'] = 'pychron'
                msg['To'] = 'nmgrlab@gmail.com'
                msg['Subject'] = 'Error Stack'

                msg.attach(MIMEText('\n'.join([t[0] for t in self.text])))

                #attach the most recent log file
                logdir = os.path.join(paths.root_dir, 'logs')
                logs = os.listdir(logdir)
                logs.reverse()
                for pi in logs:
                    if pi.startswith('pychron'):
                        pi = os.path.join(logdir, pi)
                        break

                with open(pi, 'rb') as f:
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload(f.read())
                    Encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(pi))
                    msg.attach(part)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login('nmgrlab', 'argon4039')

                server.sendmail('pychron', msg['To'], msg.as_string())
            except Exception, err:
                print err  # for debugging only
            finally:
                do_later(self.ui.dispose)

        t = Thread(target=send_report)
        t.start()

    def traits_view(self):
        v = super(ErrorDisplay, self).traits_view()
        v.content.content[0].content.append(HGroup(spring, Item('report', show_label=False)))
        return v

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
from traits.api import HasTraits, List, Float, Str, Button
from traitsui.api import View, Item, CustomEditor, Handler, HGroup, VGroup, spring

#=============standard library imports ========================
import wx
import wx.richtext as rt
from src.helpers.color_generators import colors8i
from pyface.timer.do_later import do_later
from email.mime.base import MIMEBase
from src.paths import paths
#=============local library imports  ==========================
class DisplayHandler(Handler):
    def closed(self, info, is_ok):

        object = info.object

        object.delegated_text = object.text

        object.opened = False
        return True

    def init(self, info):
        info.object.ui = info.ui
        info.object.opened = True

class RichTextDisplay(HasTraits):
    '''
    '''
    _display = None
    title = Str
    ui = None
    width = Float(625)
    height = Float(415)
    delegated_text = List
    text = List
    editable = False
    ok_to_open = True

    opened = False

    default_color = Str('red')
    bg_color = Str('white')

    x = Float(10)
    y = Float(20)

    #height of the text panel == height-_hspacer
    _hspacer = 25


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

        rtc.SetBackgroundColour(self.bg_color)

        rtc.SetEditable(self.editable)
        self._display = rtc

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(rtc, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)
        #panel.Layout()


        if self.delegated_text:
            for msg, kw in self.delegated_text:
                self._add_(msg, **kw)

        return panel

    def _add_(self, msg, new_line=True, color=None, **kw):
        '''
            
        '''
        d = self._display
        if color is None:
            color = wx.Colour(*colors8i[self.default_color])

        elif isinstance(color, str):
            if color in colors8i:
                color = wx.Colour(*colors8i[color])
            else:
                color = wx.Colour(*colors8i[self.default_color])
        else:
            color = wx.Colour(*color)

        size = 9
        family = wx.FONTFAMILY_MODERN
        style = wx.FONTSTYLE_NORMAL
        weight = wx.FONTWEIGHT_NORMAL
        font = wx.Font(size, family, style, weight)
        d.BeginFont(font)
#        d.BeginFontSize(10)
        d.BeginTextColour(color)
        d.WriteText(msg)
        d.EndTextColour()
#        d.EndFontSize()
        d.EndFont()

        if new_line:
            self._display.Newline()

        lp = d.GetLastPosition()
        d.ShowPosition(lp + 600)

    def add_text(self, msg, **kw):
        '''
        '''

        if isinstance(msg, (list, tuple)):
            for mi in msg:
                self.text.append((mi, kw))
        else:
            self.text.append((msg, kw))

        if self._display:
            if isinstance(msg, (list, tuple)):
                for mi in msg:
                    self._add_(mi, **kw)
            else:
                self._add_(msg, **kw)
            if len(self.text) > 500:
                a = self.text.pop(0)[0]
                self._display.Remove(0, len(a) + 1)
                self._display.SetInsertionPointEnd()

        else:
            if isinstance(msg, (list, tuple)):
                for mi in msg:
                    self.delegated_text.append((mi, kw))
            else:
                self.delegated_text.append((msg, kw))


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

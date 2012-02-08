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
from traits.api import HasTraits, List, Float, Str, Button
from traitsui.api import View, Item, CustomEditor, Handler, HGroup, VGroup, spring

#=============standard library imports ========================
import wx
import wx.richtext as rt
from src.helpers.color_generators import colors8i
from pyface.timer.do_later import do_later
from email.mime.base import MIMEBase
from src.helpers.paths import root_dir
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

    x = Float(10)
    y = Float(20)

    #height of the text panel == height-_hspacer
    _hspacer = 25


#    def _do_later(self, func, args=None, obj=None):
#
#        if obj is None:
#            obj = self._display
#
#        func = getattr(obj, func)
#        if args is not None:
#            if isinstance(args, tuple):
#                a = (func,) + args
#                a = args
#            else:
#                a = (func, args)
#                a = (args,)
#        else:
#            a = (func,)
#            a = ()
#        func(*a)

    def close(self):

        if self.ui is not None:
            self.ui.dispose()

    def traits_view(self):
        '''
        '''
        return View(
                    VGroup(
                           Item('_display', show_label=False,
                         editor=CustomEditor(factory=self.factory),
                         )
                           ),
                     handler=DisplayHandler,
                     title=self.title,
                     #resizable = False,
                     width=self.width,
                     height=self.height,
                     x=self.x,
                     y=self.y,
                     )

    def factory(self, window, editor):
        '''

        '''
        panel = wx.Panel(window,
                       - 1,
                       style=wx.DEFAULT_FRAME_STYLE
                       )

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        rtc = rt.RichTextCtrl(panel,
                            size=(self.width, self.height - self._hspacer),
                            style=wx.VSCROLL | wx.HSCROLL | wx.TE_READONLY
                            )

        rtc.SetEditable(self.editable)

        sizer.Add(rtc,
                  1, wx.GROW | wx.ALL
                  )
        #panel.SetAutoLayout(True)
        panel.SetSizer(sizer)
        #panel.Layout()

        self._display = rtc

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

#        self._do_later('BeginFontSize', args=10)
#        self._do_later('BeginTextColour', args=color)
#        self._do_later('WriteText', args=msg)
#        self._do_later('EndTextColour')
#        self._do_later('EndFontSize')
#
#        if new_line:
#            self._do_later('Newline')
#
#        lp = d.GetLastPosition()
#        self._do_later('ShowPosition', args=lp + 600)
        d.BeginFontSize(10)
        d.BeginTextColour(color)
        d.WriteText(msg)
        d.EndTextColour()
        d.EndFontSize()

        if new_line:
            self._display.Newline()
#            self._do_later('Newline')

        lp = d.GetLastPosition()
        d.ShowPosition(lp + 600)
#        self._do_later('ShowPosition', args=lp + 600)

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
#                self._do_later('Remove', args=(0, len(a) + 1))
#                self._do_later('SetInsertionPointEnd')
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
                logdir = os.path.join(root_dir, 'logs')
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

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
#============= standard library imports ========================

#============= local library imports  ==========================

from src.managers.displays.rich_text_display import RichTextDisplay, ErrorDisplay
try:
    import wx
    sw, sh = wx.DisplaySize()
except:
    sw, sh = 1200, 900
gWarningDisplay = RichTextDisplay(
                                  title='Warnings',
                                  width=450,
                                  default_color='red'
                                  )
gLoggerDisplay = RichTextDisplay(title='Logger',
                                 width=450,
                                 x=sw - 450,
                                 y=20
                                 )
gTraceDisplay = ErrorDisplay(title='Error Stack',
                                 width=825,
                                 x=(sw - 825) / 2,
                                 y=100,
                                 default_color='black'
                                 )

#============= EOF =============================================
#from traits.api import HasTraits, List, Str, Property, Enum
#from traitsui.api import View, Item, TabularEditor
#from traitsui.tabular_adapter import TabularAdapter
#class TabularLoggerAdapter(TabularAdapter):
#    columns = [('Sender', 'sender'),
#               ('Timestamp', 'timestamp'),
#             ('Message', 'message')]
#    
#    def get_width(self, object, trait, col):
#        if col == 0:
#            return 0.20
#        elif col == 1:
#            return 0.25
#        else:
#            return 0.65
#    def get_bg_color(self, object, trait, row):
#        ms = getattr(object, trait)
#        obj = ms[row]
#        return 'white' if obj.kind == 'info' else 'red'
#    
#class Message(HasTraits):
#    sender = Str
#    message = Property
#    _message = Str
#    timestamp = Str
#    
#    kind = Enum('info', 'warning')
#    def _get_message(self):
#        msg = self._message
#        if msg[0] in ['=', '*']:
#            msg = msg[6:-6]
#        return msg
#    
#class TabularLoggerDisplay(HasTraits):
#    
#    messages = List(Message)
#    
#    #======TextDisplay protocol==================================
#    def close(self):
#        pass
#    def add_text(self, msg, **kw):
#        args = msg.split(':')
#        sender = args[0]
#        
#        msg = ''.join(args[1:])
#        args = msg.split(' ')
#        tstamp = ' '.join(args[:2])
#        
#        msg = ''.join(args[2:])
#        
#        
#        m = Message(sender = sender,
#                    timestamp = tstamp,
#                    _message = msg,
#                    kind = kw['kind']
#                  )
#        self.messages.insert(0, m)
#        
#    #============================================================
#    
#    
#    def traits_view(self):
#        editor = TabularEditor(adapter = TabularLoggerAdapter())
#        v = View(Item('messages', editor = editor, show_label = False),
#                 resizable = True,
#                 x = 0.01,
#                 y = 0.5,
#                 width = 0.65,
#                 height = 0.5,
#                 )
#        return v
#    
#    
#gLoggerDisplay = TabularLoggerDisplay()

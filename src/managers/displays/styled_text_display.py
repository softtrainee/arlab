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
from traits.api import HasTraits, Str, Button, Bool
from traitsui.api import View, Item, HGroup, Handler
from traitsui.wx.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
#============= standard library imports ========================
from wx import Panel, CLIP_CHILDREN
import wx.stc
#============= local library imports  ==========================
class StyledTextHandler(Handler):
    def init(self, info):
        '''
            @type info: C{str}
            @param info:
        '''
        object = info.object

        for d in object.delegated_text:
            object._write(**d)

class _StyledTextEditor(Editor):
    '''
        G{classtree}
    '''

    def init(self, parent):
        '''
            @type parent: C{str}
            @param parent:
        '''
        self.control = self._create_control(parent)

    def _create_control(self, parent):
        '''
            @type parent: C{str}
            @param parent:
        '''
        panel = Panel(parent, -1, style=CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)


        stc = wx.stc.StyledTextCtrl(panel,
                            size=(self.object.width, self.object.height),
                          #  style = wx.VSCROLL #| wx.HSCROLL
                            #|wx.NO_BORDER

                            )

        sizer.Add(stc,
                  0, wx.EXPAND
                  )
        panel.SetSizer(sizer)


        self.object.stc = stc
        #self.stc = stc

        return panel
    def update_editor(self):
        '''
        '''
        self.control.Refresh()

class StyledTextEditor(BasicEditorFactory):
    '''
        G{classtree}
    '''
    klass = _StyledTextEditor

class StyledTextDisplay(HasTraits):
    '''
        G{classtree}
    '''
    stc = None
    width = 200
    height = 500
    delegated_text = None
    handler = StyledTextHandler
    clear = Button
    title = Str
    clearable = Bool(True)

    def __init__(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        super(StyledTextDisplay, self).__init__(*args, **kw)
        self._styles = [None] * 32
        self._free = 1
        self.delegated_text = []
    def _clear_fired(self):
        '''
        '''
        self.delegated_text = []
        self.stc.ClearAll()
    def get_style(self, color='black'):
        '''
            @type color: C{str}
            @param color:
        '''
        free = self._free
        if color and isinstance(color, (str, unicode)):
            color = color.lower()
        else:
            color = 'black'

        try:
            style = self._styles.index(color)
            return style
        except ValueError:
            style = free
            self._styles[style] = color
            self.stc.StyleSetForeground(style, wx.NamedColour(color))
            free += 1
            if free > 31:
                free = 0
            self._free = free
            return style
    def add_text(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        self._write(**kw)

    def _write(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        stc = self.stc
        if stc is not None:

            msg = kw['msg']
            end = stc.GetLength()
            if 'newline' in kw:

                newline = kw['newline']
            else:
                newline = True

            if newline and not msg.endswith(('\n', '\r')):
                msg = '{}\n'.format(msg)
            stc.AddText(msg)
            if 'color' in kw:
                color = kw['color']
            else:
                color = 'black'

            lentext = len(msg.encode('utf8'))
            stc.StartStyling(end, 31)
            stc.SetStyling(lentext, self.get_style(color=color))

            stc.EnsureCaretVisible()

        else:

            self.delegated_text.append(kw)

    __call__ = _write

    def traits_view(self):
        '''
        '''
        v = View(HGroup(Item('clear', show_label=False,
                                visible_when='clearable')),
               Item('stc', show_label=False, editor=StyledTextEditor(
                                                  ),
                    ),
            width=self.width + 50,
            height=self.height + 50,
            resizable=True,
            handler=StyledTextHandler
              )
        return v

#============= EOF ====================================


if __name__ == '__main__':
    s = StyledTextDisplay()

    s.configure_traits()

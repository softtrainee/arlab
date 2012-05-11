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
from traits.api import Str, Instance, Color, Enum , Bool
from traitsui.wx.code_editor import SourceEditor
from traitsui.basic_editor_factory import BasicEditorFactory
#============= standard library imports ========================
import wx
#============= local library imports  ==========================

class _ScriptEditor(SourceEditor):
    def init(self, parent):
        '''
            @type parent: C{str}
            @param parent:
        '''

        super(_ScriptEditor, self).init(parent)

        wx.EVT_RIGHT_DOWN(self.control, self._on_right_down)

    def _on_right_down(self, event):
        '''
            @type event: C{str}
            @param event:
        '''

        point = event.GetPosition()

        pos = self.control.PositionFromPoint(point)
        line_num = self.control.LineFromPosition(pos)
        curline = self.control.GetLine(line_num)
        on_sub = False
        if 'SUB' in curline or 'Sub' in curline or 'sub' in curline:
            on_sub = True
            self.object._current_sub = curline

        menu = self.object._get_contextual_menu(on_sub)
        wxmenu = menu.create_menu(self.control)

        self.control.PopupMenuXY(wxmenu, point[0] - 10, point[1] - 10)
        wxmenu.Destroy()



class ScriptEditor(BasicEditorFactory):
    '''
        G{classtree}
    '''
    klass = _ScriptEditor

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Object trait containing list of line numbers to mark (optional)
    mark_lines = Str

    # Background color for marking lines
    mark_color = Color(0xECE9D8)
    # Object trait containing the currently selected line (optional)
    selected_line = Str

    # Object trait containing the currently selected text (optional)
    selected_text = Str

    # Object trait containing the currently selected text start position (optional)
    selected_start_pos = Str

    # Object trait containing the currently selected text end position (optional)
    selected_end_pos = Str

    # Background color for selected lines
    #selected_color = Color( 0xA4FFFF )
    selected_color = Color((255, 255, 255))
    # Where should the search toolbar be placed?
    search = Enum('top', 'bottom', 'none')

    # Background color for lines that match the current search
    search_color = Color(0xFFFF94)

    # Current line
    line = Str

    # Current column
    column = Str

    # Should code folding be enabled?
    foldable = Bool(True)

    # Should line numbers be displayed in the margin?
    show_line_numbers = Bool(True)

    # Is user input set on every change?
    auto_set = Bool(True)

    # Should the editor auto-scroll when a new **selected_line** value is set?
    auto_scroll = Bool(True)

    # Optional key bindings associated with the editor    
    key_bindings = Instance('traitsui.key_bindings.KeyBindings')

    # Calltip clicked event
    calltip_clicked = Str

    # The lexer to use. Default is 'python'; 'null' indicates no lexing.
    lexer = Str('python')

    # Object trait containing the list of line numbers to dim (optional)
    dim_lines = Str

    # Object trait to dim lines to. Can be of form #rrggbb or a color spec. If
    # not specified, dark grey is used.
    dim_color = Str

    # Object trait containing the list of line numbers to put squiggles under
    # (optional)
    squiggle_lines = Str

    # Object trait for the color of squiggles. If not specified, red is used.
    squiggle_color = Str
#============= EOF ====================================

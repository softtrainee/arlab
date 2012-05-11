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
from traits.api import Any #, Float, Bool, List
from traitsui.wx.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory

#============= standard library imports ========================
#from wx import Panel
#============= local library imports  ==========================

class _Canvas3DEditor(Editor):
    '''
    '''
    manager = Any
    def init(self, parent):
        '''
        '''
        self.control = self._create_control(parent)

    def _create_control(self, parent):
        '''

        '''
        from extraction_line_canvas3D import ExtractionLineCanvas3D
        panel = ExtractionLineCanvas3D(parent, self.object.manager)
        panel.setup()
        self.object.canvas3D.canvas = panel

        return panel

    def update_editor(self):
        '''
        '''
        self.control.Refresh()

class Canvas3DEditor(BasicEditorFactory):
    '''
        G{classtree}
    '''
    klass = _Canvas3DEditor
#============= EOF ====================================

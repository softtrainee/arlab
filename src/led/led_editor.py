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
from traitsui.wx.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
from src.led.wxLED import wxLED
#============= standard library imports ========================

#============= local library imports  ==========================

#============= views ===================================
class _LEDEditor(Editor):
    def init(self, parent):
        '''

        '''
        if self.control is None:
            self.control = self._create_control(parent)
            self.value.on_trait_change(self.update_object, 'state')

    def update_object(self, obj, name, new):
        '''

        '''
        if name == 'state':
            if self.control is not None:
                self.control.set_state(new)

#    def update_editor(self, *args, **kw):
#        '''
#        '''
#        self.control = self._create_control(None)
#        self.value.on_trait_change(self.update_object, 'state')

    def _create_control(self, parent):
        '''

        '''
        panel = wxLED(parent, self.value, self.value.state)
        return panel

class LEDEditor(BasicEditorFactory):
    '''
    '''
    klass = _LEDEditor
#============= EOF ====================================

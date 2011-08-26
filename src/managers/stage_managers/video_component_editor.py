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
#============= enthought library imports =======================
from traits.api import Bool
#from enable.component_editor import ComponentEditor , _ComponentEditor
#============= standard library imports ========================
from wx import EVT_IDLE, EVT_PAINT, BufferedPaintDC
from src.managers.stage_managers.stage_component_editor import LaserComponentEditor, \
    _LaserComponentEditor
#============= local library imports  ==========================


class _VideoComponentEditor(_LaserComponentEditor):
    '''
    '''
    def init(self, parent):
        '''
        Finishes initializing the editor by creating the underlying toolkit
        widget.
   
        '''
        super(_VideoComponentEditor, self).init(parent)
        self.control.Bind(EVT_IDLE, self.onIdle)

#        print self.context_object, self.object, self.value

#        pause_canvas = False
#        if pause_canvas:
#            self.value.on_trait_change(self.update_editor_item,
#                                            'pause'
#                                            )
#    def update_editor_item(self, obj, name, old, new):
#        if isinstance(new, bool):
#            self.render = not new


    def onIdle(self, event):
        '''
      
        '''


        if self.control is not None:

            self.control.Refresh()

        #force  the control to refresh perodically rendering a smooth video stream
        event.RequestMore()

class VideoComponentEditor(LaserComponentEditor):
    '''
    '''
    klass = _VideoComponentEditor

#============= EOF ====================================

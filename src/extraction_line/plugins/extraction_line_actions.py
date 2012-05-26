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
from pyface.action.api import Action
from src.envisage.core.action_helper import open_manager

#============= standard library imports ========================

#============= local library imports  ==========================
EL_PROTOCOL = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
def get_manager(window):
    return window.application.get_service(EL_PROTOCOL)

class OpenExtractionLineManager(Action):
    description = 'Open extraction line manager'
    name = 'Open Extraction Line Manager'
    def perform(self, event):

        man = get_manager(event.window)
        app = self.window.application
        open_manager(app, man)

class LoadCanvasAction(Action):
    '''
    '''
    description = 'load an updated canvas file'
    name = 'Load Canvas'
    enabled = False
    def perform(self, event):
        '''
        
        '''
        manager = get_manager(self.window)
        manager.window = self.window
        manager.load_canvas()

class RefreshCanvasAction(Action):
    description = 'reload the scene graph to reflect changes made to setupfiles'
    name = 'Refresh Canvas'
#    enabled = False
    def perform(self, event):
        manager = get_manager(self.window)
        manager.window = self.window
        manager.reload_scene_graph()


class OpenViewControllerAction(Action):
    description = 'Open User views'
    name = 'Open User Views'
    enabled = True

    def __init__(self, *args, **kw):
        super(OpenViewControllerAction, self).__init__(*args, **kw)

        man = get_manager(self.window)
        man.on_trait_change(self.update, 'ui')

    def update(self, obj, name, old, new):
        if new:
            self.enabled = True
        else:
            self.enabled = False

    def perform(self, event):
        '''
        '''
        manager = get_manager(event.window)
        app = self.window.application
        open_manager(app, manager.view_controller, kind='livemodal',
                     parent=manager.ui.control
                     )


class OpenDeviceStreamerAction(Action):
    description = 'Open the device streamer manager'
    name = 'Open Device Streamer'

    enabled = False

    def __init__(self, *args, **kw):
        super(OpenDeviceStreamerAction, self).__init__(*args, **kw)
        manager = get_manager(self.window)
        if manager.device_stream_manager is not None:
            self.enabled = True

    def perform(self, event):
        manager = get_manager(self.window)
        manager.window = self.window
        manager.show_device_streamer()


class OpenPyScriptEditorAction(Action):
    def perform(self, event):
        manager = get_manager(self.window)
        manager.open_pyscript_editor()

#============= EOF ====================================

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

#============= standard library imports ========================

#============= local library imports  ==========================
#from src.scripts.core.scripts_manager import SEditor
#from src.experiments.experiments_manager import EEditor
#from src.canvas.designer.canvas_manager import CEditor
#from src.data_processing.modeling.modeler_manager import MEditor
from src.helpers.gdisplays import gLoggerDisplay
from src.helpers.paths import doc_html_dir

#def get_manager(window, editor=None):
#    if editor is None:
#        editor = window.active_editor
#
#    service_id = None
#    if isinstance(editor, SEditor):
#
#        service_id = 'src.scripts.core.scripts_manager.ScriptsManager'
#
#    elif isinstance(editor, EEditor):
#        service_id = 'src.experiments.experiments_manager.ExperimentsManager'
#
#
#    elif isinstance(editor, CEditor):
#        service_id = 'src.canvas.designer.canvas_manager.CanvasManager'
#
#    elif isinstance(editor, MEditor):
#        service_id = 'src.data_processing.modeling.modeler_manager.ModelerManager'
#
#    if service_id:
#        manager = window.application.get_service(service_id)
#        return manager
#
#class SaveAction(Action):
#    '''
#    '''
#    accelerator = 'Ctrl+S'
#    enabled = False
#
#    def __init__(self, *args, **kw):
#        super(SaveAction, self).__init__(*args, **kw)
#        self.window.on_trait_change(self.update, 'active_editor')
#
#    def update(self, obj, name, old, new):
#        manager = get_manager(self.window, editor=new)
#        if manager is not None:
#            manager.on_trait_change(self.update_dirty, 'selected.dirty')
#            #manager.on_trait_change(self.update_file_path, 'selected.file_path')
#            s = manager.selected
#            if s and hasattr(s, 'file_path'):
#                if manager.selected.file_path:
#                    self.enabled = True
#                else:
#                    self.enabled = False
#        else:
#            self.enabled = False
#
##    def update_file_path(self, obj, name, old, new):
#    def update_dirty(self, obj, name, old, new):
#        manager = get_manager(self.window)
#        if manager is None:
#            return
#        if new:
#            if manager.selected:
#                if hasattr(manager.selected, 'file_path'):
#                    if manager.selected.file_path:
#                        self.enabled = True
#                    else:
#                        self.enabled = False
#        else:
#            self.enabled = False
#
#    def perform(self, event):
#        '''
#        '''
#        manager = get_manager(self.window)
#        func = 'save'
#        if manager:
#            getattr(manager, func)()
#
#class SaveAsAction(Action):
#    accelerator = 'Ctrl+Shift+S'
#    def perform(self, event):
#        '''
#        '''
#        editor = event.window.active_editor
#        func = None
#        if isinstance(editor, SEditor):
#            func = 'save_as'
#            service_id = 'src.scripts.core.scripts_manager.ScriptsManager'
#
#        elif isinstance(editor, EEditor):
#            service_id = 'src.experiments.experiments_manager.ExperimentsManager'
#            func = 'save_as'
#
#        elif isinstance(editor, CEditor):
#            service_id = 'src.canvas.designer.canvas_manager.CanvasManager'
#            func = 'save_as'
#
#        if func:
#            manager = event.window.application.get_service(service_id)
#            getattr(manager, func)()


class LoggerAction(Action):
    def perform(self, event):
        if not gLoggerDisplay.opened:
            gLoggerDisplay.edit_traits()
        else:
            gLoggerDisplay.ui.control.Raise()
        #parent=self.window.control)


class GotoHelpPageAction(Action):
    def perform(self, event):
        import webbrowser
        webbrowser.open_new('http://code.google.com/p/arlab/wiki/CheatSheet')


class DocumentationPageAction(Action):
    def perform(self, event):
        import webbrowser
        p = 'file://{}/index.html'.format(doc_html_dir)
        webbrowser.open_new(p)


class GotoAPIPageAction(Action):
    def perform(self, event):
        import webbrowser
        webbrowser.open_new('http://argon131.nmt.edu/~ross/pychron/index.html')

#class OpenUpdateManagerAction(Action):
#    def perform(self, event):
#        from src.managers.update_manager import UpdateManager
#        manager = UpdateManager()
#        manager.edit_traits(parent=self.window.control)
#        
#class RefreshSourceAction(Action):
#    accelerator = 'Ctrl+R'
#    def perform(self, event):
#        from traits.util.refresh import refresh
#        refresh()

#============= EOF ====================================

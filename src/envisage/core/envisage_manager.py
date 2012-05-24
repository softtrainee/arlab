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
from traits.api import HasTraits, Instance, Any, Str, on_trait_change
from pyface.workbench.api import WorkbenchWindow
from pyface.api import FileDialog, OK

#============= standard library imports ========================
import os
#============= local library imports  ==========================
class EnvisageManager(HasTraits):
    '''
        G{classtree}
    '''

    window = Instance(WorkbenchWindow)
    selected = Any
    default_directory = Str
    wildcard = Str
    editor_klass = Any
    klass = Any
    def sync_editor(self, oldname):
        editor = self.window.application.workbench.active_window.get_editor(self.selected,
                                                                            kind=self.editor_klass)
        editor.name = self.selected.name

    def get_service(self, protocol):
        app = self.window.application
        if isinstance(protocol, (list, tuple)):
            for pi in protocol:
                s = app.get_service(pi)
                if s is not None:
                    break
        else:
            s = app.get_service(protocol)
        return s

    def save_as(self):
        path = self._file_dialog('save as')
        if path is not None:
            self.save(path=path)

    def _file_dialog(self, action):
        df = FileDialog(action=action,
              default_directory=self.default_directory,
              wildcard=self.wildcard)
        if df.open() == OK:
            return df.path

    def save(self, *args, **kw):
        if self.selected is not None:
            if not self.selected.file_path:
                if 'path' in kw:
                    path = kw['path']
                else:
                    path = self._file_dialog('save as')

#                if path is not None:
#                    self.selected.file_path = path
            print self.selected, self.selected.file_path
            if path is not None:
                oldname = self.selected.save(**kw)
                if oldname is not None:
                    #sync the editors name
                    self.sync_editor(oldname)

    def open(self, path=None):
        cancel = False
        if path is None:
            path = self._file_dialog('open')
            if path is None:
                cancel = True

        if not cancel:

            obj = self.klass_factory()

            if os.path.isfile(path):
                if not self._bootstrap_hook(obj, path):
                    self.new()
                else:
                    self.add_and_edit(obj)
            else:
                self.warning('%s does not exisit' % path)

    def klass_factory(self):
        return self.klass()


    def add_and_edit(self, e):
        pass

    def _bootstrap_hook(self, obj, path):
        return obj.bootstrap(path)

#    @on_trait_change('window:selection[]')
#    def _on_active_sleechanged(self, obj, trait_name, old, new):
#        print obj,trait_name,old,new
#        
#    @on_trait_change('window:active_part')
#    def _on_active_part_changed(self, obj, trait_name, old, new):
#        print obj,trait_name,old,new
#        
    @on_trait_change('window:active_editor')
    def _on_active_editor_changed(self, obj, trait_name, old, new):
        '''

        '''
        if isinstance(new, self.editor_klass):
            self.selected = new.obj
        else:
            self.selected = None

#    @on_trait_change('window:editor_opened')
#    def on_editor_opened(self, obj, name, old, new):
#        '''
#            @type obj: C{str}
#            @param obj:
#
#            @type name: C{str}
#            @param name:
#
#            @type old: C{str}
#            @param old:
#
#            @type new: C{str}
#            @param new:
#        '''
#        if isinstance(new, self.editor_klass):
#            obj.active_editor = new

#============= views ===================================
#============= EOF ====================================

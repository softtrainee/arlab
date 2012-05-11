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
from traits.api import Property, String, Any
from traitsui.api import View, Item
from traitsui.menu import Menu, Action

#============= standard library imports ========================
import os
#============= local library imports  ==========================
from script_editor import ScriptEditor

from src.envisage.core.envisage_editable import EnvisageEditable
#from core_script import CoreScript

class EnvisageScript(EnvisageEditable):
    '''
        G{classtree}
    '''
    text = Property(depends_on='_text_')
    _text_ = String('')
    manager = Any
    parent = Any
    _current_sub = None
    _original_text = None

    file_extension = '.rs'
    _script = Any

    script_package = None
    script_klass = None

    def read(self):
        '''
        '''
        ok = True
        if self.file_path == '':
            pass
        elif os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as f:
                self._text_ = f.read()
        else:
            self.warning('Invalid file path %s does not exist' % self.file_path)
            ok = False

        return ok

    def _get_text(self):
        '''
        '''
        return self._text_

    def _set_text(self, t):
        '''
            @type t: C{str}
            @param t:
            
        '''
        if self._original_text is None:
            self._original_text = self._text_
        self._text_ = t
        if self._original_text == self._text_:
            self.dirty = False
        else:
            self._original_text = None
            self.dirty = True


#===============================================================================
# context menu handlers
#===============================================================================
    def goto_sub(self):
        '''
        '''
        sub = self._current_sub.split(' ')[1]



        if self.parent:
            path = self.parent.validator.parser.__check_valid_subroutine__(sub)
            self.parent.open(path=path)
#            if path:
#                self.parent.add_script(path)

        #self.parent.selected=self.parent.scripts[:-1][0]
    def _get_contextual_menu(self, on_sub):
        '''
            @type on_sub: C{str}
            @param on_sub:
        '''
        actions = []

        if on_sub:
            actions.append(Action(name='GO TO SUB',
                        on_perform=self.goto_sub))

        return Menu(*actions)

    def bootstrap(self, path=''):
        '''
            @type p: C{str}
            @param p:
        '''
        self.file_path = path

        self._script = self._script_factory()
        return self.read()

    def save(self, path=None):
        '''
        '''
        oldname, path = self._pre_save(path)
        self._dump_items(path, self.text, use_pickle=False)
        self.file_path = path

        root, name = os.path.split(path)
        self._script.source_dir = root
        self._script.file_name = name
        return oldname

    def _script_factory(self):
        sdir = os.path.split(self.file_path)[0]

        kw = dict(source_dir=sdir,
                 file_name=self.name,
                 manager=self.manager,
                 file_path=self.file_path
                 )

        sp = self.script_package
        sk = self.script_klass

        m = __import__(sp, globals(), locals(), [sk], -1)
        klass = getattr(m, sk)
        e = klass(**kw)
        return e

    def execute(self):
        '''
        '''
        ok = True
        if not self.parent.errors:
            self._script.manager = self.manager
            self._script.bootstrap()
#            e = CoreScript(source_dir = sdir,
#                                     file_name = self.name,
#                                     manager = self.manager,
#                                     )

#            e.bootstrap()
#            self._script = e

        else:
            self.warning('Errors found in script')
            for er in self.parent.errors:
                self.warning('%s %s' % (er.linenum, er.error))

            ok = False

        return ok

    def kill(self):
        if self._script is not None:
            self._script.kill_script()
#============= views ===================================
    def traits_view(self):
        '''
        '''
        v = View(Item('text', show_label=False, style='custom',
                           editor=ScriptEditor()

                    )
              )
        return v
#============= EOF ====================================

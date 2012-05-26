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
from traits.api import Str, Enum, Bool, Instance, String, Dict, Property, \
     Event, Button, Any, List
from traitsui.api import View, Item, HGroup, spring, \
    Handler, VGroup, HTMLEditor, CodeEditor, ShellEditor
from pyface.wx.dialog import confirmation

#============= standard library imports ========================
import os

#============= local library imports  ==========================
from src.managers.manager import Manager
from traitsui.menu import Action
from src.helpers.paths import scripts_dir
from pyface.api import warning
#from src.scripts.pyscripts.pyscript import PyScript, HTML_HELP
from src.scripts.pyscripts.api import *
from src.scripts.pyscripts.pyscript_runner import PyScriptRunner
from src.envisage.core.action_helper import open_manager
import time
from pyface.message_dialog import information
#from traitsui.wx.code_editor import SourceEditor
#from traitsui.wx.basic_editor_factory import BasicEditorFactory
#from traitsui.editors.code_editor import ToolkitEditorFactory

SCRIPT_PATHS = dict(bakeout=('src.scripts.bakeout_script', 'BakeoutScript',
                             'src.scripts.bakeout_script_parser',
                             'BakeoutScriptParser',
                             ),

                    extractionline=('src.scripts.extraction_line_script',
                                             'ExtractionLineScript',
                            'src.scripts.extraction_line_script_parser',
                            'ExtractionLineScriptParser',
                                             )
                            )

SCRIPT_EXTENSIONS = dict(bakeout='.bo')


class ScriptHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui
        if not info.initialized:
            info.object.load_help()
            info.object.load_context()

    def save(self, info):
        info.object.save()

    def save_as(self, info):
        info.object.save_as()

    def open_script(self, info):
        info.object.open_script()

    def test_script(self, info):
        info.object.test_script()

#    def execute_script(self, info):
#        info.object.execute_script()

    def object_save_path_changed(self, info):
        if info.initialized:
            info.ui.title = 'Script Editor - {}'.format(info.object.save_path)


class PyScriptManager(Manager):
    show_kind = Bool(False)
    kind = Enum('ExtractionLine', 'Bakeout')
    body = String('''def main():
    pass

''')
    help_message = Str
    save_enabled = Bool(False)
    _executing = Bool(False)
    execute_enabled = Bool(False)
    execute_visible = Bool(True)

    save_path = String
    _original_body = Str
    _parser = None
    title = 'Script Editor - '

    default_directory_name = Str
    context = Dict

    execute_button = Event
    execute_label = Property(depends_on='_executing')

    help_button = Button('Help')

    runner = Instance(PyScriptRunner, ())
    name_count = 0

    scripts = Dict

    def _help_button_fired(self):

        import webbrowser
#        self.s
        print self.help_path

        #to open in browser needs file:// prepended
        webbrowser.open('file://{}'.format(self.help_path))

#        self.edit_traits(view='help_view')

    def _get_execute_label(self):
        return 'Stop' if self._executing else 'Execute'

    def _execute_button_fired(self):
        if self._executing:
            self._executing = False
            self.stop_script()
        else:
            self._executing = True
            self.execute_script()

    def _check_save(self):
        return self.test_script()

#        if self.script_validator.errors:
#            n = len(self.script_validator.errors)
#            is_are = 'is' if n == 1 else 'are'
#            e_es = 'error' if n == 1 else 'errors'
#            d = confirmation(None, '''There {} {} {}.
#Are you sure you want to save ?'''.format(is_are, n, e_es))
#            r = d == 5103
#        else:
#            r = True
#
#        return r

    def _get_default_directory(self):
        if self.default_directory_name:
            return os.path.join(scripts_dir, self.default_directory_name)
        else:
            return scripts_dir

    def save_as(self):
        if not self._check_save():
            return

        p = self.save_file_dialog(default_directory=self._get_default_directory())
#        p = '/Users/ross/Desktop/foo.txt'
        if p is not None:
#            ext = SCRIPT_EXTENSIONS[self.kind.lower()]
            ext = '.py'
            if not p.endswith(ext):
                p += ext

            self._dump_script(p)
            self.save_path = p

    def save(self):
        if not self._check_save():
            return

        p = self.save_path
        self._dump_script(p)
        self.save_enabled = False

    def _pyscript_factory(self, klassname, **kw):
        klass = globals()['{}PyScript'.format(klassname)]
        if self.save_path:
            r, n = os.path.split(self.save_path)
            kw['root'] = r
            kw['name'] = n

        return klass(manager=self.parent,
                     parent=self,
                     ** kw)

    def load_context(self):
#        ps = PyScript(manager=self.parent)
        ps = self._pyscript_factory(self.kind)
        ps.bootstrap()

        self.context = ps.get_context()

    def load_help(self):
        ps = self._pyscript_factory(self.kind)
        m = ps.get_help()
#        self.help_path = ps.get_help_path()
        self.help_message = m

    def open_script(self):
        p = self.open_file_dialog(default_directory=self._get_default_directory())
#        p = os.path.join(self._get_default_directory(), 'btest.py')
        if p is not None:
            self._load_script(p)
            self.save_path = p

    def test_script(self):
        self.execute_enabled = False
#        if os.path.isfile(self.save_path):
#            root, name = os.path.split(self.save_path)
#            ps = PyScript(root=root,
#                        name=name)
        ps = self._pyscript_factory(self.kind)
        ps.set_text(self.body)

        ps.bootstrap(load=False)
        try:
            err = ps._test()
        except Exception, err:
            pass

        if err:
            warning(None, 'This is not a valid PY script\n{}'.format(err))
        else:
            n = 'new script' if not self.save_path else os.path.basename(self.save_path)
            msg = 'No syntax errors found in {}'.format(n)
            information(None, msg)
            self.info(msg)
            self.execute_enabled = True
            return True

    def stop_script(self):
        self.script.cancel()

    def execute_script(self, path=None):
        open_manager(self.application,
                     self.runner)
        ps = self._pyscript_factory(self.kind, runner=self.runner)
        load = False
        if path is None:
            ps.set_text(self.body)
        else:
            load = True
            r, n = os.path.split(path)
            ps.root = r
            ps.name = n
            ps.logger_name = self._generate_unique_name(n)

        ps.bootstrap(load=load)
        ps.execute(new_thread=True)
        self.script = ps

        key = self._generate_unique_key(ps)
        ps.hash_key = key
        self.scripts[key] = ps
        return key

    def get_script_state(self, key):
        try:
            ps = self.scripts[key]
            return ps.state
        except KeyError:
            #assume the script has completed
            # if it isnt in the scripts dictionary
            # the script is remove by the runner when it completes
            return '2k'

    def _generate_unique_key(self, ps):
        from hashlib import md5

        seed = '{}{}'.format(ps.logger_name, time.time())
        return md5(seed).hexdigest()

    def _generate_unique_name(self, name):
        self.name_count += 1
        return '{}-{:03n}'.format(name, self.name_count)

    def _load_script(self, p):
        self.info('loading script {}'.format(p))
        with open(p, 'r') as f:
            self.body = f.read()
            self._original_body = self.body

    def _dump_script(self, p):

        self.info('saving script to {}'.format(p))
        with open(p, 'w') as f:
            f.write(self.body)
        self._original_body = self.body

    def _body_changed(self):
        if self._original_body:
            if self.body == self._original_body:
                self.save_enabled = False
            else:
                self.execute_enabled = False
                self.save_enabled = True

    def help_view(self):
        v = View(Item('help_message',
                              editor=HTMLEditor(),
                              show_label=False),
                 resizable=True,
                 width=700,
                 height=0.85,
                 x=0.5,
                 title='{}PyScript Help'.format(self.kind)
                 )
        return v

    def traits_view(self):
        editor = VGroup(HGroup(spring, 'kind', visible_when='show_kind'),
                 Item('body', editor=CodeEditor(), show_label=False))

        shell_grp = Item('context', editor=ShellEditor(share=True),
                          style='custom', show_label=False)
        v = View(VGroup(
                 HGroup(editor,
                        VGroup(
                               Item('help_button', show_label=False),
                               shell_grp)),

                 self._button_factory('execute_button', 'execute_label',
                                      enabled_when='object.execute_enabled',
                                      visible_when='object.execute_visible',
                                      align='left'),
                 ),
                 resizable=True,
                 buttons=[
                          Action(name='Test', action='test_script'),
                          Action(name='Open', action='open_script'),
                          Action(name='Save', action='save',
                                enabled_when='object.save_enabled'),
                          Action(name='Save As', action='save_as')
                          ],
                 width=700,
                 height=500,
                 handler=ScriptHandler,
                 title=self.title
                 )
        return v

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup

    logging_setup('scripts')
#    s = PyScriptManager(kind='ExtractionLine',
#                        default_directory_name='pyscripts')
    s = PyScriptManager(kind='Bakeout')
#    s.open_script()
    s.configure_traits()
#============= EOF =============================================

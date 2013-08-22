# @PydevCodeAnalysisIgnore
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
# from traits.etsconfig.etsconfig import ETSConfig
# ETSConfig.toolkit = 'qt4'

#============= enthought library imports =======================
from traits.api import Str, Enum, Bool, Instance, String, Dict, Property, \
     Event, List, Int
from traitsui.api import View, Item, HGroup, Group, spring, \
    VGroup, ListStrEditor, InstanceEditor, VSplit
from pyface.file_dialog import FileDialog
from traitsui.menu import Action
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.paths import paths
from src.pyscripts.pyscript_runner import PyScriptRunner
from src.saveable import SaveableHandler
# from src.pyscripts.code_editor import PyScriptCodeEditor
from src.viewable import Viewable
from src.ui.code_editor import PyScriptCodeEditor
from pyface.constant import OK

SCRIPT_PKGS = dict(Bakeout='src.pyscripts.bakeout_pyscript',
                    ExtractionLine='src.pyscripts.extraction_line_pyscript',
                    Measurement='src.pyscripts.measurement_pyscript'
                    )


class ScriptHandler(SaveableHandler):
    def init(self, info):
        info.object.ui = info.ui
        if not info.initialized:
#            info.object.load_help()
            info.object.load_context()
            info.object.load_commands()


    def test_script(self, info):
        info.object.test_script()

    def object_save_path_changed(self, info):
        info.ui.title = 'Script Editor - {}'.format(info.object.save_path)


class PyScriptEditor(Viewable):
#    show_kind = Bool(False)
    _kind = 'ExtractionLine'
#    _kind = Enum('ExtractionLine', 'Bakeout', 'Measurement')
    body = String

    save_enabled = Bool(False)

    save_path = String
    _original_body = Str
    _parser = None
    title = 'Script Editor - '

#    default_directory = Property
#    default_directory_name = Str
    context = Dict

    runner = Instance(PyScriptRunner, ())
    name_count = 0

    scripts = Dict

    core_commands = List
    script_commands = List
    selected_command = Str
    selected_index = Int
    selected_command_object = Property(depends_on='selected_command')

    refresh_scripts_event = Event

    def closed(self, ok):
        if ok:
            self.refresh_scripts_event = True
        return True

    def save_file_dialog(self, **kw):
        dlg = FileDialog(action='save as', **kw)
        if dlg.open() == OK:
            return dlg.path

    def save_as(self):
        if not self._check_save():
            return

        p = self.save_file_dialog(default_directory=self.default_directory)
#        p = '/Users/ross/Desktop/foo.txt'
        if p is not None:
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

    def load_context(self):
        ps = self._pyscript_factory(self._kind)
        ps.bootstrap()

        self.context = ps.get_context()

    def load_commands(self):
        ps = self._pyscript_factory(self._kind)
        prepcommands = lambda cmds: [c[0] if isinstance(c, tuple) else c for c in cmds]

#        self.core_commands = prepcommands(ps.get_core_commands())
#        self.script_commands = prepcommands(ps.get_script_commands())
        self.script_commands = prepcommands(ps.get_commands())
        self.script_commands.sort()

    def open_script(self, path=None):
#        p = os.path.join(self._get_default_directory(), 'btest.py')
        if path is not None:
            self._load_script(path)
            self.save_path = path
            self.save_enabled = True
            return True

    def test_script(self, report_success=True):
        ps = self._pyscript_factory(self._kind)
        ps.text = self.body

        ps.bootstrap(load=False)
        ps.set_default_context()

        try:
            err = ps.test()
        except Exception, err:
            pass

        if err:
            self.warning_dialog('This is not a valid PY script\n{}'.format(err))
        else:
            if report_success:
                n = 'new script' if not self.save_path else os.path.basename(self.save_path)
                msg = 'No syntax errors found in {}'.format(n)
                self.information_dialog(msg)
                self.info(msg)
            return True

#===============================================================================
# private
#===============================================================================
    def _check_save(self):
        return self.test_script(report_success=False)

    def _pyscript_factory(self, klassname, **kw):

        klassname = '{}PyScript'.format(klassname)
        m = __import__(SCRIPT_PKGS[self._kind], fromlist=[klassname])
        klass = getattr(m, klassname)
        if self.save_path:
            r, n = os.path.split(self.save_path)
            kw['root'] = r
            kw['name'] = n
        else:
            kw['root'] = os.path.join(paths.scripts_dir, 'pyscripts')

        return klass(
#                     manager=self.parent,
                     parent=self,
                     **kw)

    def parse(self, txt):
        self.body = txt
        self._original_body = self.body
        self._parse()

    def _parse(self):
        pass
#===============================================================================
# persistence
#===============================================================================
    def _load_script(self, p):
        self.info('loading script {}'.format(p))
        with open(p, 'r') as f:
            self.parse(f.read())

    def _dump_script(self, p):

        self.info('saving script to {}'.format(p))
        with open(p, 'w') as f:
            f.write(self.body)
        self._original_body = self.body

#===============================================================================
# property get/set
#===============================================================================
#    def _get_default_directory(self):
#        if self.default_directory_name:
#            return os.path.join(paths.scripts_dir, self.default_directory_name)
#        else:
#            return paths.scripts_dir
#===============================================================================
# handlers
#===============================================================================
#    def _kind_changed(self):
#        self.load_commands()

    def _body_changed(self):
        if self._original_body:
            if self.body == self._original_body:
                self.save_enabled = False
            else:
                self.save_enabled = True

    def _command_text_factory(self, scmd):
        cmd = self._command_object(scmd)
        return cmd.get_text()

    def _get_selected_command_object(self):
        a = self._command_object(self.selected_command)
        return a

    def _command_object(self, scmd):

        cmd = None
        words = scmd.split('_')
        klass = ''.join(map(str.capitalize, words))

        pkg = 'src.pyscripts.commands.api'
        cmd_name = '{}_command_editor'.format(scmd)
        try:
            cmd = getattr(self, cmd_name)
        except AttributeError:

            m = __import__(pkg, globals={}, locals={}, fromlist=[klass])
            try:
                cmd = getattr(m, klass)()
                setattr(self, cmd_name, cmd)
            except AttributeError, e :
                if scmd:
                    print e

        return cmd

#===============================================================================
# groups
#===============================================================================
    def _get_commands_group(self, name, label):
        return Group(Item(name,
                          style='custom',
                          show_label=False,
                          editor=ListStrEditor(operations=[],
                                        editable=False,
#                                        right_clicked='',
                                        selected='selected_command'
                                        ),
                         width=200,
#                         height= -200,
#                         resizable=False,
#                         scrollable=True
                        ),
#                     label=label,
#                     show_border=True,
                     )
    def _get_parameters_group(self):
        return

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
#        help_grp = Group(
#
#                       )

        editor = VSplit(
                        Item('body',
                             height=0.75,
                             editor=PyScriptCodeEditor(fontsize=14),
                             show_label=False),
                        Item('selected_command_object',
                            show_label=False,
                            style='custom',
                            height=0.25,
                            editor=InstanceEditor(view='help_view')
                            ),
                        )

#        command_grp = VGroup(
#                             Item('_kind'),
#                             self._get_commands_group('script_commands', 'Commands'),
#                             show_border=True
#                             )
        command_grp = self._get_commands_group('script_commands', 'Commands'),

        src_grp = HGroup(
                        command_grp,
                        editor,
                        label='Source'
                        )

        param_grp = self._get_parameters_group()
        tabs = Group(src_grp, layout='tabbed')
        if param_grp:
            tabs.content.insert(0, param_grp)

        v = View(
                 tabs,
                 resizable=True,
                 buttons=[
                          Action(name='Test', action='test_script'),
                          Action(name='Save', action='save',
                                enabled_when='object.save_enabled'),
                          Action(name='Save As', action='save_as')
                          ],
                 width=0.5,
                 height=0.65,
#                 height=850,
                 handler=ScriptHandler,
                 title=self.title
                 )
        return v

if __name__ == '__main__':
    from launchers.helpers import build_version
    build_version('_qt')
    from src.helpers.logger_setup import logging_setup
    logging_setup('scripts')
#    s = PyScriptEditor(_kind='ExtractionLine')
#    s = PyScriptEditor(_kind='Bakeout')
    s = PyScriptEditor(kind='Measurement')

    p = os.path.join(paths.scripts_dir, 'extraction', 'jan_diode.py')
    s.open_script(path=p)
    s.configure_traits()
#============= EOF =============================================
#    def _get_execute_label(self):
#        return 'Stop' if self._executing else 'Execute'
#
#    def _execute_button_fired(self):
#        if self._executing:
#            self._executing = False
#            self.stop_script()
#        else:
#            self._executing = True
#            self.execute_script()
#    def _calc_graph_button_fired(self):
#        ps = self._pyscript_factory(self._kind, runner=self.runner)
#        ps.set_text(self.body)
#
#        #graph calculated in secs
#        ps.calculate_graph()

#    def _generate_unique_key(self, ps):
#        from hashlib import md5
#
#        seed = '{}{}'.format(ps.logger_name, time.time())
#        return md5(seed).hexdigest()
#
#    def _generate_unique_name(self, name):
#        self.name_count += 1
#        return '{}-{:03n}'.format(name, self.name_count)
#    def stop_script(self):
#        self.script.cancel()
#
#    def execute_script(self, path=None):
# #        open_manager(self.application,
# #                     self.runner)
#
#        ps = self._pyscript_factory(self._kind, runner=self.runner)
#        load = False
#        if path is None:
#            ps.set_text(self.body)
#        else:
#            load = True
#            r, n = os.path.split(path)
#            ps.root = r
#            ps.name = n
#            ps.logger_name = self._generate_unique_name(n)
#
#        ps.bootstrap(load=load)
#        ps.execute(new_thread=True)
#        self.script = ps
#
#        key = self._generate_unique_key(ps)
#        ps.hash_key = key
#        self.scripts[key] = ps
#        return key
#
#    def get_script_state(self, key):
#        try:
#            ps = self.scripts[key]
#            return ps.state
#        except KeyError:
#            #assume the script has completed
#            # if it isnt in the scripts dictionary
#            # the script is remove by the runner when it completes
#            return '2k'

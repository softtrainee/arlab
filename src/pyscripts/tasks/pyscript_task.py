#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, String, List, Instance, Property, Any, Enum
from traitsui.api import View, Item, EnumEditor, UItem, Label
from src.envisage.tasks.base_task import BaseManagerTask
from src.envisage.tasks.editor_task import EditorTask
from pyface.tasks.split_editor_area_pane import SplitEditorAreaPane
from src.pyscripts.tasks.pyscript_editor import PyScriptEditor, \
    ExtractionLineEditor, MeasurementEditor
from src.pyscripts.tasks.pyscript_panes import CommandsPane, DescriptionPane, \
    ExamplePane, EditorPane
import os
from src.paths import paths
from pyface.tasks.task_layout import PaneItem, TaskLayout, Tabbed
from src.pyscripts.parameter_editor import ParameterEditor
from traitsui.menu import ModalButtons
#============= standard library imports ========================
#============= local library imports  ==========================

class PyScriptTask(EditorTask):

    kind = String
    kinds = List(['ExtractionLine', 'Measurement'])
    selected_command = String
#    commands = Instance(Commands, ())
    selected = Any
    description = Property(String, depends_on='selected')
    example = Property(String, depends_on='selected')

#    editor = Instance(ParameterEditor, ())
    default_directory = paths.scripts_dir

    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.pyscript',
                          left=Tabbed(
                                     PaneItem('pychron.pyscript.commands'),
                                     PaneItem('pychron.pyscript.editor')
                                     ),
#                          top=PaneItem('pychron.pyscript.description'),
#                          bottom=PaneItem('pychron.pyscript.example'),


                          )
    def create_dock_panes(self):
        self.commands_pane = CommandsPane()
        self.editor_pane = EditorPane()
        return [
                self.commands_pane,
                self.editor_pane,
#                CommandsPane(),
                DescriptionPane(model=self),
                ExamplePane(model=self),
#                EditorPane(model=self)
                ]

    def _active_editor_changed(self):
        if self.active_editor:
            self.commands_pane.commands = self.active_editor.commands.script_commands
            self.editor_pane.editor = self.active_editor.editor

    def save(self):
        pass

    def new(self):

        # todo ask for script type

        info = self.edit_traits(view='kind_select_view')
        print info, info.result
        if info.result:
            self._open_editor(path='')
            return True

#    def open(self):
#        path = '/Users/ross/Pychrondata_diode/scripts/measurement/jan_unknown.py'
#        self._open_file(path)
#        return True

    def _open_file(self, path):
        self.info('opening pyscript: {}'.format(path))
        self._open_editor(path)

    def _extract_kind(self, path):
        with open(path, 'r') as fp:
            for line in fp:
                if line.startswith('#!'):
                    return line.strip()[2:]

    def _open_editor(self, path):
        if path:
            kind = self._extract_kind(path)
            if kind is not None:
                self.kind = kind

        if self.kind == 'Measurement':
            klass = MeasurementEditor
        else:
            klass = ExtractionLineEditor
        editor = klass(path=path,
#                                kind=self.kind
                                )

#        self.editor.editor = editor
#        editor.editor = self.editor

        self.editor_area.add_editor(editor)
        self.editor_area.activate_editor(editor)

    def _save_file(self, path):
        pass


#    def _kind_changed(self):
#        if self.kind:
#            self.commands.load_commands(self.kind)
#            pm = self.parameter_editor_factory(self.kind)
#            print pm
#            self.editor = pm

#    def parameter_editor_factory(self, kind):
#        pkg = 'src.pyscripts.parameter_editor'
#        klass = '{}ParameterEditor'.format(kind)
# #        cmd_name = '{}_command_editor'.format(scmd)
# #        try:
# #            cmd = getattr(self, cmd_name)
# #        except AttributeError:
#
#        m = __import__(pkg, globals={}, locals={}, fromlist=[klass])
#        return getattr(m, klass)()
# #        try:
#            cmd = getattr(m, klass)()
#            setattr(self, cmd_name, cmd)
#        except AttributeError, e :

    def _selected_command_changed(self):
        if self.selected_command:
            scmd = self.selected_command
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

            self.selected = cmd

    def _get_description(self):
        if self.selected:
            return self.selected.description
        return ''

    def _get_example(self):
        if self.selected:
            return self.selected.example
        return ''

    def kind_select_view(self):
        v = View(
                 Label('Select kind of new PyScript'),
                 UItem('kind', editor=EnumEditor(name='kinds')),
                 kind='livemodal',
                 buttons=['OK', 'Cancel'],
                 title=' ',

               )

        return v

#            print self.selected_command
#    def _menu_bar_factory(self, menus=None):
#        if menus is None:
#            menus = []
#        menus.extend([
#                      SMenu()
#                      ])
#
#        return super(PyScriptTask, self)._menu_bar_factory(menus=menus)

#============= EOF =============================================

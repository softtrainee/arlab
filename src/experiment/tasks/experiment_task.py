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
from traits.api import HasTraits, on_trait_change
# from traitsui.api import View, Item
from pyface.tasks.task_layout import PaneItem, TaskLayout, Splitter, Tabbed
#============= standard library imports ========================
#============= local library imports  ==========================
# from src.envisage.tasks.base_task import BaseManagerTask
from src.experiment.tasks.experiment_panes import ExperimentFactoryPane, StatsPane, \
     ControlsPane, ConsolePane, ExplanationPane, WaitPane, IsotopeEvolutionPane, \
    SummaryPane
# from pyface.tasks.task_window_layout import TaskWindowLayout
from src.envisage.tasks.editor_task import EditorTask
from src.experiment.tasks.experiment_editor import ExperimentEditor
from src.paths import paths
import hashlib
import os
from pyface.constant import CANCEL, YES, NO

class ExperimentEditorTask(EditorTask):
    wildcard = '*.txt'
    group_count = 0
    name = 'Experiment'

    def _menu_bar_factory(self, menus=None):
        return super(ExperimentEditorTask, self)._menu_bar_factory(menus=menus)

    def _default_directory_default(self):
        return paths.experiment_dir

    def _default_layout_default(self):
        return TaskLayout(
                          left=Splitter(
                                        PaneItem('pychron.experiment.wait', height=125),
                                        Tabbed(
                                               PaneItem('pychron.experiment.factory'),
                                               PaneItem('pychron.experiment.isotope_evolution'),
                                               PaneItem('pychron.experiment.summary'),
                                               ),
                                         orientation='vertical'
                                      ),
                          right=Splitter(
                                         PaneItem('pychron.experiment.stats'),
                                         Tabbed(
                                                PaneItem('pychron.experiment.console', height=425),
                                                PaneItem('pychron.experiment.explanation', height=425),
                                                ),

#                                         PaneItem('pychron.experiment.wait'),
                                         orientation='vertical'
                                         ),
                          top=PaneItem('pychron.experiment.controls')
                          )

    def create_dock_panes(self):

        self.isotope_evolution_pane = IsotopeEvolutionPane()
        self.summary_pane = SummaryPane()

        return [
                ExperimentFactoryPane(model=self.manager.experiment_factory),
                StatsPane(model=self.manager),
                ControlsPane(model=self.manager.executor),
                ConsolePane(model=self.manager.executor),
                WaitPane(model=self.manager.executor),
                ExplanationPane(),
                self.isotope_evolution_pane,
                self.summary_pane,
                ]

#===============================================================================
# generic actions
#===============================================================================
    def open(self):
#        import os
#        path = os.path.join(paths.experiment_dir, 'aaa.txt')
        path = self.open_file_dialog()
        if path:
#            self.window.reset_layout()
            manager = self.manager
            if manager.verify_database_connection(inform=True):
                if manager.load():
                    with open(path, 'r') as fp:
                        txt = fp.read()

                        qtexts = self._split_text(txt)
                        for qi in qtexts:
                            editor = ExperimentEditor(path=path)
                            editor.new_queue(qi)
                            self._open_editor(editor)

                    qs = [ei.queue
                          for ei in self.editor_area.editors]

                    manager.test_queues(qs)
                    manager.update_info()
                    manager.path = path
                    manager.executor.reset()

#                    manager.start_file_listener(path)

            return True

    def _split_text(self, txt):
        ts = []
        tis = []
        a = ''
        for l in txt.split('\n'):
            a += l
            if l.startswith('*' * 80):
                ts.append(''.join(tis))
                tis = []
                continue

            tis.append(l)
        ts.append('\n'.join(tis))
        return ts

    def merge(self):
        eqs = [self.active_editor.queue]
        self.active_editor.merge_id = 1
        self.active_editor.group = self.group_count
        self.group_count += 1
        for i, ei in enumerate(self.editor_area.editors):
            if not ei == self.active_editor:
                eqs.append(ei.queue)
                ei.merge_id = i + 2
                ei.group = self.group_count

        path = self.save_file_dialog()
        if path:
            self.active_editor.save(path, eqs)
            for ei in self.editor_area.editors:
                ei.path = path

    def new(self):
        editor = ExperimentEditor()
        editor.new_queue()
        self._open_editor(editor)

    def _save_file(self, path):
        self.active_editor.save(path)

        self.manager.experiment_queues = [ei.queue for ei in self.editor_area.editors]
        self.manager.test_queues()
        self.manager.update_info()

        '''
            if the queue is edited while the executor is running the end_at_run_completion is True
            set it to its previous value
        '''
        ex = self.manager.executor
        if ex.isAlive():
            if ex.changed_flag:
                ex.end_at_run_completion = ex.prev_end_at_run_completion
            ex.changed_flag = False

    def _active_editor_changed(self):
        if self.active_editor:
            self.manager.experiment_queue = self.active_editor.queue

    @on_trait_change('active_editor:queue:update_needed')
    def _update_runs(self, new):
        self.manager.update_info()
        self.active_editor.dirty = True
#        self.debug('runs changed {}'.format(len(new)))
#        executor = self.manager.executor
#        if executor.isAlive():
#            executor.end_at_run_completion = True
#            executor.changed_flag = True
#        else:
#            self.manager.executor.executable = False
#        self.manager.experiment_queues = [ei.queue for ei in self.editor_area.editors]

    @on_trait_change('editor_area:editors[]')
    def _update_editors(self, new):
        self.manager.experiment_queues = [ei.queue for ei in new]
#        self.manager.executor.executable = False

    @on_trait_change('manager:executor:current_run:plot_panel')
    def _update_plot_panel(self, new):
        self.isotope_evolution_pane.plot_panel = new
        self.summary_pane.plot_panel = new

    @on_trait_change('manager:add_queues_flag')
    def _add_queues(self, new):
        self.debug('add_queues_flag trigger n={}'.format(self.manager.add_queues_count))
        for _i in range(new):
            self.new()

    @on_trait_change('manager:activate_editor_event')
    def _set_active_editor(self, new):
        self.debug('activating editor {}'.format(new))
        for ei in self.editor_area.editors:
            if id(ei.queue) == new:
                self.debug('editor {} activated'.format(new))
                self.editor_area.activate_editor(ei)
                break

    @on_trait_change('manager:execute_event')
    def _execute(self):
        editor = self.active_editor
        if editor is None:
            if self.editor_area.editors:
                editor = self.editor_area.editors[0]

        if editor:
            p = editor.path
            if os.path.isfile(p):
                group = editor.group
                min_idx = editor.merge_id
        #        print p
                text = open(p, 'r').read()
                hash_val = hashlib.sha1(text).hexdigest()
                qs = [ei.queue
                        for ei in self.editor_area.editors
                            if ei.group == group and ei.merge_id >= min_idx]

                self.manager.execute_queues(qs, p, text, hash_val)

    @on_trait_change('window:closing')
    def _prompt_on_close(self, event):
        '''
            Prompt the user to save when exiting.
        '''
        if self.manager.executor.isAlive():
            name = self.manager.executor.experiment_queue.name
            result = self._confirmation('{} is running. Are you sure you want to quit?'.format(name))

            if result in (CANCEL, NO):
                event.veto = True
            else:
                self.manager.executor.cancel(confirm=False)
        else:
            super(ExperimentEditorTask, self)._prompt_on_close(event)

#============= EOF =============================================

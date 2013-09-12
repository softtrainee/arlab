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
from traits.api import on_trait_change, Bool, Instance, Int
# from traitsui.api import View, Item
from pyface.tasks.task_layout import PaneItem, TaskLayout, Splitter, Tabbed
from pyface.constant import CANCEL, NO
from apptools.preferences.preference_binding import bind_preference
#============= standard library imports ========================
import shutil
import weakref
import os
#============= local library imports  ==========================
# from src.envisage.tasks.base_task import BaseManagerTask
from src.experiment.tasks.experiment_panes import ExperimentFactoryPane, StatsPane, \
     ControlsPane, ConsolePane, ExplanationPane, WaitPane, IsotopeEvolutionPane, \
     SummaryPane
# from pyface.tasks.task_window_layout import TaskWindowLayout
from src.envisage.tasks.editor_task import EditorTask
from src.experiment.tasks.experiment_editor import ExperimentEditor
from src.paths import paths
from src.helpers.filetools import add_extension
from src.ui.gui import invoke_in_main_thread
from src.loading.panes import LoadDockPane, LoadTablePane
from src.loading.loading_manager import LoadingManager
from src.messaging.notify.notifier import Notifier
from src.lasers.pattern.pattern_maker_view import PatternMakerView


class ExperimentEditorTask(EditorTask):
    wildcard = '*.txt'
    group_count = 0
    name = 'Experiment'

    auto_figure_window = None
    use_auto_figure = Bool
    use_notifications = Bool
    notifications_port = Int

    loading_manager = Instance('src.loading.loading_manager.LoadingManager')
    notifier = Instance(Notifier)

    def _loading_manager_default(self):
        lm = self.window.application.get_service('src.loading.loading_manager.LoadingManager')
        lm.trait_set(db=self.manager.db,
                     show_group_positions=True)
#         lm = LoadingManager(db=self.manager.db,
#                             show_group_positions=True
#                             )
        return lm

    def _default_directory_default(self):
        return paths.experiment_dir

    def _default_layout_default(self):
        return TaskLayout(
                          left=Splitter(
                                        PaneItem('pychron.experiment.wait', height=100),
                                        Tabbed(
                                               PaneItem('pychron.experiment.factory'),
                                               PaneItem('pychron.experiment.isotope_evolution'),
#                                                PaneItem('pychron.experiment.summary'),
                                               ),
                                         orientation='vertical'
                                      ),
                          right=Splitter(
                                         Tabbed(
                                                PaneItem('pychron.experiment.stats'),
                                                PaneItem('pychron.experiment.console', height=425),
                                                PaneItem('pychron.experiment.explanation', height=425),
                                                ),
#                                          PaneItem('pychron.extraction_line.canvas_dock'),
#                                         PaneItem('pychron.experiment.wait'),
                                         orientation='vertical'
                                         ),
                          top=PaneItem('pychron.experiment.controls')
                          )

    def new_pattern(self):
        pm = PatternMakerView()
        self.window.application.open_view(pm)

    def open_pattern(self):
        pm = PatternMakerView()
        if pm.load_pattern():
            self.window.application.open_view(pm)

    def send_test_notification(self):
        self.debug('sending test notification')
        db = self.manager.db
#         an=db.get_last_analysis('bu-FD-o')
        an = db.get_last_analysis('ba-01-o')
        an = self.manager.make_analyses([an])[0]
        if an:
            self.debug('test push {}'.format(an.record_id))
            self._publish_notification(an)
        else:
            self.debug('problem recalling last analysis')

    def deselect(self):
        if self.active_editor:
            self.active_editor.queue.selected = []
            self.active_editor.queue.executed_selected = []

    def prepare_destroy(self):
        if self.use_notifications:
            self.notifier.close()
            self.notifier = None

        self.manager.experiment_factory.destroy()
        super(ExperimentEditorTask, self).prepare_destroy()

    def activated(self):

        bind_preference(self, 'use_auto_figure',
                        'pychron.experiment.use_auto_figure')

        bind_preference(self, 'use_notifications',
                        'pychron.experiment.use_notifications')

        bind_preference(self, 'notifications_port',
                        'pychron.experiment.notifications_port')

        bind_preference(self.manager.executor, 'use_auto_save',
                        'pychron.experiment.use_auto_save')
        bind_preference(self.manager.executor, 'auto_save_delay',
                        'pychron.experiment.auto_save_delay')

        super(ExperimentEditorTask, self).activated()

    def create_dock_panes(self):
        self.isotope_evolution_pane = IsotopeEvolutionPane()

        self.load_pane = self.window.application.get_service('src.loading.panes.LoadDockPane')
#         self.load_pane = LoadDockPane()
#         self.load_table_pane = LoadTablePane(model=self.loading_manager)
        self.load_table_pane = self.window.application.get_service('src.loading.panes.LoadTablePane')
        self.load_table_pane.model = self.loading_manager

        self.experiment_factory_pane = ExperimentFactoryPane(model=self.manager.experiment_factory)
        self.wait_pane = WaitPane(model=self.manager.executor)
        panes = [
                self.experiment_factory_pane,
                StatsPane(model=self.manager),
                ControlsPane(model=self.manager.executor),
                ConsolePane(model=self.manager.executor),
#                 ExplanationPane(),
                self.isotope_evolution_pane,
                self.load_pane,
                self.load_table_pane,
                self.wait_pane
#                 self.summary_pane,
                ]

        panes = self._add_canvas_pane(panes)

        app = self.window.application
        from src.lasers.laser_managers.ilaser_manager import ILaserManager
        man = app.get_service(ILaserManager)
        if man:
            if hasattr(man.stage_manager, 'video'):
                from src.image.tasks.video_task import VideoTask
                vt = VideoTask()
    #             plugin = app.get_plugin('pychron.video')
    #             task = plugin.tasks[0].factory()
    #             self.window.add_task(task)

                video = man.stage_manager.video
                man.initialize_video()
                pane = vt.new_video_dock_pane(video=video)
                panes.append(pane)

        return panes


#===============================================================================
# generic actions
#===============================================================================
    def _open_experiment(self, path, **kw):
        with open(path, 'r') as fp:
            txt = fp.read()

            qtexts = self._split_text(txt)
            for qi in qtexts:
                editor = ExperimentEditor(path=path)
                editor.new_queue(qi)
                self._open_editor(editor)

                # loading queue editor set dirty
                # clear dirty flag
                editor.dirty = False

    def open(self, path=None):

#         self._test_auto_figure()
#         return

#        import os
#        ps = (os.path.join(paths.experiment_dir, 'demo.txt'),)
        if path is None:
            ps = self.open_file_dialog(action='open files',
#                                        default_directroy=
                                       )
        else:
            ps = (path,)

        if ps:
            manager = self.manager
            if manager.verify_database_connection(inform=True):
                if manager.load():
                    for path in ps:
                        self.manager.info('Opening experiment {}'.format(path))
                        self._open_experiment(path)

                    manager.path = path
                    manager.executor.reset()
                    manager.update_info()

#                     manager.update_queues()
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

    def reset_queues(self):
        for editor in self.editor_area.editors:
            editor.queue.reset()

        # reset the experimentors db session
        # since the executor session will have made changes
        man = self.manager
        ex = man.executor
        man.update_info()
        man.stats.reset()

        ex.end_at_run_completion = False
        ex.set_extract_state('')

#     def merge(self):
#         eqs = [self.active_editor.queue]
#         self.active_editor.merge_id = 1
#         self.active_editor.group = self.group_count
#         self.group_count += 1
#         for i, ei in enumerate(self.editor_area.editors):
#             if not ei == self.active_editor:
#                 eqs.append(ei.queue)
#                 ei.merge_id = i + 2
#                 ei.group = self.group_count
#
#         path = self.save_file_dialog()
#         if path:
#             self.active_editor.save(path, eqs)
#             for ei in self.editor_area.editors:
#                 ei.path = path

    def new(self):
        editor = ExperimentEditor()
        editor.new_queue()
        self._open_editor(editor)

        self.manager.executor.executable = False

    def _save_file(self, path):
        if self.active_editor.save(path):
            self.manager.refresh_executable()
            self.debug('queues saved')
            self.manager.reset_run_generator()

    def _active_editor_changed(self):
        if self.active_editor:
            self.manager.experiment_queue = self.active_editor.queue

    def _publish_notification(self, run):
        msg = 'RunAdded {}'.format(run.uuid)
        self.info('pushing notification {}'.format(msg))
        self.notifier.send_notification(msg)

    def _open_auto_figure(self):
        if self.use_auto_figure:
            app = self.window.application
            from pyface.tasks.task_window_layout import TaskWindowLayout
            win = app.create_window(TaskWindowLayout('pychron.processing.auto_figure'))
            win.open()

            win.active_task.attached = True
            self.auto_figure_window = win

            self.window.activate()

    def _test_auto_figure(self):
        self.use_auto_figure = True

        self._open_auto_figure()
        task = self.auto_figure_window.active_task

#         task.plot_series('bu-FC-J', 'blank_unknown', 'jan', 'Fusions CO2', days=100)
#         task.plot_series('bu-FD-J', 'blank_unknown', 'jan', 'Fusions Diode', days=100)
        task.plot_sample_ideogram('NM-779')

#===============================================================================
# handlers
#===============================================================================
    @on_trait_change('manager:executor:auto_save_event')
    def _auto_save(self):
        self.save()

    @on_trait_change('source_pane:[selected_connection, source:+]')
    def _update_source(self, name, new):
        from src.image.video_source import parse_url
        if name == 'selected_connection':
            islocal, r = parse_url(new)
            if islocal:
                pass
            else:
                self.source_pane.source.host = r[0]
                self.source_pane.source.port = r[1]
        else:
            url = self.source_pane.source.url()

            self.video_source.set_url(url)

    @on_trait_change('loading_manager:group_positions')
    def _update_group_positions(self, new):
        if not new:
            ef = self.manager.experiment_factory
            rf = ef.run_factory
            rf.position = ''
        else:
            pos = self.loading_manager.selected_positions
            self._update_selected_positions(pos)

    @on_trait_change('loading_manager:selected_positions')
    def _update_selected_positions(self, new):
        ef = self.manager.experiment_factory
        ef.selected_positions = new
        if new:
            rf = ef.run_factory

            nn = new[0]

            rf.selected_irradiation = nn.irradiation
            rf.selected_level = nn.level
            rf.labnumber = nn.labnumber

            # filter rows that dont match the first rows labnumber
            ns = [str(ni.positions[0]) for ni in new
                  if ni.labnumber == nn.labnumber]

            group_positions = self.loading_manager.group_positions
#             group_positions = False
            if group_positions:
                rf.position = ','.join(ns)

    @on_trait_change('manager.experiment_factory:queue_factory:load_name')
    def _update_load(self, new):
        lm = self.loading_manager
#         lm.db.reset()

        if lm.load_name != new:
            lm.load_name = new
            canvas = lm.make_canvas(new, editable=False)
            self.load_pane.component = weakref.ref(canvas)()

        lm.load_load(new, group_labnumbers=False)

        self.load_pane.load_name = new

    @on_trait_change('active_editor:queue:update_needed')
    def _update_runs(self, new):
        self.manager.update_info()
        if self.active_editor.queue.initialized:
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
        if new is not None:
            self.isotope_evolution_pane.plot_panel = new
#         self.summary_pane.plot_panel = new

    @on_trait_change('manager:executor:run_completed')
    def _update_run_completed(self, new):
        if self.auto_figure_window:
            task = self.auto_figure_window.active_task
            invoke_in_main_thread(task.refresh_plots, new)

        if self.use_notifications:
            self._publish_notification(new)

        load_name = self.manager.executor.experiment_queue.load_name
        if load_name:
            self._update_load(load_name)

    @on_trait_change('manager:add_queues_flag')
    def _add_queues(self, new):
        self.debug('add_queues_flag trigger n={}'.format(self.manager.add_queues_count))
        for _i in range(new):
            self.new()

    @on_trait_change('manager:activate_editor_event')
    def _set_active_editor(self, new):
#        self.debug('activating editor {}'.format(new))
        for ei in self.editor_area.editors:
            if id(ei.queue) == new:
#                self.debug('editor {} activated'.format(new))
                try:
                    self.editor_area.activate_editor(ei)
                except AttributeError:
                    pass
                break
    def _backup_editor(self, editor):
        p = editor.path
        p = add_extension(p, '.txt')

        if os.path.isfile(p):
            # make a backup copy of the original experiment file
            bp = os.path.basename(p)
            pp = os.path.join(paths.backup_experiment_dir,
                            '{}.orig'.format(bp))
            self.info('{} - saving a backup copy to {}'.format(bp, pp))
            shutil.copyfile(p, pp)

    @on_trait_change('manager:execute_event')
    def _execute(self):
        if self.editor_area.editors:
            for ei in self.editor_area.editors:
                self._backup_editor(ei)

            qs = [ei.queue for ei in self.editor_area.editors
                    if ei != self.active_editor]

            if self.active_editor:
                qs.insert(0, self.active_editor.queue)

            # launch execution thread
            # if successful open an auto figure task
            if self.manager.execute_queues(qs):
                self._open_auto_figure()
            else:
                self.warning('experiment queue did not start properly')

    @on_trait_change('manager:executor:[measuring,extracting]')
    def _update_measuring(self, name, new):
        if new:
            if name == 'measuring':
                self._show_pane(self.isotope_evolution_pane)
            elif name == 'extracting':
                self._show_pane(self.wait_pane)

    @on_trait_change('active_editor:queue:dclicked')
    def _edit_event(self):
        p = self.experiment_factory_pane
        self._show_pane(p)

    def _show_pane(self, p):
        ctrl = p.control
        if not p.visible:
            ctrl.show()
        ctrl.raise_()



#         editor = self.active_editor
#         if editor is None:
#             if self.editor_area.editors:
#                 editor = self.editor_area.editors[0]
#
#         if editor:
#             p = editor.path
#             p = add_extension(p, '.txt')
#
#             if os.path.isfile(p):
#                 # make a backup copy of the original experiment file
#                 shutil.copyfile(p, '{}.orig'.format(p))
#
# #                 group = editor.group
# #                 min_idx = editor.merge_id
# #                 text = open(p, 'r').read()
# #                 hash_val = hashlib.sha1(text).hexdigest()
# #                 qs = [ei.queue
# #                         for ei in self.editor_area.editors
# #                             if ei.group == group and ei.merge_id >= min_idx]
#                 qs = [ei.queue for ei in self.editor_area.editors]
#                 # launch execution thread
#                 # if successful open an auto figure task
# #                 if self.manager.execute_queues(qs, p, text, hash_val):
#                 if self.manager.execute_queues(qs, p):
#                     self._open_auto_figure()

    @on_trait_change('manager:[save_event, executor:auto_save_event]')
    def _save_queue(self):
        self.save()

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

    @on_trait_change('active_editor:dirty')
    def _update_active_editor_dirty(self):
        if self.active_editor.dirty:
            self.manager.executor.executable = False
#===============================================================================
# default/factory
#===============================================================================

    def _notifier_factory(self):
        n = Notifier()
        n.setup(self.notifications_port)
        return n

    def _manager_factory(self):
        from src.experiment.experimentor import Experimentor
        from src.helpers.parsers.initialization_parser import InitializationParser
        ip = InitializationParser()
        plugin = ip.get_plugin('Experiment', category='general')
        mode = ip.get_parameter(plugin, 'mode')

        app = None
        if self.window:
            app = self.window.application

        exp = Experimentor(application=app,
                           mode=mode,
#                            connect=False
                           )

        return exp

    def _manager_default(self):
        return self._manager_factory()

    def _notifier_default(self):
        return self._notifier_factory()
#============= EOF =============================================

#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import Button, Event, Enum, Property, Bool, Float, Dict, \
    Instance, Str, Any, on_trait_change, String, List
from traitsui.api import View, Item, HGroup, Group, spring
from apptools.preferences.preference_binding import bind_preference
#============= standard library imports ========================
# from threading import Thread
import time
import os
#============= local library imports  ==========================
from src.globals import globalv
# from src.experiment.automated_run.tabular_adapter import ExecuteAutomatedRunAdapter
# from src.ui.tabular_editor import myTabularEditor
# from src.experiment.manager import ExperimentManager
from src.managers.manager import Manager
from src.pyscripts.pyscript_runner import PyScriptRunner, RemotePyScriptRunner
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.experiment.utilities.mass_spec_database_importer import MassSpecDatabaseImporter
# from src.displays.rich_text_display import RichTextDisplay
from src.paths import paths
from src.helpers.parsers.initialization_parser import InitializationParser
# from src.experiment.set_selector import SetSelector
from src.experiment.stats import StatsGroup
from src.pyscripts.extraction_line_pyscript import ExtractionLinePyScript
from src.lasers.laser_managers.ilaser_manager import ILaserManager
from src.database.orms.isotope_orm import meas_AnalysisTable, gen_AnalysisTypeTable, \
    meas_MeasurementTable
from src.constants import NULL_STR
from src.monitors.automated_run_monitor import AutomatedRunMonitor, \
    RemoteAutomatedRunMonitor
# from src.experiment.automated_run.automated_run import AutomatedRun
from src.experiment.automated_run.factory import AutomatedRunFactory
# from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.displays.display import DisplayController
from src.experiment.experimentable import Experimentable
from src.ui.thread import Thread
# from src.experiment.experimentable import Experimentable

# @todo: display total time in iso format
# @todo: display current exp sets mass spectrometer, extract device and tray

class ExperimentExecutor(Experimentable):
    spectrometer_manager = Instance(Manager)
    extraction_line_manager = Instance(Manager)
    ion_optics_manager = Instance(Manager)
    massspec_importer = Instance(MassSpecDatabaseImporter)
    info_display = Instance(DisplayController)
    pyscript_runner = Instance(PyScriptRunner)
    data_manager = Instance(H5DataManager, ())

#    current_run = Instance(AutomatedRun)

    end_at_run_completion = Bool(False)
    delay_between_runs_readback = Float
    delaying_between_runs = Bool(False)
    resume_runs = Bool(False)
    changed_flag = Bool(False)

    show_sample_map = Button
    execute_button = Event
    resume_button = Button('Resume')
    execute_label = Property(depends_on='_alive')
    truncate_button = Button('Truncate')
    truncate_style = Enum('Immediate', 'Quick', 'Next Integration')
    '''
        immediate 0= is the standard truncation, measure_iteration stopped at current step and measurement_script truncated
        quick     1= the current measure_iteration is truncated and a quick baseline is collected, peak center?
        next_int. 2= same as setting ncounts to < current step. measure_iteration is truncated but script continues
    '''

#    right_clicked = Any
#    selected_row = Any
    selected = Any
    dclicked = Event
    right_clicked = Event
    recall_run = Button
    edit_run = Button
    save_button = Button('Save')
    save_as_button = Button('Save As')
    edit_enabled = Property(depends_on='selected')
    recall_enabled = Property(depends_on='selected')

    _alive = Bool(False)
    _last_ran = None
    _prev_baselines = Dict
    _prev_blanks = Dict
    _was_executed = False
    err_message = None

#    repo_kind = Str
    db_kind = Str
    username = Str

    mode = 'normal'

    measuring = Bool(False)
    stats = Instance(StatsGroup)

    new_run_gen_needed = False

    statusbar = String

    executable = Bool

    def isAlive(self):
        return self._alive

    def info(self, msg, log=True, color=None, *args, **kw):
        self.statusbar = msg
        if self.info_display:
            if color is None:
                color = 'green'
            self.info_display.add_text(msg, color=color)

        if log:
            super(ExperimentExecutor, self).info(msg, *args, **kw)

    def bind_preferences(self):
        super(ExperimentExecutor, self).bind_preferences()

        prefid = 'pychron.experiment'

        bind_preference(self.massspec_importer.db, 'name', '{}.massspec_dbname'.format(prefid))
        bind_preference(self.massspec_importer.db, 'host', '{}.massspec_host'.format(prefid))
        bind_preference(self.massspec_importer.db, 'username', '{}.massspec_username'.format(prefid))
        bind_preference(self.massspec_importer.db, 'password', '{}.massspec_password'.format(prefid))

    def experiment_blob(self):
        return '{}\n{}'.format(self.experiment_queue.path, self.text)

#    def closed(self, ok):
#        self.selected = None
#        return super(ExperimentExecutor, self).closed(ok)
#
#    def opened(self, ui):
#        self.info_display.clear()
#        self.end_at_run_completion = False
#        self._was_executed = False
#        self.stats.reset()
#        self.statusbar = ''
#        super(ExperimentExecutor, self).opened(ui)

    def add_backup(self, uuid_str):
        with open(paths.backup_recovery_file, 'a') as fp:
            fp.write('{}\n'.format(uuid_str))

    def remove_backup(self, uuid_str):
        with open(paths.backup_recovery_file, 'r') as fp:
            r = fp.read()

        r = r.replace(uuid_str, '')
        with open(paths.backup_recovery_file, 'w') as fp:
            fp.write(r)

    def execute_procedure(self, name=None):
        if name is None:
            name = self.open_file_dialog(default_directory=paths.procedures_dir)
            if not name:
                return
            name = os.path.basename(name)

        self._execute_procedure(name)

    def cancel(self):
        if self.confirmation_dialog('Cancel {} in Progress'.format(self.title),
                                     title='Confirm Cancel'
                                     ):
            arun = self.experiment_queue.current_run
            if arun:
                arun.cancel()
            self._alive = False
            self.stats.stop_timer()

    def execute(self):
        self.debug('starting execution')
                    # check for blank before starting the thread

        if self._pre_execute_check():
            self.info_display.clear()
            self.stats.start_timer()
            self.stats.nruns_finished = 0

            t = Thread(target=self._execute)
            t.start()
            self.debug('execution started')
            self._execute_thread = t

    def _pre_execute_check(self):
        exp = self.experiment_queues[0]
        if self._has_preceeding_blank_or_background(exp):
            if not self.massspec_importer.connect():
                if not self.confirmation_dialog('Not connected to a Mass Spec database. Do you want to continue with pychron only?'):
                    self._alive = False
                    return

            nonfound = self._check_for_managers(exp)
            if nonfound:
                self.warning_dialog('Canceled! Could not find managers {}'.format(','.join(nonfound)))
                self.info('experiment canceled because could not find managers {}'.format(nonfound))
                self._alive = False
                return
            else:
                mon, isok = self._monitor_factory()

                if mon and not isok:
                    self.warning_dialog('Canceled! Error in the AutomatedRunMonitor configuration file')
                    self.info('experiment canceled because automated_run_monitor is not setup properly')
                    self._alive = False
                    return
            return True

#===============================================================================
# stats
#===============================================================================
    def increment_nruns_finished(self):
        self.stats.nruns_finished += 1

#    def reset_stats(self):
# #        self._alive = True
#        self.stats.start_timer()
#
#    def stop_stats_timer(self):
# #        self._alive = False
#        self.stats.stop_timer()

#===============================================================================
# handlers
#===============================================================================
#    @on_trait_change('experiment_queues[]')
#    def _update_stats(self):
#        self.stats.experiment_queues = self.experiment_queues
#        self.stats.calculate()
#===============================================================================
# private
#===============================================================================
    def _execute(self):
#         if self.isAlive():
#             if self.confirmation_dialog('Cancel {} in Progress'.format(self.title),
#                                      title='Confirm Cancel'
#                                      ):
#                 arun = self.experiment_queue.current_run
#                 if arun:
#                     arun.cancel()
#                 self._alive = False
#         else:
#            if self._was_executed:
#                self.load_experiment_queue(self.experiment_queue.path)

#            self.stop_file_listener()

        # test runs first
        for exp in self.experiment_queues:
            err = exp.test_runs()
            if err:
                self.info('experiment canceled. {}'.format(err))
                self.warning('experiment canceled')
                return


        self._execute_experiment_queues()
#                 t = Thread(target=self._execute_experiment_queues)
#                 t.start()
#                 self._execute_thread = t

        self.err_message = False
        self._was_executed = True
#             else:
#                 self.info('experiment canceled because no blank was configured')
#                 self._alive = False

    def _check_for_managers(self, exp):
        nonfound = []
        if self.extraction_line_manager is None:
            if not globalv.experiment_debug:
                nonfound.append('extraction_line')

        if exp.extract_device != NULL_STR:
            extract_device = exp.extract_device.replace(' ', '_').lower()
            man = self.application.get_service(ILaserManager, 'name=="{}"'.format(extract_device))
            if not man:
                if not globalv.experiment_debug:
                    nonfound.append(extract_device)
            elif man.mode == 'client':
                if not man.test_connection():
                    nonfound.append(extract_device)

        needs_spec_man = any([ai.measurement_script for ai in self._get_all_automated_runs()])

        if self.spectrometer_manager is None and needs_spec_man:
            if not globalv.experiment_debug:
                nonfound.append('spectrometer')

        return nonfound

    def _execute_experiment_queues(self):
#        self.stats.calculate()

#         if not self.massspec_importer.connect():
#             if not self.confirmation_dialog('Not connected to a Mass Spec database. Do you want to continue with pychron only?'):
#                 self._alive = False
#                 return
#
#         exp = self.experiment_queues[0]
#         nonfound = self._check_for_managers(exp)
#         if nonfound:
#             self.warning_dialog('Canceled! Could not find managers {}'.format(','.join(nonfound)))
#             self.info('experiment canceled because could not find managers {}'.format(nonfound))
#             self._alive = False
#             return
#         else:
#             mon, isok = self._monitor_factory()
#
#             if mon and not isok:
#                 self.warning_dialog('Canceled! Error in the AutomatedRunMonitor configuration file')
#                 self.info('experiment canceled because automated_run_monitor is not setup properly')
#                 self._alive = False
#                 return

        self.pyscript_runner.connect()
        self._alive = True

        exp = self.experiment_queue

        # check the first aliquot before delaying
        arv = exp.cleaned_automated_runs[0]
        self._check_run_aliquot(arv)

        # delay before starting
        delay = exp.delay_before_analyses
        self._delay(delay, message='before')

#        self.set_selector.selected_index = -2
        rc = 0
        ec = 0
        for i, exp in enumerate(self.experiment_queues):
            if self.isAlive():
                self.experiment_queue = exp
                t = self._execute_automated_runs(i + 1, exp)
                if t:
                    rc += t
                    ec += 1

            if self.end_at_run_completion:
                break

        self.info('Executed {:n} sets. total runs={:n}'.format(ec, rc))
        self._alive = False

    def _delay(self, delay, message='between'):
        self.delay_between_runs_readback = delay
        self.info('Delay {} runs {}'.format(message, delay))
        self.delaying_between_runs = True
        self.resume_runs = False
        st = time.time()
        while time.time() - st < delay:
            if not self.isAlive():
                break
            if self.resume_runs:
                break

            time.sleep(0.5)
            self.delay_between_runs_readback -= 0.5
        self.delaying_between_runs = False

    def _execute_procedure(self, name):
        self.pyscript_runner.connect()

        root = paths.procedures_dir
        self.info('executing procedure {}'.format(os.path.join(root, name)))

        els = ExtractionLinePyScript(root=root,
                                     name=name,
                                     runner=self.pyscript_runner
                                     )
        if els.bootstrap():
            try:
                els._test()
                els.execute(new_thread=True, bootstrap=False)
            except Exception, e:
                self.warning(e)
                self.warning_dialog('Invalid Script {}'.format(name))

    def _execute_automated_runs(self, iexp, exp):

        self.info('Starting automated runs set= Set{}'.format(iexp))

#        self.set_selector.selected_index = iexp - 1
        exp._alive = True

        self.db.reset()

        # save experiment to database
        self.info('saving experiment {} to database'.format(exp.name))

        self.db.add_experiment(exp.name)
        self.db.commit()

        rgen, nruns = exp.new_runs_generator(self._last_ran)
        cnt = 0
        totalcnt = 0

        while self.isAlive():
            self.db.reset()
            force_delay = False

            # check for mods
            if self._check_for_file_mods():
                self._reload_from_disk()
                cnt = 0
                self.info('the experiment set was modified')
                rgen, nruns = exp.new_runs_generator(self._last_ran)
                force_delay = True

            if force_delay or (self.isAlive() and \
                               cnt < nruns and \
                                        not cnt == 0):
                # delay between runs
                delay = exp.delay_between_analyses
                self._delay(delay)

            runargs = None
            try:
#                if cnt >= self.max_allowable_runs:
#                    self.warning_dialog('Max allowable runs exceeded cnt= {} max= {}. Stopping experiment'.format(cnt, self.max_allowable_runs))
#                    break

                runspec = rgen.next()
                if not runspec.skip:
                    runargs = self._launch_run(runspec, cnt)

            except StopIteration:
                break

            cnt += 1
            if runargs:
                t, run = runargs
                self._last_ran = runspec

                if run.overlap:
                    self.info('overlaping')
                    run.wait_for_overlap()
                else:
                    t.join()

                self.debug('current run finished')
                if self.isAlive():
                    totalcnt += 1
                    if run.analysis_type.startswith('blank'):
                        pb = run.get_baseline_corrected_signals()
                        if pb is not None:
                            self._prev_blanks = pb

                self._report_execution_state(run)

            if self.end_at_run_completion:
                break

        if self.err_message:
            '''
                set last_run to None if this run wasnt successfully
                experiment set will restart at last successful run
            '''
            self._last_ran = None
            if run:
                run.state = 'fail'
            self.warning('automated runs did not complete successfully')
            self.warning('error: {}'.format(self.err_message))

        self._end_runs()
        if run:
            self.info('Set{}. Automated runs ended at {}, runs executed={}'.format(iexp, run.runid, totalcnt))

        return totalcnt

    def _report_execution_state(self, run):
        if self.err_message:
            msg = self.err_message
        else:
            msg = 'Success'

        man = self.application.get_service('src.social.twitter_manager.TwitterManager')
        if man is not None:
            man.post('{} {}'.format(msg, run.runid))

        man = self.application.get_service('src.social.email_manager.EmailManager')
        if man is not None:
            if msg == 'Success':
                msg = '{}\n{}'.format(msg, run.assemble_report())
#                man.broadcast(msg)

    def _launch_run(self, run, cnt):
#        repo = self.repository
#        dm = self.data_manager
#        runner = self.pyscript_runner
        run = self._setup_automated_run(cnt, run)
#        self._setup_automated_run(cnt, run, repo, dm, runner)
        run.pre_extraction_save()
        self.info('========== {} =========='.format(run.runid))

        ta = Thread(name=run.runid,
                   target=self._do_automated_run,
                   args=(run,)
                   )
        ta.start()
        return ta, run

    def _check_run_aliquot(self, arv):
        '''
            check the secondary database for this labnumber 
            get last aliquot
        '''
        if self.massspec_importer:
            db = self.massspec_importer.db
            try:
                _ = int(arv.labnumber)
                al = db.get_lastest_analysis_aliquot(arv.labnumber)
                if al is not None:
                    if al > arv.aliquot:
                        old = arv.aliquot
                        arv.aliquot = al + 1
                        self.message('{}-{:02n} exists in secondary database. Modifying aliquot to {:02n}'.format(arv.labnumber,
                                                                                                                  old,
                                                                                                       arv.aliquot))
            except ValueError:
                pass


#    def _setup_automated_run(self, i, arun, repo, dm, runner):
    def _setup_automated_run(self, i, arv):
        '''
            convert the an AutomatedRunSpec an AutomatedRun
        '''

        # the first run was checked before delay before runs
        if i > 1:
            self._check_run_aliquot(arv)


        arun = arv.make_run()

        exp = self.experiment_queue
        exp.current_run = arun
        self.debug('setup run {} of {}'.format(i, exp.name))
        self.debug('%%%%%%%%%%%%%%% Comment= {} %%%%%%%%%%%%%'.format(arun.comment))

        '''
            save this runs uuid to a hidden file
            used for analysis recovery
        '''
        self.add_backup(arun.uuid)

#        arun.index = i
        arun.experiment_name = exp.path
        arun.experiment_manager = self
        arun.spectrometer_manager = self.spectrometer_manager
        arun.extraction_line_manager = self.extraction_line_manager
        arun.ion_optics_manager = self.ion_optics_manager
        arun.data_manager = self.data_manager
        arun.db = self.db
        arun.massspec_importer = self.massspec_importer
        arun.runner = self.pyscript_runner

        arun.integration_time = 1.04
#        arun.repository = repo
        arun.info_display = self.info_display

        arun.username = self.username

        mon, _ = self._monitor_factory()
        if mon is not None:
            mon.automated_run = arun
            arun.monitor = mon
        return arun

    def _get_blank(self, kind):
        db = self.db
        sel = db.selector_factory(style='single')
        sess = db.get_session()
        q = sess.query(meas_AnalysisTable)
        q = q.join(meas_MeasurementTable)
        q = q.join(gen_AnalysisTypeTable)
        q = q.filter(gen_AnalysisTypeTable.name == 'blank_{}'.format(kind))
        dbs = q.all()

        sel.load_records(dbs, load=False)

        sel.selected = sel.records[-1]

        info = sel.edit_traits(kind='livemodal')
        if info.result:
            dbr = sel.selected
            if dbr:
                dbr = sel._record_factory(dbr)
                dbr.load()
                self.info('using {} as the previous {} blank'.format(dbr.record_id, kind))

                self._prev_blanks = dbr.get_baseline_corrected_signal_dict()

                return True

    def _has_preceeding_blank_or_background(self, exp):
        if globalv.experiment_debug:
            return True

        types = ['air', 'unknown', 'cocktail']
        btypes = ['blank_air', 'blank_unknown', 'blank_cocktail']
        # get first air, unknown or cocktail
        aruns = self.experiment_queue.automated_runs
        fa = next(((i, a) for i, a in enumerate(aruns)
                    if a.analysis_type in types and not a.skip), None)

        if fa:
            ind, an = fa
            if ind == 0:
                if self.confirmation_dialog("First {} not preceeded by a blank. Select from database?".format(an.analysis_type)):
                    return self._get_blank(an.analysis_type)
                else:
                    return
            else:
                pa = aruns[ind - 1]
#                print pa, pa.analysis_type, btypes
                if not pa.analysis_type in btypes or pa.skip:
                    if self.confirmation_dialog("First {} not preceeded by a blank. Select from database?".format(an.analysis_type)):
                        return self._get_blank(an.analysis_type)
                    else:
                        return

        return True

    def _do_automated_run(self, arun):
        def isAlive():
            if not self.isAlive():
                self.err_message = 'User quit'
                return False
            else:
                return True

        if not arun.start():
            self.err_message = 'Monitor failed to start'
            return

        if not isAlive():
            return

        if arun.extraction_script:
            if not arun.do_extraction():
                self._alive = False

        if not isAlive():
            return

        if arun.measurement_script:
            self.measuring = True
            if not arun.do_measurement():
                self._alive = False
            self.measuring = False

        if not isAlive():
            return

        if arun.post_measurement_script:
            if not arun.do_post_measurement():
                if not arun.state == 'truncate':
                    self._alive = False

        arun.finish()
        self.increment_nruns_finished()

        if arun.state == 'truncate':
            fstate = 'truncated'
        else:
            arun.state = 'success'
            fstate = 'finished'

        self.info('Automated run {} {}'.format(arun.runid, fstate))

    def _end_runs(self):
        self._last_ran = None
        self.stats.stop_timer()

    def _get_all_automated_runs(self):
        ans = super(ExperimentExecutor, self)._get_all_automated_runs()

        startid = 0
        exp = self.experiment_queue
        if exp and exp._cached_runs:
            try:
                startid = exp._cached_runs.index(self._last_ran) + 1
            except ValueError:
                pass

        return ans[startid:]

    def _reload_from_disk(self):
        super(ExperimentExecutor, self)._reload_from_disk()
        self._update_stats()

    def _recall_run(self):
        selected = self.selected
        if selected and self.recall_enabled:
            selected = selected[-1]
            db = self.db
            # recall the analysis and display
            db.selector.open_record(selected.uuid)

    def _edit_run(self):
        selected = self.selected
        self.save_enabled = False
        if self.edit_enabled and selected:
            base_run = selected[0]
            ae = AutomatedRunFactory()
            ae.load_from_run(base_run)

#            ae = AutomatedRunEditor(run=selected[-1])
            info = ae.edit_traits(kind='livemodal', view='edit_view')
            if info.result:
                ae.commit_changes(selected)
                self._update()
                self.stats.calculate()
                self.new_run_gen_needed = True
                self.save_enabled = True

#    def _load_experiment_queue_hook(self):
#        self.executable = all([ei.executable for ei in self.experiment_queues])

#===============================================================================
# handlers
#===============================================================================
    def _save_button_fired(self):
        self.save()

    def _save_as_button_fired(self):
        self.save_as()

#     def _experiment_queue_changed(self):
#         if self.experiment_queue:
#             nonfound = self._check_for_managers(self.experiment_queue)
#             if nonfound:
#                 self.warning_dialog('Could not find managers {}'.format(','.join(nonfound)))

    def _resume_button_fired(self):
        self.resume_runs = True

    def _dclicked_changed(self):
        self._recall_run()

    def _recall_run_fired(self):
        self._recall_run()

    def _right_clicked_fired(self):
        self._edit_run()

    def _edit_run_fired(self):
        self._edit_run()

    def _selected_changed(self):
        sel = self.selected
        if sel:
            if len(sel) == 1:
                self.stats.calculate_at(sel[-1])
                self.stats.calculate()
#            self.experiment_queue.selected = sel#[self.selected]

#    def _execute_button_fired(self):
#        self._execute()

    def _truncate_button_fired(self):
        self.experiment_queue.truncate_run(self.truncate_style)

    def _show_sample_map_fired(self):

        lm = self.experiment_queue.sample_map
        if lm is None:
            self.warning_dialog('No Tray map is set. Add "tray: <name_of_tray>" to ExperimentSet file')
        elif lm.ui:
            lm.ui.control.Raise()
        else:
            self.open_view(lm)

#    def traits_view(self):
#        editor = myTabularEditor(adapter=ExecuteAutomatedRunAdapter(),
#                                 dclicked='dclicked',
#                                 right_clicked='right_clicked',
#                                 selected='selected',
#                                 editable=False,
#                                 auto_resize=True,
#                                 multi_select=True,
#                                 auto_update=True,
#                                 scroll_to_bottom=False
#                                 )
#
#        tb = HGroup(
#                    Item('resume_button', enabled_when='object.delaying_between_runs', show_label=False),
#                    Item('delay_between_runs_readback',
#                         label='Delay Countdown',
#                         style='readonly', format_str='%i',
#                         width= -50),
#
#                    spring,
#                    Item('show_sample_map', show_label=False,
#                         enabled_when='object.experiment_queue.sample_map'
#                         ),
#                    spring,
#                    Item('end_at_run_completion'),
#                    Item('truncate_button', show_label=False,
#                         enabled_when='object.measuring'),
#                    Item('truncate_style', show_label=False,
#                         enabled_when='object.measuring'),
#                    self._button_factory('execute_button',
#                                             label='execute_label',
#                                             enabled='executable',
#                                             ))
#        sel_grp = Item('set_selector', show_label=False, style='custom')
#        exc_grp = Group(tb,
#                        HGroup(sel_grp,
# #                               Item('object.experiment_queue.stats',
#                               Item('stats',
#                                   style='custom'),
#                             spring,
#                             Item('info_display',
#                                  style='custom'),
#                               show_labels=False,
#                              ),
#                       show_labels=False,
#                       show_border=True,
#                       label='Execute')
#        v = View(
# #                 sel_grp,
#                 exc_grp,
#                 HGroup(
#                        Item('object.experiment_queue.mass_spectrometer', style='readonly'),
#                        Item('object.experiment_queue.extract_device', style='readonly'),
#                        Item('object.experiment_queue.tray', style='readonly')
#                        ),
#                 Item('object.experiment_queue.automated_runs',
#                      style='custom',
#                      show_label=False,
#                      editor=editor
#                      ),
#                 HGroup(Item('recall_run', enabled_when='recall_enabled'),
#                        Item('edit_run', enabled_when='edit_enabled'),
#                        Item('save_button', enabled_when='save_enabled'),
#                        Item('save_as_button'),
#                        show_labels=False),
#                 statusbar='statusbar',
#                 width=1150,
#                 height=800,
#                 resizable=True,
#                 title=self.title,
#                 handler=self.handler_klass,
#                 )
#        return v

#===============================================================================
# property get/set
#===============================================================================
    def _get_execute_label(self):
        return 'Start' if not self._alive else 'Stop'

    def _get_edit_enabled(self):
        if self.selected:
            states = [ri.state == 'not run' for ri in self.selected]
            return all(states)

    def _get_recall_enabled(self):
        if self.selected:
            if len(self.selected) == 1:
                return self.selected[0].state == 'success'
#===============================================================================
# defaults
#===============================================================================
    def _massspec_importer_default(self):
        msdb = MassSpecDatabaseImporter()
        return msdb

#    def _experiment_set_default(self):
#        return ExperimentSet(db=self.db)
#
    def _info_display_default(self):
        return DisplayController(
                                 bg_color='black',
                                 default_color='limegreen'
                                 )

#    def _set_selector_default(self):
#        s = SetSelector(
#                        experiment_manager=self,
#                        # experiment_sets=self.experiment_sets,
#                        editable=False
#                        )
#
#        return s

    def _monitor_factory(self):
        mon = None
        isok = True
        self.debug('mode={}'.format(self.mode))
        if self.mode == 'client':
            ip = InitializationParser()
            exp = ip.get_plugin('Experiment', category='general')
            monitor = exp.find('monitor')
            host, port, kind = None, None, None

            if monitor is not None:
                comms = monitor.find('communications')
                host = comms.find('host')
                port = comms.find('port')
                kind = comms.find('kind')

                if host is not None:
                    host = host.text  # if host else 'localhost'
                if port is not None:
                    port = int(port.text)  # if port else 1061
                if kind is not None:
                    kind = kind.text

                mon = RemoteAutomatedRunMonitor(host, port, kind, name=monitor.text.strip())
        else:
            mon = AutomatedRunMonitor()

        if mon is not None:
#        mon.configuration_dir_name = paths.monitors_dir
            isok = mon.load()

        return mon, isok
    def _pyscript_runner_default(self):
        if self.mode == 'client':
#            em = self.extraction_line_manager
            ip = InitializationParser()
            elm = ip.get_plugin('Experiment', category='general')
            runner = elm.find('runner')
            host, port, kind = None, None, None

            if runner is not None:
                comms = runner.find('communications')
                host = comms.find('host')
                port = comms.find('port')
                kind = comms.find('kind')

            if host is not None:
                host = host.text  # if host else 'localhost'
            if port is not None:
                port = int(port.text)  # if port else 1061
            if kind is not None:
                kind = kind.text  # if kind else 'udp'

            runner = RemotePyScriptRunner(host, port, kind)
        else:
            runner = PyScriptRunner()

        return runner
#============= EOF =============================================
#        # bootstrap the extraction script and measurement script
#        if not arun.extraction_script:
#            self.err_message = 'Invalid runscript {}'.format(arun.script_info.extraction_script_name)
# #            self.err_message = 'Invalid runscript {extraction_line_script}'.format(**arun.configuration)
#            return
# #        else:
# #            arun.extraction_script.syntax_checked = True
#
#        if not arun.measurement_script:
#            self.err_message = 'Invalid measurement_script {}'.format(arun.script_info.measurement_script_name)
#            return
#        else:
#            arun.measurement_script.syntax_checked = True

#        if not arun.post_measurement_script:
#            self.err_message = 'Invalid post_measurement_script {post_measurement_script}'.format(**arun.configuration)
#            return
#        else:
#            arun.post_measurement_script.syntax_checked = True

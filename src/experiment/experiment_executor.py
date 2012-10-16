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
    Instance, Str, DelegatesTo
from traitsui.api import View, Item, HGroup, Group, VGroup, spring
#============= standard library imports ========================
#============= local library imports  ==========================
#from src.loggable import Loggable
from src.experiment.automated_run_tabular_adapter import AutomatedRunAdapter
from src.traits_editors.tabular_editor import myTabularEditor
from src.experiment.experiment_manager import ExperimentManager
from src.managers.manager import Manager
from src.pyscripts.pyscript_runner import PyScriptRunner, RemotePyScriptRunner
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.data_processing.mass_spec_database_importer import MassSpecDatabaseImporter
from src.repo.repository import Repository, FTPRepository
from src.displays.rich_text_display import RichTextDisplay
from src.paths import paths
from threading import Thread
import time
from src.helpers.parsers.initialization_parser import InitializationParser
from apptools.preferences.preference_binding import bind_preference


class ExperimentExecutor(ExperimentManager):
    spectrometer_manager = Instance(Manager)
    extraction_line_manager = Instance(Manager)
    ion_optics_manager = Instance(Manager)
    massspec_importer = Instance(MassSpecDatabaseImporter)
    repository = Instance(Repository)
    info_display = Instance(RichTextDisplay)
    pyscript_runner = Instance(PyScriptRunner)
    data_manager = Instance(H5DataManager, ())

    end_at_run_completion = Bool(False)
    delay_between_runs_readback = Float

    show_lab_map = Button
    execute_button = Event
    execute_label = Property(depends_on='_alive')
    truncate_button = Button('Truncate')
    truncate_style = Enum('Immediate', 'Quick', 'Next Integration')
    '''
        immediate 0= is the standard truncation, measure_iteration stopped at current step and measurement_script truncated
        quick     1= the current measure_iteration is truncated and a quick baseline is collected, peak center?
        next_int. 2= same as setting ncounts to < current step. measure_iteration is truncated but script continues
    '''

    _alive = Bool(False)
    _last_ran = None
    _prev_baselines = Dict
    err_message = None

    repo_kind = Str
    db_kind = Str
    username = Str

    mode = 'normal'

    measuring = DelegatesTo('experiment_set')
    def isAlive(self):
        return self._alive

    def info(self, msg, *args, **kw):
        super(ExperimentManager, self).info(msg, *args, **kw)
        if self.info_display:
            self.info_display.add_text(msg, color='yellow')

    def bind_preferences(self):
        super(ExperimentExecutor, self).bind_preferences()

        prefid = 'pychron.experiment'
        bind_preference(self, 'repo_kind', '{}.repo_kind'.format(prefid))

        if self.repo_kind == 'FTP':
            bind_preference(self.repository, 'host', '{}.ftp_host'.format(prefid))
            bind_preference(self.repository, 'username', '{}.ftp_username'.format(prefid))
            bind_preference(self.repository, 'password', '{}.ftp_password'.format(prefid))
            bind_preference(self.repository, 'remote', '{}.repo_root'.format(prefid))

        bind_preference(self.massspec_importer.db, 'name', '{}.massspec_dbname'.format(prefid))
        bind_preference(self.massspec_importer.db, 'host', '{}.massspec_host'.format(prefid))
        bind_preference(self.massspec_importer.db, 'username', '{}.massspec_username'.format(prefid))
        bind_preference(self.massspec_importer.db, 'password', '{}.massspec_password'.format(prefid))


#===============================================================================
# private
#===============================================================================
    def _execute(self):
        if self.isAlive():
            if self.confirmation_dialog('Cancel {} in Progress'.format(self.title),
                                     title='Confirm Cancel'
                                     ):
                self._alive = False
                arun = self.experiment_set.current_run
                if arun:
                    arun.cancel()

        else:

            t = Thread(target=self._execute_experiment_sets)
            t.start()

    def _execute_experiment_sets(self):
        self.end_at_run_completion = False
        if not self.massspec_importer.db.connect():
            if not self.confirmation_dialog('Not connected to a Mass Spec database. Do you want to continue with pychron only?'):
                self._alive = False
                return

        exp = self.experiment_sets[0]
        #check for a preceeding blank
        if not self._has_preceeding_blank_or_background(exp):
            self.info('experiment canceled because no blank or background was configured')
            self._alive = False
            return

        if self.mode == 'client':
#            em = self.extraction_line_manager
            ip = InitializationParser()
            elm = ip.get_plugin('ExtractionLine', category='hardware')
            runner = elm.find('runner')
            host, port, kind = None, None, None
            if runner:
                comms = runner.find('communications')
                host = comms.find('host')
                port = comms.find('port')
                kind = comms.find('kind')

            host = host if host else 'localhost'
            port = port if port else 1061
            kind = kind if kind else 'udp'

            runner = RemotePyScriptRunner(host, port, kind)
        else:
            runner = PyScriptRunner()

        self.pyscript_runner = runner

        self._alive = True
        self.set_selector.selected_index = -2
        rc = 0
        ec = 0
        for i, exp in enumerate(self.experiment_sets):
            self.experiment_set = exp
            t = self._execute_automated_runs(i + 1, exp)
            if t:
                rc += t
                ec += 1
        self.info('Executed {:n} sets. total runs={:n}'.format(rc, ec))
        self._alive = False

    def _execute_automated_runs(self, iexp, exp):

        self.info('Starting automated runs set= Set{}'.format(iexp))

        self.set_selector.selected_index = iexp - 1
        exp._alive = True
        exp.reset_stats()
        self.db.reset()
        exp.save_to_db()

        rgen, nruns = exp.new_runs_generator(self._last_ran)
        cnt = 0
        totalcnt = 0
        while self.isAlive():
            self.db.reset()

#            if the user is editing the experiment set dont continue?
            if self.editing_signal:
                self.editing_signal.wait()

            #check for mods
            if self.check_for_mods():
                cnt = 0
                self.info('the experiment set was modified')
                #load the exp and get an new rgen
#                tt = self._extract_experiment_text(exp.path, iexp)
#                exp.load_automated_runs(text=tt)
#                ts = self._parse_experiment_file(exp.path)
#                for ti, ei in zip(self.experiment_sets, ts):
#                    ei.load_automated_runs(text=ti)
                self._reload_from_disk()
                rgen, nruns = exp.new_runs_generator(self._last_ran)

            if self.isAlive() and \
                    cnt < nruns and \
                            not cnt == 0:
                delay = exp.delay_between_analyses
                self.delay_between_runs_readback = delay
                self.info('Delay between runs {}'.format(delay))

                #delay between runs
                st = time.time()
                while time.time() - st < delay:
                    if not self.isAlive():
                        break
                    time.sleep(0.5)
                    self.delay_between_runs_readback -= 0.5

            try:
                t, run = self._launch_run(rgen, cnt)
            except StopIteration:
                break

            self._last_ran = run

            if run.overlap:
                self.info('overlaping')
                run.wait_for_overlap()
            else:
                t.join()

            cnt += 1
            totalcnt += 1
            if self.end_at_run_completion:
                break

        if self.err_message:
            '''
                set last_run to None is this run wasnt successfully
                experiment set will restart at last successful run
            '''
            self._last_ran = None
            run.state = 'fail'
            self.warning('automated runs did not complete successfully')
            self.warning('error: {}'.format(self.err_message))

        self._end_runs()
        self.info('Set{}. Automated runs ended at {}, runs executed={}'.format(iexp + 1, run.runid, totalcnt))
        return totalcnt

    def _launch_run(self, runsgen, cnt):
        repo = self.repository
        dm = self.data_manager
        runner = self.pyscript_runner

        run = runsgen.next()
        self._setup_automated_run(cnt, run, repo, dm, runner)

        run.pre_extraction_save()
        ta = Thread(name=run.runid,
                   target=self._do_automated_run,
                   args=(run,)
                   )
        ta.start()
        return ta, run

    def _setup_automated_run(self, i, arun, repo, dm, runner):
        exp = self.experiment_set
        exp.current_run = arun

        arun.index = i
        arun.experiment_name = exp.name
        arun.experiment_manager = self
        arun.spectrometer_manager = self.spectrometer_manager
        arun.extraction_line_manager = self.extraction_line_manager
        arun.ion_optics_manager = self.ion_optics_manager
        arun.data_manager = dm
        arun.db = self.db
        arun.massspec_importer = self.massspec_importer
        arun.runner = runner
        arun.integration_time = 1.04
        arun.repository = repo
        arun.info_display = self.info_display
        arun.username = self.username

    def _has_preceeding_blank_or_background(self, exp):
        if exp.automated_runs[0].analysis_type not in ['blank', 'background']:
            #the experiment set doesnt start with a blank
            #ask user for preceeding blank
            return False
        return True

    def _do_automated_run(self, arun):
        def isAlive():
            if not self.isAlive():
                self.err_message = 'User quit'
                return False
            else:
                return True

        arun.start()

        #bootstrap the extraction script and measurement script
        if not arun.extraction_script:
            self.err_message = 'Invalid runscript {extraction_line_script}'.format(**arun.configuration)
            return
        else:
            arun.extraction_script.syntax_checked = True

        if not arun.measurement_script:
            self.err_message = 'Invalid measurement_script {measurement_script}'.format(**arun.configuration)
            return
        else:
            arun.measurement_script.syntax_checked = True

        if not arun.post_measurement_script:
            self.err_message = 'Invalid post_measurement_script {post_measurement_script}'.format(**arun.configuration)
            return
        else:
            arun.post_measurement_script.syntax_checked = True

        if not isAlive():
            return

        arun.state = 'extraction'
        if not arun.do_extraction():
            self._alive = False

        if not isAlive():
            return

        #do_equilibration
        evt = arun.do_equilibration()
        if evt:
            self.info('waiting for the inlet to open')
            evt.wait()
            self.info('inlet opened')

        if not isAlive():
            return

        arun.state = 'measurement'
        if not arun.do_measurement():
            self._alive = False

        if not isAlive():
            return

        if not arun.do_post_measurement():
            self._alive = False


        arun.finish()
        self.experiment_set.increment_nruns_finished()

        if arun.state == 'truncate':
            fstate = 'truncated'
        else:
            arun.state = 'success'
            fstate = 'finished'
#        fstate = 'truncated' if arun.state == 'truncate' else 'finished'
        self.info('Automated run {} {}'.format(arun.runid, fstate))

    def _end_runs(self):
        self._last_ran = None
#        self._alive = False
        exp = self.experiment_set
#        exp.stats.nruns_finished = len(exp.automated_runs)
        exp.stop_stats_timer()

#===============================================================================
# handlers
#===============================================================================
    def _execute_button_fired(self):
        self._execute()

    def _truncate_button_fired(self):
        self.experiment_set.truncate_run(self.truncate_style)

    def _show_lab_map_fired(self):

        lm = self.experiment_set.lab_map
        if lm is None:
            self.warning_dialog('No Tray map is set. Add "tray: <name_of_tray>" to ExperimentSet file')
        elif lm.ui:
            lm.ui.control.Raise()
        else:
            self.open_view(lm)

    def traits_view(self):
        editor = myTabularEditor(adapter=AutomatedRunAdapter(),
#                             update=update,
                             right_clicked='object.right_clicked',
                             selected='object.selected',
#                             refresh='object.refresh',
#                             activated_row='object.activated_row',
                             auto_resize=True,
                             multi_select=True,
                             auto_update=True,
                             scroll_to_bottom=False
                            )
#        editor = self.experiment_set._automated_run_editor(update='object.experiment_set.current_run.update')
        tb = HGroup(
                    Item('delay_between_runs_readback',
                         label='Delay Countdown',
                         style='readonly', format_str='%i',
                         width= -50),
                    spring,
                    Item('show_lab_map', show_label=False),
                    spring,
                    Item('end_at_run_completion'),
                    Item('truncate_button', show_label=False,
                         enabled_when='object.measuring'),
                    Item('truncate_style', show_label=False,
                         enabled_when='object.measuring'),
                    self._button_factory('execute_button',
                                             label='execute_label',
                                             enabled='object.experiment_set.executable',
                                             ))
        sel_grp = Item('set_selector', show_label=False, style='custom')
        exc_grp = Group(tb,
                        HGroup(sel_grp,
                               Item('object.experiment_set.stats',
                                   style='custom'),
                             spring,
                             Item('info_display',
                                  style='custom'),
                               show_labels=False,
                              ),
                       show_labels=False,
                       show_border=True,
                       label='Execute')
        v = View(
#                 sel_grp,
                 exc_grp,
                 Item('object.experiment_set.automated_runs',
                      style='custom',
                      show_label=False,
                      editor=editor
                      ),
                 width=1150,
                 height=750,
                 resizable=True,
                 title=self.experiment_set.name,
                 handler=self.handler_klass,
                 )
        return v

#===============================================================================
# property get/set
#===============================================================================
    def _get_execute_label(self):
        return 'Start' if not self._alive else 'Stop'
#===============================================================================
# defaults
#===============================================================================
    def _massspec_importer_default(self):
        msdb = MassSpecDatabaseImporter()
        return msdb



#    def _experiment_set_default(self):
#        return ExperimentSet(db=self.db)

    def _info_display_default(self):
        return  RichTextDisplay(height=300,
                                width=575,
                                default_size=12,
                                bg_color='black',
                                default_color='limegreen')

    def _repository_default(self):
        if self.repo_kind == 'local':
            klass = Repository
        else:
            klass = FTPRepository

        repo = klass()
        #use local data dir
        repo.root = paths.isotope_dir
        return repo
#============= EOF =============================================

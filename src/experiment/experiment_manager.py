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
from traits.api import Instance, Button, Float, Str, \
    DelegatesTo, Bool, Property, Event, Dict
from traitsui.api import View, Item, Group, VGroup, HGroup, spring
from traitsui.menu import Action
from pyface.timer.do_later import do_later
from apptools.preferences.preference_binding import bind_preference
#import apptools.sweet_pickle as pickle
#============= standard library imports ========================
from threading import Thread
import time

#============= local library imports  ==========================
from src.managers.manager import Manager, SaveableManagerHandler
from src.experiment.experiment_set import ExperimentSet

from src.paths import paths
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.data_processing.mass_spec_database_importer import MassSpecDatabaseImporter
from src.pyscripts.pyscript_runner import PyScriptRunner, RemotePyScriptRunner
from globals import globalv
from src.displays.rich_text_display import RichTextDisplay
from src.repo.repository import Repository, FTPRepository
from src.spectrometer.molecular_weights import MOLECULAR_WEIGHTS


class ExperimentManagerHandler(SaveableManagerHandler):
    def object_experiment_set_changed(self, info):
        if info.initialized:
            info.ui.title = info.object.title


class ExperimentManager(Manager):
    '''
        manager to handle running multiple analyses
    '''
    spectrometer_manager = Instance(Manager)
    extraction_line_manager = Instance(Manager)
    ion_optics_manager = Instance(Manager)
#    laser_manager = Instance(Manager)

    data_manager = Instance(H5DataManager, ())

    experiment_config = None

    experiment_set = Instance(ExperimentSet)

    pyscript_runner = Instance(PyScriptRunner)

    db = Instance(IsotopeAdapter)
    massspec_importer = Instance(MassSpecDatabaseImporter)
    info_display = Instance(RichTextDisplay)
    _dac_peak_center = Float
    _dac_baseline = Float

    mode = 'normal'

    test2 = Button

    _alive = Bool(False)
    execute_button = Event
    execute_label = Property(depends_on='_alive')

#    open_button = Button
#    save_button = Button
#    default_save_directory = Str

    title = DelegatesTo('experiment_set', prefix='name')

    dirty = DelegatesTo('experiment_set')
    err_message = None

    repository = Instance(Repository)
    repo_kind = Str
    db_kind = Str

    username = Str
    end_at_run_completion = Bool(False)
    delay_between_runs_readback = Float
    editing_signal = None

    _last_ran = None
    _prev_baselines = Dict

    def __init__(self, *args, **kw):
        super(ExperimentManager, self).__init__(*args, **kw)
        self.bind_preferences()
        self.populate_default_tables()

#        self.info_display.clear()

#    def opened(self):
#        pass
#        do_later(self.test_connections)
#        self.test_connections()
#        self.populate_default_tables()

    def test_connections(self):
        if not self.db.connect():
            self.warning_dialog('Failed connecting to database. {}'.format(self.db.url))
            return

        if not self.repository.connect():
            self.warning_dialog('Failed connecting to repository {}'.format(self.repository.url))
            return

        return True

    def populate_default_tables(self):
        db = self.db
        if self.db:
            db.connect()
            for name, mass in MOLECULAR_WEIGHTS.iteritems():
                db.add_molecular_weight(name, mass)

            for at in ['blank', 'air', 'cocktail', 'background', 'unknown']:
                db.add_analysis_type(at)

            for mi in ['obama', 'jan']:
                db.add_mass_spectrometer(mi)

            db.commit()

    def bind_preferences(self):
        if self.db is None:
            self.db = self._db_factory()
        prefid = 'pychron.experiment'

        bind_preference(self, 'repo_kind', '{}.repo_kind'.format(prefid))
        bind_preference(self.db, 'kind', '{}.db_kind'.format(prefid))
        bind_preference(self, 'username', '{}.username'.format(prefid))

        if self.repo_kind == 'FTP':
            bind_preference(self.repository, 'host', '{}.ftp_host'.format(prefid))
            bind_preference(self.repository, 'username', '{}.ftp_username'.format(prefid))
            bind_preference(self.repository, 'password', '{}.ftp_password'.format(prefid))
            bind_preference(self.repository, 'remote', '{}.repo_root'.format(prefid))

        if self.db.kind == 'mysql':
            bind_preference(self.db, 'host', '{}.db_host'.format(prefid))
            bind_preference(self.db, 'username', '{}.db_username'.format(prefid))
            bind_preference(self.db, 'password', '{}.db_password'.format(prefid))

        bind_preference(self.db, 'name', '{}.db_name'.format(prefid))
#        if not self.db.connect():
#            self.warning_dialog('Not Connected to Database {}'.format(self.db.url))
#            self.db = None

    def info(self, msg, *args, **kw):
        super(ExperimentManager, self).info(msg, *args, **kw)
        if self.info_display:
            do_later(self.info_display.add_text, msg, color='yellow')

    def save(self):
        self.save_experiment_set()

    def save_as(self):
        self.save_as_experiment_set()

    def open_recent(self):
        db = self.db
        if db.connect():
            db.reset()
            selector = db.selector_factory(style='simple')

            selector.set_data_manager(kind=self.repo_kind,
                                      repository=self.repository,
                                      workspace_root=paths.default_workspace)


            self.open_view(selector)

#    def get_spectrometer_manager(self):
#        sm = self.spectrometer_manager
#        if sm is None:
#            protocol = 'src.managers.spectrometer_manager.SpectrometerManager'
#            if self.application is not None:
#                sm = self.spectrometer_manager = self.application.get_service(protocol)
#
#        return sm

    def end_runs(self):

        self._alive = False
        exp = self.experiment_set
        exp.stats.nruns_finished = len(exp.automated_runs)
        exp.stop_stats_timer()

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
        arun._debug = globalv.experiment_debug
        arun.info_display = self.info_display

        arun.username = self.username

#        arun.preceeding_blank=
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

    def do_automated_runs(self):
        self.end_at_run_completion = False
        #connect to massspec database warning if not

        #explicitly set db connection info here for now
        self.massspec_importer.db.kind = 'mysql'
#        self.massspec_importer.db.host = '129.138.12.131'
        self.massspec_importer.db.username = 'root'
        self.massspec_importer.db.password = 'Argon'
        self.massspec_importer.db.name = 'massspecdata_test'

        if not self.massspec_importer.db.connect():
            if not self.confirmation_dialog('Not connected to a Mass Spec database. Do you want to continue with pychron only?'):
                self._alive = False
                return

        #check for a preceeding blank
        if not self._has_preceeding_blank_or_background():
            self.info('experiment canceled because no blank was found of configured')
            self._alive = False
            return

        self.info('start automated runs')

        if self.mode == 'client':
            runner = RemotePyScriptRunner('localhost', 1061, 'udp')
#            runner = RemotePyScriptRunner('129.138.12.153', 1061, 'udp')
        else:
            runner = PyScriptRunner()

        self.pyscript_runner = runner
        self._alive = True

        exp = self.experiment_set
        exp.reset_stats()

#        dm = H5DataManager()
#        self.data_manager = dm
#        repo = self.repository

        self.db.reset()
        exp.save_to_db()

        rgen, nruns = exp.new_runs_generator()

        cnt = 0
        totalcnt = 0
        while self.isAlive():


#            if the user is editing the experiment set dont continue?
            if self.editing_signal:
                self.editing_signal.wait()

            #check for mods
            if exp.check_for_mods():
                cnt = 0
                self.info('the experiment set was modified')
                #load the exp and get an new rgen
                exp.load_automated_runs()
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
#            if run.analysis_type == 'unknown':
#                self._last_ran = run

            if run.overlap:
                self.info('overlaping')
                run.wait_for_overlap()
            else:
                t.join()

            if self.end_at_run_completion:
                break


            cnt += 1
            totalcnt += 1

        if self.err_message:
            run.state = 'fail'
            self.warning('automated runs did not complete successfully')
            self.warning('error: {}'.format(self.err_message))
        else:
            exp.stop_stats_timer()
            self.end_runs()

        self.info('automated runs ended at {}, runs executed={}'.format(run.runid, totalcnt))

    def _has_preceeding_blank_or_background(self):
        if self.experiment_set.automated_runs[0].analysis_type not in ['blank', 'background']:
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

        self.db.reset()
        arun.start()

        #bootstrap the extraction script and measurement script
        if not arun.extraction_script:
            self.err_message = 'Invalid runscript {extraction_line_script}'.format(**arun.configuration)
            return

        if not arun.measurement_script:
            self.err_message = 'Invalid measurement_script {measurement_script}'.format(**arun.configuration)
            return

        if not arun.post_measurement_script:
            self.err_message = 'Invalid post_measurement_script {post_measurement_script}'.format(**arun.configuration)
            return

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

        arun.state = 'success'
        self.info('Automated run {} finished'.format(arun.runid))
        arun.finish()

    def isAlive(self):
        return self._alive

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
            self._alive = True
#        target = self.do_experiment
        #target = self.spectrometer_manager.deflection_calibration
            t = Thread(target=self.do_automated_runs)
            t.start()

    def new_experiment_set(self):
#        self.experiment_set = ExperimentSet()
        exp = self._experiment_set_factory()
        arun = exp.automated_run_factory()
        exp.automated_run = arun
#        exp.automated_runs.append(arun)
        self.experiment_set = exp

#    def close(self, isok):
#        self.dirty_save_as = False
#===============================================================================
# persistence
#===============================================================================
    def load_experiment_set(self, path=None, edit=False):
#        self.bind_preferences()

        #make sure we have a database connection
        if not self.test_connections():
            return

        self.info_display.clear()
        self.experiment_set = None
        if path is None:
            path = self.open_file_dialog(default_directory=paths.experiment_dir)

        if path is not None:
            exp = self._experiment_set_factory(path=path)
            exp.isediting = edit
#            exp = ExperimentSet(path=path)
#            try:

            if exp.load_automated_runs():
                self.experiment_set = exp
                self.experiment_set.automated_run = exp.automated_runs[-1]
#                exp._update_aliquots()
                return True

#            except Exception, e:
#
#                import traceback
#                traceback.print_stack()

#                self.warning_dialog('Invalid Experiment file {}. Error- {}'.format(path, e))


#            except Exception:
#                self.warning_dialog('Invalid experiment file {}'.format(path))
    def save_as_experiment_set(self):
        p = self.save_file_dialog(default_directory=paths.experiment_dir)
        self._dump_experiment_set(p)
        self.experiment_set.path = p
        self.experiment_set.dirty = False

    def save_experiment_set(self):
        p = self.experiment_set.path
        self._dump_experiment_set(p)
        self.experiment_set.dirty = False

    def _dump_experiment_set(self, p):
#        if not p:
#            p = '/Users/ross/Pychrondata_experiment/experiments/foo.txt'
#            p = self.save_file_dialog(default_directory=paths.experiment_dir)
        if not p:
            return

        self.info('saving experiment to {}'.format(p))
        self.experiment_set.dirty = False

        header = ['identifier', 'extraction', 'measurement']
        with open(p, 'wb') as f:
            writeline = lambda m: f.write(m + '\n')
            tab = lambda l: writeline('\t'.join(map(str, l)))

            #write metadata
            writeline(self.experiment_set.name)
            writeline('#' + '=' * 80)
            tab(header)
            for arun in self.experiment_set.automated_runs:
                tab([arun.identifier, arun.measurement_script.name, arun.extraction_script.name])

#===============================================================================
# handlers
#===============================================================================
    def _execute_button_fired(self):
        self._execute()
#    def _open_button_fired(self):
#        p = '/Users/ross/Pychrondata_experiment/experiments/foo.txt'
#        self.load_experiment_set(path=p)
#
##        self._load_experiment(path=None)
#    def _save_button_fired(self):
##        p = '/Users/ross/Pychrondata_experiment/experiments/foo.exp'
#        self._dump_experiment_set()
##        self._dump_experiment(path=None)
#
#    def _save_as_button_fired(self):
#        self._dump_experiment_set()

#    def _test2_fired(self):
#        sm = self.get_spectrometer_manager()
#        print sm.spectrometer_microcontroller
#        self.analyze_data()
#        dm = H5DataManager()
#
#        path = '/Users/ross/Pychrondata/data/automated_runs/B-01-intensity015.hdf5'
#        dm.open_data(path)
#        t = dm.get_table('H1', 'signals')
#        print t
#        for r in t.iterrows():
#            print r['time'], r['value']
#        self.new_experiment()
#        self.execute()

#    @on_trait_change('experiment:automated_run:identifier')
#    def identifier_update(self, obj, name, old, new):
#        print name, old, new
#        if new:
#            if new == 'A':
#                self.experiment.ok_to_add = True
#            else:
#                #check db for this sample identifier
#                db = self.data_manager
#                sample = db.get_sample(dict(identifier=new))
#                if sample is not None:
#                    self.experiment.analysis.sample_data_record = sample
#                    self.experiment.ok_to_add = True
#        else:
#            self.experiment.ok_to_add = False
#===============================================================================
# views
#===============================================================================
    def execute_view(self):

        editor = self.experiment_set._automated_run_editor(update='object.experiment_set.current_run.update')

        tb = HGroup(
                    Item('delay_between_runs_readback',
                         label='Delay Countdown',
                         style='readonly', format_str='%i',
                         width= -50),
                    spring,
                    Item('end_at_run_completion'),
                    self._button_factory('execute_button',
                                             label='execute_label',
                                             enabled='object.experiment_set.executable',
                                             ))
        exc_grp = Group(tb,
                       HGroup(Item('object.experiment_set.stats',
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
                 exc_grp,
                 Item('object.experiment_set.automated_runs',
                      style='custom',
                      show_label=False,
                      editor=editor
                      ),
                 width=900,
                 height=700,
                 resizable=True,
                 title=self.experiment_set.name,
                 handler=self.handler_klass
                 )
        return v

    def traits_view(self):

        exc_grp = Group(
#                       Item('test2'),
#                       Item('open_button'),
#                       Item('save_button'),
                       Item('object.experiment_set.stats',
                            style='custom'),
                       show_labels=False,
                       show_border=True,
                       label='Execute')
        exp_grp = Group(
                       Item('experiment_set',
                       show_label=False, style='custom'),
                       show_border=True,
                       label='Experiment'
                )

        v = View(
                VGroup(exc_grp,
                       exp_grp),
                 resizable=True,
                 width=0.85,
                 height=0.75,
                 buttons=['OK', 'Cancel',
                          Action(name='Save', action='save', enabled_when='object.dirty'),
                          Action(name='Save As', action='save_as'),

                          ],
                 handler=ExperimentManagerHandler,
                 title=self.title
                 )
        return v

#    def execute_view(self):
#        return self.traits_view()
    def test_view(self):
        v = View('test')
        return v

#===============================================================================
# property get/set
#===============================================================================
    def _get_execute_label(self):
        return 'Start' if not self._alive else 'Stop'
#===============================================================================
# factories
#===============================================================================
    def _experiment_set_factory(self, **kw):
        return ExperimentSet(
                             db=self.db,
                             **kw)

#===============================================================================
# defaults
#===============================================================================
    def _default_save_directory_default(self):
        return paths.experiment_dir

    def _massspec_importer_default(self):
        msdb = MassSpecDatabaseImporter()
        return msdb

    def _db_default(self):
        return self._db_factory()

    def _db_factory(self):
        db = IsotopeAdapter()
        return db

    def _experiment_set_default(self):
        return ExperimentSet(db=self.db)

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

def main():
    paths.build('_experiment')
    from src.helpers.logger_setup import logging_setup

    logging_setup('experiment_manager')

    globalv.show_infos = False

#    s = SpectrometerManager()
#    s.bootstrap()
#    s.molecular_weight = 'Ar40'
#    ini = Initializer()
#    ini.add_initialization(dict(name = 'spectrometer_manager',
#                                manager = s
#                                ))
#    ini.run()

#    e = ExperimentManager(spectrometer_manager=s)
    e = ExperimentManager()

#    e.configure_traits(view='test_view')
#    e.analyze_data()
    e.configure_traits(view='execute_view')

def dum_run(r):
    print 'start ', r
    time.sleep(1)
    print 'finish   ', r
#    for i in range(5):


def test():

    runs = (ri for ri in range(4))
    while 1:
        try:
            run = runs.next()
        except StopIteration:
            break
        t = Thread(target=dum_run, args=(run,))
        t.start()
        time.sleep(1.8)

if __name__ == '__main__':
    main()
#    test()
#============= EOF ====================================

#===============================================================================
# ##analysis code 
#===============================================================================
#    def analyze_data(self):
#        '''
#            provide a list of run numbers
#            get intercept and error for ni points
#            correct the data for baseline and blank
#            calculate blank intercept using nj points
#            calculate intercept
#            calculate mswd 
#        '''
##===============================================================================
## gather data
##===============================================================================
#        runlist = ['B-01', 'A-01', 'A-02', 'A-03', 'A-04', 'B-02',
#                   'A-05', 'A-06', 'A-07', 'B-03'
#                   ]
#
#        blanks, airs, unknowns, b_bs, a_bs, u_bs = self.gather_data(runlist)
##        self.permuate_data(blanks, airs, a_bs, b_bs)
#
#        self.plot_air_series(blanks, airs, b_bs, a_bs)
#
#    def plot_air_series(self, blanks, airs,
#                        blank_baselines,
#                        air_baselines):
#        g = StackedGraph()
##        g.new_plot(xtitle='npts',
##                   ytitle='40/36')
##        g.new_plot(ytitle='40/36 err')
#        g.new_plot(ytitle='Population SD',
#                   show_legend=True
#                   )
#
##        xs = [100, 200, 500, 1000, 2000]
#        for si, fit in enumerate([
#                                  ('linear', 1), ('parabolic', 2),
#                                  ('cubic', 3),
#                                  ('exponential', 'quick_exponential')
#                                  ]):
#            self._plot_air_series(g, fit, si, blanks, airs, blank_baselines, air_baselines)
#
#        g.set_y_limits(0, 1)
#        g.edit_traits()
#
#    def _plot_air_series(self, g, fit, si, blanks, airs, blank_baselines, air_baselines):
#        xs = range(100, 2000, 100)
#        name, fit = fit
#        cor_ratioss = [self.calculate_ratios(ni, fit, blanks, airs,
#                                             blank_baselines,
#                                   air_baselines,
#                                  )
#                     for ni in xs
#                     ]
#
#        n = len(airs['h1'])
##        scatter_args = dict(type='scatter', marker='circle',
##                         marker_size=1.75)
#        scatter_args = dict()
##        for i in range(n):
###            g.new_series(plotid=0, **scatter_args)
###            g.new_series(plotid=1, **scatter_args)
##            g.new_series(plotid=0)
##            g.new_series(plotid=1)
#
#        g.new_series(plotid=0, **scatter_args)
#
#        g.set_series_label(name, series=si)
#        for ci, xi in zip(cor_ratioss, xs):
##            print ci
#            ms, sds = zip(*[(i.nominal_value, i.std_dev()) for i in ci])
#            ms = array(ms)
#            sds = array(sds)
##            print SD
##            for si in range(n):
##                g.add_datum((xi, ms[si]), plotid=0, series=si)
##                g.add_datum((xi, sds[si]), plotid=1, series=si)
#
#            g.add_datum((xi, ms.std()), plotid=0, series=si)
#
##            g.new_series(xs, ms, type='scatter', plotid=0)
##            g.new_series(xs, sds, type='scatter', plotid=1)
#
#        g.set_x_limits(0, xs[-1] + 100)
#
#    def gather_data(self, runlist):
#        blanks = dict()
#        airs = dict()
#        unknowns = dict()
#        air_baselines = dict()
#        blank_baselines = dict()
#        unknown_baselines = dict()
#
#        for rid in runlist:
#            self.info('loading run {} signal file'.format(rid))
#            #open signal file
#            p = os.path.join(paths.data_dir,
#                            'automated_runs',
#                            'mswd_counting_experiment',
#                            '{}-intensity001.txt'.format(rid))
#            xs, h1s, cdds = loadtxt(p, unpack=True, delimiter=',',
#                        skiprows=int(2 / 3. * self.equilibration_time))
#
#            self.info('loading run {} baseline file'.format(rid))
#            #open baseline file
#            p = os.path.join(paths.data_dir,
#                             'automated_runs',
#                             'mswd_counting_experiment',
#                             '{}-baseline001.txt'.format(rid))
#            _xs_baseline, h1s_baseline, cdds_baseline = loadtxt(p,
#                                            unpack=True, delimiter=',')
#
#            #calculate baseline
#            h1_baseline = ufloat((h1s_baseline.mean(), h1s_baseline.std()))
#            cdd_baseline = ufloat((cdds_baseline.mean(), cdds_baseline.std()))
#
##===============================================================================
## 
##===============================================================================
##            h1_baseline = 0
##            cdd_baseline = 0
#
#            #if the sample is a blank add to blank list
#            if rid.startswith('B'):
#                int_dict = blanks
#                baselines = blank_baselines
#            elif rid.startswith('A'):
#                int_dict = airs
#                baselines = air_baselines
#            else:
#                int_dict = unknowns
#                baselines = unknown_baselines
#
#            for k, v, b in [('h1', (xs, h1s), h1_baseline),
#                            ('cdd', (xs, cdds), cdd_baseline)]:
#                try:
#                    int_dict[k].append(v)
#                except KeyError:
#                    int_dict[k] = [v]
#                try:
#                    baselines[k].append(b)
#                except KeyError:
#                    baselines[k] = [b]
#
#        return (blanks, airs, unknowns,
#                blank_baselines, air_baselines, unknown_baselines)
#
#    def permuate_data(self, blanks, airs, blank_baselines, air_baselines):
#
#        g = Graph()
#        g.new_plot(xtitle='npoints',
#                   ytitle='mswd',
#                   title='MSWD {}-Airs vs Counting Time'.format(len(airs['h1']))
#                   )
#        g.edit_traits()
#
#        s = 10
#        e = 2000
#        step = 10
#        nxs = arange(s, e, step)
#
#        mswds = [self._calculate_mswd(ni,
#                blanks, airs, blank_baselines, air_baselines) for ni in nxs]
#
#        g.new_series(nxs, mswds)
#        snxs = smooth(nxs)
#        smswds = smooth(mswds)
#        g.new_series(snxs, smswds)
#        g.add_horizontal_rule(1)
#
#        g.redraw()
#
#    def _calculate_mswd(self, ni, fit, blanks, airs,
#                         blank_baselines, air_baselines):
#
#        cor_ratios = self.calculate_ratios(ni, fit, blanks, airs,
#                                           blank_baselines, air_baselines)
#        verbose = False
#        if verbose:
#            self.info('40Ar/36Ar for npts {}'.format(ni))
#            self.info('average={} n={}'.format(cor_ratios.mean(),
#                                           cor_ratios.shape[0]
#                                           ))
#
#        x, errs = zip(*[(cr.nominal_value,
#                         cr.std_dev()) for cr in cor_ratios])
##
#        return calculate_mswd(x, errs)
#
#    def calculate_ratios(self, ni, fit, blanks, airs,
#                            blank_baselines,
#                            air_baselines):
#        permutate_blanks = False
#        if permutate_blanks:
#            ti = ni
#        else:
#            ti = -1
#
#        h1bs, cddbs = self._calculate_correct_intercept(fit, blanks, blank_baselines,
#                                                        dict(h1=0, cdd=0),
#                                                        truncate=ti)
#
#        h1bs, cddbs = h1bs.mean(), cddbs.mean()
##        h1bs, cddbs = 0, 0
##        print 'asdfas', len(airs['h1']), len(airs['cdd'])
##        print 'asdfas', len(air_baselines['h1']), len(air_baselines['cdd'])
#        cor_h1, cor_cdd = self._calculate_correct_intercept(fit,
#                                                            airs,
#                                                            air_baselines,
#                                                                dict(h1=h1bs,
#                                                                     cdd=cddbs
#                                                                     ),
#                                                            truncate=ni
#                                                            )
#
#        cor_ratios = cor_h1 / cor_cdd
#
#        return cor_ratios
#
#    def _calculate_correct_intercept(self, fit, signals, baselines,
#                                      blanks, truncate= -1):
#        cor_h1 = []
#        cor_cdd = []
#
#        from src.data_processing.regression.regressor import Regressor
#        r = Regressor()
#
#        for (xs, h1s), h1b, (xs2, cdds), cddb in zip(signals['h1'],
#                                               baselines['h1'],
#                                               signals['cdd'],
#                                               baselines['cdd']
#                                               ):
#            if fit == 'quick_exponential':
#                c, ce = r.quick_exponential(xs[:truncate], h1s[:truncate])
#                h1_int = ufloat((c[0],
#                                 ce[0]))
#
#                c, ce = r.quick_exponential(xs2[:truncate], cdds[:truncate])
#
#                cdd_int = ufloat((c[0],
#                               ce[0]))
#            else:
#                o = OLS(xs[:truncate], h1s[:truncate], fitdegree=fit)
#                h1_int = ufloat((o.get_coefficients()[fit],
#                                o.get_coefficient_standard_errors()[fit]))
#                o = OLS(xs2[:truncate], cdds[:truncate], fitdegree=fit)
#                cdd_int = ufloat((o.get_coefficients()[fit],
#                                o.get_coefficient_standard_errors()[fit]))
#
#            #apply baseline correction
#            h1_cor_int = h1_int - h1b
#            cdd_cor_int = cdd_int - cddb
#
#            #apply blank correction
#            h1_cor_int -= blanks['h1']
#            cdd_cor_int -= blanks['cdd']
#
#            cor_h1.append(h1_cor_int)
#            cor_cdd.append(cdd_cor_int)
#
#        return array(cor_h1), array(cor_cdd)



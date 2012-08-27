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
from traits.api import Instance, Button, Float, on_trait_change, Str, \
    DelegatesTo, Bool, Property, Event
from traitsui.api import View, Item, Group, VGroup
from traitsui.menu import Action
#import apptools.sweet_pickle as pickle
#============= standard library imports ========================
from threading import Thread
from threading import Event as TEvent
import os
import time

#============= local library imports  ==========================
from src.managers.manager import Manager, SaveableManagerHandler
from src.experiment.experiment_set import ExperimentSet

from src.paths import paths
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.helpers.filetools import unique_path
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.data_processing.mass_spec_database_importer import MassSpecDatabaseImporter
from src.pyscripts.pyscript_runner import PyScriptRunner, RemotePyScriptRunner

DEBUG = True
class ExperimentManagerHandler(SaveableManagerHandler):
    def object_active_experiment_set_changed(self, info):
        if info.initialized:
            info.ui.title = info.object.title


class ExperimentManager(Manager):
    '''
        manager to handle running multiple analyses
    '''
    spectrometer_manager = Instance(Manager)
    data_manager = Instance(Manager)

    extraction_line_manager = Instance(Manager)
    laser_manager = Instance(Manager)
    ion_optics_manager = Instance(Manager)

    experiment_config = None

    active_experiment_set = Instance(ExperimentSet, ())

    pyscript_runner = Instance(PyScriptRunner)

    db = Instance(IsotopeAdapter)
    massspec_importer = Instance(MassSpecDatabaseImporter)
#    delay_between_runs = Int(5)

    _dac_peak_center = Float
    _dac_baseline = Float

#    ncounts = Int
#    n_baseline_counts = Int

#    _alive = False

    mode = 'normal'
#    equilibration_time = 15

    test2 = Button

    _alive = Bool(False)
    execute_button = Event
    execute_label = Property(depends_on='_alive')

#    open_button = Button
#    save_button = Button
#    default_save_directory = Str

    title = DelegatesTo('active_experiment_set', prefix='name')
#    stats = DelegatesTo('active_experiment_set')

#    def load_experiment_configuration(self, p):
#        anals = []
#        with open(p, 'r') as f:
#            for l  in f:
#
#                an = self._automated_analysis_factory(l.split('\t'))
#                anals.append(an)
#
#    def _automated_analysis_factory(self, args):
#        a = AutomatedAnalysisParameters()
#        a.rid = args[0]
#        a.runscript_name = args[1]
#
#        return a
    dirty = DelegatesTo('active_experiment_set')

    def save(self):
        self.save_experiment_set()

    def save_as(self):
        self.save_as_experiment_set()

    def open_recent(self):
        db = self.db

        selector = db.selector_factory(style='simple')
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
        exp = self.active_experiment_set
        exp.stats.nruns_finished = len(exp.automated_runs)
        exp.stop_stats_timer()
        self.info('automated runs complete')

    def do_automated_runs(self):

#        app = self.application
#        if app is not None:
#            protocol = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
#            man = app.get_service(protocol)
#            self.extraction_line_manager = man

        if self.mode == 'client':
            runner = RemotePyScriptRunner('129.138.12.153', 1061, 'udp')
        else:
            runner = PyScriptRunner()

        self._alive = True
        self.info('start automated runs')
#        self.csv_data_manager = CSVDataManager()

#        sm = self.get_spectrometer_manager()
        exp = self.active_experiment_set
        nruns = len(exp.automated_runs)

        err_message = ''

        dm = H5DataManager()

        exp.reset_stats()

        for i, arun in enumerate(exp.automated_runs):
            exp.current_run = arun

            arun.index = i
            arun.experiment_manager = self
            arun.spectrometer_manager = self.spectrometer_manager
            arun.extraction_line_manager = self.extraction_line_manager
            arun.ion_optics_manager = self.ion_optics_manager
            arun.data_manager = dm
            arun.db = self.db
            arun.massspec_importer = self.massspec_importer
            arun.runner = runner
            arun.integration_time = 1.06
            arun._debug = DEBUG
#            if arun.identifier.startswith('B'):
#                arun.isblank = True

            if not self._continue_check():
                break

            self.info('Start automated run {}'.format(arun.identifier))

            #bootstrap the extraction script and measurement script
            if not arun.extraction_script:
                err_message = 'Invalid runscript {extraction_line_script}'.format(**arun.configuration)
                self.warning(err_message)
                continue # or should we continue

            if not arun.measurement_script:
                err_message = 'Invalid measurement_script {measurement_script}'.format(**arun.configuration)
                self.warning(err_message)
                continue

            arun.state = 'extraction'
            arun.do_extraction()

            if not self._continue_check():
                break

            # do eq in a separate thread
            # this way we can measure during eq.
            # ie do_equilibration is nonblocking

            #use an Event object so that we dont finish before eq is done
            event = TEvent()
            event.clear()

            eqtime = arun.get_measurement_parameter('equilibration_time', default=15)
            inlet_valve = arun.get_measurement_parameter('inlet_valve', default='H')
            outlet_valve = arun.get_measurement_parameter('outlet_valve', default='V')

            self.do_equilibration(event, eqtime,
                                  inlet_valve, outlet_valve)

            if not self._continue_check():
                break

            self.debug('waiting for the inlet to open')
            event.wait()
            self.debug('inlet opened')

            arun.state = 'measurement'
            arun.do_measurement()

            if not self._continue_check():
                break

            self.info('Automated run {} finished'.format(arun.identifier))

            if not self._continue_check():
                break

            arun.state = 'success'
            if i + 1 == nruns:
                exp.stop_stats_timer()
                self.end_runs()
                return

            delay = self.active_experiment_set.delay_between_runs
            self.info('Delay between runs {}'.format(delay))
            #delay between runs
            st = time.time()
            while time.time() - st < delay:
                if not self._continue_check():
                    break
                time.sleep(0.5)

        else:
            exp.stop_stats_timer()
            self.end_runs()
            return


        #executed if break out of for loop
        arun.state = 'fail'
        self.warning('automated runs did not complete successfully')
        self.warning('error: {}'.format(err_message))


    def _continue_check(self):
        c = self.isAlive()
        if c:
            return True
        else:
            self.info('automated runs cancelled')

    def isAlive(self):
        return self._alive

    def do_equilibration(self, event, eqtime, inlet, outlet):

        def eq(ev):

            elm = self.extraction_line_manager
            if elm:
                #close mass spec ion pump
                elm.close_valve(outlet)
                time.sleep(1)

                #open inlet
                elm.open_valve(inlet)
                time.sleep(1)
            ev.set()

            #delay for eq time
            self.info('equilibrating for {}sec'.format(eqtime))
            time.sleep(eqtime)

            self.info('finish equilibration')
            if elm:
                elm.close_valve(inlet)

        self.info('starting equilibration')
        t = Thread(target=eq, args=(event,))
        t.start()

    def _execute(self):
        if self.isAlive():

            if self.confirmation_dialog('Cancel {} in Progress'.format(self.title),
                                     title='Confirm Cancel'
                                     ):
                self._alive = False
        else:
            self._alive = True
#        target = self.do_experiment
        #target = self.spectrometer_manager.deflection_calibration
            t = Thread(target=self.do_automated_runs)
            t.start()

    def new_experiment_set(self):
        self.active_experiment_set = ExperimentSet()


#    def close(self, isok):
#        self.dirty_save_as = False
#===============================================================================
# persistence
#===============================================================================
    def load_experiment_set(self, path=None):
        if path is None:
            path = self.open_file_dialog(default_directory=paths.experiment_dir)

        if path is not None:

            exp = ExperimentSet(path=path)
            with open(path, 'rb') as f:
                #read meta
                #read until break
                for line in f:
                    if line.startswith('#====='):
                        break
                delim = '\t'
                header = map(str.strip, f.next().split(delim))
                for ai in f:
                    args = map(str.strip, ai.split(delim))
                    identifier = args[header.index('identifier')]
                    measurement = args[header.index('measurement')]
                    extraction = args[header.index('extraction')]
                    arun = exp._automated_run_factory(
                                                      extraction,
                                                      measurement,
                                                      identifier=identifier,
                                                      )
                    exp.automated_runs.append(arun)

            self.active_experiment_set = exp

#            except Exception:
#                self.warning_dialog('Invalid experiment file {}'.format(path))
    def save_as_experiment_set(self):
        p = self.save_file_dialog(default_directory=paths.experiment_dir)
        self._dump_experiment_set(p)
        self.active_experiment_set.path = p
        self.active_experiment_set.dirty = False

    def save_experiment_set(self):
        p = self.active_experiment_set.path
        self._dump_experiment_set(p)
        self.active_experiment_set.dirty = False

    def _dump_experiment_set(self, p):
#        if not p:
#            p = '/Users/ross/Pychrondata_experiment/experiments/foo.txt'
#            p = self.save_file_dialog(default_directory=paths.experiment_dir)
#

        if not p:
            return

        self.info('saving experiment to {}'.format(p))
        self.active_experiment_set.dirty = False

        header = ['identifier', 'extraction', 'measurement']
        with open(p, 'wb') as f:
            writeline = lambda m: f.write(m + '\n')
            tab = lambda l: writeline('\t'.join(map(str, l)))

            #write metadata
            writeline(self.active_experiment_set.name)
            writeline('#' + '=' * 80)
            tab(header)
            for arun in self.active_experiment_set.automated_runs:
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
        editor = self.active_experiment_set._automated_run_editor(update='object.active_experiment_set.current_run.update')

        exc_grp = Group(
                        self._button_factory('execute_button',
                                             label='execute_label', align='right'),
                       Item('object.active_experiment_set.stats',
                            style='custom'),
                       show_labels=False,
                       show_border=True,
                       label='Execute')
        v = View(
                 exc_grp,
                 Item('object.active_experiment_set.automated_runs',
                      style='custom',
                      show_label=False,
                      editor=editor
                      ),
                 width=700,
                 height=500,
                 resizable=True
                 )
        return v

    def traits_view(self):

        exc_grp = Group(
#                       Item('test2'),
#                       Item('open_button'),
#                       Item('save_button'),
                       Item('object.active_experiment_set.stats',
                            style='custom'),
                       show_labels=False,
                       show_border=True,
                       label='Execute')
        exp_grp = Group(
                       Item('active_experiment_set',
                       show_label=False, style='custom'),
                       show_border=True,
                       label='Experiment'
                )

        v = View(
                VGroup(exc_grp,
                       exp_grp),
                 resizable=True,
                 width=850,
                 height=600,
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
# defaults
#===============================================================================
    def _default_save_directory_default(self):
        return paths.experiment_dir

    def _massspec_importer_default(self):
        msdb = MassSpecDatabaseImporter()
        if msdb.db.isConnected():
            return msdb

    def _db_default(self):
        db = IsotopeAdapter(kind='sqlite',
#                            dbname=paths.isotope_db,
                            dbname='/Users/ross/Pychrondata_test/testing/isotope_test.sqlite'
                            )
        if db.connect():
            return db

if __name__ == '__main__':
    paths.build('_experiment')
    from src.helpers.logger_setup import logging_setup

    logging_setup('experiment_manager')


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
    e.configure_traits()
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



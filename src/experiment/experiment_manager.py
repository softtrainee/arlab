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
from traits.api import Instance, Button, Float, Int, on_trait_change
from traitsui.api import View, Item
#============= standard library imports ========================
from threading import Thread, Event
import os
import time
from numpy import loadtxt, array, arange, diagonal, sqrt
import math
#============= local library imports  ==========================
#from src.initializer import Initializer
from src.managers.spectrometer_manager import SpectrometerManager
from src.managers.manager import Manager
from src.managers.remote_manager import RemoteExtractionLineManager
#from src.helpers.paths import scripts_dir
#from src.managers.data_managers.pychron_db_data_manager import PychronDBDataManager
from src.experiment.experiment import Experiment
from src.managers.data_managers.csv_data_manager import CSVDataManager

from src.paths import paths
from src.managers.data_managers.h5_data_manager import H5DataManager
paths.build('_test')

from src.scripts.extraction_line_script import ExtractionLineScript
from src.data_processing.regression.ols import OLS
from uncertainties import ufloat
from src.data_processing.statistical_calculations import calculate_mswd
from src.graph.graph import Graph
from src.data_processing.time_series.time_series import smooth
from src.graph.stacked_graph import StackedGraph

DEBUG = True

#class AutomatedAnalysisParameters(HasTraits):
#    runscript_name = Str
#    rid = Str


class ExperimentManager(Manager):
    '''
        manager to handle running multiple analyses
    '''
    spectrometer_manager = Instance(Manager)
    experiment_config = None

    experiment = Instance(Experiment, (), kw=dict(name='dore'))

    data_manager = Instance(Manager)

    #these are remote managers
    extraction_line_manager = Instance(Manager)
    laser_manager = Instance(Manager)

    delay_between_runs = Int(5)

    _dac_peak_center = Float
    _dac_baseline = Float

    ncounts = Int
    n_baseline_counts = Int

    _alive = False

    mode = 'normal'
    equilibration_time = 15

    test2 = Button

#    def _data_manager_default(self):
#        '''
#            normally the dbmanager connection parameters are set ie host, name etc
#            for now just use default root, localhost
#        '''
#        dbman = PychronDBDataManager()
#
#        db = dbman.database
#        db.connect()
#
#        return dbman

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
    def recall_analysis(self):
        pass

    def get_spectrometer_manager(self):
        sm = self.spectrometer_manager
        if sm is None:
            protocol = 'src.managers.spectrometer_manager.SpectrometerManager'
            if self.application is not None:
                sm = self.spectrometer_manager = self.application.get_service(protocol)

        return sm

    def do_automated_runs(self):
        if self.mode == 'client':
            man = RemoteExtractionLineManager(host='129.138.12.153',
                                              port=1061)
            self.extraction_line_manager = man

        self._alive = True
        self.info('start automated runs')
#        self.csv_data_manager = CSVDataManager()

#        sm = self.get_spectrometer_manager()
        n = len(self.experiment.automated_runs)

        err_message = ''

        dm = H5DataManager()
        for i, arun in enumerate(self.experiment.automated_runs):
            arun._index = i

            self.experiment.current_run = arun

            arun.experiment_manager = self
            arun.spectrometer_manager = self.spectrometer_manager
            arun.extraction_line_manager = self.extraction_line_manager
            arun.data_manager = dm

            arun.configuration = dict(extraction_line_script=os.path.join(paths.scripts_dir,
                                                        'extraction',
                                                        'Quick_Air_x1.py'),

                                      measurement_script=os.path.join(paths.scripts_dir,
                                                                      'measurement',
                                                                      'measureTest.py')
                                      )


            if not self._continue_check():
                break

            self.info('Start automated run {}'.format(arun.identifier))

            arun._debug = DEBUG
            if arun.identifier.startswith('B'):
                arun.isblank = True

            arun.state = 'extraction'
            if not arun.do_extraction():
                self._alive = False
                err_message = 'Invalid runscript {extraction_line_script}'.format(**arun.configuration)
                break

            if not self._continue_check():
                break

            # do eq in a separate thread
            # this way we can measure during eq.
            # ie do_equilibration is nonblocking

            #use an Event object so that we dont finish before eq is done
            event = Event()
            event.clear()
            self.do_equilibration(event)

            if not self._continue_check():
                break

            self.debug('waiting for the inlet to open')
            event.wait()
            self.debug('inlet opened')

            if DEBUG:
                st = 0
            else:
                st = time.time()

            arun.state = 'measurement'
            if not arun.do_measurement(st):
                err_message = 'Invalid measurement_script {measurement_script}'.format(**arun.configuration)
                break

            if not self._continue_check():
                break

            self.info('Automated run {} finished'.format(arun.identifier))
            break

            if not self._continue_check():
                break

            if i + 1 == n:
                break

            arun.state = 'success'

            self.info('Delay between runs {}'.format(self.delay_between_runs))
            #delay between runs
            st = time.time()
            while time.time() - st < self.delay_between_runs:
                if not self._continue_check():
                    break
                time.sleep(0.5)

        else:
            self.info('automated runs complete')
            return

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

    def do_equilibration(self, event):

        def eq(ev):
            ion_pump_id = 'V'
            inlet_id = 'H'

            eqtime = self.equilibration_time
            elm = self.extraction_line_manager
            if elm:
                #close mass spec ion pump
                elm.close_valve(ion_pump_id)
                time.sleep(1)

                #open inlet
                elm.open_valve(inlet_id)
                time.sleep(1)
            ev.set()

            #delay for eq time
            self.info('equilibrating for {}sec'.format(eqtime))
            time.sleep(eqtime)

            self.info('finish equilibration')
            if elm:
                elm.close_valve(inlet_id)

        self.info('starting equilibration')
        t = Thread(target=eq, args=(event,))
        t.start()

#    def do_extraction(self, arun):
#
#        self.info('Do extraction. Runscript = {}'.format(name))
#        ec = ExtractionLineScript(source_dir=os.path.join(scripts_dir,
#                                                 'extraction_scripts'),
#                                  file_name=name
#                                  )
#
#        ec.bootstrap()
#        ec.join()
#
#        self.time_zero = ec.get_time_zero()

#    def _measure(self, ncounts, dac):
#        #set magnet to be on the peak
#        self.spectometer_manager.set_dac(dac)
#        dm = self.data_manager
#
#        dm.new_frame()
#
#        st = time.time()
#        for _ in xrange(ncounts):
#
#            time.sleep(0.9)
#
#            data = self.spectometer_manager.get_intensities(tagged=True)
#            keys, signals = zip(*data)
#
#            h1 = signals[keys.index('H1')]
#            cdd = signals[keys.index('CDD')]
#            x = time.time() - st
#            dm.write_to_frame((x, h1, cdd))
#
#            self.graph.record(h1, x=x)
#            self.graph.record(cdd, x=x, series=1)

#    def do_measurement(self):
#        self._measure(self.ncounts, self._dac_peak_center)

#    def do_peak_center(self):
#        spec = self.spectometer_manager
#        if spec is not None:
#            spec.peak_center()

#    def do_baseline(self):
#        self._measure(self.n_baseline_counts, self._dac_baseline)

#    def load_experiment_config(self):
#        self.info('loading experiment configuration')
#        self.analysis_config = dict(
#                                           extraction_line_script=os.path.join(scripts_dir, 'runscripts', 'test.rs'),
#                                           analysis_script=os.path.join(scripts_dir, 'analysisscripts', 'test.rs'),
#                                           identifier=4
#                                  )
    def new_experiment(self):
        exp = Experiment()
        self.experiment = exp
        exp.edit_traits()

    def _test2_fired(self):
#        sm = self.get_spectrometer_manager()
#        print sm.spectrometer_microcontroller
#        self.analyze_data()
        dm = H5DataManager()

        path = '/Users/ross/Pychrondata/data/automated_runs/B-01-intensity015.hdf5'
        dm.open_data(path)
        t = dm.get_table('H1', 'signals')
        print t
        for r in t.iterrows():
            print r['time'], r['value']

    def _test_fired(self):
        self.execute()

    def execute(self):
        if self.isAlive():
            self._alive = False
        else:
            self._alive = True
#        target = self.do_experiment
        #target = self.spectrometer_manager.deflection_calibration
            t = Thread(target=self.do_automated_runs)
            t.start()

#    def _add_fired(self):
#        self.experiment.analyses.append(self.experiment.analysis)
#        self.experiment.analysis = Analysis()
#
#    def _apply_fired(self):
#        for s in self.heat_schedule.steps:
#            a = Analysis(heat_step = s)
#            self.experiment.analyses.append(a)

    @on_trait_change('experiment:automated_run:identifier')
    def identifier_update(self, obj, name, old, new):
        print name, old, new
        if new:
            if new == 'A':
                self.experiment.ok_to_add = True
            else:
                #check db for this sample identifier
                db = self.data_manager
                sample = db.get_sample(dict(identifier=new))
                if sample is not None:
                    self.experiment.analysis.sample_data_record = sample
                    self.experiment.ok_to_add = True
        else:
            self.experiment.ok_to_add = False

    def traits_view(self):
        v = View(Item('test', show_label=False),
                 Item('test2'),
                 Item('experiment', show_label=False, style='custom'),

                 resizable=True,
                 width=500,
                 height=500,
                 handler=self.handler_klass
                 )
        return v

    def execute_view(self):
        return self.traits_view()

if __name__ == '__main__':
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
#    e.analyze_data()
    e.configure_traits()

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


#============= EOF ====================================

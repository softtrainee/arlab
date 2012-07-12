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
from traits.api import Any, Str, String, Int, List, Enum, Property, Event, Float, Instance
from traitsui.api import View, Item, VGroup, EnumEditor
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
import os
import time
#============= local library imports  ==========================
#from src.managers.data_managers.pychron_db_data_manager import PychronDBDataManager
from src.loggable import Loggable
from src.scripts.extraction_line_script import ExtractionLineScript
#from src.scripts.measurement.measurement_script import MeasurementScript
from src.experiment.heat_schedule import HeatStep
#from src.graph.graph import Graph
from src.graph.stacked_graph import StackedGraph
from pyface.timer.do_later import do_later
import random
from src.data_processing.regression.regressor import Regressor
from src.scripts.pyscripts.measurement_pyscript import MeasurementPyScript
from src.scripts.pyscripts.extraction_line_pyscript import ExtractionLinePyScript


class AutomatedRunAdapter(TabularAdapter):

    state_image = Property
    state_text = Property

    def _columns_default(self):
        hp = ('Temp', 'temp_or_power')
        power = True
        if power:
            hp = ('Power', 'temp_or_power')

        return  [('', 'state'), ('id', 'identifier'), ('sample', 'sample'),
               hp, ('Duration', 'duration')]

    def _get_state_text(self):
        return ''

    def _get_state_image(self):
        if self.item:
            im = 'gray'
            if self.item.state == 'extraction':
                im = 'yellow'
            elif self.item.state == 'measurement':
                im = 'orange'
            elif self.item.state == 'success':
                im = 'green'
            elif self.item.state == 'fail':
                im = 'red'

            #get the source path
            root = os.path.split(__file__)[0]
            while not root.endswith('src'):
                root = os.path.split(root)[0]
            root = os.path.split(root)[0]
            root = os.path.join(root, 'resources')
            return os.path.join(root, '{}_ball.png'.format(im))


class AutomatedRun(Loggable):
    spectrometer_manager = Any
    extraction_line_manager = Any
    experiment_manager = Any

    extraction_line_script_name = Str
    extraction_line_scripts = List(['script1', 'script2', 'script5'])

    measurement_script_name = Str
    measurement_scripts = List(['script1', 'script2', 'script5'])

    sample = Str

    identifier = String(enter_set=True, auto_set=False)
    state = Enum('not run', 'extraction', 'measurement', 'success', 'fail')

    heat_step = Instance(HeatStep)
    duration = Property(depends_on='heat_step,_duration')
    temp_or_power = Property(depends_on='heat_step,_temp_or_power')
    _duration = Float
    _temp_or_power = Float
    position = Int

    update = Event

    data_manager = Any

    sample_data_record = Any

    isblank = False

    _debug = True

    _active_detectors = None

    def extraction_line_script_factory(self, ec):
        #get the klass

        key = 'extraction_line_script'
        path = os.path

        source_dir = path.dirname(ec[key])
        file_name = path.basename(ec[key])

        if file_name.endswith('.py'):
            klass = ExtractionLinePyScript
            params = dict(root=source_dir,
                    name=file_name,)
        elif file_name.endswith('.rs'):
            klass = ExtractionLineScript
            params = dict(source_dir=source_dir,
                    file_name=file_name,)

        if klass:
            return klass(
                    hole=self.position,
                    heat_duration=self.duration,
                    temp_or_power=self.temp_or_power,

                    manager=self.extraction_line_manager,
                    isblank=self.isblank,
                    **params

                    )
#===============================================================================
# doers
#===============================================================================
    def do_extraction(self):
        self.info('extraction')
        self.state = 'extraction'

        ec = self.configuration

        els = self.extraction_line_script_factory(ec)

        if els.bootstrap(new_thread=False):
            els.execute()
#        '''
#            could calculate the approximate run time then
#            set the join timeout to rtime +padding
#            this could prevent permanent lock ups?
#            use machine learning to improve this time estimate?
#        '''
#            els.join()

            self.info('extraction finished')
            return True
        else:
            return False

    def do_measurement(self, starttime):
        #use a measurement_script to explicitly define 
        #measurement sequence
        ec = self.configuration
        ms = MeasurementPyScript(root=os.path.dirname(ec['measurement_script']),
                name=os.path.basename(ec['measurement_script']),
                starttime=starttime,
                arun=self
                )

        if ms.bootstrap(new_thread=False):
            self._pre_analysis_save()

            ms.execute()
#        '''
#            could calculate the approximate run time then
#            set the join timeout to rtime +padding
#            this could prevent permanent lock ups?
#            use machine learning to improve this time estimate?
#        '''
#            els.join()
            self._post_analysis_save()
            self.info('measurement finished')
            return True
        else:
            return False
#        ncounts = self.ncounts
#        if self.isblank:
#            ncounts = 400
#
#        self.info('measuring signal intensities. collecting {} counts'.format(ncounts))
#        if self.spectrometer_manager:
#            self.spectrometer_manager.spectrometer.set_magnet_position(self.reference_mass)
#        time.sleep(self.magnet_settling_time)
#        self._measure(ncounts,
#                      starttime,
#                      series=0,
#                      update_x=True
#                      )

#        g.set_x_limits(0,
#                       self.ncounts + self.nbaseline_counts + self.delay_before_baseline)


    def do_data_collection(self, ncounts, starttime, series=0):

        gn = 'signals'
        self._build_tables(gn)
        self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series)

    def do_sniff(self, ncounts, starttime, series=0):
        gn = 'sniffs'
        self._build_tables(gn)

        self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series)

    def do_baselines(self, ncounts, starttime, detector=None,
                     position=None, series=0):
        sm = self.spectrometer_manager
        if sm:
            if position is not None:
                sm.spectrometer.set_magnet_position(position)

        gn = 'baselines'
        self._build_tables(gn)
        if detector is None:
            self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series)
        else:
            masses = [1, 2]
            self._peak_hop(gn, detector, masses, ncounts, starttime, series)

    def do_peak_center(self, **kw):
        sm = self.spectrometer_manager
        if sm is not None:
            sm.spectrometer._alive = True
            sm.peak_center(**kw)
            sm.spectrometer._alive = False

    def set_spectrometer_parameter(self, name, v):
        self.info('setting spectrometer parameter {} {}'.format(name, v))
        sm = self.spectrometer_manager
        if sm is not None:
            sm.spectrometer.set_parameter(name, v)

    def set_magnet_position(self, v, **kw):
        sm = self.spectrometer_manager
        if sm is not None:
            sm.spectrometer.set_magnet_position(**kw)

    def activate_detectors(self, dets):
        self._active_detectors = dets

        g = StackedGraph(window_width=500,
                         window_height=700,
                         window_y=0.05 + 0.01 * self._index,
                         window_x=0.6 + 0.01 * self._index,
                         window_title='Plot Panel {}'.format(self.identifier)
                         )

        for i, l in enumerate(dets):
            g.new_plot()
            g.new_series(type='scatter',
                         marker='circle',
                         marker_size=1.25,
                         label=l, plotid=i)



#            g.new_series(type='scatter',
#                         marker='circle',
#                         marker_size=1.25,
#                         label=l, plotid=i)

        self.graph = g
        do_later(self.graph.edit_traits)

        do_later(self.experiment_manager.ui.control.Raise)

#===============================================================================
# 
#===============================================================================

    def regress(self, kind, series=0):
        r = Regressor()
        g = self.graph

        time_zero_offset = int(self.experiment_manager.equilibration_time * 2 / 3.)
        for pi in range(len(g.plots)):
            x = g.get_data(plotid=pi, series=series)[time_zero_offset:]
            y = g.get_data(plotid=pi, series=series, axis=1)[time_zero_offset:]

            rdict = r._regress_(x, y, kind)

            self.info('intercept {}+/-{}'.format(rdict['coefficients'][-1],
                                                 rdict['coeff_errors'][-1]
                                                 ))
            g.new_series(rdict['x'],
                         rdict['y'],
                         plotid=pi, color='black')
            kw = dict(color='red',
                         line_style='dash',
                         plotid=pi)

            g.new_series(rdict['upper_x'],
                         rdict['upper_y'],
                         **kw
                         )
            g.new_series(rdict['lower_x'],
                         rdict['lower_y'],
                         **kw
                         )
            g.redraw()

    def _pre_analysis_save(self):
        self.info('pre analysis save')
        dm = self.data_manager
        #make a new frame for saving data
        dm.new_frame(directory='automated_runs',
                     base_frame_name='{}-intensity'.format(self.identifier))


        #create initial structure
        dm.new_group('baselines')
        dm.new_group('sniffs')
        dm.new_group('signals')


    def _post_analysis_save(self):
        self.info('post analysis save')

        #save to a database
#        db = self.database
#        db.add_analysis()
#        db.add_analysis_path()

    def traits_view(self):

        scripts = VGroup(
                       Item('extraction_line_script_name',
                        editor=EnumEditor(name='extraction_line_scripts')),
                       Item('measurement_script_name',
                            editor=EnumEditor(name='measurement_scripts')),
                       label='Scripts',
                       show_border=True
                       )
        v = View(
                 Item('identifier'),
                 scripts,

                 )
        return v

    def _state_changed(self):
        #update the analysis table
        self.update = True

    def _build_tables(self, gn):
        dm = self.data_manager
        #build tables
        for di in self._active_detectors:
            dm.new_table('/{}'.format(gn), di)

    def _get_data_writer(self, grpname):
        dm = self.data_manager
        def write_data(x, keys, signals):
#            print x, keys, signals
#            print grpname
            for k in self._active_detectors:
                t = dm.get_table(k, '/{}'.format(grpname))
                nrow = t.row
                nrow['time'] = x
                nrow['value'] = signals[keys.index(k)]
                nrow.append()
                t.flush()

        return write_data

    def _peak_hop(self, name, detector, masses, ncounts, starttime, series):
        self.info('peak hopping {} detector={}'.format(name, detector))
        spec = None
        sm = self.spectrometer_manager
        if sm:
            spec = sm.spectrometer

        for i in xrange(0, ncounts, 1):
            for mi, mass in enumerate(masses):
                ti = self.integration_time * 0.99 if not self._debug else 0.01
                time.sleep(ti)
                if spec is not None:
                    #position mass m onto detector
                    spec.set_magnet_position()

                x = time.time() - starttime
                if i % 100 == 0 or x > self.graph.get_x_limits()[1]:
                    self.graph.set_x_limits(0, x + 10)

                signals = [1200 * (1 + random.random()),
                        3.5 * (1 + random.random())]

                v = signals[mi]

                kw = dict(series=series, do_after=1,)
#                print len(self.graph.series[mi])
                if len(self.graph.series[mi]) < series + 1:
                    kw['marker'] = 'circle'
                    kw['type'] = 'scatter'
                    kw['marker_size'] = 1.25
                    self.graph.new_series(x=[x], y=[v], plotid=mi, **kw)
                else:
                    self.graph.add_datum((x, v), plotid=mi, ** kw)

    def _measure_iteration(self, grpname, data_write_hook,
                           ncounts, starttime, series,
#                 update_x=True,
#                 sniff=False
                 ):
        self.info('measuring {}'.format(grpname))

        dm = self.data_manager
        sm = self.spectrometer_manager

        for i in xrange(0, ncounts, 1):
            if i % 50 == 0:
                self.info('collecting point {}'.format(i + 1))

            m = self.integration_time * 0.99 if not self._debug else 0.01
            time.sleep(m)

            if not self._debug:
                data = sm.get_intensities(tagged=True)
                keys, signals = zip(*data)
            else:
                keys = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']

                if series == 0:
                    signals = [10, 1000, 8, 8, 8, 3]
                else:
                    r = random.randint(0, 75)
                    signals = [0.1, (0.015 * (i - 2800 + r)) ** 2,
                               0.1, 1, 0.1, (0.001 * (i - 2000 + r)) ** 2
                               ]

            h1 = signals[keys.index('H1')]
            cdd = signals[keys.index('CDD')]

            x = time.time() - starttime# if not self._debug else i + starttime

            data_write_hook(x, keys, signals)
#                dm.write_to_frame((x, h1, cdd))

            if i % 100 == 0:
                self.graph.set_x_limits(0, x + 10)

#                self.graph.set_x_limits(0, min(i + 100,
##                                               x
#                                               #ncounts + self.nbaseline_counts + self.delay_before_baseline
#                                               )
#                                        )
            kw = dict(series=series, do_after=1,)
            if len(self.graph.series[0]) < series + 1:
                kw['marker'] = 'circle'
                kw['type'] = 'scatter'
                kw['marker_size'] = 1.25
                self.graph.new_series(x=[x], y=[h1], plotid=0, **kw)
                self.graph.new_series(x=[x], y=[cdd], plotid=1, **kw)
            else:
                self.graph.add_datum((x, h1), plotid=0, ** kw)
                self.graph.add_datum((x, cdd), plotid=1, **kw)
#===============================================================================
# property get/set
#===============================================================================
    def _get_duration(self):
        if self.heat_step:
            d = self.heat_step.duration
        else:
            d = self._duration
        return d

    def _get_temp_or_power(self):
        if self.heat_step:

            t = self.heat_step.temp_or_power
        else:
            t = self._temp_or_power
        return t

    def _validate_duration(self, d):
        return self._validate_float(d)

    def _validate_temp_or_power(self, d):
        return self._validate_float(d)

    def _validate_float(self, d):
        try:
            return float(d)
        except ValueError:
            pass

    def _set_duration(self, d):
        if d is not None:
            if self.heat_step:
                self.heat_step.duration = d
            else:
                self._duration = d

    def _set_temp_or_power(self, t):
        if t is not None:
            if self.heat_step:
                self.heat_step.temp_or_power = t
            else:
                self._temp_or_power = t
#============= EOF =============================================

'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
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
from src.graph.graph import Graph
from src.graph.stacked_graph import StackedGraph
from pyface.timer.do_later import do_later
import random
from src.data_processing.regression.regressor import Regressor


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

#    measurement_script_name = Str
#    measurement_scripts = List(['script1', 'script2', 'script5'])
#    measurement_script = Instance(MeasurementScript)

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

    ncounts = Int(2000)
    nbaseline_counts = Int(100)
    reference_mass = 39.962
    baseline_mass = 33.5
    integration_time = 1

    isblank = False

    def do_extraction(self):
        self.info('extraction')
        self.state = 'extraction'

        ec = self.configuration
        els = ExtractionLineScript(
                source_dir=os.path.dirname(ec['extraction_line_script']),
                file_name=os.path.basename(ec['extraction_line_script']),

                hole=self.position,
                heat_duration=self.duration,
                temp_or_power=self.temp_or_power,

                manager=self.extraction_line_manager,
                isblank=self.isblank
                )

        a = els.bootstrap(new_thread=False)
        if a:
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

    def do_peak_center(self):
        sm = self.spectrometer_manager
        if sm is not None:
            sm.spectrometer._alive = True
            sm.peak_center()
            sm.spectrometer._alive = False

    def do_measurement(self, starttime, count=0):
        dm = self.data_manager
        dm.new_frame(directory='automated_runs',
                     base_frame_name='{}-intensity'.format(self.identifier))

        g = StackedGraph(window_width=500,
                         window_height=700,
                         window_y=0.05 + 0.01 * count,
                         window_x=0.6 + 0.01 * count,
                         window_title='Plot Panel {}'.format(self.identifier)
                         )

        for i, l in enumerate(['H1', 'CDD']):
            g.new_plot()
            g.new_series(type='scatter',
                         marker='circle',
                         marker_size=1.25,
                         label=l, plotid=i)
            g.new_series(type='scatter',
                         marker='circle',
                         marker_size=1.25,
                         label=l, plotid=i)

        g.set_x_limits(0, self.ncounts + self.nbaseline_counts)
        self.graph = g
        do_later(self.graph.edit_traits)

        do_later(self.experiment_manager.ui.control.Raise)

        self.info('measuring signal intensities')
        self._measure(self.ncounts,
                      self.reference_mass, starttime,
                      series=0
                      )

    def do_baseline(self, dac, starttime):
        dm = self.data_manager
        dm.new_frame(directory='automated_runs',
                     base_frame_name='{}-baseline'.format(self.identifier))
        self.info('measuring baseline intensities')
        self._measure(self.nbaseline_counts,
                       self.baseline_mass, starttime,
                       series=1
                       )

    def regress(self):
        r = Regressor()
        g = self.graph

        for pi in range(len(g.plots)):
            x = g.get_data(plotid=pi)
            y = g.get_data(plotid=pi, axis=1)
            rdict = r._regress_(x, y, 2)
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

    def _measure(self, ncounts, refmass, starttime, series=0):
        dm = self.data_manager
        sm = self.spectrometer_manager

        #set magnet to be on the peak
        if sm is not None:
            sm.spectrometer.set_magnet_position(refmass)

        data = None
        step = 30
        for i in xrange(0, ncounts, step):
            self.info('collecting point {}'.format(i + 1))

            m = self.integration_time * 0.99 if sm is not None else 0.01
            time.sleep(m)

            if sm is not None:
                data = sm.get_intensities(tagged=True)

            if data is None:
                keys = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']
                if series == 1:
                    signals = [10, 1000, 8, 8, 8, 3]
                else:
                    r = random.randint(0, 75)
                    signals = [0.1, (0.015 * (i - 2800 + r)) ** 2,
                               0.1, 1, 0.1, (0.001 * (i - 2000 + r)) ** 2
                               ]

            else:
                keys, signals = zip(*data)

            h1 = signals[keys.index('H1')]
            cdd = signals[keys.index('CDD')]

            x = time.time() - starttime if sm is not None else i + starttime

            dm.write_to_frame((x, h1, cdd))

            self.graph.add_datum((x, h1), series=series, do_after=1)
            self.graph.add_datum((x, cdd), series=series,
                                  plotid=1, do_after=1)
    def finish(self, success):
        '''
            use a DBDataManager to save the analysis to database
        '''

        if success:
            self.state = 'success'
        else:
            self.state = 'fail'

        self.save_to_db()
        self.info('finish')

    def save_to_db(self):
        db = self.data_manager

        #add an analysis
        #relate to sample
        analysis = db.add_analysis(
                        status=0 if self.state else 1,
                        sample=self.sample_data_record
                        )

        spec = db.get_spectrometer('obama')

        signals = self.measurement_script.signals
        signals = signals.transpose()
        times = signals[0]

        #relate to signal with analysis and detector
        for d, s in zip(spec.detectors, signals[1:]):
            db.add_signal(times=times,
                          intensities=s,
                          analysis=analysis,
                          detector=d
                          )

    def traits_view(self):

        scripts = VGroup(
                       Item('extraction_line_script_name',
                        editor=EnumEditor(name='extraction_line_scripts')),
#                       Item('measurement_script_name', editor=EnumEditor(name='measurement_scripts')),
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
        return self._valiate_float(d)

    def _validate_temp_or_power(self, d):
        return self._valiate_float(d)

    def _valiate_float(self, d):
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

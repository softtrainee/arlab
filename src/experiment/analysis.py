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
from src.scripts.measurement.measurement_script import MeasurementScript
from src.experiment.heat_schedule import HeatStep

class AnalysisAdapter(TabularAdapter):

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


class Analysis(Loggable):
    spectrometer_manager = Any

    extraction_line_script_name = Str
    extraction_line_scripts = List(['script1', 'script2', 'script5'])
    measurement_script_name = Str
    measurement_scripts = List(['script1', 'script2', 'script5'])
    measurement_script = Instance(MeasurementScript)

    sample = Str

    identifier = String(enter_set = True, auto_set = False)
    state = Enum('not run', 'extraction', 'measurement', 'success', 'fail')

    heat_step = Instance(HeatStep)
    duration = Property(depends_on = 'heat_step,_duration')
    temp_or_power = Property(depends_on = 'heat_step,_temp_or_power')
    _duration = Float
    _temp_or_power = Float
    position = Int

    update = Event

    data_manager = Any

    sample_data_record = Any
    def do_analysis(self):
        #do extraction
        if self.extraction():
            time.sleep(2)
        #do measurement script
        if self.measurement():
            time.sleep(2)

        success = True
        #finish the measurement
        self.finish(success)

    def extraction(self):
        self.info('extraction')
        self.state = 'extraction'

        ec = self.configuration
        els = ExtractionLineScript(
                            source_dir = os.path.dirname(ec['extraction_line_script']),
                            file_name = os.path.basename(ec['extraction_line_script']),

                            hole = self.position,
                            heat_duration = self.duration,
                            temp_or_power = self.temp_or_power
                            )
        els.bootstrap()
        '''
            could calculate the approximate run time then set the join timeout to rtime +padding
            this could prevent permanent lock ups?
            use machine learning to improve this time estimate?
             
        '''
        els.join()

        self.info('extraction finished')
        return True

    def pre_measurement(self):
        self.info('pre measurement')

    def measurement(self):

        self.pre_measurement()
        self.info('measurement')
        self.state = 'measurement'

        ec = self.configuration

        #@todo: MeasurementScript needs accurate identifier
        ms = MeasurementScript(
                            manager = self.spectrometer_manager,
                            source_dir = os.path.dirname(ec['analysis_script']),
                            file_name = os.path.basename(ec['analysis_script']),
                            identifier = ec['identifier']
                            )
        self.measurement_script = ms
        ms.bootstrap()
        ms.join()

        self.post_measurement()

        return True

    def post_measurement(self):
        self.info('post measurement')

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
                        status = 0 if self.state else 1,
                        sample = self.sample_data_record
                        )

        spec = db.get_spectrometer('obama')

        signals = self.measurement_script.signals
        signals = signals.transpose()
        times = signals[0]

        #relate to signal with analysis and detector
        for d, s in zip(spec.detectors, signals[1:]):
            db.add_signal(times = times,
                          intensities = s,
                          analysis = analysis,
                          detector = d
                          )





    def traits_view(self):

        scripts = VGroup(
                       Item('analysis_script', editor = EnumEditor(name = 'extraction_line_scripts')),
                       Item('measurement_script_name', editor = EnumEditor(name = 'measurement_scripts')),
                       label = 'Scripts',
                       show_border = True
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

    def _set_duration(self, d):
        if self.heat_step:
            self.heat_step.duration = d
        else:
            self._duration = d

    def _set_temp_or_power(self, t):
        if self.heat_step:
            self.heat_step.temp_or_power = t
        else:
            self._temp_or_power = t
#============= EOF =============================================

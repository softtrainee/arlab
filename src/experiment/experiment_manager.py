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
from traits.api import HasTraits, Instance, List, Button, Int, on_trait_change, Str, Bool
from traitsui.api import View, Item, VGroup, HGroup, spring, \
    TabularEditor
#============= standard library imports ========================
from threading import Thread
import os
import time
#============= local library imports  ==========================
#from src.initializer import Initializer
from src.managers.spectrometer_manager import SpectrometerManager
from src.experiment.analysis import Analysis, AnalysisAdapter

from src.managers.manager import Manager
from src.helpers.logger_setup import setup
from src.helpers.paths import scripts_dir


from src.managers.data_managers.pychron_db_data_manager import PychronDBDataManager
from src.experiment.heat_schedule import HeatSchedule

class Experiment(HasTraits):
    analyses = List(Analysis)
    analysis = Instance(Analysis, ())
    current_analysis = Instance(Analysis, ())
    heat_schedule = Instance(HeatSchedule, ())
    name = Str

    ok_to_add = Bool(False)
    apply = Button
    add = Button
    def _add_fired(self):
        self.analyses.append(self.analysis)
        self.analysis = Analysis()

    def _apply_fired(self):
        for s in self.heat_schedule.steps:
            a = Analysis(heat_step = s)
            self.analyses.append(a)

    def traits_view(self):
        new_analysis = Item('analysis', style = 'custom', show_label = False)

        editor = TabularEditor(adapter = AnalysisAdapter(),
                                operations = ['move'],
                                update = 'object.current_analysis.update'
                                )
        analysis_table = Item('analyses', show_label = False,
                              editor = editor,
                              height = 0.5
                             )


        heat_schedule_table = Item('heat_schedule', style = 'custom', show_label = False,
                                   height = 0.35
                                   )
        v = View(
                 'name',
                 new_analysis,
                 HGroup(spring, Item('apply', enabled_when = 'ok_to_add'),
                                Item('add', enabled_when = 'ok_to_add'),
                                show_labels = False),
                 VGroup(
                        heat_schedule_table,
                        analysis_table
                        ),

                 )

        return v

class ExperimentManager(Manager):
    spectrometer_manager = Instance(Manager)
    experiment_config = None


    experiment = Instance(Experiment, (), kw = dict(name = 'dore'))
    delay_before_analysis = Int

    data_manager = Instance(Manager)



    def _data_manager_default(self):
        '''
            normally the dbmanager connection parameters are set ie host, name etc
            for now just use default root, localhost
        '''
        dbman = PychronDBDataManager()

        db = dbman.database
        db.connect()

        return dbman

    def do_experiment(self):
        self.info('experiment started')
        #load an experiment config
        self.load_experiment_config()

        for a in self.experiment.analyses:
#        a = Analysis(spectrometer_manager = self.spectrometer_manager,
#                     configuration = self.analysis_config)
            self.current_analysis = a

            #set the analysis attributes
            a.spectrometer_manager = self.spectrometer_manager
            a.configuration = self.analysis_config
            a.data_manager = self.data_manager

            #delay before analysis
            time.sleep(self.delay_before_analysis + 1)

            a.do_analysis()

        self.info('experiment finished')

    def load_experiment_config(self):
        self.info('loading experiment configuration')
        self.analysis_config = dict(
                                           extraction_line_script = os.path.join(scripts_dir, 'runscripts', 'test.rs'),
                                           analysis_script = os.path.join(scripts_dir, 'analysisscripts', 'test.rs'),
                                           identifier = 4
                                  )

    def _test_fired(self):
        target = self.do_experiment
        #target = self.spectrometer_manager.deflection_calibration
        t = Thread(target = target)
        t.start()

#    def _add_fired(self):
#        self.experiment.analyses.append(self.experiment.analysis)
#        self.experiment.analysis = Analysis()
#
#    def _apply_fired(self):
#        for s in self.heat_schedule.steps:
#            a = Analysis(heat_step = s)
#            self.experiment.analyses.append(a)

    @on_trait_change('experiment:analysis:identifier')
    def identifier_update(self, obj, name, old, new):
        print name, old, new
        if new:

            #check db for this sample identifier
            db = self.data_manager
            sample = db.get_sample(dict(identifier = new))
            if sample is not None:
                self.experiment.analysis.sample_data_record = sample
                self.experiment.ok_to_add = True
        else:
            self.ok_to_add = False
    def traits_view(self):
        v = View(Item('test', show_label = False),
                 Item('experiment', show_label = False, style = 'custom'),

                 resizable = True,
                 width = 500,
                 height = 500
                 )
        return v
if __name__ == '__main__':
    setup('experiment_manager')


    s = SpectrometerManager()
#    ini = Initializer()
#    ini.add_initialization(dict(name = 'spectrometer_manager',
#                                manager = s
#                                ))
#    ini.run()

    e = ExperimentManager(
                          spectrometer_manager = s
                          )
    e.configure_traits()



#============= EOF ====================================

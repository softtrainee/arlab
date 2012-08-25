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
from traits.api import HasTraits, List, Instance, Str, Button, Any, \
    Bool, Property, Float, Int, on_trait_change, Dict
from traitsui.api import View, Item, TabularEditor, VGroup, HGroup, spring, \
    EnumEditor
#============= standard library imports ========================
import os
import time
import datetime
#============= local library imports  ==========================
from src.experiment.automated_run import AutomatedRun, AutomatedRunAdapter
from src.experiment.heat_schedule import HeatSchedule
from pyface.timer.api import Timer
from src.paths import paths
from src.loggable import Loggable

class ExperimentStats(HasTraits):
    elapsed = Property(depends_on='_elapsed')
    _elapsed = Float
    nruns = Int
    nruns_finished = Int
    etf = Str
    total_time = Property(depends_on='_total_time')
    _total_time = Float
    _timer = Any(transient=True)
    def calculate_etf(self, runs):
        self.nruns = len(runs)

        dur = sum([a.get_estimated_duration() for a in runs])
        self._total_time = dur

        dt = (datetime.datetime.now() + \
                       datetime.timedelta(seconds=int(dur)))
        self.etf = dt.strftime('%I:%M:%S %p %a %m/%d')

    def _get_total_time(self):
        dur = self._total_time
        return '{:0.3f} hrs ({} secs)'.format(dur / 3600., dur)

    def _get_elapsed(self):
        return str(datetime.timedelta(seconds=self._elapsed))

    def traits_view(self):
        v = View(VGroup(
                        Item('nruns',
                            label='Total Runs',
                            style='readonly'
                            ),
                        Item('nruns_finished',
                             label='Completed',
                             style='readonly'
                             ),
                        Item('total_time',
                              style='readonly'),
                        Item('etf', style='readonly', label='Est. finish'),
                        Item('elapsed',
                             style='readonly'),
                        )
                 )
        return v

    def start_timer(self):
        st = time.time()
        def update_time():
            self._elapsed = int(time.time() - st)

        self._timer = Timer(1000, update_time)
        self._timer.Start()

    def stop_timer(self):
        self._timer.Stop()

class ExperimentSet(Loggable):
    automated_runs = List(AutomatedRun)
    automated_run = Instance(AutomatedRun)
    current_run = Instance(AutomatedRun)
    heat_schedule = Instance(HeatSchedule, (), transient=True)

    ok_to_add = Bool(False)
    apply = Button
    add = Button

    name = Property(depends_on='path')
    path = Str
    stats = Instance(ExperimentStats, (), transient=True)

    loaded_scripts = Dict

    test_configuration = Property

    measurement_script = Str
    measurement_scripts = Property(depends_on='_measurement_scripts')
    _measurement_scripts = List

    extraction_script = Str
    extraction_scripts = Property(depends_on='_extraction_scripts')
    _extraction_scripts = List

    delay_between_runs = Float(1)

    dirty = Property(depends_on='_dirty,path')
    _dirty = Bool(False)

    def _set_dirty(self, d):
        self._dirty = d

    def _get_dirty(self):
        return self._dirty and os.path.isfile(self.path)

    def _load_script_names(self, name):
        p = os.path.join(paths.scripts_dir, name)
        if os.path.isdir(p):
            prep = lambda x:x
    #        prep = lambda x: os.path.split(x)[0]

            return [prep(s)
                    for s in os.listdir(p)
                        if not s.startswith('.') and s.endswith('.py')
                        ]
        else:
            self.warning_dialog('{} script directory does not exist!'.format(p))


    def update_loaded_scripts(self, new):
        self.loaded_scripts[new.name] = new



    def reset_stats(self):
        self.stats.start_timer()

    def stop_stats_timer(self):
        self.stats.stop_timer()

    def _auto_increment_runid(self, rid):
        try:
            head, tail = rid.split('-')
            rid = '{}-{}'.format(head, int(tail) + 1)
        except ValueError:
            try:
                rid = str(int(rid) + 1)
            except ValueError:
                pass

        return rid

#===============================================================================
# handlers
#===============================================================================
    def _add_fired(self):

        self.automated_runs.append(self.automated_run)

        #@todo: auto increment the runid
        rid = self._auto_increment_runid(self.automated_run.identifier)
        self.automated_run = self._automated_run_factory(rid)
        self.ok_to_add = False


    def _apply_fired(self):
        for s in self.heat_schedule.steps:
            a = AutomatedRun(heat_step=s)
            self.automated_runs.append(a)

    @on_trait_change('current_run,automated_runs[]')
    def update_stats(self, obj, name, old, new):
        self.dirty = True
        #updated the experiments stats
        if name == 'current_run':
            if not new is self.automated_runs[0]:
                #skip the first update 
                self.stats.nruns_finished += 1

        elif name == 'automated_runs_items':
            self.stats.calculate_etf(self.automated_runs)
#===============================================================================
# views
#===============================================================================
    def _automated_run_editor(self, update=''):
        return TabularEditor(adapter=AutomatedRunAdapter(),
                             update=update
                                )
    def traits_view(self):
        new_analysis = VGroup(
                              Item('automated_run',
                                   show_label=False,
                                   style='custom'
                                   ),
                              HGroup(
                                     spring,
                                     Item('add', show_label=False),
                                     )
                              )


        analysis_table = Item('automated_runs', show_label=False,
                              editor=self._automated_run_editor(update='object.current_run.update'),
                              height=0.5
                             )

        heat_schedule_table = Item('heat_schedule', style='custom',
                                   show_label=False,
                                   height=0.35
                                   )
        v = View(
                 HGroup(
                 VGroup(
                        new_analysis,
                        Item('measurement_script',
                             label='Measurement',
                             editor=EnumEditor(name='measurement_scripts',
                                                                     evaluate=lambda x:x
                                                                    )),
                        Item('extraction_script',
                             label='Extraction',
                             editor=EnumEditor(name='extraction_scripts',
                                                                     evaluate=lambda x:x
                                                                    ))
                        ),
                 VGroup(
                         heat_schedule_table,
                         HGroup(spring, Item('apply', enabled_when='ok_to_add'),
                                show_labels=False),
                        analysis_table,
#                        stats
                        ),
                 ))

        return v


#===============================================================================
# factories
#===============================================================================
    def _automated_run_factory(self, **kw):
        '''
             always use this factory for new AutomatedRuns
             it sets the configuration, loaded scripts and binds our update_loaded_script
             handler so we are aware of scripts that have been tested
        '''

        a = AutomatedRun(
                         configuration=self.test_configuration,
                         scripts=self.loaded_scripts,
                         **kw
                         )

        a.on_trait_change(self.update_loaded_scripts, '_measurement_script')
        a.on_trait_change(self.update_loaded_scripts, '_extraction_script')
        return a

#===============================================================================
# property get/set
#===============================================================================
    def _get_name(self):
        if self.path:
            return os.path.splitext(os.path.basename(self.path))[0]
        else:
            return 'New ExperimentSet'

    def _get_extraction_scripts(self):
        es = self._load_script_names('extraction')
        if es:
            self.extraction_script = es[0]
        return es

    def _get_measurement_scripts(self):
        ms = self._load_script_names('measurement')
        if ms:
            self.measurement_script = ms[0]
        return ms
    def _get_test_configuration(self):
        c = dict(extraction_script=os.path.join(paths.scripts_dir,
                                                        'extraction',
                                                        'Quick_Air_x1.py'),

                  measurement_script=os.path.join(paths.scripts_dir,
                                                  'measurement',
                                                  'measureTest.py')
                  )
        return c
#===============================================================================
# defaults
#===============================================================================
    def _automated_run_default(self):
        return self._automated_run_factory()
#===============================================================================
# debugging
#===============================================================================
#    def add_run(self):
#        a = self._automated_run_factory('B-1')
#        self.automated_runs.append(a)
#        print a.measurement_script
#
#        a = self._automated_run_factory('B-2')
#        self.automated_runs.append(a)
#        a = AutomatedRun(identifier='B-dd12',
#                         scripts=self.loaded_scripts,
#                         configuration=self.test_configuration
#                         )
#        self.automated_runs.append(a)
#        self.automated_runs.append(a)
#    def _automated_runs_default(self):
#        return [
#
#                AutomatedRun(identifier='B-01'),
#                AutomatedRun(identifier='A-01'),
#                AutomatedRun(identifier='A-02'),
#                AutomatedRun(identifier='A-03'),
#                AutomatedRun(identifier='A-04'),
#                AutomatedRun(identifier='B-02'),
#                AutomatedRun(identifier='A-05'),
#                AutomatedRun(identifier='A-06'),
#                AutomatedRun(identifier='A-07'),
#                AutomatedRun(identifier='A-08'),
#                AutomatedRun(identifier='A-09'),
#                AutomatedRun(identifier='A-10'),
#                AutomatedRun(identifier='B-03'),
#                ]
#============= EOF =============================================


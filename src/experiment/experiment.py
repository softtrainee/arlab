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



from traits.api import HasTraits, List, Instance, Str, Button, Bool
from traitsui.api import View, Item, TabularEditor, VGroup, HGroup, spring

from src.experiment.automated_run import AutomatedRun, AutomatedRunAdapter
from src.experiment.heat_schedule import HeatSchedule


class Experiment(HasTraits):
    automated_runs = List(AutomatedRun)
    automated_run = Instance(AutomatedRun, ())
    current_run = Instance(AutomatedRun, ())
    heat_schedule = Instance(HeatSchedule, ())
    name = Str

    ok_to_add = Bool(False)
    apply = Button
    add = Button

    def _automated_runs_default(self):
        return [

                AutomatedRun(identifier='B-01'),
                AutomatedRun(identifier='A-01'),
                AutomatedRun(identifier='A-02'),
                AutomatedRun(identifier='A-03'),
                AutomatedRun(identifier='A-04'),
                AutomatedRun(identifier='B-02'),
                AutomatedRun(identifier='A-05'),
                AutomatedRun(identifier='A-06'),
                AutomatedRun(identifier='A-07'),
                AutomatedRun(identifier='A-08'),
                AutomatedRun(identifier='A-09'),
                AutomatedRun(identifier='A-10'),
                AutomatedRun(identifier='B-03'),

                ]

    def _add_fired(self):
        self.automated_runs.append(self.automated_run)
        self.automated_run = AutomatedRun()
        self.ok_to_add = False

    def _apply_fired(self):
        for s in self.heat_schedule.steps:
            a = AutomatedRun(heat_step=s)
            self.automated_runs.append(a)

    def traits_view(self):
        new_analysis = Item('automated_run', style='custom', show_label=False)

        editor = TabularEditor(adapter=AutomatedRunAdapter(),
#                                operations=['move', 'delete',
#                                            'insert', 'append',
#                                             'edit'],
#                                drag_move=True,
                                update='object.current_run.update'
                                )
        analysis_table = Item('automated_runs', show_label=False,
                              editor=editor,
                              height=0.5
                             )

        heat_schedule_table = Item('heat_schedule', style='custom', show_label=False,
                                   height=0.35
                                   )
        v = View(
                 'name',
                 new_analysis,
                 HGroup(spring, Item('apply', enabled_when='ok_to_add'),
                                Item('add', enabled_when='ok_to_add'),
                                show_labels=False),
                 VGroup(
                        heat_schedule_table,
                        analysis_table
                        ),
                 title='Experiment Editor'
                 )

        return v
#============= EOF ====================================


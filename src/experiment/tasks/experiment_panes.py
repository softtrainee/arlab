#===============================================================================
# Copyright 2013 Jake Ross
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
# from traits.api import HasTraits
from traitsui.api import View, Item, UItem, VGroup, HGroup, spring, \
    ButtonEditor
from pyface.tasks.traits_task_pane import TraitsTaskPane
from pyface.tasks.traits_dock_pane import TraitsDockPane
#============= standard library imports ========================
#============= local library imports  ==========================

class AnalysesPane(TraitsTaskPane):
    def traits_view(self):
        v = View(
                 UItem('experiment_queue', style='custom'),
                 )
        return v

class ExperimentFactoryPane(TraitsDockPane):
    id = 'pychron.experiment.factory'
    name = 'Experiment Editor'
    def traits_view(self):
        v = View(
                 VGroup(
                        Item('object.experiment_factory.queue_factory.username'),
                        Item('object.experiment_factory.queue_factory.delay_before_analyses'),
                        Item('object.experiment_factory.queue_factory.delay_between_analyses')
                        ),
                 UItem('experiment_factory', style='custom'),
                 )
        return v

class StatsPane(TraitsDockPane):
    id = 'pychron.experiment.stats'
    name = 'Stats'
    def traits_view(self):
        v = View(
                 UItem('stats', style='custom')
                 )
        return v

class ControlsPane(TraitsDockPane):
    id = 'pychron.experiment.controls'
    def traits_view(self):
        v = View(
                 HGroup(
                        UItem('resume_button', enabled_when='delaying_between_runs'),
                        Item('delay_between_runs_readback',
                              label='Delay Countdown',
                              style='readonly', format_str='%i',
                              width= -50),
                        spring,
                        Item('show_sample_map', show_label=False,
                             enabled_when='experiment_queue.sample_map'
                             ),
                        spring,
                        Item('end_at_run_completion'),
                        UItem('truncate_button', enabled_when='measuring'),
                        UItem('truncate_style', enabled_when='measuring'),
                        UItem('execute_button',
                              enabled_when='executable',
                              editor=ButtonEditor(label_value='execute_label'))
                        ),
                 )
        return v

class ConsolePane(TraitsDockPane):
    id = 'pychron.experiment.console'
    name = 'Console'
    def traits_view(self):
        v = View(UItem('info_display', style='custom'))
        return v
#============= EOF =============================================

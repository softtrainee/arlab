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
from traits.api import HasTraits, on_trait_change, Instance, Button, \
    Property, String
from traitsui.api import View, Item, HGroup, VGroup, UItem, UCustom

#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.experiment_manager import ExperimentManager
# from src.paths import paths
from src.saveable import SaveableButtons
from src.experiment.automated_run.factory import AutomatedRunFactory
from src.experiment.queue.factory import ExperimentQueueFactory
from src.experiment.queue.experiment_queue import ExperimentQueue
from src.constants import NULL_STR
from src.experiment.automated_run.uv.factory import UVAutomatedRunFactory

class ExperimentFactory(HasTraits):
    run_factory = Instance(AutomatedRunFactory)
    queue_factory = Instance(ExperimentQueueFactory)

    add_button = Button('add')

    queue = Instance(ExperimentQueue)

    ok_run = Property(depends_on='_mass_spectrometer, _extract_device')
    ok_add = Property(depends_on='_mass_spectrometer, _extract_device, _labnumber')
    _mass_spectrometer = String
    _extract_device = String
    _labnumber = String

    def set_selected_runs(self, runs):
        self.run_factory.set_selected_runs(runs)

    def _add_button_fired(self):
        new_runs = self.run_factory.new_runs()
        self.queue.add_runs(new_runs)

    @on_trait_change('queue_factory:[mass_spectrometer, extract_device, delay_+, tray]')
    def _update_queue(self, name, new):
        if name == 'mass_spectrometer':
            self._mass_spectrometer = new
            self.run_factory.set_mass_spectrometer(new)

        elif name == 'extract_device':
            self._set_extract_device(new)

        print name, new
        self.queue.trait_set(**{name:new})

    @on_trait_change('run_factory:[labnumber]')
    def _update_labnumber(self, name, new):
        if name == 'labnumber':
            self._labnumber = new

#===============================================================================
# private
#===============================================================================
    def _set_extract_device(self, ed):
        self._extract_device = ed
        self.run_factory = self._run_factory_factory()
        self.queue.set_extract_device(ed)
#===============================================================================
# property get/set
#===============================================================================
    def _get_ok_add(self):
        return  self.ok_run and self._labnumber

    def _get_ok_run(self):
        return (self._mass_spectrometer and self._mass_spectrometer != NULL_STR) and\
                (self._extract_device and self._extract_device != NULL_STR)
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        grp = VGroup(
                     UCustom('queue_factory'),
                     UCustom('run_factory', enabled_when='ok_run'),
                     HGroup(UItem('add_button', enabled_when='ok_add'))
                     )
        v = View(grp)
        return v

    def _run_factory_factory(self):
        if self._extract_device == 'Fusions UV':
            klass = UVAutomatedRunFactory
        else:
            klass = AutomatedRunFactory

        rf = klass(db=self.db,
                   extract_device=self._extract_device,
                   mass_spectrometer=self._mass_spectrometer,
                   application=self.application)
        return rf
#===============================================================================
# defaults
#===============================================================================
    def _run_factory_default(self):
        return self._run_factory_factory()

    def _queue_factory_default(self):
        eq = ExperimentQueueFactory(db=self.db,
                                 application=self.application
                                 )
        return eq

class ExperimentEditor(ExperimentManager):
    experiment_factory = Instance(ExperimentFactory)
#===============================================================================
# persistence
#===============================================================================
#    def load_experiment_set(self, saveable=False, *args, **kw):
#        r = super(ExperimentEditor, self).load_experiment_set(*args, **kw)
#
#        # loading the experiment set will set dirty =True
#        # change back to false. not really dirty
# #        if r:
# #            self.experiment_set.dirty = False
#        self.save_enabled = saveable
#        return r

    @on_trait_change('experiment_queue:selected')
    def _update_selected(self, new):
        self.experiment_factory.set_selected_runs(new)

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        factory_grp = UItem('experiment_factory',
                            style='custom',
                            width=0.35
                            )
        exp_grp = UItem('experiment_queue',
                            style='custom',
                            width=0.55
                            )

        sel_grp = UItem('set_selector',
                       style='custom',
                       width=0.10,
                       )
        v = View(
                 HGroup(
                        sel_grp,
                        factory_grp,
                        exp_grp
                       ),
                 resizable=True,
                 width=0.80,
                 height=0.85,
                 buttons=['OK', 'Cancel'] + SaveableButtons,
#                          Action(name='Save', action='save',
#                                 enabled_when='dirty'),
#                          Action(name='Save As',
#                                 action='save_as',
# #                                 enabled_when='dirty_save_as'
#                                 ),

#                          ],
                 handler=self.handler_klass,
#                 handler=SaveableManagerHandler,
                 title='Experiment'
                 )
        return v

#===============================================================================
# defaults
#===============================================================================
    def _experiment_factory_default(self):
        e = ExperimentFactory(db=self.db,
                              application=self.application,
                              queue=self.experiment_queue
                              )
        e.queue_factory.mass_spectrometer = 'Jan'
        e.queue_factory.extract_device = 'Fusions Diode'
        e.queue_factory.delay_between_analyses = 100
        e.queue_factory.delay_before_analyses = 10312
        return e

#===============================================================================
# handlers
#===============================================================================
#    @on_trait_change('experiment_set:automated_runs:dirty')
#    def _update_dirty(self, n):
# #        self._dirty = n
#        self.save_enabled = n

#===============================================================================
# property get/set
#===============================================================================
#    def _get_dirty(self):
#        return self._dirty and os.path.isfile(self.path)

#============= EOF =============================================

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
from traits.api import HasTraits, Instance, Button, Bool, Property, \
    on_trait_change, String
from traitsui.api import View, Item, HGroup, VGroup, UItem, UCustom
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.automated_run.uv.factory import UVAutomatedRunFactory
from src.experiment.automated_run.factory import AutomatedRunFactory
from src.experiment.queue.factory import ExperimentQueueFactory
from src.experiment.queue.experiment_queue import ExperimentQueue
from src.constants import NULL_STR
from src.loggable import Loggable

class ExperimentFactory(Loggable):
    run_factory = Instance(AutomatedRunFactory)
    queue_factory = Instance(ExperimentQueueFactory)

    add_button = Button('add')
    auto_increment = Bool(True)

    queue = Instance(ExperimentQueue)

    ok_run = Property(depends_on='_mass_spectrometer, _extract_device')
    ok_add = Property(depends_on='_mass_spectrometer, _extract_device, _labnumber')
    _mass_spectrometer = String
    _extract_device = String
    _labnumber = String

    #===========================================================================
    # permisions
    #===========================================================================
    _max_allowable_runs = 25


    def set_selected_runs(self, runs):
        self.run_factory.set_selected_runs(runs)

    def _add_button_fired(self):
        new_runs = self.run_factory.new_runs(auto_increment=self.auto_increment)
        self.queue.add_runs(new_runs)

        tol = self._max_allowable_runs
        n = len(self.queue.automated_runs)
        if n >= tol:
            self.warning_dialog('You are at or have existed your max. allowable runs. N={} Max={}'.format(n, tol))

    @on_trait_change('queue_factory:[mass_spectrometer, extract_device, delay_+, tray]')
    def _update_queue(self, name, new):
        if name == 'mass_spectrometer':
            self._mass_spectrometer = new
            self.run_factory.set_mass_spectrometer(new)

        elif name == 'extract_device':
            self._set_extract_device(new)

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
        '''
            tol should be a user permission
        '''
        tol = self._max_allowable_runs
        ntest = len(self.queue.automated_runs) < tol
        return  self.ok_run and self._labnumber and ntest

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
                     HGroup(
                            UItem('add_button', enabled_when='ok_add'),
                            Item('auto_increment')
                            )

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

#============= EOF =============================================

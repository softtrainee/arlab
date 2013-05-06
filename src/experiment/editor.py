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
from traits.api import HasTraits, on_trait_change, Instance, Str, Int
from traitsui.api import View, Item, HGroup, VGroup, UItem, UCustom

#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.manager import ExperimentManager
# from src.paths import paths
from src.saveable import SaveableButtons
from globals import globalv
from src.experiment.factory import ExperimentFactory



class ExperimentEditor(ExperimentManager):
    foo = Int
    boo = Str
    experiment_factory = Instance(ExperimentFactory)
    @on_trait_change('experiment_queue:selected')
    def _update_selected(self, new):
        self.experiment_factory.set_selected_runs(new)

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
#        factory_grp = UItem('experiment_factory',
#                            style='custom',
#                            width=0.35,
#                            )
#        factory_grp = VGroup(
#                            Item('object.experiment_factory.queue_factory.username'),
# #                       Item('mass_spectrometer',
# #                            editor=EnumEditor(name='mass_spectrometers'),
# #                            ),
# #                       Item('extract_device',
# #                            editor=EnumEditor(name='extract_devices'),
# #                            ),
# # #                       Item('tray',
# # #                            editor=EnumEditor(name='trays'),
# # #                            tooltip='Select an sample tray for this set'
# # #                            ),
#
#                       Item('object.experiment_factory.queue_factory.delay_before_analyses',
# #                            tooltip='Set the time in seconds to delay before starting this queue',
# #                            label='Delay before Analyses (s)'
#                            ),
#                       Item('object.experiment_factory.queue_factory.delay_between_analyses',
# #                            tooltip='Set the delay between analysis in seconds',
# #                            label='Delay between Analyses (s)'
#                            ),
#                           )
#        exp_grp = UItem('experiment_queue',
#                            style='custom',
#                            width=0.55
#                            )
#
#        sel_grp = UItem('set_selector',
#                       style='custom',
#                       width=0.10,
#                       )
#        v = View(
#                 HGroup(
#                        sel_grp,
#                        factory_grp,
#                        exp_grp
#                       ),
#                 resizable=True,
# #                 width=0.80,
# #                 height=0.90,
#                 buttons=['OK', 'Cancel'] + SaveableButtons,
# #                          Action(name='Save', action='save',
# #                                 enabled_when='dirty'),
# #                          Action(name='Save As',
# #                                 action='save_as',
# # #                                 enabled_when='dirty_save_as'
# #                                 ),
#
# #                          ],
#                 handler=self.handler_klass,
# #                 handler=SaveableManagerHandler,
#                 title='Experiment'
#                 )
        factory_grp = VGroup(Item('foo'), Item('boo'))
        v = View(factory_grp)
        return v

    def _experiment_queue_changed(self):
        eq = self.experiment_queue
        if eq:
            self.experiment_factory.queue = self.experiment_queue
            qf = self.experiment_factory.queue_factory
            for a in ('username', 'mass_spectrometer', 'extract_device', 'username',
                      'delay_before_analyses', 'delay_between_analyses'
                      ):
                setattr(qf, a, getattr(eq, a))

    @on_trait_change('can_edit_script, max_allowable_runs')
    def _update_value(self, name, value):
        setattr(self.experiment_factory, name, value)

#    def _can_edit_scripts_changed(self):
#        self.experiment_factory._can_edit_script = self.can_edit_scripts
#===============================================================================
# defaults
#===============================================================================
    def _experiment_factory_default(self):
        e = ExperimentFactory(db=self.db,
                              application=self.application,
                              queue=self.experiment_queue,
                              max_allowable_runs=self.max_allowable_runs,
                              can_edit_scripts=self.can_edit_scripts
                              )

        if globalv.experiment_debug:
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

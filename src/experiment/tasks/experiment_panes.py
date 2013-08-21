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
from traits.api import Color, Instance
from traitsui.api import View, Item, UItem, VGroup, HGroup, spring, \
    ButtonEditor, EnumEditor, UCustom, Group, Spring, VFold, Label, InstanceEditor, \
    CheckListEditor
# from pyface.tasks.traits_task_pane import TraitsTaskPane
from pyface.tasks.traits_dock_pane import TraitsDockPane
from src.experiment.utilities.identifier import SPECIAL_NAMES
# from src.ui.tabular_editor import myTabularEditor
# from src.experiment.automated_run.tabular_adapter import AutomatedRunSpecAdapter
from src.constants import MEASUREMENT_COLOR, EXTRACTION_COLOR, \
    NOT_EXECUTABLE_COLOR, SKIP_COLOR, SUCCESS_COLOR, CANCELED_COLOR, \
    TRUNCATED_COLOR, FAILED_COLOR, END_AFTER_COLOR
from src.ui.custom_label_editor import CustomLabel
#============= standard library imports ========================
#============= local library imports  ==========================

#===============================================================================
# editing
#===============================================================================
def make_qf_name(name):
            return 'object.queue_factory.{}'.format(name)

def make_rf_name(name):
    return 'object.run_factory.{}'.format(name)

def QFItem(name, **kw):
    return Item(make_qf_name(name), **kw)

def RFItem(name, **kw):
    return Item(make_rf_name(name), **kw)

def make_rt_name(name):
    return 'object.experiment_queue.runs_table.{}'.format(name)

def RTItem(name, **kw):
    return Item(make_rt_name(name), **kw)

class ExperimentFactoryPane(TraitsDockPane):
    id = 'pychron.experiment.factory'
    name = 'Experiment Editor'
    def traits_view(self):
        v = View(
                 VGroup(
                     VGroup(
                            QFItem('username'),
                            HGroup(
                                   QFItem('mass_spectrometer',
                                          show_label=False,
                                          editor=EnumEditor(name=make_qf_name('mass_spectrometers')),
                                          ),
                                   QFItem('extract_device',
                                          show_label=False,
                                          editor=EnumEditor(name=make_qf_name('extract_devices')),
                                          )
                                   ),
                            QFItem('load_name',
                                   show_label=False,
                                   editor=EnumEditor(name=make_qf_name('load_names'))
                                   ),

                            QFItem('delay_before_analyses'),
                            QFItem('delay_between_analyses')
                            ),

                     HGroup(
                            UItem('save_button',),
                            UItem('add_button', enabled_when='ok_add'),
                            UItem('clear_button',
                                     tooltip='Clear all runs added using "frequency"'
                                     ),
                            UItem('edit_mode_button',
                                   enabled_when='edit_enabled',
#                                   show_label=False
                                   ),
                            CustomLabel(make_rf_name('edit_mode_label'),
                                        color='red',
                                        width=40
                                        ),
                            spring,
                            RFItem('end_after', width=30),
                            RFItem('skip')
                            ),
                    CustomLabel(make_rf_name('info_label'),
                                ),
    #                  UCustom('run_factory', enabled_when='ok_run'),
                    VFold(
                          VGroup(
                                self._get_info_group(),
                                self._get_extract_group(),
                                label='General'
                                ),
#                     self._get_position_group(),
                     self._get_script_group(),
                     enabled_when=make_qf_name('ok_make')
                     ),
                     HGroup(
                            UItem('add_button', enabled_when='ok_add'),
                            UItem('clear_button',
                                     tooltip='Clear all runs added using "frequency"'
                                  ),
                            Label('Auto Increment'),
                            Item('auto_increment_id', label='L#'),
                            Item('auto_increment_position', label='Position'),
                            )
                        ),
                 width=225
                 )
        return v

    def _get_info_group(self):
        grp = Group(
#                   HGroup(spring, CustomLabel('help_label', size=14), spring),
                   HGroup(
                          RFItem('selected_irradiation',
#                                 label='Irradiation',

                                 show_label=False,
                                 editor=EnumEditor(name=make_rf_name('irradiations'))),
                          RFItem('selected_level',
                                 show_label=False,
#                                 label='Level',
                                 editor=EnumEditor(name=make_rf_name('levels'))),

#                          RFItem('project', editor=EnumEditor(name=make_rf_name('projects')),
#                                 ),

                          ),

                   HGroup(RFItem('special_labnumber',
                                 show_label=False,
                                 editor=EnumEditor(values=SPECIAL_NAMES),
                               ),
                          RFItem('frequency', width=50),
                          spring
                          ),
                   HGroup(RFItem('labnumber',
                              tooltip='Enter a Labnumber',
                              width=100,
                              ),
                          RFItem('_labnumber', show_label=False,
#                              editor=EnumEditor(name=make_rf_name('labnumbers')),
                              editor=CheckListEditor(name=make_rf_name('labnumbers')),
                              width=-20,
                              ),
                              spring,
                         ),
                   HGroup(
                           RFItem('aliquot',
                                  width=50
                                  ),
                           RFItem('irradiation',
                                      tooltip='Irradiation info retreived from Database',
                                      style='readonly',
                                      width=90,
                                      ),
                           RFItem('sample',
                                    tooltip='Sample info retreived from Database',
                                    style='readonly',
                                    width=100,
                                    show_label=False
                                    ),
                          spring
                          ),
                    HGroup(
                           RFItem('weight',
                                  label='Weight (mg)',
                                  tooltip='(Optional) Enter the weight of the sample in mg. Will be saved in Database with analysis',
                                  ),
                           RFItem('comment',
                                  tooltip='(Optional) Enter a comment for this sample. Will be saved in Database with analysis'
                                  )
                           ),
                       show_border=True,
                       label='Sample Info'
                       )
        return grp

    def _get_script_group(self):
        script_grp = VGroup(
                        RFItem('extraction_script', style='custom', show_label=False),
                        RFItem('measurement_script', style='custom', show_label=False),
                        RFItem('post_equilibration_script', style='custom', show_label=False),
                        RFItem('post_measurement_script', style='custom', show_label=False),
                        show_border=True,
                        label='Scripts'
                        )
        return script_grp

#     def _get_position_group(self):
#         grp = VGroup(
#  #                         Item('autocenter',
#  #                              tooltip='Should the extract device try to autocenter on the sample'
#  #                              ),
#                          HGroup(RFItem('position',
#                                      tooltip='Set the position for this analysis. Examples include 1, P1, L2, etc...'
#                                      ),
#                                 RFItem('endposition', label='End',
#                                      enabled_when='position'
#                                      )
#                                 ),
#  #                         Item('multiposition', label='Multi. position run'),
#                          show_border=True,
#                          label='Position'
#                      )
#         return grp

    def _get_extract_group(self):
        sspring = lambda width = 17:Spring(springy=False, width=width)

        extract_grp = VGroup(
                             HGroup(sspring(width=33),
                                    RFItem('extract_value', label='Extract',
                                         tooltip='Set the extract value in extract units',
                                         enabled_when=make_rf_name('extractable')
                                         ),
                                    RFItem('extract_units',
                                            show_label=False,
                                            editor=EnumEditor(name=make_rf_name('extract_units_names'))),
                                    spring,
#                                     Label('Step Heat Template'),
                                    ),
                             HGroup(
                                RFItem('template',
                                        label='Step Heat Template',
                                        editor=EnumEditor(name=make_rf_name('templates')),
                                        show_label=False,
                                        ),
                                RFItem('edit_template',
                                       show_label=False,
                                       editor=ButtonEditor(label_value=make_rf_name('edit_template_label'))
                                     )
                                    ),
                             HGroup(RFItem('extract_group_button', show_label=False,
                                           tooltip='Group selected runs as a step heating experiment'
                                           ),
                                    RFItem('extract_group', label='Group ID')),
                             RFItem('duration', label='Duration (s)',
                                  tooltip='Set the number of seconds to run the extraction device.'

                                  ),
                             RFItem('cleanup', label='Cleanup (s)',
                                  tooltip='Set the number of seconds to getter the sample gas'
                                  ),
                             RFItem('beam_diameter'),
                             RFItem('ramp_duration', label='Ramp Dur. (s)'),
                             # Item('ramp_rate', label='Ramp Rate (C/s)'),
                             HGroup(
                                    RFItem('pattern',
                                           editor=EnumEditor(name=make_rf_name('patterns'))),
                                    RFItem('edit_pattern',
                                           show_label=False,
                                           editor=ButtonEditor(label_value=make_rf_name('edit_pattern_label'))
                                           )
                                    ),

                             HGroup(RFItem('position',
                                     tooltip='Set the position for this analysis. Examples include 1, P1, L2, etc...'
                                     ),
                                RFItem('endposition', label='End',
                                     enabled_when='position'
                                     )
                                ),

                             label='Extract',
                             show_border=True
                             )
        return extract_grp
#         return VGroup(extract_grp, self._get_position_group(),
#                       label='Extraction'
#                       )

#===============================================================================
# execution
#===============================================================================
class WaitPane(TraitsDockPane):
    id = 'pychron.experiment.wait'
    name = 'Wait'
    def traits_view(self):
        v = View(
                 UItem('wait_dialog',
                        style='custom'),
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
    name = 'Controls'
    id = 'pychron.experiment.controls'

    movable = False
    closable = False
    floatable = False

    def traits_view(self):
        v = View(
                 HGroup(
                        UItem('resume_button', enabled_when='delaying_between_runs'),
                        Spring(springy=False, width=-10),
                        Item('delay_between_runs_readback',
                              label='Delay Countdown',
                              style='readonly', format_str='%i',
                              width=-50),

                        CustomLabel('extraction_state_label',
                                    color_name='extraction_state_color',
                                    size=24
                                    ),
                        spring,
#                        Item('show_sample_map', show_label=False,
#                             enabled_when='experiment_queue.sample_map'
#                             ),
#                        spring,

                        # temporary disable refresh/reset queue button

#                         UItem('refresh_button',
#                               enabled_when='not object._alive',
#                               editor=ButtonEditor(label_value='refresh_label')
#                               ),

                        Spring(width=-20, springy=False),
                        Item('end_at_run_completion'),
                        Spring(width=-20, springy=False),
                        UItem('cancel_run_button', enabled_when='can_cancel'),
                        UItem('truncate_button', enabled_when='measuring'),
                        UItem('truncate_style', enabled_when='measuring'),
                        UItem('execute_button',
                              enabled_when='executable',
                              editor=ButtonEditor(label_value='execute_label')),
                        ),
                 )
        return v

class ConsolePane(TraitsDockPane):
    id = 'pychron.experiment.console'
    name = 'Console'
    def traits_view(self):
        v = View(UItem('info_display', style='custom'))
        return v

class ExplanationPane(TraitsDockPane):
    id = 'pychron.experiment.explanation'
    name = 'Explanation'
    measurement = Color(MEASUREMENT_COLOR)
    extraction = Color(EXTRACTION_COLOR)
    success = Color(SUCCESS_COLOR)
    skip = Color(SKIP_COLOR)
    canceled = Color(CANCELED_COLOR)
    truncated = Color(TRUNCATED_COLOR)
    failed = Color(FAILED_COLOR)
    not_executable = Color(NOT_EXECUTABLE_COLOR)
    end_after = Color(END_AFTER_COLOR)

    def traits_view(self):
        v = View(
               VGroup(
                   HGroup(Label('Extraction'), spring,
                          UItem('extraction',
                                style='readonly')
                          ),
                   HGroup(Label('Measurement'), spring,
                          UItem('measurement',
                                style='readonly')
                          ),
                   HGroup(Label('Skip'), spring,
                          UItem('skip',
                                style='readonly')
                          ),
                   HGroup(Label('Success'), spring,
                          UItem('success',
                                style='readonly')
                          ),
                   HGroup(Label('Truncated'), spring,
                          UItem('truncated',
                                style='readonly')
                          ),
                   HGroup(Label('Canceled'), spring,
                          UItem('canceled',
                                style='readonly')
                          ),
                   HGroup(Label('Failed'), spring,
                          UItem('failed',
                                style='readonly')
                          ),
                   HGroup(Label('Not Executable'), spring,
                          UItem('not_executable',
                                style='readonly')
                          ),
                   HGroup(Label('End After'), spring,
                          UItem('end_after',
                                style='readonly')
                          ),
                      )

               )
        return v


class IsotopeEvolutionPane(TraitsDockPane):
    id = 'pychron.experiment.isotope_evolution'
    name = 'Isotope Evolutions'
    plot_panel = Instance('src.experiment.plot_panel.PlotPanel')
    def traits_view(self):
        v = View(UItem('plot_panel',
#                        editor=InstanceEditor(view='graph_view'),
                       style='custom',
                       width=600
                       ),

                 )
        return v

class SummaryPane(TraitsDockPane):
    id = 'pychron.experiment.summary'
    name = 'Summary'
    plot_panel = Instance('src.experiment.plot_panel.PlotPanel')
    def traits_view(self):
        v = View(UItem('plot_panel', editor=InstanceEditor(view='summary_view'),
                       style='custom'))
        return v


# from pyface.tasks.enaml_dock_pane import EnamlDockPane
# class TestEnamlPane(EnamlDockPane):
#    def create_component(self):
#        pass

#============= EOF =============================================

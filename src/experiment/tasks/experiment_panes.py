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
from traits.api import Color
from traitsui.api import View, Item, UItem, VGroup, HGroup, spring, \
    ButtonEditor, EnumEditor, UCustom, Group, Spring, VFold, Label
# from pyface.tasks.traits_task_pane import TraitsTaskPane
from pyface.tasks.traits_dock_pane import TraitsDockPane
from src.experiment.utilities.identifier import SPECIAL_NAMES
# from src.ui.tabular_editor import myTabularEditor
# from src.experiment.automated_run.tabular_adapter import AutomatedRunSpecAdapter
from src.constants import MEASUREMENT_COLOR, EXTRACTION_COLOR, \
    NOT_EXECUTABLE_COLOR, SKIP_COLOR, SUCCESS_COLOR
from src.ui.custom_label_editor import CustomLabel
#============= standard library imports ========================
#============= local library imports  ==========================


# def CBItem(name, maker=None, **kw):
#    if maker is None:
#        maker = make_rf_name
#    return Item(maker(name), **kw)
#    return HGroup(Item(maker(name), height=10, **kw), UItem(maker('cb_{}'.format(name)),
#                                          visible_when=maker('cbs_enabled')
#                                          ),
#
#                  )

def make_qf_name(name):
            return 'object.queue_factory.{}'.format(name)

def make_rf_name(name):
    return 'object.run_factory.{}'.format(name)

def QFItem(name, **kw):
    return Item(make_qf_name(name), **kw)

def RFItem(name, **kw):
    return Item(make_rf_name(name), **kw)

# def RF_CBItem(name, **kw):
#    return CBItem(name, make_rf_name, **kw)


def make_rt_name(name):
    return 'object.experiment_queue.runs_table.{}'.format(name)

def RTItem(name, **kw):
    return Item(make_rt_name(name), **kw)

# class AnalysesPane(TraitsTaskPane):
#    def traits_view(self):
#
#        v = View(
#                 VGroup(
#                        HGroup(spring, Item('refresh', show_label=False)),
#                        RTItem('automated_runs',
#                               show_label=False,
#                               editor=myTabularEditor(adapter=AutomatedRunSpecAdapter(),
#                                            operations=['delete',
#                                                        'move',
# #                                                        'edit'
#                                                        ],
#                                            editable=True,
#                                            selected='selected',
#                                            rearranged='rearranged',
#                                            pasted='pasted',
# #                                             copy_cache='copy_cache',
# #                                             update='update_needed',
#                                            drag_move=True,
#                                            auto_update=True,
#                                            multi_select=True,
#                                            scroll_to_bottom=False
#                                            )
#                      )
#                    )
#                 )
#        return v

class ExperimentFactoryPane(TraitsDockPane):
    id = 'pychron.experiment.factory'
    name = 'Experiment Editor'
    def traits_view(self):
        v = View(
                 VGroup(
                     VGroup(
                            QFItem('username'),
                            QFItem('mass_spectrometer',
                                 editor=EnumEditor(name=make_qf_name('mass_spectrometers')),
                             ),
                            QFItem('extract_device',
                                 editor=EnumEditor(name=make_qf_name('extract_devices')),
                             ),
                            QFItem('delay_before_analyses'),
                            QFItem('delay_between_analyses')
                            ),

                     HGroup(UItem('add_button', enabled_when='ok_add'),
                            UItem('edit_mode_button',
                                   enabled_when='edit_enabled',
#                                   show_label=False
                                   ),
                            CustomLabel(make_rf_name('edit_mode_label'),
                                        color='red',
                                        width=40
                                        ),
                            spring),

    #                  UCustom('run_factory', enabled_when='ok_run'),
                    VFold(
                     self._get_info_group(),
                     self._get_extract_group(),
                     self._get_position_group(),
                     self._get_script_group(),
                     enabled_when=make_qf_name('ok_make')
                     ),
#                      Group(
#                           layout='tabbed'),

                     HGroup(
                            UItem('add_button', enabled_when='ok_add'),
                            Item('auto_increment'),
                            UItem('clear_button',
                                     tooltip='Clear all runs added using "frequency"'
                                     )
                            )
                        )
                 )
        return v

    def _get_info_group(self):
        grp = Group(
                   RFItem('project', editor=EnumEditor(name=make_rf_name('projects')),
                       ),
                   HGroup(
                          RFItem('selected_irradiation',
                               label='Irradiation',
                               editor=EnumEditor(name=make_rf_name('irradiations'))),
                          RFItem('selected_level',
                               label='Level',
                               editor=EnumEditor(name=make_rf_name('levels'))),
                          ),

                   HGroup(RFItem('special_labnumber', editor=EnumEditor(values=SPECIAL_NAMES),
                               ),
                          RFItem('frequency')
                          ),
                   HGroup(RFItem('labnumber',
                              tooltip='Enter a Labnumber'
                              ),
                          RFItem('_labnumber', show_label=False,
                              editor=EnumEditor(name=make_rf_name('labnumbers')),
                              width=100,
                              ),
                         ),
                   RFItem('aliquot'),
                   RFItem('sample',
                        tooltip='Sample info retreived from Database',
                        style='readonly'
                        ),
                   RFItem('irradiation',
                          tooltip='Irradiation info retreived from Database',
                          style='readonly'
                          ),
                   RFItem('weight',
                        label='Weight (mg)',
                        tooltip='(Optional) Enter the weight of the sample in mg. Will be saved in Database with analysis'
                        ),
                   RFItem('comment',
                        tooltip='(Optional) Enter a comment for this sample. Will be saved in Database with analysis'
                        ),

                       show_border=True,
                       label='Info'
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

    def _get_position_group(self):
        grp = VGroup(
 #                         Item('autocenter',
 #                              tooltip='Should the extract device try to autocenter on the sample'
 #                              ),
                         HGroup(RFItem('position',
                                     tooltip='Set the position for this analysis. Examples include 1, P1, L2, etc...'
                                     ),
                                RFItem('endposition', label='End',
                                     enabled_when='position'
                                     )
                                ),
 #                         Item('multiposition', label='Multi. position run'),
                         show_border=True,
                         label='Position'
                     )
        return grp

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
#                                         editor=EnumEditor(name=make_rf_name('templates'))
                                        editor=EnumEditor(name='templates'
#                                                           make_rf_name('templates')
                                                          )
                                       ),
                                 RFItem('edit_template',
                                        show_label=False,
                                      editor=ButtonEditor(label_value=make_rf_name('edit_template_label'))
                                      )
                                    ),

                             RFItem('duration', label='Duration (s)',
                                  tooltip='Set the number of seconds to run the extraction device.'

                                  ),
                             RFItem('cleanup', label='Cleanup (s)',
                                  tooltip='Set the number of seconds to getter the sample gas'
                                  ),
                             # Item('ramp_rate', label='Ramp Rate (C/s)'),
                             RFItem('pattern', editor=EnumEditor(name=make_rf_name('patterns'))),
                             label='Extract',
                             show_border=True
                             )
        return extract_grp

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

class ExplanationPane(TraitsDockPane):
    id = 'pychron.experiment.explanation'
    name = 'Explanation'
    measurement = Color(MEASUREMENT_COLOR)
    extraction = Color(EXTRACTION_COLOR)
    success = Color(SUCCESS_COLOR)
    skip = Color(SKIP_COLOR)
    not_executable = Color(NOT_EXECUTABLE_COLOR)

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
                   HGroup(Label('Not Executable'), spring,
                          UItem('not_executable',
                                style='readonly')
                          ),
                      )

               )
        return v
#============= EOF =============================================

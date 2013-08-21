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
from traits.api import HasTraits, Property
from traitsui.api import View, Item, TabularEditor, VGroup, spring, HGroup, \
    EnumEditor, ImageEditor, VFold, UItem, Spring
from pyface.tasks.traits_task_pane import TraitsTaskPane
# from src.irradiation.irradiated_position import IrradiatedPositionAdapter
from pyface.tasks.traits_dock_pane import TraitsDockPane
# from src.ui.custom_label_editor import CustomLabel
from traitsui.tabular_adapter import TabularAdapter
from src.processing.entry.irradiated_position import IrradiatedPositionAdapter
# from traitsui.editors.progress_editor import ProgressEditor
#============= standard library imports ========================
#============= local library imports  ==========================

class IrradiationEditorPane(TraitsDockPane):
    id = 'pychron.labnumber.editor'
    name = 'Editor'
    def traits_view(self):
        v = View(
                 VGroup(
                        UItem('load_file_button'),
                        UItem('generate_labnumbers_button'),
                         HGroup(
                                Item('project',
                                     editor=EnumEditor(name='projects')),
                                UItem('add_project_button')
                              ),
                         HGroup(
                               Item('material',
                                    editor=EnumEditor(name='materials')),
                               UItem('add_material_button')
                             ),
                         HGroup(
                                Item('sample',
                                     editor=EnumEditor(name='samples')),
                                UItem('add_sample_button')
                              ),
                        ),

               )
        return v


class ImportNameAdapter(TabularAdapter):
    columns = [('Name', 'name')]

class ImportedNameAdapter(TabularAdapter):
    columns = [('Name', 'name'), ('Skipped', 'skipped')]
    skipped_text = Property

    def _get_skipped_text(self):
        return 'Yes' if self.item.skipped else ''

    def get_bg_color(self, obj, trait, row, column=0):
        color = 'white'
        if self.item.skipped:
            color = 'red'
        return color

class LabnumbersPane(TraitsTaskPane):
    def traits_view(self):
        v = View(Item('irradiated_positions',
                             editor=TabularEditor(adapter=IrradiatedPositionAdapter(),
                                                  refresh='refresh_table',
                                                  multi_select=True,
                                                  selected='selected',
                                                  operations=['edit']
                                                  ),
                             show_label=False
                             )
                 )
        return v


class ImporterPane(TraitsDockPane):
    name = 'Importer'
    id = 'pychron.labnumber.importer'
    def traits_view(self):
        v = View(
                 VGroup(
                     HGroup(
                            HGroup(Item('include_analyses', label='Analyses'),
                                Item('include_blanks', label='Blanks'),
                                Item('include_airs', label='Airs'),
                                Item('include_cocktails', label='Cocktails'),
                                label='Include',
                                show_border=True,
                                ),
                            VGroup(
                                   HGroup(spring,
                                          UItem('import_button'),
                                          Item('dry_run'),

                                          ),
                                   label='Import',
                                   show_border=True
                                   )
                            ),
                     VGroup(
                         HGroup(spring, Item('data_source')),
#                         VFold(
                         VGroup(
                             VGroup(
                                    Item('object.importer.dbconn_spec', style='custom', show_label=False),
                                    HGroup(spring, Item('object.importer.connect_button', show_label=False)),
                                    label='Source'
                                    ),
                             VGroup(

                                    HGroup(Item('import_kind', show_label=False),
                                           UItem('open_button', visible_when='import_kind=="rid_list"'),
                                           ),
                                    UItem('text_selected'),
                                    HGroup(
                                           Item('names', show_label=False, editor=TabularEditor(adapter=ImportNameAdapter(),
                                                                    editable=False,
                                                                    selected='selected',
                                                                    multi_select=True,
                                                                    scroll_to_row='scroll_to_row'
                                                                    )),
#                                    CustomLabel('custom_label1',
#                                             color='blue',
#                                             size=10),
                                            Item('imported_names', show_label=False, editor=TabularEditor(adapter=ImportedNameAdapter(),
                                                                    editable=False,
                                                                    ))
                                           ),
#                                    HGroup(spring, Item('import_button', show_label=False)),
                                    label='Results'
                                 )
                           )
                        )
                    )
                 )
        return v


class IrradiationPane(TraitsDockPane):
    name = 'Irradiation'
    id = 'pychron.labnumber.irradiation'
    def traits_view(self):
        v = View(
                   HGroup(
                          VGroup(HGroup(Item('irradiation',
                                             editor=EnumEditor(name='irradiations')
                                             ),
                                        Item('edit_irradiation_button',
                                             enabled_when='edit_irradiation_enabled',
                                             show_label=False)
                                        ),
                                 HGroup(Item('level', editor=EnumEditor(name='levels')),
                                        spring,
                                        Item('edit_level_button',
                                             enabled_when='edit_level_enabled',
                                             show_label=False)
                                        ),
                                 Item('add_irradiation_button', show_label=False),
                                 Item('add_level_button', show_label=False),
#                                        Item('irradiation_tray',
#                                             editor=EnumEditor(name='irradiation_trays')
#                                             )
                                 ),
                          spring,
                          VGroup(
                                 Item('tray_name', style='readonly', show_label=False),
#                                  Item('irradiation_tray_image',
#                                       editor=ImageEditor(),
#                                       height=100,
#                                       width=200,
#                                       style='custom',
#                                       show_label=False),
                                 ),
                               ),
#                            label='Irradiation',
#                            show_border=True
                   )
        return v

#     def traits_view(self):
#        irradiation = Group(
#                            HGroup(
#                                   VGroup(HGroup(Item('irradiation',
#                                                      editor=EnumEditor(name='irradiations')
#                                                      ),
#                                                 Item('edit_irradiation_button',
#                                                      enabled_when='edit_irradiation_enabled',
#                                                      show_label=False)
#                                                 ),
#                                          HGroup(Item('level', editor=EnumEditor(name='levels')),
#                                                 spring,
#                                                 Item('edit_level_button',
#                                                      enabled_when='edit_level_enabled',
#                                                      show_label=False)
#                                                 ),
#                                          Item('add_irradiation_button', show_label=False),
#                                          Item('add_level_button', show_label=False),
# #                                        Item('irradiation_tray',
# #                                             editor=EnumEditor(name='irradiation_trays')
# #                                             )
#                                          ),
#                                   spring,
#                                   VGroup(
#                                          Item('tray_name', style='readonly', show_label=False),
#                                          Item('irradiation_tray_image',
#                                               editor=ImageEditor(),
#                                               height=200,
#                                               width=200,
#                                               style='custom',
#                                               show_label=False),
#                                          ),
#                                        ),
#                            label='Irradiation',
#                            show_border=True
#                            )
#
#        auto = Group(
#                    Item('auto_assign', label='Auto-assign Labnumbers'),
#                    Item('auto_startrid', label='Start Labnumber',
#                         enabled_when='auto_assign'
#                         ),
#                    Item('auto_project', label='Project',
#                         enabled_when='auto_assign'
#                         ),
#                    Item('auto_sample', label='Sample',
#                         enabled_when='auto_assign'
#                         ),
#                    Item('auto_material', label='Material',
#                         enabled_when='auto_assign'
#                         ),
#                     Item('auto_j', format_str='%0.2e', label='Nominal J.'),
#                     Item('auto_j_err', format_str='%0.2e', label='Nominal J Err.'),
#                    Item('auto_assign_overwrite', label='Overwrite exisiting Labnumbers',
#                         enabled_when='auto_assign'
#                         ),
#                      HGroup(Item('freeze_button', show_label=False), Item('thaw_button', show_label=False),
#                              enabled_when='selected'),
#                      show_border=True,
#                      label='Auto-Assign'
#
#                      )
#
#        samples = Group(
#
#                        Item('irradiated_positions',
#                             editor=TabularEditor(adapter=IrradiatedPositionAdapter(),
#                                                  update='_update_sample_table',
#                                                  multi_select=True,
#                                                  selected='selected',
#                                                  operations=['edit']
#                                                  ),
#                             show_label=False
#                             ),
#                        label='Lab Numbers',
#                        show_border=True
#                        )
# #        flux = Group(
# #                     HGroup(
# #                            Item('flux_monitor', show_label=False, editor=EnumEditor(name='flux_monitors')),
# #                            Item('edit_monitor_button', show_label=False)),
# #                     Item('flux_monitor_age', format_str='%0.3f', style='readonly', label='Monitor Age (Ma)'),
# #                     Spring(height=50, springy=False),
# #                     Item('calculate_flux_button',
# #                          enabled_when='calculate_flux_enabled',
# #                          show_label=False),
# #                     label='Flux',
# #                     show_border=True
# #                     )
#        v = View(VGroup(
#                        HGroup(auto, irradiation,
# #                               flux
#                               ),
#                        samples,
#                        HGroup(spring, Item('save_button', show_label=False))
#                        ),
#============= EOF =============================================

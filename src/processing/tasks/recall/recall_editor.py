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
from traits.api import Property, Instance, Any, DelegatesTo
from traitsui.api import View, UItem, InstanceEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.base_editor import BaseTraitsEditor
# from src.database.records.isotope_record import IsotopeRecord
# from src.database.records.isotope_record import IsotopeRecord


class RecallEditor(BaseTraitsEditor):

    model = Any

    analysis_summary = Any
#     analysis_summary = Any  # DelegatesTo('model')
#     analysis_summary = DelegatesTo('model')
    name = Property(depends_on='model')
#    def trait_context(self):
#        """ Use the model object for the Traits UI context, if appropriate.
#        """
#        if self.record:
#            return { 'object': self.record}
#
#        return super(RecallEditor, self).trait_context()
#     def _model_changed(self):
#         if self.model:
#             keys = self.model.isotope_keys
#             self.tool.load_fits(keys)
#     def _get_analysis_summary(self):
#         if self.model:
#             return self.model.analysis_summary

#     def _set_analysis_summary(self):


    def traits_view(self):
        v = View(
#                 Group(
#                  VFold(
                       UItem('analysis_summary',
                             editor=InstanceEditor(),
                             label='Summary',
                             style='custom'),
#                         UItem('signal_graph',
#                               style='custom',
#                               label='Signals',
# #                              defined_when='signal_graph'
#                               ),
#                         UItem('baseline_graph',
#                               style='custom',
# #                              defined_when='baseline_graph',
#                               label='Baselines',
#                               ),
#                         UItem('peak_center_graph',
#                               style='custom',
# #                              defined_when='peak_center_graph',
#                               label='Peak Center',
#                               ),
#                       layout='tabbed'
#                        ),
                resizable=True
               )
        return v

    def _create_control(self, parent):
        ui = self.edit_traits(kind='subpanel', parent=parent)
        self.ui = ui
        return ui.control

    def _get_name(self):
#         if self.analysis_summary:
#             return self.analysis_summary.record.record_id
        if self.model:
            return self.model.record_id
        else:
            return 'Untitled'

#============= EOF =============================================

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
from traits.api import HasTraits, List, Int, Any
from traitsui.api import View, Item, UItem, CheckListEditor

#============= standard library imports ========================
#============= local library imports  ==========================

class TableConfigurer(HasTraits):
    columns = List
    available_columns = List
    adapter = Any

    def _adapter_changed(self):
        #cols=self.adapter.column_dict.keys()
        adp = self.adapter

        #acols=adp.ocolumns
        #if not acols:
        #    adp.ocolumns=acols=[c for c,_ in adp.columns]
        acols = [c for c, _ in adp.all_columns]

        t = [c for c, _ in adp.columns]
        cols = [c for c in acols if c in t]

        self.trait_set(columns=cols, trait_change_notify=False)
        self.available_columns = acols

    def _columns_changed(self):
        cols = self._assemble_columns()
        self.adapter.columns = cols

    def _assemble_columns(self):
        d = self.adapter.all_columns_dict
        return [(k, d[k]) for k, _ in self.adapter.all_columns if k in self.columns]

    def traits_view(self):
        v = View(UItem('columns',
                       style='custom',
                       editor=CheckListEditor(name='available_columns', cols=3)),
                 buttons=['OK', 'Revert'],
                 kind='livemodal',
                 title=self.title,
                 resizable=True,
                 width=300
        )
        return v

#class SampleTableConfigurer(HasTraits):
#    column_mapper={'Sample':'name',
#                   'Material':'material'}
#    available_columns=(['Sample','Material'])
#
#class AnalysisTableConfigurer(HasTraits):
#
#    available_columns=(['Sample','Material'])
#============= EOF =============================================


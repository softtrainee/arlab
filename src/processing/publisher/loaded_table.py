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
from traits.api import HasTraits, List, Button, Any, Dict, cached_property, Property
from traitsui.api import View, Item, Controller, SetEditor, UItem, \
    HGroup, spring
#============= standard library imports ========================
import os
from uncertainties import ufloat
#============= local library imports  ==========================
from src.processing.autoupdate_parser import AutoupdateParser
from src.processing.publisher.analysis import PubAnalysis, Marker
from src.constants import ARGON_KEYS, PLUSMINUS
from src.traits_editors.tabular_editor import myTabularEditor
from traitsui.tabular_adapter import TabularAdapter


class LoadedTableAdapter(TabularAdapter):
    columns = Property(depends_on='visible_columns,visible_columns[]')
    visible_columns = List(['runid', 'age', 'age_error', 'k_ca'])
    column_m = {'runid':('RunID', 'runid'),
                'age':('Age', 'age'),
                'age_error':(u'{}1s'.format(PLUSMINUS), 'age_error'),
                'k_ca':('K/Ca', 'k_ca'),
                'labnumber':('Lab. #', 'labnumber')
                }
    age_text = Property
    age_error_text = Property
    def _get_age_error_text(self):
        return self._get_std_dev('age')

    def _get_age_text(self):
        return self._get_nominal_value('age')

    def _get_nominal_value(self, attr):
        v = getattr(self.item, attr)
        if not isinstance(v, str):
            v = v.nominal_value
        return v

    def _get_std_dev(self, attr):
        v = getattr(self.item, attr)
        if not isinstance(v, str):
            v = v.std_dev
        return v

    @cached_property
    def _get_columns(self):
        cols = []
        visible_columns = self.visible_columns
        for attr in visible_columns:
            cols.append(self.column_m[attr])

        return cols

class MeanLoadedTableAdapter(LoadedTableAdapter):
    visible_columns = ['labnumber', 'age']

class LoadedTableController(Controller):
    load_button = Button
    selected = Any
    columns_button = Button('Columns')
    columns = List
    column_dict = Dict({'RunID':'runid',
                        'Age':'age',
                        'AgeError':'age_error',
                        'K/Ca':'k_ca'
                        })

    def controller_load_button_changed(self, info):
        p = '/Users/ross/Sandbox/autoupdate_stepheat.txt'
        self.model.load(p)

    def controller_columns_button_changed(self, info):
        v = View(Item('controller.columns',
                      editor=SetEditor(ordered=True,
                                       values=['RunID', 'Age', 'AgeError', 'K/Ca']),
                      ),
                 buttons=['OK', 'Cancel'],
                 kind='livemodal'
                 )
        info = self.edit_traits(v)
        if info.result:
            cs = [self.column_dict[ci] for ci in self.columns]
            self._loaded_table_adapter.visible_columns = cs

    def traits_view(self):
        self._loaded_table_adapter = LoadedTableAdapter()
        self._mean_loaded_table_adapter = MeanLoadedTableAdapter()
        v = View(
                 HGroup(UItem('controller.columns_button'),
                        spring, UItem('controller.load_button')),
                 UItem('analyses', editor=myTabularEditor(
                                                          multi_select=True,
                                                          selected='controller.selected',
                                                          adapter=self._loaded_table_adapter)),
                 UItem('means', editor=myTabularEditor(
                                                          adapter=self._mean_loaded_table_adapter)),

                 )

        return v
#============= EOF =============================================

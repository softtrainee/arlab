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
from traits.api import Str, Password, Enum, List, Button, Any, Int, \
    on_trait_change, Bool
from traitsui.api import View, Item, Group, VGroup, HGroup, ListStrEditor
from src.envisage.tasks.base_preferences_helper import BasePreferencesHelper
from traitsui.list_str_adapter import ListStrAdapter
from envisage.ui.tasks.preferences_pane import PreferencesPane

#============= standard library imports ========================
#============= local library imports  ==========================


class ExtractionLinePreferences(BasePreferencesHelper):
    name = 'ExtractionLine'
    preferences_path = 'pychron.extraction_line'
    id = 'pychron.extraction_line.preferences_page'
    check_master_owner = Bool


class ExtractionLinePreferencesPane(PreferencesPane):
    model_factory = ExtractionLinePreferences
    category = 'ExtractionLine'
    def traits_view(self):
        vgrp = VGroup(
                    Item('check_master_owner',
                         label='Check Ownership',
                         tooltip='Check valve ownership even if this is the master computer'
                         ),

                    label='Valves'
                    )
        return View(
                    vgrp,

                    )

#============= EOF =============================================

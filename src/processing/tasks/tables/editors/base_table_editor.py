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
from traits.api import HasTraits, List, Any
from traitsui.api import View, Item
from src.envisage.tasks.base_editor import BaseTraitsEditor
from src.processing.tasks.tables.editors.adapters import TableBlank
#============= standard library imports ========================
#============= local library imports  ==========================

class BaseTableEditor(BaseTraitsEditor):
    items = List
    oitems = List
    col_widths = List
    selected = Any
    def clean_rows(self):
        return self._clean_items()

    def _clean_items(self):
        return filter(lambda x: not isinstance(x, TableBlank), self.oitems)
#============= EOF =============================================

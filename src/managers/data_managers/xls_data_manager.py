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
from traits.api import HasTraits
from traitsui.api import View, Item
from src.managers.data_managers.data_manager import DataManager
import xlrd
#============= standard library imports ========================
#============= local library imports  ==========================

class XLSDataManager(DataManager):
    def open(self, p):
        self.wb = xlrd.open_workbook(p)

    def get_column_idx(self, names, sheet=None):
        if isinstance(sheet, str):
            sheet = self.wb.sheet_by_name(sheet)
        elif isinstance(sheet, int):
            sheet = self.wb.sheet_by_index(sheet)

        if sheet:
            header = sheet.row_values(0)
            if not isinstance(names, (list, tuple)):
                names = (names,)

            for attr in names:
                for ai in (attr, attr.lower(), attr.upper()):
                    if ai in header:
                        return header.index(ai)
#============= EOF =============================================

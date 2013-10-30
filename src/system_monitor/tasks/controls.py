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
from traitsui.api import EnumEditor

#============= standard library imports ========================
#============= local library imports  ==========================
from traitsui.extras.checkbox_column import CheckboxColumn
from traitsui.table_column import ObjectColumn
from src.processing.tasks.analysis_edit.fits import FitSelector


class SystemMonitorControls(FitSelector):
    def _get_columns(self):
        cols = [ObjectColumn(name='name', editable=False),
                CheckboxColumn(name='show'),
                ObjectColumn(name='fit',
                             editor=EnumEditor(name='fit_types'),
                             width=75),
        ]

        return cols

    #============= EOF =============================================

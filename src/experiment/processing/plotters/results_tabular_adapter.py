#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, Str, Float, Property
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
#============= local library imports  ==========================

class ResultsTabularAdapter(TabularAdapter):
    columns = Property
    age_format = Str('%0.3f')
    error_format = Str('%0.3f')
    mswd_format = Str('%0.2f')

    default_columns = Property
    additional_columns = Property
    def _get_default_columns(self):
        return [('Age', 'age'),
               ('Error(1s)', 'error'),
               ('MSWD', 'mswd'),
             ]

    def _get_additional_columns(self):
        return []
    def _get_columns(self):
        return self.default_columns + self.additional_columns


class BaseResults(HasTraits):
    age = Float
    error = Float
    mswd = Float
    error_calc_method = Str

class IdeoResultsAdapter(ResultsTabularAdapter):
    pass
class InverseIsochronResultsAdapter(ResultsTabularAdapter):
    trapped_4036_format = Str('%0.2f')
    trapped_4036err_format = Str('%0.2f')

    def _get_additional_columns(self):
        return [('40/36_tr', 'trapped_4036'), ('40/36_tr err.', 'trapped_4036err')]
class SpectrumResultsAdapter(ResultsTabularAdapter):
    pass

class IdeoResults(BaseResults):
    pass
class InverseIsochronResults(BaseResults):
    trapped_4036 = Float
    trapped_4036err = Float

class SpectrumResults(BaseResults):
    pass
#============= EOF =============================================

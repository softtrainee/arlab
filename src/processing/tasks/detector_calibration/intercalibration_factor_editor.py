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
from traits.api import HasTraits, on_trait_change
from traitsui.api import View, Item
from src.processing.tasks.analysis_edit.interpolation_editor import InterpolationEditor
#============= standard library imports ========================
from numpy import array, Inf
from src.helpers.isotope_utils import sort_isotopes
#============= local library imports  ==========================

class IntercalibrationFactorEditor(InterpolationEditor):
    standard = 1.0

    @on_trait_change('unknowns[]')
    def _update_unknowns(self):

        '''
            TODO: find reference analyses using the current _unknowns
        '''
        self._make_unknowns()
        self.rebuild_graph()

    def _make_references(self):
        keys = set([ki  for ui in self._references
                        for ki in ui.isotope_keys])
        keys = sort_isotopes(keys)
        if 'Ar40' in keys and 'Ar36' in keys:
            self.tool.load_fits(['Ar40/Ar36'])

    def _set_interpolated_values(self, iso, reg, xs):
        p_uys = reg.predict(xs)
        p_ues = reg.predict_error(xs)
        return p_uys, p_ues

    def _get_reference_values(self, iso):
        n, d = iso.split('/')
        nys = array([ri.isotopes[n].uvalue for ri in self._references])
        dys = array([ri.isotopes[d].uvalue for ri in self._references])
        rys = nys / (dys * self.standard)


        rys = [ri.nominal_value for ri in rys]
        return rys, None
#============= EOF =============================================

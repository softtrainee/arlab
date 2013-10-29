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
from traits.api import HasTraits, List, Property, cached_property, Str, Any
from traitsui.api import View, UItem
#============= standard library imports ========================
import os
from uncertainties import ufloat
#============= local library imports  ==========================
from src.processing.autoupdate_parser import AutoupdateParser
from src.processing.publisher.analysis import Marker, PubAnalysis, ComputedValues  # , \
#    PubAnalysisMean
from src.pychron_constants import ARGON_KEYS, IRRADIATION_KEYS, DECAY_KEYS
from src.ui.tabular_editor import myTabularEditor
from src.processing.publisher.loaded_table import LoadedTableAdapter


class Group(HasTraits):
    analyses = List
    name = Str
    selected = Any
    right_clicked = Any

    def traits_view(self):
        self._loaded_table_adapter = LoadedTableAdapter()
        v = View(
            UItem('analyses', editor=myTabularEditor(
                multi_select=True,
                editable=False,
                selected='selected',
                adapter=self._loaded_table_adapter,
                right_clicked='right_clicked'
            )
            ),
        )
        return v


class TableModel(HasTraits):
    groups = List


class LoadedTable(TableModel):
    computed_values = Property(depends_on='groups, groups[]')

    @cached_property
    def _get_computed_values(self):
        return [ComputedValues(analyses=gi.analyses) for gi in self.groups]

    def load(self, p):
        ap = AutoupdateParser()
        if os.path.isfile(p):
            samples = ap.parse(p, self._analysis_factory)
            for i, si in enumerate(samples):
                self.groups.append(Group(analyses=si.analyses,
                                         name=si.analyses[0].labnumber
                ))

    def _analysis_factory(self, params):
        a = PubAnalysis()
        a.sample = params['sample']
        a.material = params['material']
        a.sample_group = params['sample_group']
        a.set_runid(params['run_id'])

        a.age = ufloat(params['age'], params['age_err'])
        a.k_ca = ufloat(params['k_ca'], params['k_ca_err'])
        a.j = ufloat(params['j'], params['j_err'])
        a.rad40_percent = ufloat(params['rad40_percent'], params['rad40_percent_err'])
        a.rad40 = ufloat(params['rad40'], params['rad40_err'])
        a.k39 = ufloat(1, 0)
        a.extract_value = params['power']

        for si in ARGON_KEYS:
            v = params[si]
            e = params['{}Er'.format(si)]
            #            print v, e
            setattr(a, si, ufloat(v, e))
            v = params['{}_blank'.format(si)]
            e = params['{}_blankerr'.format(si)]
            setattr(a, '{}_blank'.format(si), ufloat(v, e))

        for df, _ in DECAY_KEYS:
            setattr(a, df, params[df])

        for ir, _ in IRRADIATION_KEYS:
            setattr(a, ir, ufloat(params[ir],
                                  params['{}_err'.format(ir)]
            ))
        return a


class SelectedTable(TableModel):
    pass

#============= EOF =============================================

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
from traits.api import HasTraits, List, Property, cached_property
#============= standard library imports ========================
import os
from uncertainties import ufloat
#============= local library imports  ==========================
from src.processing.autoupdate_parser import AutoupdateParser
from src.processing.publisher.analysis import Marker, PubAnalysis, \
    PubAnalysisMean
from src.constants import ARGON_KEYS


class TableModel(HasTraits):
    analyses = List
    cleaned_analyses = Property(depends_on='analyses')
    grouped_analyses = Property(depends_on='analyses')

    @cached_property
    def _get_cleaned_analyses(self):
        return [ai for ai in self.analyses if not isinstance(ai, Marker)]

    @cached_property
    def _get_grouped_analyses(self):
        from itertools import groupby
        from operator import attrgetter
        return groupby(self.cleaned_analyses, attrgetter('sample_group'))

class LoadedTable(TableModel):
    means = Property(depends_on='analyses, analyses[]')
    @cached_property
    def _get_means(self):
        return [PubAnalysisMean(analyses=list(ans)) for i, ans in self.grouped_analyses]

    def load(self, p):
        ap = AutoupdateParser()
        if os.path.isfile(p):
            samples = ap.parse(p, self._analysis_factory)
            n = len(samples)
            ans = []
            for i, si in enumerate(samples):
                ans.extend(si.analyses)
                if i < (n - 1):
                    ans.append(Marker())
            self.analyses = ans

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

        return a

class SelectedTable(TableModel):
    pass

#============= EOF =============================================

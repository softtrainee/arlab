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
from traits.api import HasTraits, Str, List, Dict
from traitsui.api import View, Item
import struct
#============= standard library imports ========================
#============= local library imports  ==========================

class BaseNode(HasTraits):
    pass

class AnalysisNode(BaseNode):
    rid = Str('54341-01')
    sample = Str('py-2')
    irradiation = Str('PY-111')
    iso_series = Dict
    def _get_isotope_names(self):
        return ['Ar40', 'Ar39', 'Ar38', 'Ar36']
    isotope_names = property(fget=_get_isotope_names)

    def traits_view(self):
        v = View(
               Item('rid', style='readonly'),
               Item('sample', style='readonly'),
               Item('irradiation', style='readonly')
               )
        return v
    def add_iso_series(self, n, x, y):
        self.iso_series[n] = (x, y)

class ExperimentNode(BaseNode):
    name = Str('Exp1')
    analyses = List(BaseNode)
    experiments = List(BaseNode)

    def traits_view(self):
        v = View(
                 Item('name', show_label=False, style='readonly'),
                 )
        return v

    def load_database_reference(self, ref, kwargs):
        anode = AnalysisNode(**kwargs)

        #save peak regressions
        for iso in ref.isotopes:
            ps = iso.peak_time_series
            xs, ys = self.parse_timeblob(ps.PeakTimeBlob)
            anode.add_iso_series(iso.Label, xs, ys)

        self.analyses.append(anode)

    @classmethod
    def parse_timeblob(cls, blob):
        v, t = zip(*[struct.unpack('>ff', blob[i:i + 8]) for i in xrange(0, len(blob), 8)])
        return t, v
#============= EOF =============================================

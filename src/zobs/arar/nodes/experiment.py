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
from traits.api import Str, List, Any, Float, Int, Instance
from traitsui.api import View, Item, TabularEditor
#============= standard library imports ========================
import struct
#============= local library imports  ==========================
from analysis import AnalysisNode
from src.arar.nodes.series import SeriesNode

class ExperimentNode(SeriesNode):
    name = 'Experiment 1'
#    experiments = List(CoreNode)
#    airs = List(AnalysisNode)
#    blanks = List(AnalysisNode)
    series = List(SeriesNode)
#    air_series = Instance(SeriesNode, ())
#    blank_series = Instance(SeriesNode, ())
    selected_analysis = Any
    age = Float
    age_err = Float
    def _series_default(self):
        return [SeriesNode(name='airs'), SeriesNode(name='blanks')]

    def traits_view(self):
        def readonly(name, **kw):
            return Item(name, style='readonly', **kw)

        v = View(
                 readonly('name', show_label=False),
                 readonly('age', format_str='%0.3f'),
                 readonly('age_err', label='Error', format_str='%0.3f'),
                 self._get_analysis_grp()
                 )
        return v

    def has_node(self, node):
        return node in self.analyses

    def load_analysis_reference(self, ref, rid, kwargs):
        if not next((a for a in self.analyses if a.rid == rid), None):
            anode = self._analysis_factory(ref, rid, kwargs)
            self.analyses.append(anode)

    def _analysis_factory(self, ref, rid, kwargs):
        anode = AnalysisNode(rid=rid, **kwargs)

        # save peak regressions
        for iso in ref.isotopes:
            ps = iso.peak_time_series
            xs, ys = self.parse_timeblob(ps.PeakTimeBlob)
            anode.add_iso_series(iso.Label, xs, ys)
            r = iso.results[-1]
            label = iso.Label.lower()
            d = {label:r.Iso,
                       '{}_er'.format(label):r.IsoEr
                       }
            anode.trait_set(**d)
        return anode

    def load_series_reference(self, sname, ref, rid, kwargs):
        series = next((s for s in self.series if s.name == sname), None)
        if series:
            if not next((a for a in series.analyses if a.rid == rid), None):
                anode = self._analysis_factory(ref, rid, kwargs)
                series.analyses.append(anode)

    @classmethod
    def parse_timeblob(cls, blob):
        v, t = zip(*[struct.unpack('>ff', blob[i:i + 8]) for i in xrange(0, len(blob), 8)])
        return t, v

#============= EOF =============================================

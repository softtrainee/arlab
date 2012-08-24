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
from traits.api import Str, Float, Dict
from traitsui.api import View, Item, VGroup
#============= standard library imports ========================
import re
#============= local library imports  ==========================

from core import CoreNode
class AnalysisNode(CoreNode):
    rid = Str('54341-01')
    sample = Str('py-2')
    irradiation = Str('PY-111')
    iso_series = Dict
    age = Float
    age_err = Float
    def _get_isotope_names(self):

        return sorted(self.iso_series.keys(),
                      reverse=True,
                      key=lambda x: re.sub('\D', '', x))

    isotope_names = property(fget=_get_isotope_names)

    def traits_view(self):
        readonly = lambda n:Item(n, style='readonly')
        readonly_float = lambda n:Item(n, format_str='%0.3f', style='readonly')

        info_grp = VGroup(
                          readonly('rid'),
                          readonly('sample'),
                          readonly('irradiation'),
                          label='Summary',
                          show_border=True
                        )
        age_grp = VGroup(
                         readonly_float('age'),
                         readonly_float('age_err'),
                         label='Age',
                         show_border=True
                         )
        v = View(VGroup(info_grp, age_grp)
               )
        return v

    def add_iso_series(self, n, x, y):
        self.iso_series[n] = (x, y)

    def replot(self):
        n = len(self.isotope_names)
        r = 1
        c = 3
        if n % c:
            r = 2
        g = self._graph_factory((r, c))

        def axis_formatter(x):
            if x > 0.01:
                return '{:0.2f}'.format(x)
            else:
                return '{:0.2e}'.format(x)

        for i, iso in enumerate(self.isotope_names):
            g.new_plot(title=iso,
                       padding_right=5,
                       padding_top=20,
                       padding_left=75,
                       padding_bottom=50,
                       xtitle='Time (s)',
                       ytitle='Signal (fA)'
#                       fill_padding=True,
#                       bgcolor='yellow'
                       )

            g.set_axis_traits(tick_label_formatter=axis_formatter, plotid=i, axis='y')
#            g.set_axis_traits(plotid=i, axis='y')
            x, y = self.iso_series[iso]
#            x = range(10)
#            y = [i * i for i in x]
            g.new_series(x, y, type='scatter', marker='circle', marker_size=0.75)
        return g
#============= EOF =============================================

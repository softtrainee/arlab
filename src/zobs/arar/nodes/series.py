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
from traits.api import List, Str, Any
from traitsui.api import View, Item, TabularEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from core import CoreNode
from src.arar.nodes.analysis import AnalysesAdapter

class SeriesNode(CoreNode):
    analyses = List(CoreNode)
    column_clicked = Any
    reverse_sort = False
    _sort_field = None

    def traits_view(self):
        v = View(self._get_analysis_grp())
        return v

    def replot(self):
        if not self.analyses:
            return

        isos = zip(*[[getattr(a, isoname.lower()) for isoname in a.isotope_names] for a in self.analyses])

        n = len(a.isotope_names)
        c = 3
        r = n / c
        if n % c:
            r += 1

        def axis_formatter(x):
            if x > 0.01:
                return '{:0.2f}'.format(x)
            elif abs(x) < 1e-7:
                return '{:n}'.format(x)
            else:
                return '{:0.2e}'.format(x)

        g = self._graph_factory((r, c))
        for i, (ti, iso) in enumerate(zip(a.isotope_names, isos)):
            g.new_plot(title=ti,
                       padding_right=5,
                       padding_top=20,
                       padding_left=75,
                       padding_bottom=50,
                       xtitle='Analysis #',
                       ytitle='Signal (fA)')
            n = len(iso)
            x = range(n)
            g.new_series(x, iso, plotid=i,
                         type='scatter', marker='circle', marker_size=1.25)

            g.set_y_limits(min(iso), max(iso), pad='0.1', plotid=i)
            g.set_x_limits(0, n, pad=1, plotid=i)
            g.set_axis_traits(tick_label_formatter=axis_formatter, plotid=i, axis='y')

        return g

    def _sort_columns(self, values, field=None):
        # get the field to sort on
        if field is None:
            field = self._sort_field
            if field is None:
                return

        values.sort(key=lambda x: getattr(x, field),
                    reverse=self.reverse_sort)
        self._sort_field = field

    def _column_clicked_changed(self, event):
        values = event.editor.value

        fields = [name for _, name in event.editor.adapter.columns]
        field = fields[event.column]
        self.reverse_sort = not self.reverse_sort

        self._sort_columns(values, field)

    def _get_analysis_grp(self):
        g = Item('analyses',
                      show_label=False,
                      height=300,
                      editor=TabularEditor(adapter=AnalysesAdapter(),
                                           column_clicked='object.column_clicked',
                                           selected='object.selected_analysis',
                                           editable=False, operations=[]))
        return g

#============= EOF =============================================

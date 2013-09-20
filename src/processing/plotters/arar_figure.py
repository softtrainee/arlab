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
from traits.api import HasTraits, Any, Int, Str, Tuple, Property, \
    Event
from traitsui.api import View, Item
from chaco.tools.data_label_tool import DataLabelTool
#============= standard library imports ========================
#============= local library imports  ==========================
from src.stats.core import calculate_mswd, validate_mswd
from src.helpers.formatting import floatfmt
from src.processing.plotters.flow_label import FlowDataLabel

class BaseArArFigure(HasTraits):
    analyses = Any
    sorted_analyses = Property(depends_on='analyses')

    group_id = Int
    padding = Tuple((60, 10, 5, 40))
    ytitle = Str
    replot_needed = Event
    _reverse_sorted_analyses = False
    graph = Any

    options = Any

    def build(self, plots):
        '''
            make plots
        '''
        graph = self.graph
        p = graph.new_plot(ytitle=self.ytitle,
                       padding=self.padding
                       )
        p.value_range.tight_bounds = False

        for po in plots:
            p = graph.new_plot(padding=self.padding,
                           bounds=[50, po.height])
            p.value_range.tight_bounds = False

        self.graph = graph

    def plot(self, *args, **kw):
        pass


    def _get_mswd(self, ages, errors):
        mswd = calculate_mswd(ages, errors)
        n = len(ages)
        valid_mswd = validate_mswd(mswd, n)
        return mswd, valid_mswd, n

    def _cmp_analyses(self, x):
        return x.timestamp

    def _unpack_attr(self, attr):
        return (getattr(ai, attr) for ai in self.sorted_analyses)

    def _set_y_limits(self, a, b, min_=None, max_=None,
                        pid=0, pad=None):
        mi, ma = self.graph.get_y_limits(plotid=pid)
        mi = min(mi, a)
        ma = max(ma, b)
        if min_ is not None:
            mi = min_
        if max_ is not None:
            ma = max_
        self.graph.set_y_limits(min_=mi, max_=ma, pad=pad)

#===========================================================================
# aux plots
#===========================================================================
    def _plot_radiogenic_yield(self, po, plot, pid):

        ys, es = zip(*[(ai.nominal_value, ai.std_dev)
                       for ai in self._unpack_attr('rad40_percent')])
        return self._plot_aux('%40Ar*', 'rad40_percent', ys, po, plot, pid, es)

    def _plot_kcl(self, po, plot, pid):
        ys, es = zip(*[(ai.nominal_value, ai.std_dev)
                       for ai in self._unpack_attr('kcl')])
        return self._plot_aux('K/Cl', 'kcl', ys, po, plot, pid, es)

    def _plot_kca(self, po, plot, pid):
        ys, es = zip(*[(ai.nominal_value, ai.std_dev)
                       for ai in self._unpack_attr('kca')])
        return self._plot_aux('K/Ca', 'kca', ys, po, plot, pid, es)

    def _plot_moles_K39(self, po, plot, pid):
        ys, es = zip(*[(ai.nominal_value, ai.std_dev)
                       for ai in self._unpack_attr('k39')])

        return self._plot_aux('K39(fA)', 'k39', ys, po, plot, pid, es)
#===============================================================================
# labels
#===============================================================================
    def _add_data_label(self, s, text, point, bgcolor='transparent',
                        label_position='top right', color=None, append=True, **kw):
        if color is None:
            color = s.color

        label = FlowDataLabel(component=s, data_point=point,
                          label_position=label_position,
                          label_text=text,
                          border_visible=False,
                          bgcolor=bgcolor,
                          show_label_coords=False,
                          marker_visible=False,
                          text_color=color,

                          # setting the arrow to visible causes an error when reading with illustrator
                          # if the arrow is not drawn
                          arrow_visible=False,
                          **kw
                          )
        s.overlays.append(label)
        tool = DataLabelTool(label)
        if append:
            label.tools.append(tool)
        else:
            label.tools.insert(0, tool)
        return label

    def _build_label_text(self, x, we, mswd, valid_mswd, n):
        display_n = True
        display_mswd = n >= 2
        if display_n:
            n = 'n= {}'.format(n)
        else:
            n = ''

        if display_mswd:
            vd = '' if valid_mswd else '*'
            mswd = '{}mswd= {:0.2f}'.format(vd, mswd)
        else:
            mswd = ''

        x = floatfmt(x, 3)
        we = floatfmt(we, 4)
        pm = '+/-'

        return u'{} {}{} {} {}'.format(x, pm, we, mswd, n)

#===============================================================================
# property get/set
#===============================================================================
    def _get_sorted_analyses(self):
        return sorted([a for a in self.analyses],
                      key=self._cmp_analyses,
                      reverse=self._reverse_sorted_analyses
                      )
#============= EOF =============================================

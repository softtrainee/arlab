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
from traits.api import HasTraits, Property, Instance, on_trait_change, Any, \
    cached_property, Int, Button, Event, DelegatesTo
from traitsui.api import View, Item, HGroup, Group, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
from kiva.fonttools import Font
#============= standard library imports ========================
# import numpy as np
from numpy import Inf, array, random
import re
#============= local library imports  ==========================
from src.database.isotope_analysis.summary import Summary
from src.graph.graph import Graph
from src.database.orms.isotope_orm import proc_SelectedHistoriesTable
from src.constants import PLUSMINUS
import time


class HistoryView(HasTraits):
    summary = Any
    apply = Button
    applied_history = Event

    selected_history = Any

    def _apply_fired(self):
        summary = self.summary
        dbhist = summary.selected_history.history
        record = summary.record
        selhistory = record.selected_histories
        if not selhistory:
            selhistory = proc_SelectedHistoriesTable(analysis=record)

        setattr(selhistory, summary.apply_name, dbhist)
        self.summary.oselected_history = summary.selected_history
        self.applied_history = summary.selected_history

    def traits_view(self):
        v = View(Group(
                          Item('object.summary.histories', show_label=False,
                          editor=TabularEditor(
                                     adapter=HistoryTabularAdapter(),
                                     editable=False,
                                     operations=[],
                                     auto_update=True,
                                     horizontal_lines=True,
                                     selected='object.selected_history')),
                          Item('apply',
                               enabled_when='summary.selected_history!=summary.oselected_history',
                               show_label=False),
                          show_border=True,
                          label='histories',
                        )
                 )
        return v

class HistoryTabularAdapter(TabularAdapter):
    columns = [('User', 'user'), ('Date', 'create_date')]

    user_text = Property
    user_width = Int(50)
    create_date_width = Int(120)

    def get_font(self, obj, trait, row):
        import wx
        s = 9
        name = 'Bitstream Vera Sans Mono'
        return Font(name)


    def _get_user_text(self):
        u = self.item.user
        return u if u is not None else '---'

class History(HasTraits):
    history = Any

    @cached_property
    def _get_user(self):
        return self.summary.user

    @cached_property
    def _get_create_date(self):
        return self.summary.create_date

    def __getattr__(self, attr):
        return getattr(self.history, attr)

class HistorySummary(Summary):
    histories = Property
    graph = Instance(Graph)
    history_view = Instance(HistoryView)
    selected_history = DelegatesTo('history_view')
    history_name = ''
    def _graph_default(self):
        g = Graph(container_dict=dict(padding=5, stack_order='top_to_bottom'))
        g.width = self.record.item_width * 0.73
        return g

    def _history_view_default(self):
        return HistoryView(summary=self)

    def refresh(self):
        hist = None
        if self.histories:
            selh = self.record._dbrecord.selected_histories
            hist = getattr(selh, self.apply_name)

            sh = next((hi for hi in self.histories if hi.history == hist), None)

            super(HistorySummary, self).build_summary(history=hist)

            self.oselected_history = sh
            self.selected_history = None
            self.selected_history = sh



    def _get_isotope_keys(self, history, name):
        isokeys = sorted([bi.isotope for bi in getattr(history, name)
#                              if bi.use_set
                          ],
                         key=lambda x:re.sub('\D', '', x),
                       reverse=True)
        return isokeys

    @on_trait_change('selected_history')
    def _update_summary(self):
        if self.selected_history:
            self._build_summary()

    @cached_property
    def _get_histories(self):
        hn = self.history_name
        dbr = self.record._dbrecord
        return [History(history=hii) for hii in getattr(dbr, '{}_histories'.format(hn))]

    def _build_summary(self, history=None):
        if self.histories:
            if history is None:
                if self.selected_history:
                    history = self.selected_history

            if history:
                self._build_graph(history)

    def _build_graph(self, hi):
        hn = self.history_name
        dbr = self.record
#
        g = self.graph
        g.clear()
#        self.graph = g
        isokeys = self._get_isotope_keys(hi, hn)
        xma = -Inf
        xmi = Inf

        for i, iso in enumerate(isokeys):
            bi = next((bii for bii in getattr(hi, hn)
                       if bii.isotope == iso), None)

            g.new_plot(padding=[50, 5, 30, 5],
                       title=iso

                       )
            if bi.use_set:
#                xs = [dbr.make_timestamp(str(bs.analysis.rundate),
#                                         str(bs.analysis.runtime)) for bs in bi.sets]
                xs = [time.mktime(bs.analysis.analysis_timestamp.timetuple()) for bs in bi.sets ]
                xs = array(xs)
                if xs.shape[0]:
                    xs = xs - min(xs)
                    ys = random.random(xs.shape[0])
                    g.new_series(xs, ys, type='scatter')
                    xma = max(xma, max(xs))
                    xmi = min(xmi, min(xs))
            else:
                uv = bi.user_value
                ue = bi.user_error
                g.set_plot_title('{} {:0.5f} {}{:0.6f}'.format(iso, uv, PLUSMINUS, ue), plotid=i)

                kw = dict(plotid=i, color=(1, 0, 0))
                g.add_horizontal_rule(uv, line_style='solid',
                                      **kw)
                kw = dict(plotid=i, color=(0, 0, 0))
                g.add_horizontal_rule(uv + ue, **kw)
                g.add_horizontal_rule(uv - ue, **kw)
                g.set_y_limits(min=uv - ue,
                               max=uv + ue, pad='0.1', plotid=i)


    def traits_view(self):
        v = View(HGroup(
                        Item('history_view', style='custom',
                             show_label=False,
                             width=0.27),
                        Item('graph', show_label=False,
                             style='custom',
                             width=0.73
                             )
                        )
                 )

        return v
#============= EOF =============================================

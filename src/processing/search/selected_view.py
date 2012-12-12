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
from traits.api import HasTraits, Button, Bool, Int, Property, List, Any
from traitsui.api import View, Item, VGroup, HGroup, TabularEditor, EnumEditor
from traitsui.tabular_adapter import TabularAdapter
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.paths import paths
from src.database.core.database_selector import ColumnSorterMixin
from src.processing.search.previous_selection import PreviousSelection
from src.database.records.isotope_record import IsotopeRecord


class SelectedrecordsAdapter(TabularAdapter):
    labnumber_width = Int(90)
    rid_width = Int(50)

    aliquot_text = Property
#    rid_text = Property
    text_color = Property
    font = 'monospace'

    def _get_text_color(self):
        return self.item.color

    def _columns_default(self):
        cols = [
                ('Labnumber', 'labnumber'),
                ('Aliquot', 'aliquot'),
                ('Group', 'group_id'),
                ('Graph', 'graph_id')
                ]
        return cols

    def _get_aliquot_text(self, trait, item):
        return '{}{}'.format(self.item.aliquot, self.item.step)

class Marker(HasTraits):
    color = 'white'
    def __getattr__(self, attr):
        return ' '

class SelectedView(ColumnSorterMixin):
    selector = Any

    set_group = Button('Set Group')
    set_graph = Button('Set Graph')
    graph_by_labnumber = Button('Graph By Labnumber')
    group_by_labnumber = Button('Group By Labnumber')
    _grouped_by_labnumber = Bool(False)
    _graphed_by_labnumber = Bool(False)
    group_cnt = 0
    graph_cnt = 0

    selected_records = List
    dclicked = Any

    selected_row = Any
    selected = Any

    previous_selection = Any#Instance(PreviousSelection)
    previous_selections = List(PreviousSelection)

    def load_previous_selections(self):
        ps = []
        p = os.path.join(paths.hidden_dir, 'stored_selections')
        if os.path.isdir(p):
            for si in os.listdir(p):
                if si.startswith('.'):
                    continue
                with open(os.path.join(p, si), 'r') as fp:
                    ss = pickle.load(fp)
                    ps.append(ss)

        self.previous_selections = ps

    def dump_selection(self):
        records = self.selected_records
        if not records:
            return

        ans = [ai.dbrecord.id  for ai in records]

        s = records[0]
        e = records[-1]

        name = '{} - {}'.format(s.record_id, e.record_id)

        ps = PreviousSelection(analysis_ids=ans,
                               name=name
                               )
        p = os.path.join(paths.hidden_dir, 'stored_selections')
        if not os.path.isdir(p):
            os.mkdir(p)

        with open(os.path.join(p, name), 'w') as fp:
            pickle.dump(ps, fp)

#===============================================================================
# grouping
#===============================================================================
    def _group_by_labnumber(self):
        groups = dict()
        for ri in self.selected_records:
            if ri.labnumber in groups:
                group = groups[ri.labnumber]
                group.append(ri.labnumber)
            else:
                groups[ri.labnumber] = [ri.labnumber]

        keys = sorted(groups.keys())
        return keys

    def _set_grouping(self, attr, keys):
        pid = 0
        inserts = []
        for i, ri in enumerate(self.selected_records):
            if isinstance(ri, Marker):
                continue

            setattr(ri, attr, keys.index(ri.labnumber))
#            ri.group_id = keys.index(ri.labnumber)
            if getattr(ri, attr) != pid:
                inserts.append(i)
                pid = getattr(ri, attr)

        for i, ii in enumerate(inserts):
            if not isinstance(self.selected_records[ii + i - 1], Marker):
                self.selected_records.insert(ii + i, Marker())

    def _reset_grouping(self, attr):
        func = lambda x: not isinstance(x, Marker)
        nri = filter(func, self.selected_records)
        for ri in nri:
            setattr(ri, attr, 0)

        self.selected_records = nri

#===============================================================================
# handlers
#===============================================================================
    def _previous_selection_changed(self):
        db = self.selector.db
        ps = [IsotopeRecord(_dbrecord=db.get_analysis_record(si))
              for si in self.previous_selection.analysis_ids]
        self.selected_records = ps

    def _dclicked_changed(self):
        self.selector.open_record(self.selected)

    def _group_by_labnumber_fired(self):
        if self._grouped_by_labnumber:
            self._reset_grouping('group_id')
            if self._graphed_by_labnumber:
                keys = self._group_by_labnumber()
                self._set_grouping('graph_id', keys)
        else:
            keys = self._group_by_labnumber()
            self._set_grouping('group_id', keys)

        self._grouped_by_labnumber = not self._grouped_by_labnumber

    def _graph_by_labnumber_fired(self):
        if self._graphed_by_labnumber:
            self._reset_grouping('graph_id')
            if self._grouped_by_labnumber:
                keys = self._group_by_labnumber()
                self._set_grouping('group_id', keys)
        else:
            keys = self._group_by_labnumber()
            self._set_grouping('graph_id', keys)
        self._graphed_by_labnumber = not self._graphed_by_labnumber

    def _set_group_fired(self):
        self.group_cnt += 1
        for r in self.selected:
            r.group_id = self.group_cnt
#            r.color = 'red'

        oruns = set(self.selected_records) ^ set(self.selected)
        self.selected_records = list(oruns) + [Marker()] + self.selected

    def _set_graph_fired(self):
        self.graph_cnt += 1
        for r in self.selected:
            r.graph_id = self.graph_cnt
#            r.color = 'red'

        oruns = set(self.selected_records) ^ set(self.selected)
        self.selected_records = list(oruns) + [Marker()] + self.selected

    def traits_view(self):
        grouping_grp = VGroup(
                              HGroup(Item('set_group', show_label=False),
                                     Item('group_by_labnumber', show_label=False)),
                              HGroup(Item('set_graph', show_label=False),
                                     Item('graph_by_labnumber', show_label=False))
                              )

        selected_grp = VGroup(
                              Item('previous_selection', show_label=False,
                                   editor=EnumEditor(name='previous_selections')
                                   ),

                              Item('selected_records',
                                          show_label=False,
                                          style='custom',
                                          editor=TabularEditor(
                                                               multi_select=True,
                                                               auto_update=True,
                                                        editable=False,
#                                                        drag_move=True,
                                                        dclicked='object.dclicked',
                                                        selected='object.selected',
                                                        selected_row='object.selected_row',
                                                        column_clicked='object.column_clicked',
                                                        adapter=SelectedrecordsAdapter(),
                                                        ),
                                          ),

                              )

        v = View(
                 VGroup(
                        selected_grp,
                        grouping_grp
                        ),
                 )
        return v
#============= EOF =============================================

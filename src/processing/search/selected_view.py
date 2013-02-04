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
#============= standard library imports ========================
import os
import shelve
#============= local library imports  ==========================
from src.paths import paths
from src.database.core.database_selector import ColumnSorterMixin
from src.processing.search.previous_selection import PreviousSelection
from src.database.records.isotope_record import IsotopeRecord, IsotopeRecordView
from src.processing.analysis import Marker
from src.helpers.color_generators import colornames
import hashlib


class SelectedrecordsAdapter(TabularAdapter):
    labnumber_width = Int(90)
    rid_width = Int(50)

    aliquot_text = Property
#    rid_text = Property
#    text_color = Property
    font = 'monospace'

    def get_text_color(self, obj, trait, row):
        if isinstance(self.item, Marker):
            color = 'white'
        else:
            gid = self.item.group_id
            color = colornames[gid]
        return color

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

#class Marker(HasTraits):
#    color = 'white'
#    def __getattr__(self, attr):
#        return ' '

class SelectedView(ColumnSorterMixin):
    selector = Any

    set_group = Button('Set Group')
    set_graph = Button('Set Graph')
    graph_by_labnumber = Button('Graph By Labnumber')
    group_by_labnumber = Button('Group By Labnumber')
    group_by_aliquot = Button('Group By Aliquot')
    clear_group = Button('Clear Grouping')
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

    def _open_shelve(self):
        p = os.path.join(paths.hidden_dir, 'stored_selections')
        d = shelve.open(p)
        return d

    def load_previous_selections(self):
#        ps = []
#        p = os.path.join(paths.hidden_dir, 'stored_selections')
#        if os.path.isdir(p):
#            for si in os.listdir(p):
#                if si.startswith('.'):
#                    continue
#                with open(os.path.join(p, si), 'r') as fp:
#                    try:
#                        ss = pickle.load(fp)
#                        ps.append(ss)
#                    except Exception:
#                        pass
#        self.previous_selections = ps

        d = self._open_shelve()
        keys = sorted(d.keys(), reverse=True)
        self.previous_selections = [d[ki] for ki in keys]

    def dump_selection(self):
        records = self.selected_records
        if not records:
            return

        def make_name(rec):
            s = rec[0]
            e = rec[-1]
            return '{} - {}'.format(s.record_id, e.record_id)

        def make_hash(rec):
            md5 = hashlib.md5()
            for r in rec:
                md5.update('{}{}{}'.format(r.uuid, r.group_id, r.graph_id))
            return md5.hexdigest()

        d = self._open_shelve()

        name = make_name(records)
        ha = make_hash(records)
        ha_exists = next((True for pi in d.itervalues() if pi.hash_str == ha), False)

        if not ha_exists:
            keys = sorted(d.keys())
            next_key = '001'
            if keys:
                next_key = '{:03n}'.format(int(keys[-1]) + 1)

            records = filter(lambda ri:not isinstance(ri, Marker), records)

            name_exists = next((True for pi in d.itervalues() if pi.name == name), False)
            if name_exists:
                stored_name = sum([1 for pi in d.itervalues() if pi.name == name])
                if stored_name:
                    name = '{} ({})'.format(name, stored_name)

            ps = PreviousSelection(records, hash_str=ha, name=name)

            d[next_key] = ps

        d.close()

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

    def _group_by_aliquot(self):
        groups = dict()
        for ri in self.selected_records:
            name = '{}-{}'.format(ri.labnumber, ri.aliquot)
            if name in groups:
                group = groups[name]
                group.append(ri)
            else:
                groups[name] = [ri]

        keys = sorted(groups.keys())
        return keys

    def _set_grouping(self, attr, keys=None, identifier_func=None):
        pid = 0
        inserts = []

        if identifier_func is None:
            identifier_func = lambda x:x.labnumber

        for i, ri in enumerate(self.selected_records):
            if isinstance(ri, Marker):
                continue
            if keys:
                idn = identifier_func(ri)
                setattr(ri, attr, keys.index(idn))

            if getattr(ri, attr) != pid:
                inserts.append(i)
                pid = getattr(ri, attr)

        self._set_markers(inserts)

    def _set_markers(self, inserts):
        for i, ii in enumerate(inserts):
            if not isinstance(self.selected_records[ii + i - 1], Marker):
                self.selected_records.insert(ii + i, Marker())

    def _reset_grouping(self, attr):
#        func = lambda x: not isinstance(x, Marker)
#        nri = filter(func, self.selected_records)
        remove = []
        for ri in self.selected_records:
            setattr(ri, attr, 0)
            if isinstance(ri, Marker):
                remove.append(ri)
#                self.selected_records.remove(ri)
#            else:
#        for ri in self.selected_records:
        for ri in remove:
            self.selected_records.remove(ri)
#        for ri in nri:
#            setattr(ri, attr, 0)

#        self.selected_records = nri

#===============================================================================
# handlers
#===============================================================================
    def _previous_selection_changed(self):
        print self.previous_selection
        if self.previous_selection:
            db = self.selector.db
            def func(pi):
                iso = IsotopeRecordView(
                              graph_id=pi.graph_id,
                              group_id=pi.group_id
                              )
                dbrecord = db.get_analysis_uuid(pi.uuid)
                iso.create(dbrecord)
                return iso

            ps = [func(si) for si in self.previous_selection.analysis_ids]

            self.selected_records = ps
            self._set_grouping('graph_id')
            self._set_grouping('group_id')

    def _dclicked_changed(self):
        self.selector.open_record(self.selected)

    def _group_by_labnumber_fired(self):
        if self._grouped_by_labnumber:
            self._reset_grouping('group_id')

            keys = self._group_by_labnumber()
            self._set_grouping('group_id', keys)
            if self._graphed_by_labnumber:
                self._set_grouping('graph_id', keys)
        else:
            keys = self._group_by_labnumber()
            self._set_grouping('group_id', keys)

        self._grouped_by_labnumber = not self._grouped_by_labnumber

    def _group_by_aliquot_fired(self):
        self._reset_grouping('group_id')

        keys = self._group_by_aliquot()
        self._set_grouping('group_id', keys, identifier_func=lambda x:'{}-{}'.format(x.labnumber, x.aliquot))
#        if self._grouped_by_labnumber:
#            self._reset_grouping('group_id')
#
#            keys = self._group_by_labnumber()
#            self._set_grouping('group_id', keys)
#            if self._graphed_by_labnumber:
#                self._set_grouping('graph_id', keys)
#        else:
#            keys = self._group_by_labnumber()
#            self._set_grouping('group_id', keys)
#
#        self._grouped_by_labnumber = not self._grouped_by_labnumber

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
        if self.selected:
            self.group_cnt += 1
            for r in self.selected:
                r.group_id = self.group_cnt
#            r.color = 'red'

            oruns = set(self.selected_records) ^ set(self.selected)
            self.selected_records = list(oruns) + [Marker()] + self.selected

    def _set_graph_fired(self):
        if self.selected:
            self.graph_cnt += 1
            for r in self.selected:
                r.graph_id = self.graph_cnt
    #            r.color = 'red'

            oruns = set(self.selected_records) ^ set(self.selected)
            self.selected_records = list(oruns) + [Marker()] + self.selected

    def _clear_group_fired(self):
        self._reset_grouping('group_id')

    def traits_view(self):
        grouping_grp = VGroup(
                              Item('clear_group', show_label=False),
                              HGroup(Item('set_group',
                                          tooltip='Highlight a set of runs then Set Group',
                                          show_label=False),
                                     Item('group_by_labnumber', show_label=False,
                                          tooltip='Group analyses based on Labnumber'),
                                     Item('group_by_aliquot', show_label=False,
                                          tooltip='Group analyses based on Labnumber')
                                     ),
                              HGroup(Item('set_graph', show_label=False,
                                          tooltip='Highlight a set of runs to group in to multiple graphs'),
                                     Item('graph_by_labnumber', show_label=False,
                                          tooltip='Group analyses into graphes bases on Labnumber')
                                    )
                              )

        selected_grp = VGroup(
                              Item('previous_selection', show_label=False,
                                   editor=EnumEditor(name='previous_selections'),
                                   tooltip='List of previous selected analyses'),
                              Item('selected_records',
                                   show_label=False,
                                   style='custom',
                                   editor=TabularEditor(
                                                       multi_select=True,
                                                       auto_update=True,
                                                       editable=False,
                                                       dclicked='object.dclicked',
                                                       selected='object.selected',
                                                       selected_row='object.selected_row',
                                                       column_clicked='object.column_clicked',
                                                       adapter=SelectedrecordsAdapter())
                                   )
                              )

        v = View(
                 VGroup(
                        selected_grp,
                        grouping_grp
                        )
                 )
        return v
#============= EOF =============================================

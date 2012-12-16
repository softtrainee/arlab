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
from traits.api import HasTraits, Property, List, Button, Str, Bool, Any, Int, \
    Instance, DelegatesTo
from traitsui.api import View, Item, VGroup, HGroup, HSplit, spring, \
    InstanceEditor, EnumEditor, TabularEditor, UItem
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.processing.search.search_manager import SearchManager
from src.paths import paths
from src.constants import NULL_STR
from traitsui.tabular_adapter import TabularAdapter
from src.processing.search.selected_view import SelectedView
from src.processing.search.selector_view import SelectorView

#class Marker(HasTraits):
#    color = 'white'
#    def __getattr__(self, attr):
#        return ' '

class StoredSelection(HasTraits):
    analysis_ids = List

class InstanceUItem(UItem):
    """Convenience class for including an Instance in a View"""
    style = Str('custom')
    editor = Instance(InstanceEditor, ())


class SelectorManager(SearchManager):
    selected_view = Instance(SelectedView)
    selector_view = Instance(SelectorView)
    selected_records = DelegatesTo('selected_view')

    def _selected_view_default(self):
        sv = SelectedView()
        return sv

    def _selector_view_default(self):
        sv = SelectorView(selected_view=self.selected_view)
        return sv

    def _db_changed(self):
        self.selected_view.selector = self.selector
        self.selector_view.selector = self.selector

#===============================================================================
# view
#===============================================================================
    def traits_view(self):
        cntrl_grp = self._get_control_group()
        v = View(
                 HGroup(
                        cntrl_grp,
                        InstanceUItem('selector_view', width=0.6),
                        InstanceUItem('selected_view', width=0.25)
                      ),
                  handler=self.handler_klass,
                  buttons=['OK', 'Cancel'],
#                  width=900,
                  height=500,
                  resizable=True,
                  id='processing_selector',
                  title='Select Analyses'
               )

        return v
#============= EOF =============================================

    def select_labnumber(self, ln):
        db = self.db
        selector = db.selector
        if isinstance(ln, list):
            for li in ln:
                rs = db.get_labnumber(li)
                selector.load_records(rs.analyses, load=False, append=True)

            self.selected_records = selector.records
#            self._graph_by_labnumber_fired()
        else:
            rs = db.get_labnumber(ln)
            selector.load_records(rs.analyses, load=False)
            self.selected_records = selector.records

    def opened(self):
        self.selected_view.load_previous_selections()

    def close(self, isok):
        if isok:
            self.selected_view.dump_selection()
        return True

#    def _load_stored_selections(self):
#        p = os.path.join(paths.hidden_dir, 'stored_selections')
#        if os.path.isfile(p):
#            pass
#        for si in os.listdir(p):
#            if si.startswith('.'):
#                continue
#            ss = StoredSelection()
#            ss



#    def _load_selected_records(self):
#        for r in self.selector.selected:
#            if r not in self.selected_records:
#                self.selected_records.append(r)
#
#        self.selected_row = self.selected_records[-1]


#    def close(self, isok):
#        if isok:
#            self.update_data = True
#        return True

#    def _group_by_labnumber(self):
#
#        groups = dict()
#        for ri in self.selected_records:
#            if ri.labnumber in groups:
#                group = groups[ri.labnumber]
#                group.append(ri.labnumber)
#            else:
#                groups[ri.labnumber] = [ri.labnumber]
#
#        keys = sorted(groups.keys())
#        return keys
#
#    def _set_grouping(self, attr, keys):
#        pid = 0
#        inserts = []
#        for i, ri in enumerate(self.selected_records):
#            if isinstance(ri, Marker):
#                continue
#
#            setattr(ri, attr, keys.index(ri.labnumber))
##            ri.group_id = keys.index(ri.labnumber)
#            if getattr(ri, attr) != pid:
#                inserts.append(i)
#                pid = getattr(ri, attr)
#
#        for i, ii in enumerate(inserts):
#            if not isinstance(self.selected_records[ii + i - 1], Marker):
#                self.selected_records.insert(ii + i, Marker())
#
#    def _reset_grouping(self, attr):
#        func = lambda x: not isinstance(x, Marker)
#        nri = filter(func, self.selected_records)
#        for ri in nri:
#            setattr(ri, attr, 0)
#
#        self.selected_records = nri

#===============================================================================
# handlers
#===============================================================================
#    def _group_by_labnumber_fired(self):
#        if self._grouped_by_labnumber:
#            self._reset_grouping('group_id')
#            if self._graphed_by_labnumber:
#                keys = self._group_by_labnumber()
#                self._set_grouping('graph_id', keys)
#        else:
#            keys = self._group_by_labnumber()
#            self._set_grouping('group_id', keys)
#
#        self._grouped_by_labnumber = not self._grouped_by_labnumber
#
#    def _graph_by_labnumber_fired(self):
#        if self._graphed_by_labnumber:
#            self._reset_grouping('graph_id')
#            if self._grouped_by_labnumber:
#                keys = self._group_by_labnumber()
#                self._set_grouping('group_id', keys)
#        else:
#            keys = self._group_by_labnumber()
#            self._set_grouping('graph_id', keys)
#        self._graphed_by_labnumber = not self._graphed_by_labnumber
#
#    def _set_group_fired(self):
#        self.group_cnt += 1
#        for r in self.selected:
#            r.group_id = self.group_cnt
##            r.color = 'red'
#
#        oruns = set(self.selected_records) ^ set(self.selected)
#        self.selected_records = list(oruns) + [Marker()] + self.selected
#
#    def _set_graph_fired(self):
#        self.graph_cnt += 1
#        for r in self.selected:
#            r.graph_id = self.graph_cnt
##            r.color = 'red'
#
#        oruns = set(self.selected_records) ^ set(self.selected)
#        self.selected_records = list(oruns) + [Marker()] + self.selected

#    def _add_mean_marker_fired(self):
#        pass

#    def _append_fired(self):
#        self._load_selected_records()
#
#    def _replace_fired(self):
#        self.selected_records = []
#        self._load_selected_records()

#    def _analysis_type_changed(self):
#        self._refresh_results()
#
#    def _project_changed(self):
#        self._refresh_results()
#
#    def _machine_changed(self):
#        self._refresh_results()
#
#    def _refresh_results(self):
#        selector = self.selector
#
#        ma = self.machine
#        pr = self.project
#        an = self.analysis_type
#
#        qs = []
#        if pr != NULL_STR:
#            q = selector.query_factory(parameter='Project', criterion=pr)
#            qs.append(q)
#        if ma != NULL_STR:
#            q = selector.query_factory(parameter='Mass Spectrometer', criterion=ma)
#            qs.append(q)
#        if an != NULL_STR:
#            q = selector.query_factory(parameter='Analysis Type', criterion=an)
#            qs.append(q)
#
#        selector.execute_query(queries=qs, load=False)
#
#    def _dclicked_changed(self):
#        self.selector.open_record(self.selected)
#===============================================================================
# property get/set
#===============================================================================


#    def _get_projects(self):
#        db = self.db
##        db.reset()
#        prs = ['---', 'recent']
#        ps = db.get_projects()
#        if ps:
#            prs += [p.name for p in ps]
#        return prs
#
#    def _get_machines(self):
#        db = self.db
##        db.reset()
#        mas = ['---']
#        ms = db.get_mass_spectrometers()
#        if ms:
#            mas += [m.name for m in ms]
#        return mas
#
#    def _get_analysis_types(self):
#        db = self.db
#        ats = ['---']
#        ai = db.get_analysis_types()
#        if ai:
#            ats += [aii.name.capitalize() for aii in ai]
#
#        return ats
##        return ['Blank', 'Air', 'Unknown']

#    def _get_selected_record_labels(self):
#        return ['{} {}'.format(r.rid, r.labnumber) for r in self.selected_records]



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
from traits.api import HasTraits, Button, List, Instance, Property, Any, Event, Bool
from traitsui.api import View, Item, UItem, HGroup, VGroup, spring, EnumEditor
from pyface.tasks.traits_dock_pane import TraitsDockPane
from src.ui.tabular_editor import myTabularEditor
from src.processing.tasks.analysis_edit.ianalysis_edit_tool import IAnalysisEditTool
# from src.processing.search.previous_selection import PreviousSelection
import os
from src.paths import paths
import shelve
import hashlib
from src.processing.analysis import Marker
from src.processing.selection.previous_selection import PreviousSelection
#============= standard library imports ========================
#============= local library imports  ==========================

class TablePane(TraitsDockPane):
    append_button = Button
    replace_button = Button
    items = List
    _no_update = False
    update_needed = Event
    selected = Any
    dclicked = Any
    def load(self):
        pass
    def dump(self):
        pass
    def traits_view(self):
        v = View(VGroup(
                      UItem('items', editor=myTabularEditor(adapter=self.adapter_klass(),
                                                            operations=['move', 'delete'],
                                                            editable=True,
                                                            drag_external=True,
                                                            selected='selected',
                                                            dclicked='dclicked',
                                                            update='update_needed'
#                                                            auto_resize_rows=True
                                                            ),
                            )
                      )
               )
        return v


class HistoryTablePane(TablePane):
    previous_selection = Any
    previous_selections = List(PreviousSelection)
    def load(self):
        self.load_previous_selections()
    def dump(self):
        self.dump_selection()
#===============================================================================
# previous selections
#===============================================================================
    def load_previous_selections(self):
        d = self._open_shelve()
        keys = sorted(d.keys(), reverse=True)

        def get_value(k):
            try:
                return d[k]
            except Exception:
                pass

        self.previous_selections = filter(None, [get_value(ki) for ki in keys])

    def dump_selection(self):
        records = self.items
        if not records:
            return

        # this is a set of NonDB analyses so no presistence
        if not hasattr(records[0], 'uuid'):
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

        try:
            d = self._open_shelve()
        except Exception:
            import traceback
            traceback.print_exc()
            return

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

    def _open_shelve(self):
        p = os.path.join(paths.hidden_dir, 'stored_selections')
        d = shelve.open(p)
        return d

    def traits_view(self):
        v = View(VGroup(
                      UItem('previous_selection', editor=EnumEditor(name='previous_selections')),
                      UItem('items', editor=myTabularEditor(adapter=self.adapter_klass(),
                                                            operations=['move', 'delete'],
                                                            editable=True,
                                                            drag_external=True,
                                                            selected='selected',
                                                            dclicked='dclicked',
                                                            multi_select=True,
                                                            update='update_needed'
#                                                            auto_resize_rows=True
                                                            )
                            )
                      )
               )
        return v


class UnknownsPane(HistoryTablePane):
    id = 'pychron.analysis_edit.unknowns'
    name = 'Unknowns'

class ReferencesPane(HistoryTablePane):
    name = 'References'
    id = 'pychron.analysis_edit.references'


class ControlsPane(TraitsDockPane):
    dry_run = Bool(True)
    save_button = Button('Save')
    tool = Instance(IAnalysisEditTool)
    id = 'pychron.analysis_edit.controls'
    name = 'Controls'
    def traits_view(self):
        v = View(
                 VGroup(
                        UItem('tool', style='custom'),
                        HGroup(spring, UItem('save_button'), Item('dry_run'))
                        )
                 )
        return v



#============= EOF =============================================

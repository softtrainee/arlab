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
from traits.api import HasTraits, Button, List, Any, DelegatesTo
from traitsui.api import View, Item, InstanceEditor, HGroup, VGroup
#============= standard library imports ========================
#============= local library imports  ==========================


class SelectorView(HasTraits):
    selected_view = Any
    selector = Any
    append = Button
    replace = Button
    selected_records = DelegatesTo('selected_view')

    def _load_selected_records(self):
        for r in self.selector.selected:
            if r not in self.selected_records:
                self.selected_records.append(r)
#
#===============================================================================
# handlers
#===============================================================================
    def _append_fired(self):
        self._load_selected_records()

    def _replace_fired(self):
        self.selected_records = []
        self._load_selected_records()

    def traits_view(self):
        v = View(
                 VGroup(
                        HGroup(
                               Item('append', show_label=False, width= -80),
                               Item('replace', show_label=False, width= -80),
                               Item('object.selector.limit')
                               ),
                        Item('selector',
                          show_label=False,
                          style='custom',
                          editor=InstanceEditor(view='panel_view'))
                        )
                 )
        return v
#============= EOF =============================================

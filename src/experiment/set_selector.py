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
from traits.api import HasTraits, Any, Button, Property, Int, Str
from traitsui.api import View, Item, ListStrEditor
#============= standard library imports ========================
#============= local library imports  ==========================


class SetSelector(HasTraits):
    experiment_manager = Any
    add_button = Button('Add')
    names = Property(depends_on='experiment_manager.experiment_sets')
    selected_index = Int
    selected = Str

    def _get_names(self):
        return ['Set {}'.format(i + 1) for i in range(len(self.experiment_manager.experiment_sets))]

    def _add_button_fired(self):
        exp = self.experiment_manager
        exp.new_experiment_set()
        self.trait_set(selected_index=len(exp.experiment_sets) - 1, trait_change_notify=False)

    def _selected_index_changed(self):
        if self.selected_index >= 0:
            em = self.experiment_manager
            em.experiment_set = em.experiment_sets[self.selected_index]

    def traits_view(self):
        v = View(

                 Item('names',

                                show_label=False,
                                editor=ListStrEditor(
                                                     editable=False,
                                                     selected_index='selected_index',
                                                     operations=[])),
                 Item('add_button',
                      show_label=False),
                 )
        return v

#============= EOF =============================================

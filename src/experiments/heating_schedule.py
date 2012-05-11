#===============================================================================
# Copyright 2011 Jake Ross
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



from __future__ import with_statement
#============= enthought library imports =======================
from traits.api import HasTraits, Instance, List, String, Float, Bool, Button
from traitsui.api import View, Item, HGroup, TableEditor
from traitsui.table_column import ObjectColumn
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.helpers.paths import heating_schedule_dir

class HeatingStep(HasTraits):
    '''
        G{classtree}
    '''
    power = Float

class HeatingSchedule(HasTraits):
    '''
        G{classtree}
    '''
    steps = List(HeatingStep)
    name = String(enter_set=True, auto_set=False)
    save_as = Bool(False)
    def row_factory(self):
        '''
        '''
        return HeatingStep()

    def load_from_pickle(self):
        '''
        '''
        p = os.path.join(heating_schedule_dir, '.%s' % self.name)
        with open(p, 'r') as f:
            self.save_as = False
            self = pickle.load(f)

    def traits_view(self):
        '''
        '''
        cols = [
                ObjectColumn(name='power'),
               ]
        editor = TableEditor(columns=cols,
                              show_toolbar=True,
                           row_factory=self.row_factory
                           )
        return View(Item('name', enabled_when='save_as'),
                    Item('steps', show_label=False, editor=editor))

class HeatingScheduleEditor(HasTraits):
    '''
        G{classtree}
    '''
    schedule = Instance(HeatingSchedule)
    save = Button
    save_as = Button
    _allow_save_as = Bool(False)

    def _save_as_fired(self):
        '''
        '''
        self.schedule = self.schedule.clone_traits()
        self.schedule.save_as = True

    def _save_fired(self):
        '''
        '''
        p = os.path.join(heating_schedule_dir, '.%s' % self.schedule.name)
        with open(p, 'w') as f:
            pickle.dump(self.schedule, f)

    def _schedule_default(self):
        '''
        '''
        return HeatingSchedule(save_as=True)

    def traits_view(self):
        '''
        '''
        v = View(Item('schedule', show_label=False, style='custom'),
                 HGroup(Item('save'), Item('save_as', visible_when='_allow_save_as'), show_labels=False),
                 width=300,
                 height=300,
                 buttons=['OK', 'Cancel'])
        return v
#============= views ===================================
#============= EOF ====================================

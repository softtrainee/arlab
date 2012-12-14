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
from traits.api import HasTraits, Property, Bool, Str
from traitsui.api import View, Item, HGroup
from traitsui.menu import Action
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.experiment_manager import ExperimentManager
from src.paths import paths
import os

class ExperimentEditor(ExperimentManager):
    dirty = Property(depends_on='_dirty,path')
#    _path = Str
    _dirty = Bool

    dirty_save_as = Bool(False)

#===============================================================================
# persistence
#===============================================================================
    def load_experiment_set(self, *args, **kw):
        r = super(ExperimentEditor, self).load_experiment_set(*args, **kw)

        #loading the experiment set will set dirty =True 
        #change back to false. not really dirty
#        self.dirty = False
        if r:
            self.experiment_set.dirty = False
        return r

    def save(self):
        self.save_experiment_sets()

    def save_as(self):
        self.save_as_experiment_sets()

    def save_as_experiment_sets(self):
        p = self.save_file_dialog(default_directory=paths.experiment_dir)
        p = self._dump_experiment_sets(p)
        self._path = p

    def save_experiment_sets(self):
        self._dump_experiment_sets(self.path)
        self.dirty = False

    def _dump_experiment_sets(self, p):

        if not p:
            return
        if not p.endswith('.txt'):
            p += '.txt'

        self.info('saving experiment to {}'.format(p))
        with open(p, 'wb') as fp:
            n = len(self.experiment_sets)
            for i, exp in enumerate(self.experiment_sets):
                exp.path = p
                exp.dump(fp)
                if i < (n - 1):
                    fp.write('\n')
                    fp.write('*' * 80)

        return p

#===============================================================================
# views
#===============================================================================
    def traits_view(self):

        exp_grp = Item('experiment_set',
                            width=0.90,
                            show_label=False, style='custom')

        sel_grp = Item('set_selector',
                       width=0.10,
                       show_label=False,
                       style='custom')
        v = View(
                 HGroup(
                        sel_grp,
                        exp_grp
                       ),
                 resizable=True,
                 width=0.85,
                 height=0.75,
                 buttons=['OK', 'Cancel',
                          Action(name='Save', action='save',
                                 enabled_when='dirty'),
                          Action(name='Save As',
                                 action='save_as',
                                 enabled_when='dirty_save_as'
                                 ),

                          ],
                 handler=self.handler_klass,
#                 handler=SaveableManagerHandler,
                 title='Experiment'
                 )
        return v

#===============================================================================
# handlers
#===============================================================================
    def _update_dirty(self, n):
        self.dirty_save_as = n
        self._dirty = n

#===============================================================================
# property get/set
#===============================================================================
    def _set_dirty(self, d):
        self._dirty = d

    def _get_dirty(self):
        return self._dirty and os.path.isfile(self.path)

#============= EOF =============================================

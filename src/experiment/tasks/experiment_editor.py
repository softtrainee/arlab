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
from traits.api import HasTraits, Any, Instance, Unicode, Bool, Property, Int
from traitsui.api import View, Item, UI, UItem
from pyface.tasks.api import Editor
from src.ui.tabular_editor import myTabularEditor
from src.experiment.automated_run.tabular_adapter import AutomatedRunSpecAdapter
import os
from src.loggable import Loggable
from pyface.file_dialog import FileDialog
from src.paths import paths
from pyface.constant import OK
from src.experiment.queue.experiment_queue import ExperimentQueue
#============= standard library imports ========================
#============= local library imports  ==========================

class ExperimentEditor(Editor, Loggable):
    queue = Any
    ui = Instance(UI)
    path = Unicode
    dirty = Bool(False)
    name = Property(Unicode, depends_on='path')
    tooltip = Property(Unicode, depends_on='path')
    merge_id = Int
    group = Int

    def create(self, parent):
        self.control = self._create_control(parent)

    def destroy(self):
        self.ui.dispose()
        self.control = self.ui = None

    def _create_control(self, parent):
        v = View(
                 UItem('automated_runs',
                               show_label=False,
                               editor=myTabularEditor(adapter=AutomatedRunSpecAdapter(),
                                            operations=['delete',
                                                        'move',
 #                                                        'edit'
                                                        ],
                                            editable=True,
                                            selected='selected',
                                            rearranged='rearranged',
                                            pasted='pasted',
 #                                             copy_cache='copy_cache',
 #                                             update='update_needed',
                                            drag_move=True,
                                            auto_update=True,
                                            multi_select=True,
                                            scroll_to_bottom=False)
                       ),
                 resizable=True
                 )


        self.ui = self.queue.edit_traits(kind='subpanel',
                                         view=v

                                         )
        return self.ui.control

#===========================================================================
#
#===========================================================================
    def new_queue(self, txt):
        queue = self.queue_factory()
        if queue.load(txt):
            self.queue = queue

    def queue_factory(self):
        return ExperimentQueue()

#                             db=self.db,
#                             application=self.application,
#                             **kw)

    def save(self, path, queues=None):
        if queues is None:
            queues = [self.queue]
        if self._validate_experiment_queues(queues):
            self._dump_experiment_queues(path, queues)
        self.path = path

    def _validate_experiment_queues(self, eqs):
        for exp in eqs:
            if exp.test_runs():
                return

        return True

    def _dump_experiment_queues(self, p, queues):

        if not p:
            return
        if not p.endswith('.txt'):
            p += '.txt'

        self.info('saving experiment to {}'.format(p))
        with open(p, 'wb') as fp:
            n = len(queues)
            for i, exp in enumerate(queues):
                exp.path = p
                exp.dump(fp)
                if i < (n - 1):
                    fp.write('\n')
                    fp.write('*' * 80)

        return p


#===============================================================================
# handlers
#===============================================================================
#    def _path_changed(self):
#        '''
#            parse the file at path
#        '''
#        if os.path.isfile(self.path):
#            with open(self.path) as fp:
#                txt = fp.read()
#                queues = self._parse_text(txt)
#                for qi in queues:
#                    qu=self.new_queue()
#                    exp.load(text):


#===============================================================================
# property get/set
#===============================================================================
    def _get_tooltip(self):
        return self.path

    def _get_name(self):
        if self.path:
            name = os.path.basename(self.path)
            name, _ = os.path.splitext(name)
            if self.merge_id:
                name = '{}-{:02n}'.format(name, self.merge_id)
        else:
            name = 'Untitled'
        return name



#============= EOF =============================================

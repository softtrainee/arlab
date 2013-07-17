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
from traits.api import HasTraits, Any, Instance, Event, Unicode, Bool, Property, Int, on_trait_change
from traitsui.api import View, Item, UI, UItem, HGroup, spring, VGroup, VSplit, Label
from pyface.tasks.api import Editor

#============= standard library imports ========================
import os
#============= local library imports  ==========================

from src.ui.tabular_editor import myTabularEditor
from src.experiment.automated_run.tabular_adapter import AutomatedRunSpecAdapter
from src.experiment.queue.experiment_queue import ExperimentQueue
from src.envisage.tasks.base_editor import  BaseTraitsEditor
from src.helpers.filetools import add_extension
from src.experiment.utilities.human_error_checker import HumanErrorChecker


class ExperimentEditor(BaseTraitsEditor):
    queue = Instance(ExperimentQueue, ())  # Any
    path = Unicode

    name = Property(Unicode, depends_on='path')
    tooltip = Property(Unicode, depends_on='path')

    merge_id = Int(0)
    group = Int(0)

#     dirty = Bool(False)

#    def create(self, parent):
#        self.control = self._create_control(parent)
    def _dirty_changed(self):
        self.debug('dirty changed {}'.format(self.dirty))


    def traits_view(self):

        arun_grp = UItem('automated_runs',
                         editor=myTabularEditor(adapter=AutomatedRunSpecAdapter(),
                                   operations=['delete',
                                               'move',
#                                                        'edit'
                                               ],
                                   editable=True,
                                   dclicked='dclicked',
                                   selected='selected',
                                   rearranged='rearranged',
                                   pasted='pasted',
                                   copy_function='copy_function',
                                   refresh='refresh_table_needed',
#                                    scroll_to_bottom=True,
#                                             copy_cache='copy_cache',
#                                             update='update_needed',
#                                            drag_move=True,
#                                    auto_update=True,
                                   multi_select=True,
#                                    scroll_to_bottom=False
                                   )
                        )

        executed_grp = VGroup(Label('Completed Runs'),
                              UItem('executed_runs',
                                    editor=myTabularEditor(adapter=AutomatedRunSpecAdapter(),
                                                    editable=False,
                                                    auto_update=True,
                                                    selectable=False,
                                                    scroll_to_row='scroll_to_row'
                                                    ),
                            ))

        v = View(
                 VSplit(arun_grp,
                        executed_grp),
                 resizable=True
                )
        return v


    def trait_context(self):
        """ Use the model object for the Traits UI context, if appropriate.
        """
        if self.queue:
            return { 'object': self.queue}
        return super(ExperimentEditor, self).trait_context()

#    @on_trait_change('queue:automated_runs[], queue:changed')
    def _queue_changed(self):
#        f = lambda: self.trait_set(dirty=True)
        f = self._set_queue_dirty
        self.queue.on_trait_change(f, 'automated_runs[]')
        self.queue.on_trait_change(f, 'changed')
        self.queue.path = self.path

    def _path_changed(self):
        self.queue.path = self.path

    def _set_queue_dirty(self):
#         print 'set qirty', self.queue._no_update, self.queue.initialized
        if not self.queue._no_update and self.queue.initialized:
            self.dirty = True
#         else:
#             self.dirty = False
#===========================================================================
#
#===========================================================================
    def new_queue(self, txt=None):
        queue = self.queue_factory()
        if txt:
            if queue.load(txt):
                self.queue = queue
        else:
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
            path = self._dump_experiment_queues(path, queues)
            self.path = path
#             self.dirty = False

    def _validate_experiment_queues(self, eqs):
        hec = HumanErrorChecker()
        for qi in eqs:
            qi.executable = True
            err = hec.check(qi.automated_runs, test_all=True)
            if err:
                qi.executable = False
                hec.report_errors(err)
                break
#             if qi.test_runs():
#                 break
        else:
            return True

    def _dump_experiment_queues(self, p, queues):

        if not p:
            return

        p = add_extension(p)


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

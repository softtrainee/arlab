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
from traits.api import HasTraits, Instance, on_trait_change, List
from traitsui.api import View, Item
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from src.processing.tasks.batch_edit.batch_edit_panes import BatchEditPane
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem
#============= standard library imports ========================
#============= local library imports  ==========================

class BatchEditTask(AnalysisEditTask):
    batch_edit_pane = Instance(BatchEditPane, ())
    unknowns = List
    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.analysis_edit.batch',
                          left=Splitter(
                                     PaneItem('pychron.analysis_edit.unknowns'),
                                     PaneItem('pychron.analysis_edit.controls'),
                                     orientation='vertical'
                                     ),
                          right=Splitter(
                                         PaneItem('pychron.search.query'),
                                         PaneItem('pychron.search.results'),
                                         orientation='vertical'
                                         )
                          )
    def create_central_pane(self):
        return self.batch_edit_pane

#    @on_trait_change('batch_edit_pane:blanks:[nominal_value, std_dev]')
#    def _update_blanks(self, name, new):
#        print name, new

    @on_trait_change('unknowns_pane:items')
    def _update_unknowns_runs(self, obj, name, old, new):
        if not obj._no_update:
            self.unknowns = unks = self.manager.make_analyses(self.unknowns_pane.items)
            self.manager.load_analyses(unks)
            self.batch_edit_pane.unknowns = unks

    def new_batch(self):
        pass

    def _save_to_db(self):
        self.debug('save to database')
        cname = 'blanks'
        processor = self.manager
        for ui in self.unknowns:
            history = processor.add_history(ui, cname)
            for bi in self.batch_edit_pane.blanks:
                if bi.use:
                    self.debug('applying blank correction {} {}'.format(ui.record_id, bi.name))
                    processor.apply_fixed_correction(history, bi.name,
                                                     bi.nominal_value, bi.std_dev,
                                                     cname)
        processor.db.commit()
#============= EOF =============================================

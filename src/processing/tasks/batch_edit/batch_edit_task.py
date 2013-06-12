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
from src.processing.tasks.batch_edit.batch_edit_panes import BatchEditPane, \
    UValue
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem
from src.paths import paths
import os
import shelve
#============= standard library imports ========================
#============= local library imports  ==========================

class BatchEditTask(AnalysisEditTask):
    id = 'pychron.analysis_edit.batch'
    batch_edit_pane = Instance(BatchEditPane)
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
                                         orientation='vertical'
                                         )
                          )

    def create_central_pane(self):
#        return BatchEditPane()
        self.batch_edit_pane = BatchEditPane()
        return self.batch_edit_pane
#
# #    @on_trait_change('batch_edit_pane:blanks:[nominal_value, std_dev]')
# #    def _update_blanks(self, name, new):
# #        print name, new
#

    def prepare_destroy(self):
        p = os.path.join(paths.hidden_dir, 'batch_edit')
        d = shelve.open(p)
#
#         d['values'] = [(bi.use, bi.name, bi.nominal_value, bi.std_dev)
#                        for bi in self.batch_edit_pane.values]
#         d['blanks'] = [(bi.use, bi.name, bi.nominal_value, bi.std_dev)
#                        for bi in self.batch_edit_pane.blanks]


        d['values'] = self.batch_edit_pane.values
        d['blanks'] = self.batch_edit_pane.blanks

        d.close()

    def activated(self):
        p = os.path.join(paths.hidden_dir, 'batch_edit')
        if os.path.isfile(p):
            d = shelve.open(p)

#             self.batch_edit_pane.values = [UValue(use=use, name=name,
#                     nominal_value=v, std_dev=e)
#                     for use, name, v, e in d['values']]
#             self.batch_edit_pane.blanks = [UValue(use=use, name=name,
#                     nominal_value=v, std_dev=e)
#                     for use, name, v, e in d['blanks']]


            self.batch_edit_pane.values = d['values']
            self.batch_edit_pane.blanks = d['blanks']
#             d.close()
#             for bin in self.batch_edit_pane.blanks:
#                 print bin.use

    @on_trait_change('unknowns_pane:items')
    def _update_unknowns_runs(self, obj, name, old, new):
        if not obj._no_update:
            self.unknowns = unks = self.manager.make_analyses(self.unknowns_pane.items)
            self.manager.load_analyses(unks)
            self.batch_edit_pane.unknowns = unks

    def _prompt_for_save(self):
        return True

    def new_batch(self):
        pass
#
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

            ics = []
            for value in self.batch_edit_pane.values:
                if value.use:
                    if value.name == 'disc':
                        self._add_discrimination(ui.dbrecord, value.nominal_value,
                                                 value.std_dev)
                    else:
                        '''
                            value.name == 'IC <det_key>'
                        '''
                        det = value.name[3:]
                        ics.append((det, value.nominal_value, value.std_dev))

            dets = [args[0] for args in ics]
            for args in ics:
                self._add_ic_factory(ui.dbrecord, dets, *args)


    def _add_ic_factory(self, analysis, dets, det, v, e):
        '''
            det= current detector 
            dets= all detectors that will be added. use this so that previous ics
            are not copied. ie. if prev_hist_det in dets dont copy prev_hist_det 
        '''
        db = self.manager.db

        history = db.add_detector_intercalibration_history(analysis)
        db.flush()

        dbdet = db.get_detector(det)
        if dbdet is None:
            self.warning_dialog('Could not find Detector database entry for {}'.format(det))
            return

        # copy previous intercalibrations for other detectors
        phist = analysis.selected_histories.selected_detector_intercalibration
        if phist is not None:
            for ics in phist.detector_intercalibrations:
                if not ics.detector == dbdet and ics.detector.name not in dets:
                    db.add_detector_intercalibration(history, ics.detector,
                                                     user_value=ics.user_value,
                                                     user_error=ics.user_error,
                                                     sets=ics.sets,
                                                     fit=ics.fit
                                                     )

        db.add_detector_intercalibration(history, dbdet,
                                         user_value=v, user_error=e
                                         )
        analysis.selected_histories.selected_detector_intercalibration = history

    def _add_discrimination(self, analysis, v, e):
        db = self.manager.db
        hist = db.add_detector_parameter_history(analysis)
        db.flush()  # FLUSH NECESSARY

        db.add_detector_parameter(hist, disc=v, disc_error=e)
        analysis.dbrecord.selected_histories.selected_detector_param = hist

#============= EOF =============================================

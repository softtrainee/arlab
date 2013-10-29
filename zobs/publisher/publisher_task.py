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
from traits.api import on_trait_change
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem

from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from src.processing.tasks.analysis_edit.panes import ControlsPane
from src.processing.tasks.search_panes import QueryPane
from src.pychron_constants import ARGON_KEYS, IRRADIATION_KEYS, DECAY_KEYS

#============= standard library imports ========================
#============= local library imports  ==========================

class PublisherTask(AnalysisEditTask):
    def _default_layout_default(self):
        return TaskLayout(
            id='pychron.processing.publisher',
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

    def create_dock_panes(self):

        self._create_unknowns_pane()
        self.controls_pane = ControlsPane()
        selector = self.manager.db.selector
        return [
            self.unknowns_pane,
            self.controls_pane,
            QueryPane(model=selector)
        ]

    def new_sclf_table(self):
        from src.processing.tasks.publisher.sclf_table_editor import SCLFTableEditor

        editor = SCLFTableEditor()
        #        editor.table_image_source = '/Users/ross/Sandbox/publish.png'
        self._open_editor(editor)

    def _active_editor_changed(self):
        if self.active_editor:
            self.controls_pane.tool = self.active_editor.tool

    @on_trait_change('controls_pane:tool:make_button')
    def _make_table(self):
        items = self.unknowns_pane.items
        if items:
            from src.processing.publisher.writers.pdf_writer import PDFWriter

            out = '/Users/ross/Sandbox/testtable.pdf'
            writer = PDFWriter(filename=out)

            analyses = self.manager.make_analyses(items)
            self.manager.load_analyses(analyses)
            analyses = [self._analysis_factory(ai) for ai in analyses]
            writer.add_ideogram_table(analyses,
                                      add_title=True,
                                      add_header=True,
                                      alternate_row_colors=False
            )
            writer.publish(leftMargin=0.001,
                           rightMargin=0.001,
                           topMargin=0.001,
            )

            self.active_editor.load(out)

    @on_trait_change('controls_pane:tool:publish_button')
    def _publish_table(self):
        items = self.unknowns_pane.items
        if items:
            from src.processing.publisher.writers.pdf_writer import PDFWriter

            out = '/Users/ross/Sandbox/testtable.pdf'
            writer = PDFWriter(filename=out)
            analyses = self.manager.make_analyses(items)
            self.manager.load_analyses(analyses)
            analyses = [self._analysis_factory(ai) for ai in analyses]
            writer.add_ideogram_table(analyses,
                                      add_title=True,
                                      add_header=True,
            )
            writer.publish()


    def _analysis_factory(self, analysis):
        from src.processing.publisher.analysis import PubAnalysis

        a = PubAnalysis()
        for attr in ('sample', 'labnumber',
                     'aliquot',
                     'material', 'age', 'j', 'k_ca',
                     'rad40_percent',
                     'rad40', 'extract_value', 'duration', 'cleanup'
        ):
            setattr(a, attr, getattr(analysis, attr))
        for attr, _ in DECAY_KEYS + IRRADIATION_KEYS:
            setattr(a, attr, getattr(analysis, attr))

        for attr in ARGON_KEYS:
            setattr(a, attr, getattr(analysis, attr))

            if attr in analysis.isotopes:
                blank = analysis.isotopes[attr].blank
                v, e = blank.value, blank.error
                setattr(a, '{}_blank'.format(attr), v)
                setattr(a, '{}_blank_err'.format(attr), e)

        return a

        #============= EOF =============================================

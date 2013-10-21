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
from traits.api import on_trait_change, Property
from traitsui.tabular_adapter import TabularAdapter
from pyface.tasks.task_layout import TaskLayout, HSplitter, VSplitter, PaneItem, Tabbed
#============= standard library imports ========================
from numpy import asarray, average
#============= local library imports  ==========================
from src.processing.tasks.flux.panes import IrradiationPane
from src.processing.tasks.analysis_edit.interpolation_task import InterpolationTask
from src.processing.tasks.analysis_edit.panes import HistoryTablePane, TablePane
from src.processing.argon_calculations import calculate_flux
from pyface.tasks.task import Task
from src.envisage.tasks.editor_task import BaseEditorTask
from pyface.tasks.advanced_editor_area_pane import AdvancedEditorAreaPane


class LevelAdapter(TabularAdapter):
    columns = [('Run ID', 'identifier'), ('Pos.', ('position'))]
    #identifier_text = Property
    font = 'helvetica 10'

    #def _get_identifier_text(self):
    #print self.item
    #return self.item
    #return self.item.labnumber.identifier


class UnknownsAdapter(LevelAdapter):
    pass


class ReferencesAdapter(LevelAdapter):
    pass


class UnknownsPane(TablePane):
    id = 'pychron.analysis_edit.unknowns'
    name = 'Unknowns'


class ReferencesPane(TablePane):
    name = 'References'
    id = 'pychron.analysis_edit.references'


class FluxTask(InterpolationTask):
    name = 'Flux'
    id = 'pychron.analysis_edit.flux'
    flux_editor_count = 1
    unknowns_adapter = UnknownsAdapter
    references_adapter = ReferencesAdapter
    references_pane_klass = ReferencesPane
    unknowns_pane_klass = UnknownsPane

    def _default_layout_default(self):
        return TaskLayout(
            id='pychron.analysis_edit',
            left=HSplitter(
                VSplitter(
                    PaneItem('pychron.analysis_edit.irradiation'),
                    Tabbed(
                        PaneItem('pychron.analysis_edit.unknowns'),
                        PaneItem('pychron.analysis_edit.references')),
                    PaneItem('pychron.analysis_edit.controls'))
            ),
        )

    def create_dock_panes(self):
        panes = super(FluxTask, self).create_dock_panes()
        return panes + [
            IrradiationPane(model=self.manager)
        ]

    def new_flux(self):
        from src.processing.tasks.flux.flux_editor import FluxEditor

        editor = FluxEditor(name='Flux {:03n}'.format(self.flux_editor_count),
                            processor=self.manager
        )

        self._open_editor(editor)
        self.flux_editor_count += 1

        #self.manager.irradiation = 'NM-251'

    #         self.manager.level = 'H'

    @on_trait_change('manager:level')
    def _level_changed(self, new):
        if new:
            level = self.manager.get_level(new)
            if self.active_editor:
                self.active_editor.level = level

            if level:
                refs, unks = self.manager.group_level(level)
                r, u = list(refs), list(unks)
                self.unknowns_pane.items = u
                self.references_pane.items = r

                #self.active_editor.unknowns=u
                #self.active_editor.references= r

    @on_trait_change('active_editor:tool:calculate_button')
    def _calculate_flux(self):

        monitor_age = self.active_editor.tool.monitor_age
        if not monitor_age:
            monitor_age = 28.02e6

        # helper funcs
        def calc_j(ai):
            ar40 = ai.arar_result['rad40']
            ar39 = ai.arar_result['k39']
            return calculate_flux(ar40, ar39, monitor_age)

        def mean_j(ans):
            js, errs = zip(*[calc_j(ai) for ai in ans])
            errs = asarray(errs)
            wts = errs ** -2
            m, ss = average(js, weights=wts, returned=True)
            return m, ss ** -0.5

        proc = self.manager
        #def func(ai):
        #ai.load_age()

        #analyses = []
        #for i, ri in enumerate(self.active_editor.references[:1]):
        #    #ans = [ri for ri in ri.labnumber.analyses
        #    #            if ri.status == 0 and ri.step == '']
        #    #ans = proc.make_analyses(ans, group_id=i)
        #    #proc.load_analyses(ans, func=func)
        #
        #    analyses.extend(ans)
        #    me, sd = mean_j(ans)
        db = proc.db
        with db.session_ctx():
            refs = self.references_pane.items
            #ans=[]
            #for i, ri in enumerate(refs):
            #    a=db.get_labnumber_analyses(ri.identifier)
            for ri in refs:
                print ri.identifier
                print db.get_labnumber_analyses(ri.identifier)

            ans = [ai for ri in refs
                   for ai in db.get_labnumber_analyses(ri.identifier)]
            if ans:
                ans = proc.make_analyses(ans)
                irrad = proc.irradiation
                level = proc.level
                self._open_ideogram_editor(ans,
                                           name='Ideo - {}'.format(irrad, level))

#        ideo = proc.new_ideogram(ans=analyses)
#
#        from src.processing.tasks.analysis_edit.graph_editor import ComponentEditor
#        editor = ComponentEditor(component=ideo,
#                                 name='Ideogram')
#        self._open_editor(editor)


#============= EOF =============================================

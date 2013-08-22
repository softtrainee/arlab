# @PydevCodeAnalysisIgnore
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
from traits.api import  Instance, DelegatesTo, Str, Property
from traitsui.api import View, Item, VGroup, HGroup, \
    EnumEditor, InstanceEditor, Label, Heading
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.core.database_selector import ColumnSorterMixin
from src.viewable import Viewable
from src.database.core.database_adapter import DatabaseAdapter
from src.constants import NULL_STR


class SearchManager(Viewable, ColumnSorterMixin):
    db = Instance(DatabaseAdapter)
    selector = DelegatesTo('db')

    project = Str('---')
    projects = Property
    machine = Str('---')
    machines = Property
    analysis_type = Str('---')
    analysis_types = Property

#===============================================================================
# handlers
#===============================================================================
    def _analysis_type_changed(self):
        self._refresh_results()

    def _project_changed(self):
        self._refresh_results()

    def _machine_changed(self):
        self._refresh_results()

    def _refresh_results(self):
        selector = self.selector

        pr = self.project

        if pr == 'recent':
            selector.load_recent()
        else:
            ma = self.machine
            an = self.analysis_type
            qs = []
            if pr != NULL_STR:
                q = selector.query_factory(parameter='Project', criterion=pr)
                qs.append(q)
            if ma != NULL_STR:
                q = selector.query_factory(parameter='Mass Spectrometer', criterion=ma)
                qs.append(q)
            if an != NULL_STR:
                q = selector.query_factory(parameter='Analysis Type', criterion=an)
                qs.append(q)

            if qs:
                qq = selector.queries
                selector.execute_query(queries=qq + qs, load=False)

#===============================================================================
# property get/set
#===============================================================================
    def _get_projects(self):
        db = self.db
        prs = [NULL_STR, 'recent']
        ps = db.get_projects()
        if ps:
            prs += [p.name for p in ps]
        return prs

    def _get_machines(self):
        db = self.db
        mas = [NULL_STR]
        ms = db.get_mass_spectrometers()
        if ms:
            mas += [m.name for m in ms]
        return mas

    def _get_analysis_types(self):
        db = self.db
        ats = [NULL_STR]
        ai = db.get_analysis_types()
        if ai:
            ats += [aii.name.capitalize() for aii in ai]
        return ats
    def _get_control_group(self):
        cntrl_grp = VGroup(
                           Label('Project'),
                           Item('project', editor=EnumEditor(name='projects'),
                                show_label=False,
                                ),
                           Label('Spectrometer'),
                           Item('machine', editor=EnumEditor(name='machines'),
                                show_label=False,
                                ),
                           Label('Analysis Type'),
                           Item('analysis_type', editor=EnumEditor(name='analysis_types'),
                                show_label=False,
                                ),
                           )
        return cntrl_grp

    def modal_view(self):
        v = self.traits_view()
        v.buttons = ['OK', 'Cancel']
        v.kind = 'livemodal'
        return v

    def traits_view(self):
        cntrl_grp = self._get_control_group()
        v = View(
                 HGroup(
                        cntrl_grp,
                        Item('selector',
                              show_label=False,
                              style='custom',
                              editor=InstanceEditor(view='panel_view'),
                              height=500
                              )
                        ),
                 resizable=True,
                 title='Find Analyses'
                 )
        return v
#============= EOF =============================================

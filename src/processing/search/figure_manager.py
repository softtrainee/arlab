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
from traits.api import HasTraits, List, Property, cached_property, Str, Any
from traitsui.api import View, Item, TableEditor, EnumEditor, TabularEditor, HGroup
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
#============= local library imports  ==========================
from src.constants import NULL_STR
from src.database.records.figure_record import FigureRecord
from src.managers.manager import Manager

class FigureAdapter(TabularAdapter):
    columns = [('Name', 'name'),
               ('Date', 'create_date'),
               ]


class FigureManager(Manager):
    db = Any
    processing_manager = Any
    figures = List(FigureRecord)
    project = Str
    projects = Property

    new_figure_name = Str
    project_name = Str

    dclicked = Any
    selected = Any

    def save_figure(self, plotter):
        db = self.db
        project = db.get_project(self.project_name)
        if project is None:
            if self.confirmation_dialog('Add Project {}'.format(self.project_name)):
                project = db.add_project(self.project_name)

        if project:
            fig = db.add_figure(project=project, name=self.new_figure_name)
            self.info('saving figure {} to project {}'.format(fig.name, project.name))
            for ai in plotter.analyses:
                self.info('adding analysis {} to figure. graph={}, group={}, status={}'.format(ai.record_id,
                                                                                               ai.graph_id,
                                                                                               ai.group_id,
                                                                                               ai.temp_status
                                                                                               ))
                db.add_figure_analysis(fig,
                                        ai.dbrecord.dbrecord,
                                        graph=ai.graph_id,
                                        group=ai.group_id,
                                        status=ai.temp_status
                                        )
            db.commit()
#===============================================================================
# handlers
#===============================================================================
    def _dclicked_changed(self):
        if self.selected:
            self.processing_manager.open_figure(self.selected)

    def _project_changed(self):
        pr = self.project
        if pr != NULL_STR:
            figures = self.db.get_figures(project=pr)
            self.figures = [FigureRecord(_dbrecord=fi) for fi in figures]

    def _get_projects(self):
        db = self.db
        prs = [NULL_STR]
        ps = db.get_projects()
        if ps:
            prs += [p.name for p in ps]
        return prs

    def save_view(self):
        v = View(HGroup(Item('project_name'),
                        Item('project_name', show_label=False, editor=EnumEditor(name='projects'))),
                 Item('new_figure_name', label='Name'),
                 kind='livemodal',
                 buttons=['OK', 'Cancel']
                 )
        return v

    def traits_view(self):
        v = View(
                 Item('project', show_label=False, editor=EnumEditor(name='projects')),
                 Item('figures', show_label=False,
                      editor=TabularEditor(editable=False,
                                           selected='selected',
                                           dclicked='dclicked',
                                           adapter=FigureAdapter()
                                           ),
                      ),
                 width=500,
                 height=600,
                 resizable=True
                 )
        return v
#============= EOF =============================================

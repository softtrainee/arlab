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
from traits.api import Instance, DelegatesTo, Any
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.arar.arar_engine import ArArEngine
from src.envisage.core.envisage_editor import EnvisageEditor

class ArArEditor(EnvisageEditor):
    '''
    '''
    id_name = 'ArAr'
    view_name = 'graph_view'

class ArArManager(Manager):
    engine = Instance(ArArEngine)

    selected = DelegatesTo('engine')
    selection = Any

    def update_db_selection(self, obj, name, old, new):
        if self.selection:
            self.engine.add_data(self.selection)

    def update_db_selected(self, obj, name, old, new):
        self.selection = new

    def demo_open(self):
        db = self.application.get_service('src.database.adapters.massspec_database_adapter.MassSpecDatabaseAdapter')
        self.engine = ArArEngine(db=db)

        #new workspace
        ws = self.engine.new_workspace()

        #new experiment
        exp = ws.new_experiment('newexp', kind='ideogram')

        #load in data

        db.selector.on_trait_change(self.update_db_selection, 'add_selection_changed')
        db.selector.on_trait_change(self.update_db_selected, 'selected')

#        self.selection = db.selector.selected

##        for rid in ['17005-74', '17005-70']:
#        for rid in ['17005-73', '17005-70']:
#            ref = db.get_analysis(rid)
#            irrad_pos = db.get_irradiation_position(ref.IrradPosition)
#
#            arar_analysis = ref.araranalyses[-1]
#            kwargs = dict(rid=ref.RID,
#                        sample=ref.sample.Sample,
#                        irradiation=irrad_pos.IrradiationLevel,
#                        age=arar_analysis.Age,
#                        age_err=arar_analysis.ErrAge
#                        )
#            exp.load_database_reference(ref, kwargs)

        self.application.workbench.edit(self.engine,
                                       kind=ArArEditor,
                                       use_existing=False
                                       )

    def new_engine(self):
        self.engine = ArArEngine()

    def traits_view(self):
        return View(Item('engine', style='custom', show_label=False))




#============= EOF =============================================

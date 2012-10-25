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
from traits.api import HasTraits, Int, Str, Button, Instance, Property, DelegatesTo
from traitsui.api import View, Item, TableEditor, EnumEditor, HGroup, Label, spring
from traitsui.menu import Action
#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.managers.manager import SaveableHandler
from src.experiment.entry.production_ratio_input import ProductionRatioInput
from src.experiment.entry.chronology_input import ChronologyInput

class Irradiation(Loggable):
    db = Instance(IsotopeAdapter)
    production_ratio_input = Instance(ProductionRatioInput)
    chronology_input = Instance(ChronologyInput)

    name = Str
    ntrays = Int

    add_pr_button = Button('+')
    set_chron_button = Button('Set Chronology')

    pr_name = Str
    chron_name = Str
#    pr_names = DelegatesTo('production_ratio_input', prefix='names')

    def _add_pr_button_fired(self):
        pr = self.production_ratio_input
        pr.db.reset()
        pr.edit_traits()

    def _set_chron_button_fired(self):
        pr = self.chronology_input
        pr.db.reset()
        pr.edit_traits()

    def save(self):

        db = self.db

        ir = db.get_irradiation(self.name)
        if ir is not None:
            self.warning_dialog('Irradiation already exists')
            return

        else:
            prn = self.pr_name
            if not prn:
                prn = self.production_ratio_input.names[0]

            def make_ci(ci):
                return '{},{}%{},{}'.format(ci.startdate, ci.starttime,
                                        ci.enddate, ci.endtime)
            err = self.chronology_input.validate_chronology()
            if err :
                self.warning_dialog('Invalid Chronology. {}'.format(err))
                return

            chronblob = '$'.join([make_ci(ci) for ci in self.chronology_input.dosages])

            cr = db.add_irradiation_chronology(chronblob)
            ir = db.add_irradiation(self.name, prn, cr)

        db.commit()

    def traits_view(self):
        v = View(Item('name'),
                 Item('ntrays', label='N. Trays'),
                 HGroup(Item('pr_name', editor=EnumEditor(name='object.production_ratio_input.names')),
                        Item('add_pr_button', show_label=False)
                        ),
                 HGroup(spring, Item('set_chron_button', show_label=False)),

#                 buttons=['OK', 'Cancel'],
                 title='New Irradiation',
                 buttons=[Action(name='Save', action='save',
                                enabled_when='object.save_enabled'),
                          'Cancel'
                          ],
                 handler=SaveableHandler,
                 )
        return v

    def _production_ratio_input_default(self):
        pr = ProductionRatioInput(db=self.db)
        return pr

    def _chronology_input_default(self):
        pr = ChronologyInput(db=self.db)
        return pr
#============= EOF =============================================

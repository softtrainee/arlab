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
from traits.api import HasTraits, Int, Str, Button, Instance, \
 Property, DelegatesTo, Range, Undefined, cached_property, List
from traitsui.api import View, Item, TableEditor, EnumEditor, HGroup, Label, spring
from traitsui.menu import Action
#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.experiment.entry.production_ratio_input import ProductionRatioInput
from src.experiment.entry.chronology_input import ChronologyInput
import os
from src.paths import paths
from src.viewable import Viewable
from src.saveable import SaveableHandler, Saveable


class Irradiation(Saveable):
    db = Instance(IsotopeAdapter)
    production_ratio_input = Instance(ProductionRatioInput)
    chronology_input = Instance(ChronologyInput)

    name = Str
#    ntrays = Range(1, 200, 1)
    tray = Str
    trays = List
    add_pr_button = Button('+')
    edit_pr_button = Button('Edit')
    set_chron_button = Button('Set Chronology')


    pr_name = Str
    chron_name = Str
    previd = 0
#    pr_names = DelegatesTo('production_ratio_input', prefix='names')

#===============================================================================
# handlers
#===============================================================================
    def _add_pr_button_fired(self):
        pr = self.production_ratio_input
        pr.db.reset()
        pr.edit_traits()

    def _edit_pr_button_fired(self):
        pr = self.production_ratio_input
        if self.pr_name:
            pr.name = self.pr_name
        else:
            pr.name = pr.names[0]

        pr.db.reset()
        pr.edit_traits()

    def _set_chron_button_fired(self):
        pr = self.chronology_input
        pr.db.reset()
        pr.edit_traits()


#    def save(self):
#
#        db = self.db
#
#        ir = db.get_irradiation(self.name)
#        if ir is not None:
#            self.warning_dialog('Irradiation already exists')
#            return
#        else:
#            prn = self.pr_name
#            if not prn:
#                prn = self.production_ratio_input.names[0]
#
#            def make_ci(ci):
#                return '{},{}%{},{}'.format(ci.startdate, ci.starttime,
#                                        ci.enddate, ci.endtime)
#            err = self.chronology_input.validate_chronology()
##            if err :
##                self.warning_dialog('Invalid Chronology. {}'.format(err))
##                return
#
#            chronblob = '$'.join([make_ci(ci) for ci in self.chronology_input.dosages])
#            cr = db.add_irradiation_chronology(chronblob)
#
#            ir = db.add_irradiation(self.name, prn, cr)
#
##            holder = db.get_irradiation_holder(self.holder)
##            alpha = [chr(i) for i in range(65, 65 + self.ntrays)]
##            for ni in alpha:
##                db.add_irradiation_level(ni, ir, holder)
#
#        db.commit()
#        self.close_ui()

    def _get_map_path(self):
        return os.path.join(paths.setup_dir, 'irradiation_tray_maps')

    def traits_view(self):
        v = View(Item('name'),
#                 Item('ntrays', label='N. Trays'),
                 HGroup(Item('pr_name', editor=EnumEditor(name='object.production_ratio_input.names')),
                        Item('edit_pr_button', show_label=False),
                        Item('add_pr_button', show_label=False),
                        ),
                 HGroup(spring, Item('set_chron_button', show_label=False)),

#                 buttons=['OK', 'Cancel'],
                 title='New Irradiation',
                 buttons=[Action(name='OK', action='save',
                                enabled_when='object.save_enabled'),
                          'Cancel'
                          ],
                 handler=self.handler_klass,
                 )
        return v

    def _production_ratio_input_default(self):
        pr = ProductionRatioInput(db=self.db)
        return pr

    def _chronology_input_default(self):
        pr = ChronologyInput(db=self.db)
        return pr
#============= EOF =============================================

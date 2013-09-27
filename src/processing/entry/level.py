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
from traits.api import HasTraits, Str, List, Float, Any, Int
from traitsui.api import View, Item, EnumEditor, HGroup
from src.constants import NULL_STR
#============= standard library imports ========================
#============= local library imports  ==========================

class Level(HasTraits):
    name = Str
    tray = Str
    z = Float
    trays = List
    db = Any
    level_id = Int
#    irradiation=Str
#    dblevel = Any
    def load(self, irrad):
        db = self.db
        if not isinstance(irrad, (str, unicode)):
            irrad = irrad.name

#        self.irradiation=irrad
        with db.session_ctx() as sess:
            level = db.get_irradiation_level(irrad, self.name)
            self.level_id = int(level.id)
            if level.holder:
                name = level.holder.name
                if not name in self.trays:
                    name = NULL_STR
                self.tray = name
            z = level.z
            self.z = z if z is not None else 0


    def edit_db(self):
        db = self.db
#        irrad=self.irradiation
        with db.session_ctx():
            level = db.get_irradiation_level_byid(self.level_id)

            level.name = self.name
            level.z = self.z
            holder = db.get_irradiation_holder(self.tray)
            if holder:
                level.holder = holder
#            self.dblevel.name = self.name
#            self.dblevel.z = self.z
#            holder = self.db.get_irradiation_holder(self.tray)
#            if holder:
#                self.dblevel.holder = holder
#            self.db.commit()

    def traits_view(self):
        v = View(HGroup(Item('name'),
                        Item('z'),
                        Item('tray', show_label=False, editor=EnumEditor(name='trays'))),
                 buttons=['OK', 'Cancel'],
                 title='Edit Level'
                 )
        return v

    def _trays_changed(self):
        self.tray = self.trays[0]
#    def _tray_default(self):
#        return self.trays[0]
#============= EOF =============================================

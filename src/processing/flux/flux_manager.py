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
from traits.api import HasTraits, Property, Str, cached_property, Int, List, Float, Bool, on_trait_change
from traitsui.api import View, Item, EnumEditor, TabularEditor, TableEditor, HGroup
from src.processing.database_manager import DatabaseManager
from traitsui.tabular_adapter import TabularAdapter
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
from src.processing.argon_calculations import calculate_flux
from src.processing.flux.position import Position
import struct
#============= standard library imports ========================
#============= local library imports  ==========================
plusminus = u'\u00b1'
#class PositionAdapter(TabularAdapter):
#    columns = [
#             ('Labnumber', 'labnumber'),
#             ('Hole', 'hole'),
#             ('X', 'x'), ('Y', 'y'),
#             ('J', 'j'), (plusminus + ' J', 'jerr'),
#             ('Pred. J', 'j'), (plusminus + ' Pred. J', 'pred_jerr'),
#
#             ]


class FluxManager(DatabaseManager):
    irradiation = Str
    irradiations = Property
    irradiation_labels = Property
    level = Str
    levels = Property(depends_on='irradiation')
    level_labels = Property(depends_on='irradiation')

    holder = Property(depends_on='level')
    positions = List

    age = Float
    age_error = Float

    @on_trait_change('age,age_error')
    def _calculate(self):
        for p in self.positions:
            if p.use_j:
                self._calculate_flux(p)
            else:
                self._interpolate_flux(p)

    def _interpolate_flux(self, p):
        p.j = 0
        p.jerr = 0

    def _calculate_flux(self, p):
        j, jerr = calculate_flux(p.ar40, p.ar39, (self.age * 1e6, self.age_error * 1e6))
        p.j = j
        p.jerr = jerr

    @cached_property
    def _get_irradiations(self):
        return self.db.get_irradiations()

    def _irradiation_changed(self):
        irradname = self.irradiation
        if irradname == '---':
            return

        self.level = '---'
        self.info('loading irradiation {}'.format(irradname))

    def _level_changed(self):
        irradname = self.irradiation
        ln = self.level
        if ln == '---':
            return
        self.info('loading irradiation={}, level={}'.format(irradname, ln))

        lv = next((l for l in self.levels if l.name == ln))
        hd = lv.holder
        geom = hd.geometry
        hs = [struct.unpack('>ff', geom[i:i + 8]) for i in xrange(0, len(geom), 8)]
        n = len(hs)
        self.positions = [Position(hole=i + 1, x=x, y=y,
                                   use_j=i < n / 2,
                                   save=not i < n / 2
                                   ) for i, (x, y) in enumerate(hs)]

        print lv.positions

    def _get_holder(self):
        level = next((l for l in self.levels if l.name == self.level), None)
        return level.holder.name if level else ''


    def _get_irradiation_labels(self):
        return ['---'] + [ir.name for ir in self.irradiations]

    def _get_level_labels(self):
        return ['---'] + [ir.name for ir in self.levels]

    def _get_levels(self):
        n = self.irradiation
        irrad = next((ir for ir in self.irradiations if ir.name == n), None)
        return [l for l in irrad.levels] if irrad else []

    def traits_view(self):
        cols = [

              ObjectColumn(name='hole', width=30, editable=False),
              ObjectColumn(name='x', format='%0.1f', width=40, editable=False),
              ObjectColumn(name='y', format='%0.1f', width=40, editable=False),
              ObjectColumn(name='j', format='%0.3f', width=55),
              ObjectColumn(name='jerr', format='%0.3f', label=plusminus + ' J', width=55),
              CheckboxColumn(name='use_j', label='Use', width=30),
              ObjectColumn(name='pred_j', format='%0.3f', label='Pred. J', width=55),
              ObjectColumn(name='pred_jerr', format='%0.3f', label=plusminus + 'Pred. J', width=55),
              ObjectColumn(name='residual', format='%0.3f', label='Residual', width=55),
              CheckboxColumn(name='save', width=30)
              ]
        v = View(
                 Item('irradiation',
                      editor=EnumEditor(name='irradiation_labels')),
                 Item('level',
                      editor=EnumEditor(name='level_labels')
                      ),
                 Item('holder', style='readonly'),
                 HGroup(Item('age'), Item('age_error', label=plusminus + u'1\u03c3')),
                 Item('positions',
                      show_label=False,
                      editor=TableEditor(columns=cols,
                                         auto_size=False,
                                         row_height=18,
                                         )

#                      editor=TabularEditor(adapter=PositionAdapter())
                      ),
                 width=500,
                 height=500,
                 resizable=True
                 )
        return v

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('fluxman')
    f = FluxManager()
    f.configure_traits()
#============= EOF =============================================

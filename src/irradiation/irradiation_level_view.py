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
from traits.api import HasTraits, List, Any
from traitsui.api import View, Item, TableEditor
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.irradiation.irradiated_position import IrradiatedPosition
from src.paths import paths
from src.constants import PLUSMINUS


class IrradiationLevelView(HasTraits):
    db = Any
    irradiated_positions = List(IrradiatedPosition)
    selected = Any

    def load_positions(self, irradiation_name, level_name):
        irrad = self.db.get_irradiation(irradiation_name)
        level = next((li for li in irrad.levels if li.name == level_name), None)
        if level:
            if level.holder:
                holder = level.holder.name
                if holder:
                    self._load_irradiated_samples(holder)

            positions = level.positions
            if positions:
                for pi in positions:
                    hi = pi.position - 1
                    ir = self.irradiated_positions[hi]
                    ir = self._position_factory(pi, ir.x, ir.y)
                    ir.use = True if hi < 3 else False
                    self.irradiated_positions[hi] = ir

    def _load_irradiated_samples(self, name):
        p = os.path.join(os.path.join(paths.setup_dir, 'irradiation_tray_maps'), name)
        self.irradiated_positions = []
        with open(p, 'r') as f:
            delim = ','
            line = f.readline()
            nholes, _diam = line.split(delim)
            for ni in range(int(nholes)):
                line = f.readline()
                x, y = map(float, line.split(delim))


                use = True if ni < 3 else False
                self.irradiated_positions.append(IrradiatedPosition(hole=ni + 1,
                                                                    x=x,
                                                                    y=y,
                                                                    use=use
                                                                    ))

    def _position_factory(self, dbpos, x, y):
        ln = dbpos.labnumber
        position = int(dbpos.position)

        labnumber = ln.labnumber if ln else None
        ir = IrradiatedPosition(
                                labnumber=str(labnumber),
                                hole=position,
                                x=x,
                                y=y,
                                )
        if labnumber:
            selhist = ln.selected_flux_history
            if selhist:
                flux = selhist.flux
                if flux:
                    ir.j = flux.j
                    ir.j_err = flux.j_err
        return ir

    def traits_view(self):
        cols = [
              ObjectColumn(name='hole', width=30, editable=False),
              ObjectColumn(name='x', format='%0.1f', width=40, editable=False),
              ObjectColumn(name='y', format='%0.1f', width=40, editable=False),
              ObjectColumn(name='j', format='%0.4e', width=100),
              ObjectColumn(name='j_err', format='%0.4e', label=u'{}J'.format(PLUSMINUS), width=100),
              CheckboxColumn(name='use', label='Use', width=30),
              ObjectColumn(name='pred_j', format='%0.4e', label='Pred. J', width=100),
              ObjectColumn(name='pred_j_err', format='%0.4e', label=u'{}Pred. J'.format(PLUSMINUS), width=100),
              ObjectColumn(name='residual', format='%0.5f', label='Residual', width=100),
              CheckboxColumn(name='save', width=30)
              ]

        editor = TableEditor(columns=cols,
                                         auto_size=False,
                                         row_height=18,
                                         )
#        editor = TabularEditor(adapter=BaseIrradiatedPositionAdapter(),
# #                                                  update='_update_sample_table',
#                          multi_select=True,
#                          selected='object.selected',
#                          operations=[]
#                          )

        pos = Item('irradiated_positions',
                    show_label=False,
                    editor=editor
                    )
        v = View(pos)
        return v




#============= EOF =============================================

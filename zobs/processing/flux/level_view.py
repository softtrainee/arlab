# @PydevCodeAnalysisIgnore
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
from traits.api import HasTraits, List, Any, Event, Button, Float, \
    Str, Int, Property, Bool
from traitsui.api import View, UItem
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
import struct
from uncertainties import ufloat
#============= local library imports  ==========================
from src.pychron_constants import PLUSMINUS
from src.ui.tabular_editor import myTabularEditor


class LevelAdapter(TabularAdapter):
    columns = [('ID', 'position'),
               ('Lab #.', 'labnumber'),
               ('XY', 'xy'),
               ('Use', 'use'),
               ('J', 'j'),
               (u'{}1s'.format(PLUSMINUS), 'jerr'),
               ('Pred. J', 'pred_j'),
               (u'{}1s'.format(PLUSMINUS), 'jerr')
    ]

    position_width = Int(30)
    labnumber_width = Int(80)

    xy_text = Property
    use_text = Property
    jerr_text = Property
    j_text = Property

    def _get_jerr_text(self):
        v = ''
        if self.item.j:
            v = self.item.j.std_dev
            v = '{:0.3E}'.format(v)
        return v

    def _get_j_text(self):
        v = ''
        if self.item.j:
            v = self.item.j.nominal_value
            v = '{:0.3E}'.format(v)
        return v

    def _get_use_text(self, *args):
        if self.item.use:
            return 'X'
        else:
            return ''

    def _set_use_text(self, v):
        v = v.strip().lower()
        if v == 'x':
            self.item.use = True
        elif not v:
            self.item.use = False

    def _get_xy_text(self, *args):
        return '{:0.2f},{:0.2f}'.format(self.item.x, self.item.y)

    def _set_xy_text(self, *args):
        pass


class IrradiationPosition(HasTraits):
    position = Int
    labnumber = Str
    x = Float
    y = Float
    j = Any
    pred_j = Any
    use = Bool


class LevelView(HasTraits):
    positions = List
    selected = Any
    update = Event
    set_button = Button
    calc_j = Button
    age = Float(28)
    db = Any

    def _set_button_fired(self):
        if self.selected:
            for si in self.selected:
                si.use = True

            self.update = True

    def load(self, level):
        self._load_holder(level.holder)

        positions = level.positions
        if positions:
            for pi in positions:
                hi = pi.position - 1
                ir = self.positions[hi]

                ir = self._position_factory(pi, ir.x, ir.y)
                #                ir.use = True if hi < 3 else False
                self.positions[hi] = ir

    def _load_holder(self, holder):
        if holder is None:
            return
        geom = holder.geometry
        for i, (x, y) in enumerate([struct.unpack('>ff', geom[i:i + 8]) for i in xrange(0, len(geom), 8)]):
            ip = IrradiationPosition(position=i + 1,
                                     x=x,
                                     y=y,
                                     use=False
            )
            self.positions.append(ip)

    def _position_factory(self, dbpos, x, y):
        ln = dbpos.labnumber
        position = int(dbpos.position)

        labnumber = ln.identifier if ln else None
        ir = IrradiationPosition(
            labnumber=str(labnumber),
            position=position,
            x=x,
            y=y,
        )
        if labnumber:
            selhist = ln.selected_flux_history
            if selhist:
                flux = selhist.flux
                if flux:
                    ir.j = ufloat(flux.j, flux.j_err)
                    #                    ir.j_err = flux.j_err
        return ir


    def traits_view(self):
        v = View(UItem('set_button'),
                 UItem('calc_j'),
                 UItem('positions', style='custom',
                       editor=myTabularEditor(multi_select=True,
                                              selected='selected',
                                              update='update',
                                              adapter=LevelAdapter())
                 )
        )

        return v

        #============= EOF =============================================

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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
from src.database.isotope_analysis.summary import Summary
#============= standard library imports ========================
#============= local library imports  ==========================
PRS = ['K4039', 'K3839', 'Ca3937', 'Ca3837', 'Ca3637', 'Cl3638']
class IrradiationSummary(Summary):
    def _build_summary(self):
        pm = u'\u00b1'

        level = self.record.irradiation_level
        if level:
            pos = self.record.irradiation_position.position
            pr = self.record.production_ratios

            irrad = level.irradiation
            self._add_keyword_value('{}{} hole= '.format(irrad.name, level.name), str(pos))
#            d.add_text('{}{} hole={}'.format(irrad.name, level.name, pos))
            self._add_keyword_value('Production Ratio= ', irrad.production.name)
#            d.add_text('Production Ratio= {}'.format(irrad.production.name))

            a39 = self.record.arar_result['ar39decayfactor']
            a37 = self.record.arar_result['ar37decayfactor']

            self._add_keyword_value('39Decay= ', '{:0.5f}'.format(a39))
            self._add_keyword_value('37Decay= ', '{:0.5f}'.format(a37))

            for pri in PRS:
                try:
                    v = getattr(pr, pri)
                    e = getattr(pr, '{}_err'.format(pri))
                except AttributeError:
                    v, e = 0, 0
                key = '{}= '.format(pri)
                value = '{:0.5f} {}{:0.5f}'.format(v, pm, e)
                self._add_keyword_value(key, value)


    def _add_keyword_value(self, key, value, **kw):
        self.add_text(key, bold=True, new_line=False, *kw)
        self.add_text(value, **kw)


#============= EOF =============================================

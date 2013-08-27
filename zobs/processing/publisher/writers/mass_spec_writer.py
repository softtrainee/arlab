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
from traits.api import HasTraits
from traitsui.api import View, Item
from src.processing.publisher.writers.csv_writer import CSVWriter
#============= standard library imports ========================
#============= local library imports  ==========================

class MassSpecCSVWriter(CSVWriter):
    delimiter = ','
    header = ['Run ID# (pref. XXXX-XX)',
            'Sample',
             'J',
            'J',
            'Status (0=OK, 1=Deleted)',
            'Moles 39Ar X 10^-14',
            'Moles 40Arr X 10^-14',
            '40Ar*/39Ar,%40Ar*',
            '%40Ar*',
            '39K/Ktotal',
            '36Ar/39Ar  (corrected for D and decay)',
            '36ArCa/36ArTotal',
            '38Cl/39Ar',
            '38Cl/39Ar',
            '37Ar/39Ar',
            '37Ar/39Ar',
            'Power or Temp.',
            'Age',
            'Age Error(w/o  J;  irr. Param. Opt.)',
            '40Ar',
            '40Ar',
            '39Ar',
            '39Ar',
            '38Ar',
            '38Ar',
            '37Ar',
            '37Ar',
            '36Ar',
            '36Ar',
            'Isoch. 40/36',
            'Isoch 39/36',
            '% i40/36',
            '% i39/36',
            '% i39/40',
            'Cor. Coef. 40/39',
            'Cor.Coef. 36/39']
    attrs = ['record_id', 'sample', 'j', 'jerr', 'status',
             '', '', '', '', '', '', '', '', '', '', '', '',
             'age_value', 'age_error'
             ]

    subheader = ['Required',
            'Required',
            'Required',
            'Required',
            'Required',
            'Req. moles plot',
            'Req. moles plot',
            'Req. spectrum',
            'Req. pct. Rad. Plot',
            'Opt. In pct. Rad. Plot',
            'Opt. In spec. if use Exclude Ca39 Opt. For spectrum table',
            'Opt. For spectrum table',
            'Req. Cl / K plot',
            'Opt. In Cl / K plot',
            'Req. Ca / K plot',
            'Opt. In Ca / K plot',
            'Opt.',
            'Req. spectrum, age-prob.',
            'Req. spectrum, age-prob.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Requred spectrum',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. for isochron',
            'Req. for isochron',
            'Req. inv. isoch.',
            'Req. conv. isoch.',
            'Req. inv. isoch.',
            'Req. conv. isoch.',
            'Req. inv. isoch.']

    def add_group_marker(self):
        self._rows.append(['<new_group>'])
#============= EOF =============================================

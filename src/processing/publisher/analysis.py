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
from traits.api import HasTraits, Property, List, cached_property
# from traitsui.api import View, Item
#============= standard library imports ========================
from uncertainties import ufloat
from numpy import mean
#============= local library imports  ==========================
from src.experiment.utilities.identifier import make_runid

def make_ufloat(*args):
    if not args:
        args = (1, 0)
    return ufloat(*args)

def uone():
    return make_ufloat()


import re
STEP_REGEX = re.compile('\d{2,}[A-Za-z]+')

class Marker(HasTraits):
    def __getattr__(self, attr):
        return ''

def AnalysisProperty():
    return Property(depends_on='analyses')

class PubAnalysisMean(HasTraits):
    analyses = List
    age = AnalysisProperty()
    k_ca = AnalysisProperty()
    labnumber = AnalysisProperty()

    @cached_property
    def _get_labnumber(self):
        return self.analyses[0].labnumber

    @cached_property
    def _get_k_ca(self):
        return self._get_value('k_ca')

    @cached_property
    def _get_age(self):
        return self._get_value('age')
#        return mean([ai.age for ai in self.analyses])
    def _get_value(self, attr):
        return mean([getattr(ai, attr) for ai in self.analyses])

class PubAnalysis(HasTraits):
    labnumber = 'A'
    aliquot = 0
    step = ''
    sample = 'FC-2'
    material = 'sanidine'
    status = 0

    j = ufloat(1e-4, 1e-7)
    ic_factor = ufloat(1.03, 1e-10)
    rad40 = ufloat(99.0, 0.1)

    k39 = uone()
    k_ca = uone()

    moles_Ar40 = uone()

    Ar40 = uone()
    Ar39 = uone()
    Ar38 = uone()
    Ar37 = uone()
    Ar36 = uone()

    Ar40_blank = uone()
    Ar39_blank = uone()
    Ar38_blank = uone()
    Ar37_blank = uone()
    Ar36_blank = uone()

    extract_value = 10

    rad40_percent = uone()

    age = uone()
    blank_fit = 'LR'
    def set_runid(self, rid):
        ln, a = rid.split('-')
        self.labnumber = ln

        if STEP_REGEX.match(a):
            self.step = a[-1]
            self.aliquot = int(a[:-1])
        else:
            self.aliquot = int(a)

    @property
    def aliquot_step(self):
        if self.step:
            return self.step
        else:
            return '{:02n}'.format(self.aliquot)
#        return '{:02n}{}'.format(self.aliquot, self.step)
    @property
    def labnumber_aliquot(self):
        if self.step:
            return make_runid(self.labnumber, self.aliquot, '')
        else:
            return self.labnumber

    @property
    def runid(self):
        return make_runid(self.labnumber, self.aliquot, self.step)

    @property
    def R(self):
        return self.rad40 / self.k39
#============= EOF =============================================

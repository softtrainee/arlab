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
from numpy import mean, average, array
#============= local library imports  ==========================
from src.experiment.utilities.identifier import make_runid
from src.stats.core import calculate_weighted_mean
from src.processing.argon_calculations import calculate_plateau_age, \
    calculate_arar_age

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

class ComputedValues(HasTraits):
# class PubAnalysisMean(HasTraits):
    analyses = List
    wm_age = AnalysisProperty()
    k_ca = AnalysisProperty()
    labnumber = AnalysisProperty()
    sample = AnalysisProperty()

    plateau_age = AnalysisProperty()
    plateau_steps = AnalysisProperty()
    plateau_nsteps = AnalysisProperty()
    integrated_age = AnalysisProperty()

    plateau = AnalysisProperty()

    @cached_property
    def _get_labnumber(self):
        return self.analyses[0].labnumber

    @cached_property
    def _get_sample(self):
        return self.analyses[0].sample

    @cached_property
    def _get_k_ca(self):
        return self._get_value('k_ca')

    @cached_property
    def _get_wm_age(self):
        ages, errors, k39s = zip(*[(ai.age.nominal_value, ai.age.std_dev,
                                   ai.Ar39.nominal_value
                                   ) for ai in self.analyses])
        wm, werr = calculate_weighted_mean(ages, errors)
#        wm, werr = average(ages, weights=k39s, returned=True)
#        return ufloat(m, ss)
        return ufloat(wm, werr)

    def _get_integrated_age(self):
        ans = self.analyses

        '''
            every analysis has its own decayfactors 
            correct 37 and 39 and set a37decayfactor and a39decayfactor=1
        '''
        isotopes = zip(*[(ai.Ar40,
                          ai.Ar39 * ai.a39decayfactor,
                          ai.Ar38,
                          ai.Ar37 * ai.a37decayfactor,
                          ai.Ar36)
                          for ai in ans])
        isotopes = map(sum, isotopes)

        # make zeros for baselines, blanks and backgrounds
        baselines = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        blanks = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        backgrounds = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]

        a = ans[0]
        j = a.j
        irrad_info = (a.k4039, a.k3839, a.k3739,
                      a.ca3937, a.ca3837, a.ca3637,
                      a.cl3638,
                      [], None)

#        print a.a37decayfactor
        arar_result = calculate_arar_age(isotopes, baselines, blanks, backgrounds,
                           j, irrad_info,
                           a37decayfactor=ans[-1].a37decayfactor,
#                           a39decayfactor=1  # a.a39decayfactor,
                           )

        return arar_result['age'] / 1e6

    @cached_property
    def _get_plateau_age(self):
        if self.plateau:
            m, e, pidx = self.plateau
            si, ei = pidx[0], pidx[-1]
            if abs(ei - si) == 0:
                return None

            return ufloat(m, e)


    @cached_property
    def _get_plateau_nsteps(self):
        if self.plateau:
            _, _, pidx = self.plateau
            si, ei = pidx
            return (ei - si) + 1

    @cached_property
    def _get_plateau_steps(self):
        m = ''
        if self.plateau:
            _, _, pidx = self.plateau
            si, ei = pidx
            if abs(si - ei) > 0:
                m = '{}-{}'.format(chr(65 + si), chr(65 + ei))
        return m

    @cached_property
    def _get_plateau(self):
        ans = self.analyses
        age, error, k39 = zip(*[(ai.age.nominal_value,
                                ai.age.std_dev,
                                ai.k39)
                                for ai in ans]
                              )

        m, e, pidx = calculate_plateau_age(age, error, k39)
        for i in range(pidx[0], pidx[-1]):
            self.analyses[i].status = 'P'
        return m, e, pidx

#        return self._get_value('age')
#        return mean([ai.age for ai in self.analyses])
#    def _get_value(self, attr):
#        return mean([getattr(ai, attr) for ai in self.analyses])


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

    k4039 = uone()
    k3839 = uone()
    k3739 = uone()
    ca3937 = uone()
    ca3837 = uone()
    ca3637 = uone()
    cl3638 = uone()
    a37decayfactor = 1
    a39decayfactor = 1

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

#===============================================================================
# Copyright 2011 Jake Ross
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

#=============enthought library imports=======================
from traits.api import HasTraits, Property, Float, Enum, Str, List, Either

from uncertainties import ufloat
from src.pychron_constants import AGE_SCALARS
#=============local library imports  ==========================


class ArArConstants(HasTraits):
    lambda_b = Property(depends_on='lambda_b_v, lambda_b_e')
    lambda_b_v = Float(4.962e-10)
    lambda_b_e = Float(9.3e-13)
    lambda_e = Property(depends_on='lambda_e_v, lambda_e_e')
    lambda_e_v = Float(5.81e-11)
    lambda_e_e = Float(1.6e-13)

    lambda_k = Property
    lambda_Cl36 = Property(depends_on='lambda_Cl36_v, lambda_Cl36_e')
    lambda_Cl36_v = Float(6.3e-9)
    lambda_Cl36_e = Float(0)
    lambda_Ar37 = Property(depends_on='lambda_Ar37_v, lambda_Ar37_e')
    lambda_Ar37_v = Float(0.01975)
    lambda_Ar37_e = Float(0)
    lambda_Ar39 = Property(depends_on='lambda_Ar39_v, lambda_Ar39_e')
    lambda_Ar39_v = Float(7.068e-6)
    lambda_Ar39_e = Float(0)

    atm4036 = Property(depends_on='atm4036_v,atm4036_e')
    atm4036_v = Float(295.5)
    atm4036_e = Float(0.5)

    atm4038 = Property(depends_on='atm4038_v,atm4038_e')
    atm4038_v = Float(1575)
    atm4038_e = Float(2)

    atm3836 = Property(depends_on='atm4038_v,atm4038_e,atm4036_v,atm4036_e')

    abundance_40K = 0.000117
    mK = 39.0983
    mO = 15.9994

    k3739_mode = Enum('Normal', 'Fixed')
    fixed_k3739 = Property(depends_on='k3739_v, k3739_e')
    k3739_v = Float(0.01)
    k3739_e = Float(0.0001)

    age_units = Str('Ma')
    age_scalar = Property(depends_on='age_units')
    abundance_sensitivity = Float

    ic_factors = Either(List, Str)

    def _get_fixed_k3739(self):
        return self._get_ufloat('k3739')

    def _get_atm3836(self):
        return self.atm4036 / self.atm4038

    def _get_ufloat(self, attr):
        v = getattr(self, '{}_v'.format(attr))
        e = getattr(self, '{}_e'.format(attr))
        return ufloat(v, e)

    def _get_atm4036(self):
        return self._get_ufloat('atm4036')

    def _get_atm4038(self):
        return self._get_ufloat('atm4038')

    def _get_lambda_Cl36(self):
        return self._get_ufloat('lambda_Cl36')

    def _get_lambda_Ar37(self):
        return self._get_ufloat('lambda_Ar37')

    def _get_lambda_Ar39(self):
        return self._get_ufloat('lambda_Ar39')

    def _get_lambda_b(self):
        return self._get_ufloat('lambda_b')

    def _get_lambda_e(self):
        return self._get_ufloat('lambda_e')

    def _get_lambda_k(self):
        k = self.lambda_b + self.lambda_e
        return ufloat(k.nominal_value, k.std_dev)

    def _get_age_scalar(self):
        try:
            return AGE_SCALARS[self.age_units]
        except KeyError:
            return 1


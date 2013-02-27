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
from traits.api import HasTraits, Property, Float
#from apptools.preferences.package_globals import get_default_preferences

from uncertainties import ufloat
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

    def _get_atm3836(self):
        return self.atm4036 / self.atm4038

    def _get_ufloat(self, attr):
        v = getattr(self, '{}_v'.format(attr))
        e = getattr(self, '{}_e'.format(attr))
        return ufloat((v, e))

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
        return ufloat((k.nominal_value, k.std_dev()))

#dp = get_default_preferences()
#scope = dp.get_scope('application')
#constant_path = 'pychron.experiment.constants'
#general_path = 'pychron.experiment.general_age'

#def get_general(name, v):
#    vv = scope.get('{}.{}'.format(general_path, name))
#    v = vv if vv is not None else v
#    return v

#def get_constant(name, v, e):
#    vv = scope.get('{}.{}'.format(constant_path, name))
#    ee = scope.get('{}.{}_error'.format(constant_path, name))
#    v = vv if vv is not None else v
#    e = ee if ee is not None else e
##    print name, v, e
#    return ufloat((float(v), float(e)))
#
#class Constants(object):
#    age_units = 'Ma'
#    def __init__(self):
#        #lambda_epsilon = ufloat((5.81e-11,
#        #                                    0))
#        #lambda_beta = ufloat((4.962e-10,
#        #                                 0))
#
##        lambda_e = ufloat((5.755e-11,
##                                            1.6e-13))
##        lambda_b = ufloat((4.9737e-10,
##                                         9.3e-13))
#
#        lambda_e = get_constant('lambda_e', 5.81e-11, 1.6e-13)
##        lambda_e = get_constant('lambda_e', 5.81e-11, 0)
#        lambda_b = get_constant('lambda_b', 4.962e-10, 9.3e-13)
##        lambda_b = get_constant('lambda_b', 4.962e-10, 0)
#
#        self.lambda_k = lambda_e + lambda_b
#        #lambda_k = get_constant('lambda_K', 5.81e-11 + 4.962e-10, 0)
#
#        self.lambda_Ar37 = get_constant('lambda_Ar37', 0.01975, 0) #per day
#        #lambda_37 = ufloat((0.01975, 0)) #per day
#        self.lambda_Ar39 = get_constant('lambda_Ar39', 7.068000e-6, 0)  #per day
#        #lambda_39 = ufloat((7.068000e-6, 0))  #per day
#        self.lambda_Cl36 = get_constant('lambda_Cl36', 6.308000e-9, 0)  #per day
#        #lambda_cl36 = ufloat((6.308000e-9, 0))  #per day
#
#        #atmospheric ratios
#        self.atm4036 = get_constant('Ar40_Ar36_atm', 295.5, 0)
#        self.atm4038 = get_constant('Ar40_Ar38_atm', 1575, 2)
#
#        #atm4038 = ufloat((1575, 2))
#        self.atm3638 = self.atm4038 / self.atm4036
#        self.atm3836 = self.atm4036 / self.atm4038

#        self.age_units = get_general('age_units', 'Ma')

###decay constants
#lambda_epsilon = 5.81e-11
#lambda_epsilon_er = 1.7e-12
##                                    1.7e-12))
#lambda_beta = 4.962e-10
#lambda_beta_er = 8.6e-12
#lambdak = lambda_epsilon + lambda_beta
#
#
#lambda_37 = 0.01975 #per day
#lambda_39 = 7.068000e-6  #per day
#
#lambda_cl36 = 6.308000e-9  #per day
###atmospheric ratios
#atm4036 = 295.5
#atm4036_er = 0.5
#atm4038 = 1575
#atm4038_er = 2
##atm3638 = atm4038 / atm4036
##atm3836 = atm4038 / atm4036
#atm3836 = atm4036 / atm4038

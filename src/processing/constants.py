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

from uncertainties import ufloat
from apptools.preferences.package_globals import get_default_preferences

#=============local library imports  ==========================
dp = get_default_preferences()
scope = dp.get_scope('application')
constant_path = 'pychron.experiment.constants'
#general_path = 'pychron.experiment.general_age'

#def get_general(name, v):
#    vv = scope.get('{}.{}'.format(general_path, name))
#    v = vv if vv is not None else v
#    return v

def get_constant(name, v, e):
    vv = scope.get('{}.{}'.format(constant_path, name))
    ee = scope.get('{}.{}_error'.format(constant_path, name))
    v = vv if vv is not None else v
    e = ee if ee is not None else e
#    print name, v, e
    return ufloat((float(v), float(e)))

class constants(object):
    age_units = 'Ma'
    def __init__(self):
        #lambda_epsilon = ufloat((5.81e-11,
        #                                    0))
        #lambda_beta = ufloat((4.962e-10,
        #                                 0))

#        lambda_e = ufloat((5.755e-11,
#                                            1.6e-13))
#        lambda_b = ufloat((4.9737e-10,
#                                         9.3e-13))

        lambda_e = get_constant('lambda_e', 5.81e-11, 1.6e-13)
#        lambda_e = get_constant('lambda_e', 5.81e-11, 0)
        lambda_b = get_constant('lambda_b', 4.962e-10, 9.3e-13)
#        lambda_b = get_constant('lambda_b', 4.962e-10, 0)

        self.lambda_k = lambda_e + lambda_b
        #lambda_k = get_constant('lambda_K', 5.81e-11 + 4.962e-10, 0)

        self.lambda_Ar37 = get_constant('lambda_Ar37', 0.01975, 0) #per day
        #lambda_37 = ufloat((0.01975, 0)) #per day
        self.lambda_Ar39 = get_constant('lambda_Ar39', 7.068000e-6, 0)  #per day
        #lambda_39 = ufloat((7.068000e-6, 0))  #per day
        self.lambda_Cl36 = get_constant('lambda_Cl36', 6.308000e-9, 0)  #per day
        #lambda_cl36 = ufloat((6.308000e-9, 0))  #per day

        #atmospheric ratios
        self.atm4036 = get_constant('Ar40_Ar36_atm', 295.5, 0)
        self.atm4038 = get_constant('Ar40_Ar38_atm', 1575, 2)

        #atm4038 = ufloat((1575, 2))
        self.atm3638 = self.atm4038 / self.atm4036
        self.atm3836 = self.atm4036 / self.atm4038

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

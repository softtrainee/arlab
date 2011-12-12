'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#'''
#RossLabs 2009
#Ross  Jake Ross   jirhiker@gmail.com
#
#Oct 22, 2009
#'''
#
##=============enthought library imports=======================
#
##=============standard library imports ========================
from uncertainties import ufloat
#
##=============local library imports  ==========================


#lambda_epsilon = ufloat((5.81e-11,
#                                    1.7e-12))
#lambda_beta = ufloat((4.962e-10,
#                                 8.6e-12))
lambda_epsilon = ufloat((5.81e-11,
                                    0))
lambda_beta = ufloat((4.962e-10,
                                 0))
lambdak = lambda_epsilon + lambda_beta

lambda_37 = ufloat((0.01975, 0)) #per day
lambda_39 = ufloat((7.068000e-6, 0))  #per day
lambda_cl36 = ufloat((6.308000e-9, 0))  #per day

#atmospheric ratios
#atm4036 = ufloat((295.5, 0.5))
#atm4038 = ufloat((1575, 2))
atm4036 = ufloat((295.5, 0.5))
atm4038 = ufloat((1575, 2))
atm3638 = atm4038 / atm4036
atm3836 = atm4036 / atm4038


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

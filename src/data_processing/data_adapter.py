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



#'''
#RossLabs 2009
#Ross  Jake Ross   jirhiker@gmail.com
#
#Oct 25, 2009
#'''
#
##=============enthought library imports=======================
#
##=============standard library imports ========================
#from uncertainties import ufloat
#
##=============local library imports==========================
#from analysis import Unknown, Analysis
#from production_ratio import ProductionRatio
#def convert_db_unknown(d, style = 'nmgrl'):
#    '''
#        @type style: C{str}
#        @param style:
#    '''
#    raw_data = d
#    if style == 'nmgrl':
#        isotope_values = {'ar40':ufloat((d.Tot40, d.Tot40Er)),
#                          'ar39':ufloat((d.Tot39, d.Tot39Er)),
#                          'ar38':ufloat((d.Tot38, d.Tot38Er)),
#                          'ar37':ufloat((d.Tot37, d.Tot37Er)),
#                          'ar36':ufloat((d.Tot36, d.Tot36Er))}
#        j_value = ufloat((d.JVal, d.JEr))
#    u = Unknown(raw_data, isotope_values, j_value, ProductionRatio())
#    return u
#def new_analysis_from_signals(*args):
#    '''
#    '''
#    keys = ['ar40', 'ar39', 'ar38', 'ar37', 'ar36']
#    d = dict()
#    for i, k in enumerate(keys):
#        d[k] = ufloat(args[i])
#
#
#    return Analysis(args, d)
#def new_unknown_from_signals(*args):
#    '''
#    '''
#
#    keys = ['ar40', 'ar39', 'ar38', 'ar37', 'ar36']
#    d = dict()
#    for i, k in enumerate(keys):
#        d[k] = ufloat(args[i])
#
#    j = ufloat((1, 0.1))
#    return Unknown(args, d, j, ProductionRatio())
#
#def new_unknown():
#    '''
#    '''
#
#    return Unknown(None, {'ar40':ufloat((0, 0)),
#                      'ar39':ufloat((0, 0)),
#                      'ar38':ufloat((0, 0)),
#                      'ar37':ufloat((0, 0)),
#                      'ar36':ufloat((0, 0))},
#                      ufloat((0, 0)),
#                      ProductionRatio()
#
#                      )

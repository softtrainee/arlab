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
##=============enthought library imports=======================oup
#
##=============standard library imports ========================
#from uncertainties import ufloat
#from uncertainties.umath import log, exp
#
##=============local library imports  ==========================
#import constants
##from data_adapter import new_unknown
#
##plateau definition
#plateau_criteria = {'number_steps':3}
#
#def find_plateaus(ages):
#    def __add_plateau(s, e, p, di):
#        d = e - s
#        if d >= plateau_criteria['number_steps']:
#            p.append((s, e))
#            di.append(d)
#
#    start_i = 0
#    end_i = 0
#    plateaus = []
#    plateau_lengths = []
#    for i in range(1, len(ages)):
#        aa1 = ages[start_i]
#        aa2 = ages[i]
#
#        a1 = aa1.nominal_value
#        a2 = aa2.nominal_value
#        e1 = 2.0 * aa1.std_dev()
#        e2 = 2.0 * aa2.std_dev()
#        if not (a1 - e1) >= (a2 + e2) and not (a1 + e1) <= (a2 - e2):
#            end_i += 1
#        else:
#            __add_plateau(start_i, end_i, plateaus, plateau_lengths)
#
#            start_i = end_i + 1
#            end_i = start_i
#
#    __add_plateau(start_i, end_i, plateaus, plateau_lengths)
#
#    if len(plateau_lengths) == 0:
#        return
#
#    #get and return the indices of the longest plateau
#    max_i = plateau_lengths.index(max(plateau_lengths))
#
#    return (plateaus[max_i][0], plateaus[max_i][1] + 1)
#
#
#def age_calculation(*args):
#    '''
#    j, m40, m39, m38, m37, m36, production_ratio, days_since_irradiation, irradiation_time
#    return age in years
#    '''
#    j_value = args[0]
#    isotope_components = get_isotope_components(*args[1:])
#    #calculate the age
#
#    JR = j_value * isotope_components['rad40'] / isotope_components['k39']
#    age = (1 / constants.lambdak) * log(1 + JR)
#
#    return age
#def j_calculation(*args):
#    '''
#    age, m40, m39, m38, m37, m36, production_ratio, days_since_irradiation, irradiation_time
#        age in a (years)
#    '''
#    age = args[0]
#    isotope_components = get_isotope_components(*args[1:])
#    j_val = (exp(age * constants.lambdak) - 1) * isotope_components['k39'] / isotope_components['rad40']
#    return j_val
#
#def get_isotope_components(m40, m39, m38, m37, m36, production_ratio, days_since_irradiation, irradiation_time):
#    #iteratively calculate 37 and 39
#    k37 = 0
#    for i in range(10):
#        ca37 = m37 - k37
#        ca39 = production_ratio.ca3937 * ca37
#        k39 = m39 - ca39
#        k37 = production_ratio.k3739 * k39
#
#    #correct for decay
#    k37, k39 = correct_for_decay(k37, k39, days_since_irradiation, irradiation_time)
#
#    #38 from potassium and calcium
#    k38 = k39 * production_ratio.k3839
#    ca38 = ca37 * production_ratio.ca3837
#
#    #36 from calcium 
#    ca36 = production_ratio.ca3637 * ca37
#
#    #cosmogenic 36 from cl
#    if constants.lambda_cl36 < 0.1:
#        m = production_ratio.cl3638 * constants.lambda_cl36 * days_since_irradiation
#    a3836 = 1 / constants.atm36_38
#    mcl = m / (m * a3836 - 1)
#    cl36 = mcl * (a3836 * (m36 - ca36) - m38 + k38 + ca38)
#
#    #36 from atm
#    atm36 = m36 - ca36 - cl36
#
#    #38 from atm and cl 
#    atm38 = atm36 / constants.atm36_38
#    cl38 = m38 - k38 - atm38 - ca38
#
#    #40 from atm
#    atm40 = atm36 * constants.atm40_36
#
#    #40 from potassium
#    k40 = production_ratio.k4039 * k39
#
#    rad40 = m40 - atm40 - k40
#    values = [rad40, atm40, atm38, atm36, k40, k39, k38, k37, cl38, cl36, ca39, ca38, ca37, ca36]
#    keys = ['rad40', 'atm40', 'atm38', 'atm36', 'k40', 'k39', 'k38', 'k37', 'cl38', 'cl36', 'ca39', 'ca38', 'ca37', 'ca36']
#
#    return dict(zip(keys, values))
#
#def correct_for_decay(m37, m39, days_since_irradiation, irradiation_time):
#    '''
#    '''
#    lam = constants.lambda_37
#    m37 *= lam * irradiation_time * exp(lam * days_since_irradiation) / (1 - exp(-lam * irradiation_time))
#
#    lam = constants.lambda_39
#    m39 *= lam * irradiation_time * exp(lam * days_since_irradiation) / (1 - exp(-lam * irradiation_time))
#    return m37, m39
#
#
#
#
##============= EOF ====================================
#
#
#
##def plateau_age(data):
##    '''
##    data = rowtuple of corrected data
##    '''
##    #calculate the ages and store ref to 39
##    ages = []
##    ar_39_signals = []
##
##    integrated = new_unknown()
##    keys = ['ar40', 'ar39', 'ar38', 'ar37', 'ar36']
##    integrated.j_value = data[0].j_value
##    for d in data:
##        for k in keys:
##            integrated.isotopes[k] += d.isotopes[k]
##        ar_39_signals.append(d.isotopes['ar39'])
##
##        ages.append(calc_corrected_age(d))
##    print 'integrated age :', calc_corrected_age(integrated)
##
##    indices = find_plateaus(ages)
##    if indices is None:
##        print 'no plateau'
##    for d in data[indices[0]:indices[1]+1]:
##        print 'plateau step',d.AnalysisID,d.DataReductionSessionID
##    
##def calc_corrected_age(corrected_unknown):
##    '''
##    return age in Ma
##    
##    '''
##
##    #correct unknown for blank value
##    corrected_unknown.correct_for_blank()
##    corrected_unknown.correct_for_decay()
##
##    days_since_irradiation = corrected_unknown.days_since_irradiation()
##
##    #set up some shorthand names
##    corrected_40 = corrected_unknown.isotopes['ar40']
##    corrected_39 = corrected_unknown.isotopes['ar39']
##    corrected_38 = corrected_unknown.isotopes['ar38']
##    corrected_37 = corrected_unknown.isotopes['ar37']
##    corrected_36 = corrected_unknown.isotopes['ar36']
##
##
##    j_value = corrected_unknown.j_value
##    production_ratio = corrected_unknown.production_ratio
##
##    return __corrected_age_calc__(corrected_40, corrected_39, corrected_38, corrected_37, corrected_36,
##                           j_value, production_ratio, days_since_irradiation) / 1e6
#
#
#

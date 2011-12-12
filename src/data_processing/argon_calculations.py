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
#=============enthought library imports=======================

#============= standard library imports ========================
import math
from numpy import asarray, argmax
from src.data_processing import constants
#============= local library imports  ==========================
def calculate_mswd(x, errs):
    mswd_w = 0
    if len(x) >= 2:
        x = asarray(x)
        errs = asarray(errs)
        
    #    xmean_u = x.mean()    
        xmean_w, _err = calculate_weighted_mean(x, errs)
        
        ssw = (x - xmean_w) ** 2 / errs ** 2
    #    ssu = (x - xmean_u) ** 2 / errs ** 2
        
        d = 1.0 / (len(x) - 1)
        mswd_w = d * ssw.sum()
    #    mswd_u = d * ssu.sum()
    
    return mswd_w

def calculate_weighted_mean(x, errs, error=0):
    x = asarray(x)
    errs = asarray(errs)
    
    weights = asarray(map(lambda e: 1 / e ** 2, errs))
        
    wtot = weights.sum()
    wmean = (weights * x).sum() / wtot
    
    if error == 0:
        werr = wtot ** -0.5
    elif error == 1:
        werr = 1
    return wmean, werr

def calculate_arar_age(signals, ratios, ratio_errs, a37decayfactor, a39decayfactor, j, jer, d, der):
    s40, s40er, s39, s39er, s38, s38er, s37, s37er, s36, s36er = signals
    p36cl38cl, k4039, k3839, ca3637, ca3937, ca3837 = ratios
    k4039er, ca3637er, ca3937er = ratio_errs
    
    #convert to ufloats
    from uncertainties import ufloat
    from uncertainties.umath import log
    s40 = ufloat((s40, s40er))
    s39 = ufloat((s39, s39er))
    s38 = ufloat((s38, s38er))
    s37 = ufloat((s37, s37er))
    s36 = ufloat((s36, s36er))
    k4039 = ufloat((k4039, k4039er))
    ca3637 = ufloat((ca3637, ca3637er))
    ca3937 = ufloat((ca3937, ca3937er))
    j = ufloat((j, jer))
    d = ufloat((d, der))
    
#    #calculate the age
    ca37 = s37 * a37decayfactor
    s39 = s39 * a39decayfactor
    ca36 = ca3637 * ca37
    ca38 = ca3837 * ca37
    ca39 = ca3937 * ca37
    k39 = s39 - ca39
    k38 = k3839 * k39
#    time_since_irradiation = math.log(1 / a37decayfactor) / (-1 * constants.lambda_37 * 365.25)

    time_since_irradiation = log(1 / a37decayfactor) / (-1 * constants.lambda_37 * 365.25)

    if constants.lambda_cl36 < 0.1:
        m = p36cl38cl * constants.lambda_cl36 * time_since_irradiation
    else:
        m = p36cl38cl
    mcl = m / (m * constants.atm3836 - 1)
    cl36 = mcl * (constants.atm3836 * (s36 - ca36) - s38 + k38 + ca38)
    atm36 = s36 - ca36 - cl36
    
    atm40 = atm36 * constants.atm4036
    k40 = k39 * k4039
    ar40rad = s40 - atm40 - k40
    JR = j * ar40rad / k39
#    age = (1 / constants.lambdak) * math.log(1 + JR)
    age = (1 / constants.lambdak) * log(1 + JR)
    
    #===========================================================================
    # errors mass spec copy
    #===========================================================================

    square = lambda x: x * x
    
    Tot40Er = s40er
    Tot39Er = s39er
    Tot38Er = s38er
    Tot37Er = s37er
    Tot36Er = s36er
    
    D = d
    D2 = d * d
    D3 = d * D2
    D4 = d * D3

    T40 = s40 / D4
    T39 = s39 / D3
    T38 = s39 / D2
    T37 = s39 / D
    T36 = s36
    
    A4036 = constants.atm4036
    A3836 = constants.atm3836

    s = ca3937 * D * T37
    T = ca3637 * D * T37
    G = D3 * T39 - s
#    P = mcl * (ca3837 * D * T37 + A3836 * (T36 - T) - D2 * T38 + k3839 * G)
    R = (-k4039 * G - A4036 * (T36 - T - mcl * (ca3837 * D * T37 + A3836 * (T36 - T) - D2 * T38 + k3839 * G)) + D4 * T40)
    G2 = G * G
    
    er40 = square(D4 * j / G) * square(Tot40Er)
    
    er39 = square((j * (-D3 * k4039 + A4036 * D3 * k3839 * mcl)) / G - (D3 * j * R) / G2) * square(Tot39Er)

    er38 = square(A4036 * D2 * j * mcl / G) * square(Tot38Er)
    
    er37 = square((j * (ca3937 * D * k4039 - A4036 * 
            (-ca3637 * D - (-A3836 * ca3637 * D + ca3837 * D - ca3937 * D * k3839) * mcl))) 
            / G + (ca3937 * D * j * R) / G2) * square(Tot37Er)
    
    er36 = square(A4036 * j * (1 - A3836 * mcl) / G) * square(Tot36Er)
    '''
    square((j * (4 * T40 * D3 - K4039 * (3 * D2 * T39 - Ca3937 * T37) 
        - A4036 * (-(Ca3637 * T37) - MCl * (-(A3836 * Ca3637 * T37) 
        + Ca3837 * T37 + K3839 * (3 * D2 * T39 - Ca3937 * T37) 
        - 2 * D * T38)))) 
        / (D3 * T39 - s) - (1 * j * (3 * D2 * T39 - Ca3937 * T37) 
        * (T40 * D4 - K4039 * (D3 * T39 - s) 
        - A4036 * (T36 - T - MCl * (-(T38 * D2) + Ca3837 * T37 * D + A3836 * (T36 - T) + K3839 * (D3 * T39 - s))))) 
        / square(D3 * T39 - s)) * square(DiscEr)
      '''
    erD = square((j * (4 * T40 * D3 - k4039 * (3 * D2 * T39 - ca3937 * T37) 
        - A4036 * (-(ca3637 * T37) - mcl * (-(A3836 * ca3637 * T37) 
        + ca3837 * T37 + k3839 * (3 * D2 * T39 - ca3937 * T37) 
        - 2 * D * T38)))) 
        / (D3 * T39 - s) - (1 * j * (3 * D2 * T39 - ca3937 * T37) 
        * (T40 * D4 - k4039 * (D3 * T39 - s) 
        - A4036 * (T36 - T - mcl * (-(T38 * D2) + ca3837 * T37 * D + A3836 * (T36 - T) + k3839 * (D3 * T39 - s))))) 
        / square(D3 * T39 - s)) * square(der)

    er4039 = square(j * (s - D3 * T39) / G) * square(k4039er)
    
    er3937 = square((j * (D * k4039 * T37 - A4036 * D * k3839 * mcl * T37)) / G + (D * j * T37 * R) / G2) * square(ca3937er)
    
    er3637 = square(-((A4036 * j * (-D * T37 + A3836 * D * mcl * T37)) / G)) * square(ca3637er)
    
    erJ = square(R / G) * square(jer)
    JRer = (er40 + er39 + er38 + er37 + er36 + erD + er4039 + er3937 + er3637 + erJ) ** 0.5
    age_err = (1e-6 / constants.lambdak) * JRer / (1 + ar40rad / k39 * j)
#===============================================================================
# error pychron port 
#===============================================================================
#    s = ca3937 * s37 
#    T = ca3637 * s37
#    G = s39 - s
#    R = (-k4039 * G - constants.atm4036 * (s36 - T - mcl * (ca3837 * s37 + constants.atm3836 * (s36 - T) - s38 + k3839 * G)) + s40)
#    #ErComp(1) = square(D4 * j / G) * square(Tot40Er)
#    er40 = (d ** 4 * j / G) ** 2 * s40er ** 2
#    
#    #square((j * (-D3 * K4039 + A4036 * D3 * K3839 * MCl)) / G - (D3 * j * R) / G2) * square(Tot39Er)
#    d3 = d ** 3
#    er39 = ((j * (-d3 * k4039 + constants.atm4036 * d3 * k3839 * mcl)) / G - (d3 * j * R) / G ** 2) ** 2 * s39er ** 2
#    
#    #square(A4036 * D2 * j * MCl / G) * square(Tot38Er)
#    er38 = (constants.atm4036 * d * d * j * mcl / G) ** 2 * s38er ** 2
#    
#    #square((j * (Ca3937 * D * K4039 - A4036 * 
#    #        (-Ca3637 * D - (-A3836 * Ca3637 * D + Ca3837 * D - Ca3937 * D * K3839) * MCl))) 
#    #        / G + (Ca3937 * D * j * R) / G2) * square(Tot37Er)
#    er37 = ((j * (ca3937 * d * k4039 - constants.atm4036 
#            * (-ca3637 * d - (-constants.atm3836 * ca3637 * d + ca3837 * d - ca3937 * d * k3839) * mcl))) 
#            / G + (ca3937 * d * j * R) / G ** 2) ** 2 * s37er ** 2
#    
#    #square(A4036 * j * (1 - A3836 * MCl) / G) * square(Tot36Er)
#    er36 = (constants.atm4036 * j * (1 - constants.atm3836 * mcl) / G) ** 2 * s36er ** 2
#    
#    #square((j * (4 * T40 * D3 - K4039 * (3 * D2 * T39 - Ca3937 * T37) 
#    #    -A4036 * (-(Ca3637 * T37) - MCl * (-(A3836 * Ca3637 * T37) 
#    #    + Ca3837 * T37 + K3839 * (3 * D2 * T39 - Ca3937 * T37) 
#    #    - 2 * D * T38)))) 
#    #    / (D3 * T39 - s) - (1 * j * (3 * D2 * T39 - Ca3937 * T37) 
#    #    * (T40 * D4 - K4039 * (D3 * T39 - s) 
#    #    - A4036 * (T36 - T - MCl * (-(T38 * D2) + Ca3837 * T37 * D + A3836 * (T36 - T) + K3839 * (D3 * T39 - s))))) 
#    #    / square(D3 * T39 - s)) * square(DiscEr)
#        
#    erD = ((j * (4 * s40 / d - k4039 * (3 * s39 / d - ca3937 * s37 / d)
#        - constants.atm4036 * (-(ca3637 * s37 / d) - mcl * (-(constants.atm3836 * ca3637 * s37 / d)
#        + ca3837 * s37 / d + k3839 * (3 * s39 / d - ca3937 * s37 / d)
#        - 2 * s38 / d))))  
#        / (s39 / d - s) - (1 * j * (3 * s39 / d - ca3937 * s37 / d)
#        * (s40 / d - k4039 * (s40 / d - s)
#        - constants.atm4036 * (s36 - T - mcl * (-(s38 / d) + ca3837 * s37 + constants.atm3836 * (s36 - T) + k3839 * (s39 / d - s)))))
#        / (s39 / d - s) ** 2) ** 2 * der ** 2
#    #square(j * (s - D3 * T39) / G) * square(K4039Er)
#    er4039 = (j * (s - s39 / d) / G) ** 2 * k4039er ** 2
#    
#    #square((j * (D * K4039 * T37 - A4036 * D * K3839 * MCl * T37)) / G + (D * j * T37 * R) / G2) * square(Ca3937Er)
#    er3937 = ((j * (k4039 * s37 - constants.atm4036 * k3839 * mcl * s37)) / G + (j * s37 * R) / G ** 2) ** 2 * ca3937er ** 2
#    
#    #square(-((A4036 * j * (-D * T37 + A3836 * D * MCl * T37)) / G)) * square(Ca3637Er)
#    er3637 = (-((constants.atm4036 * j * (-s37 + constants.atm3836 * mcl * s37)) / G)) ** 2 * ca3637er ** 2
#    
#    #square(R / G) * square(JErLocal)
#    erJ = (R / G) ** 2 * jer ** 2
#    JRer = (er40 + er39 + er38 + er37 + er36 + erD + er4039 + er3937 + er3637 + erJ) ** 0.5
#    age_err = (1e-6 / constants.lambdak) * JRer / (1 + ar40rad / k39 * j)
    
    return age / 1e6, age_err
#============= EOF =====================================

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
#plateau definition
plateau_criteria = {'number_steps':3}

def overlap(a1, a2, e1, e2):
    e1 *= 2
    e2 *= 2
    if a1 - e1 < a2 + e2 and a1 + e1 > a2 - e2:
        return True

#===============================================================================
# non-recursive
#===============================================================================
def find_plateaus(ages, errors, signals):
    plats = []
    platids = []
    for i in range(len(ages)):
        ids = _find_plateau(ages, errors, signals, i)
        if ids is not None and ids.any():
            start, end = ids
            plats.append(end - start)
            platids.append((start, end))
    
#    print plats, platids
    if plats:
        plats = asarray(plats)
        platids = asarray(platids)
    
        return platids[argmax(plats)]
        
def _find_plateau(ages, errors, signals, start):
    plats = []
    platids = []
    for i in range(1, len(ages)):
        if check_plateau(ages, errors, signals, start, i):
            plats.append(i - start)
            platids.append((start, i))
    if plats:
        plats = asarray(plats)
        platids = asarray(platids)
        return platids[argmax(plats)]
        
def check_plateau(ages, errors, signals, start, end):
    for i in range(start, min(len(ages), end + 1)):
        for j in range(start, min(len(ages), end + 1)):
            if i != j:
                obit = not overlap(ages[i], ages[j], errors[i], errors[j])
                mswdbit = not check_mswd(ages, errors, start, end)
                percent_releasedbit = not check_percent_released(signals, start, end)
                n_steps_bit = (end - start) + 1 < 3
                if (obit or 
                    mswdbit or 
                    percent_releasedbit or 
                    n_steps_bit):
                    return False

    return True

def check_percent_released(signals, start, end):
    tot = sum(signals)    
    s = sum(signals[start:end + 1])
    return s / tot >= 0.5

def check_mswd(ages, errors, start, end):
    a_s = ages[start:end + 1]
    e_s = errors[start:end + 1]
#    print calculate_mswd(a_s, e_s)
    return True
#===============================================================================
# recursive
# from timeit testing recursive method is not any faster
#  use non recursive method instead purely for readablity
#===============================================================================

def find_plateaus_r(ages, errors, start=0, end=1, plats=None, platids=None):
    if plats is None:
        plats = []
        platids = []
        
    if start == len(ages) or end == len(ages):
        plats = asarray(plats)
        platids = asarray(platids)
        return platids[argmax(plats)]
    else:
        a = check_plateau_r(ages, errors, start, end)
        if a:
            plats.append((end - start))
            platids.append((start, end))
            
            return find_plateaus_r(ages, errors, start, end + 1, plats, platids)
        else:
            return find_plateaus_r(ages, errors, start + 1, end + 1, plats, platids)

def check_plateau_r(ages, errors, start, end, isplat=True):
    if end < len(ages):
        return isplat and check_plateau_r(ages, errors, start, end + 1, isplat)
    else:
        for i in range(start, min(len(ages), end + 1)):
            for j in range(start, min(len(ages), end + 1)):
                if i != j:
                    if not overlap(ages[i], ages[j], errors[i], errors[j]):
                        return False
        return True

ages = [10] * 50
errors = [1] * 1

def time_recursive():
    find_plateaus_r(ages, errors)

def time_non_recursive():
    find_plateaus(ages, errors)
    
if __name__ == '__main__':
    from timeit import Timer
    t = Timer('time_recursive', 'from __main__ import time_recursive')
    
    n = 5
    tr = t.timeit(n)
    print 'time r', tr / 5
    
    t = Timer('time_non_recursive', 'from __main__ import time_non_recursive')
    tr = t.timeit(n)
    print 'time nr', tr / 5
#    find_plateaus(ages, errors)
#def find_plateaus(ages, errors):
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
#        a1 = ages[start_i]
#        a2 = ages[i]
#        
#        e1 = 2 * errors[start_i]
#        e2 = 2 * errors[i]
#        #a1 = aa1.nominal_value
#        #a2 = aa2.nominal_value
#        #e1 = 2.0 * aa1.std_dev()
#        #e2 = 2.0 * aa2.std_dev()
#        print a1, a2, e1, e2
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

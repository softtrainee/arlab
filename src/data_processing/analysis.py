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
#from datetime import datetime, time
#import math
#import constants
#from uncertainties import ufloat
##=============local library imports  ==========================
#class Analysis(object):
#    '''
#        G{classtree}
#    '''
#    discrmination = 1
#    def __init__(self, raw_data, isotopes):
#        '''
#            @type raw_data: C{str}
#            @param raw_data:
#
#            @type isotopes: C{str}
#            @param isotopes:
#        '''
#        #a ref to the original row tuple
#        self.raw_data = raw_data
#        #dictionary of isotope signals
#        self.isotopes = isotopes
#    def correct_for_disc(self):
#        '''
#        '''
#        disc = self.discrimination
#        data = self.isotopes
#        for key in data:
#            massoffset = int(key[-2:]) - 36
#            data[key] = data[key] * math.pow(disc, massoffset)
#
#class Unknown(Analysis):
#    def __init__(self, raw_data, isotopes, j, pr):
#        '''
#            @type raw_data: C{str}
#            @param raw_data:
#
#            @type isotopes: C{str}
#            @param isotopes:
#
#            @type j: C{str}
#            @param j:
#
#            @type pr: C{str}
#            @param pr:
#        '''
#        super(Unknown, self).__init__(raw_data, isotopes)
#        self.j_value = j
#        self.production_ratio = pr
#        self.blank = None
#    def set_blank(self, blank):
#        '''
#            @type blank: C{str}
#            @param blank:
#        '''
#        self.blank = blank
#    def correct_for_blank(self):
#        '''
#        '''
#        for k in self.isotopes:
#            self.isotopes[k] -= self.blank.isotopes[k]
#
#    def days_since_irradiation(self):
#        '''
#        '''
#       # run_datetime=datetime(2008,9,23,17,10,21)
#       # irradiation_datetime=datetime(2008,8,11,8,54)
#        #run_datetime = datetime(2007, 4, 18, 12, 8, 16)
#        #irradiation_datetime = datetime(2007, 4, 5, 8, 56)
#        run_datetime = datetime(2010, 9, 19, 16, 14, 51)
#        irradiation_datetime = datetime(2010, 7, 19, 16, 14, 0)
#        time_since_irradiation = run_datetime - irradiation_datetime
#        days_since_irradiation = time_since_irradiation.days + time_since_irradiation.seconds / 86400.0
#        return days_since_irradiation
#
#    def set_j(self, j, jerr):
#        '''
#            @type j: C{str}
#            @param j:
#
#            @type jerr: C{str}
#            @param jerr:
#        '''
#        self.j_value = ufloat((j, jerr))
#
#    def correct_for_decay(self):
#        '''
#        '''
#        days_since_irradiation = self.days_since_irradiation()
#
#        start_date = datetime(2010, 1, 1, 8, 54, 0)
#        end_date = datetime(2010, 1, 1, 15, 54, 0)
#
#        td = end_date - start_date
#        ti = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6
#        irradiation_time = ti / 3600.0
#
#        lam = constants.lambda_37.nominal_value
#        self.isotopes['ar37'] = self.isotopes['ar37'] * lam * irradiation_time * math.exp(lam * days_since_irradiation) / (1 - math.exp(-lam * irradiation_time))
#        lam = constants.lambda_39.nominal_value
#        self.isotopes['ar39'] = self.isotopes['ar39'] * lam * irradiation_time * math.exp(lam * days_since_irradiation) / (1 - math.exp(-lam * irradiation_time))
#
#
##    def correct_for_decay(self):
##        #correct 37 and 39 for decay
##
##        years_since_irradiation = self.days_since_irradiation()/365.0
##        
##        start_date=datetime(2010,1,1,8,54,0)
##        end_date=datetime(2010,1,1,15,54,0)
##        
##        
##        irradiation_segments = [end_date-start_date]
##        power_segments=[1]
##        
##        num1=0
##        dem1=0
##        num2=0
##        dem2=0
##        for i,td in enumerate(irradiation_segments):
##            
##            ti=(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
##            
##            ti/=86400.0
##            pi=power_segments[i]
##            num1+=ti*pi
##            dem1+=((1 - math.exp(-constants.lambda_37.nominal_value * ti))/constants.lambda_37.nominal_value * math.exp(constants.lambda_37.nominal_value * years_since_irradiation))
##            num2+=ti*pi
##            dem2+=((1 - math.exp(-constants.lambda_39.nominal_value * ti))/constants.lambda_39.nominal_value * math.exp(constants.lambda_39.nominal_value * years_since_irradiation))
##            
##            
##            
##        #decay_correction_37 = sum(irradiation_segments) / x
##        #decay_correction_39 = sum(irradiation_segments) / y
##        self.isotopes['ar37'] *= num1/dem1
##        self.isotopes['ar39'] *= num2/dem2

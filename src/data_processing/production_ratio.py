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
#Oct 23, 2009
#'''
#
##=============enthought library imports=======================
#
##=============standard library imports ========================
##import uncertainties as un
#from uncertainties import ufloat
#
##=============local library imports  ==========================
#class ProductionRatio(object):
#    '''
#        G{classtree}
#    '''
#    ca3637 = ufloat((0.0, 0.0))
#    ca3837 = ufloat((0.0, 0.0))
#    ca3937 = ufloat((0.0, 0.0))
#    k3739 = ufloat((0.0, 0.0))
#    k3839 = ufloat((0.0, 0.0))
#    k4039 = ufloat((0.0, 0.0))
#    cl3638 = ufloat((0.0, 0.0))
#    cak = ufloat((0.0, 0.0))
#    clk = ufloat((0.0, 0.0))
#
#    def __init__(self, dbpr):
#        for item in dir(self):
#            if not item.startswith('_'):
#                nom = getattr(dbpr, item)
#                std = getattr(dbpr, '%ser' % item)
#                setattr(self, item, ufloat((nom, std)))

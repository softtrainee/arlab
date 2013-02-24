#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================

def calc_point_along_line(x1, y1, x2, y2, L):
    '''
        calculate pt (x,y) that is L units from x1, y1
        
        if calculated pt is past endpoint use endpoint
        
        
                    * x2,y2
                  /  
                /
          L--- * x,y
          |  /
          *
        x1,y1
        
        L**2=(x-x1)**2+(y-y1)**2
        y=m*x+b
        
        0=(x-x1)**2+(m*x+b-y1)**2-L**2
        
        solve for x
    '''
    run = (x2 - x1)

    if run:
        from scipy.optimize import fsolve
        m = (y2 - y1) / float(run)
        b = y2 - m * x2
        f = lambda x: (x - x1) ** 2 + (m * x + b - y1) ** 2 - L ** 2

        #initial guess x 1/2 between x1 and x2
        x = fsolve(f, x1 + (x2 - x1) / 2.)[0]
        y = m * x + b

    else:
        x = x1
        if y2 > y1:
            y = y1 + L
        else:
            y = y1 - L

    lx, hx = min(x1, x2), max(x1, x2)
    ly, hy = min(y1, y2), max(y1, y2)
    if  not lx <= x <= hx or not ly <= y <= hy:
        x, y = x2, y2

    return x, y
#============= EOF =============================================

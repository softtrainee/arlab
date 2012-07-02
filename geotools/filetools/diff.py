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




def decimalconvert(x):
    d, m, s = x.split(' ')
    return float(d) + float(m) / 60. + float(s) / 3600.
import os
p = os.path.expanduser('~')
p1 = os.path.join(p, 'Desktop', 'allsamples07.txt')
p2 = os.path.join(p, 'Desktop', 'datedsamples07.txt')
pp = os.path.join(p, 'Desktop', 'nondatedsamples07.txt')

f1 = open(p1, 'r')
f2 = open(p2, 'r')




allsamples = [(i.split(',')[0], decimalconvert(i.split(',')[1]), decimalconvert(i.split(',')[2])) for i in f1 if i[0] != 's']

datedsamples = [i.split(',')[0] for i in f2 if i[0] != 'S']

nondatedsamples = [i for i in allsamples if i[0] not in datedsamples]
print len(allsamples), len(datedsamples), len(nondatedsamples)
ff = open(pp, 'w')
import csv
writer = csv.writer(ff)
writer.writerows(nondatedsamples)
f1.close()
f2.close()
ff.close()

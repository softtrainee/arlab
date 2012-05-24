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

#=============standard library imports ========================
import csv
#=============local library imports  ==========================
from import_file_tools import find_col, import_csv


def prep_list(data, writer, header=False):
    for args in data:
        #args=line.split(',')
        if header:
            nstr = 'utm'
        else:
            nstr = '%s %s' % (args[eindex], args[nindex])
        args[eindex] = nstr
        args.pop(nindex)

        writer.writerow(args)
if __name__ == '__main__':
    p1 = '/Users/Ross/Programming/Geotools/data/trachyte_samples'
    header, data = import_csv(p1 + '.original.csv')


    outf = open(p1 + '.csv', 'w')
    eindex = find_col('E', header)
    nindex = find_col('N', header)

    writer = csv.writer(outf)

    prep_list([header], writer, header=True)
    prep_list(data, writer)


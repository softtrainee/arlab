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



'''
RossLabs 2009
Ross  Jake Ross   jirhiker@gmail.com

Nov 13, 2009
'''

#=============enthought library imports=======================

#=============standard library imports ========================
import os
import csv
#=============local library imports  ==========================
from LatLongUTMconversion import UTMtoLL, LLtoUTM
from filetools.import_file_tools import find_col, flatten
def convert_utm_ll(p, zone):
    f = open(p, 'U')
    dir = os.path.dirname(p)

    pp = os.path.basename(p).split('.')[0] + '_latlong.txt'
    npath = os.path.join(dir, pp)

    nf = open(npath, 'w')

    nwriter = csv.writer(nf)
    reader = csv.reader(f, delimiter='\t')
    header = reader.next()

    utms = flatten([(x.capitalize(), x.upper(), x) for x in ['utm']])
    utm_index = find_col(utms, header)
    print header, utm_index
    header[utm_index] = 'Latitude'
    header.insert(utm_index + 1, 'Longitude')

    utm_delimiter = ' '
    nrows = []
    nrows.append(header)
    for row in reader:
        utmcol = row[utm_index]
        args = utmcol.split(utm_delimiter)
        e = args[0]
        n = args[1]
        long, lat = UTMtoLL(23, float(n), float(e), zone)

        row[utm_index] = lat
        row.insert(utm_index, long)
        nrows.append(row)

    map(nwriter.writerow, nrows)
    f.close()
    nf.close()
    return npath

def main():
    pa = ''
    while not os.path.isfile(pa):
        pa = raw_input('input file >>> ')
    zone = raw_input('utm zone (ex. 13S)')

    print convert_utm_ll(pa, zone)
if __name__ == '__main__':
    main()

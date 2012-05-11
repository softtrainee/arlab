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
import os
import csv
#=============local library imports  ==========================
from filetools.import_file_tools import find_col, flatten
def main():
    #open the csv file

    #h = '/Users/Ross/Documents/Antarctica/MinnaBluff07-08/samplelists/'
    #source_dir=raw_input('source directory >> ')
    input_file = ''
    input_file = '/Users/Ross/Programming/Geotools/data/2.txt'
    while not os.path.isfile(input_file):
        input_file = raw_input('input file >> ')

    source_dir = os.path.dirname(input_file)
    #input_file = 'test_data.csv'
    output_file = '/Users/Ross/Programming/Geotools/data/2_new.txt'
    #output_file = raw_input('output file >> ')
    #output_file='out_test_data_csv.txt'

    f = open(input_file, 'U')
    reader = csv.reader(f, delimiter=',')
    ndata = []
    first = True
    for row in reader:
        if first:
            print row
            first = False
            lats = flatten([(i.capitalize(), i.upper(), i) for i in ['lat', 'latitude']])
            longs = flatten([(i.capitalize(), i.upper(), i) for i in ['lon', 'long', 'longitude']])
            lat_index = find_col(lats, row)
            long_index = find_col(longs, row)
            print 'hh', lat_index, long_index, row
        else:
            lat = row[lat_index]
            long = row[long_index]
            nlat = convert(lat)
            nlong = convert(long)
            row[lat_index] = -nlat
            row[long_index] = nlong

        ndata.append(row)
    f.close()
    nf = open(os.path.join(source_dir, output_file), 'w')
    writer = csv.writer(nf)
    map(writer.writerow, ndata)
    nf.close()
def convert(l, type='space'):
    if l != '':
        #d, m, s = l.split(' ')
        if type == 'tab':
            args = l.split('\t')
            if args.count('') != len(args):
                d = args[0]
                m = args[1]
                s = args[2]
                if d == '':
                    d = args[1]
                    m = args[2]
                    s = args[3]
        elif type == 'space':
            args = l.split(' ')
            d = args[0]
            m = args[1]
            s = args[2]

        #print l.split(' ')
        return float(d) + float(m) / 60.0 + float(s) / 3600.0
    else:
        return ''

if __name__ == '__main__':
    main()

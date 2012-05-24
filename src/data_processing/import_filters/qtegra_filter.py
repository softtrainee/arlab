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



#============= enthought library imports =======================
from traits.api import HasTraits
from pyface.message_dialog import warning
#============= standard library imports ========================
import os
import csv
#from src.helpers.paths import data_dir
from numpy import array, hsplit

#from pylab import *
#============= local library imports  ==========================
class QtegraFilter(HasTraits):
#    def filter(self):
#        #get the path to filter
#        #ip=os.path.join(data_dir,'sandbox','test.csv')
#        #self._parse_and_filter(ip)
#        ip=os.path.join(data_dir,'sandbox')
#        dlg = FileDialog(action = 'open', default_directory=ip)
#        if dlg.open() == OK:
#        
#            #parse and filter the file
#            self._parse_and_filter(dlg.path)

    nisotopes = 2
    with_results = False

    def filter(self, *args, **kw):
        return self._parse_and_filter(*args, **kw)

    def _parse_and_filter(self, inpath, *args, **kw):
        #make a directory to hold resutls

        iroot, iname = os.path.split(inpath)

        iname, _ext = os.path.splitext(iname)
        root = os.path.join(iroot, iname)
        if not os.path.isdir(root):
            os.mkdir(root)

        results = []
        with open(inpath, 'U') as f:
            #sniff file for dialect
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)

            reader = csv.reader(f, dialect)

            for i, line in enumerate(reader):
                if i == 2:
                    header = line

                if i > 3:
                    series = self._parse_line(header, line, i - 3)
                    if series is None:
                        break

                    for si in series:
                        si.dump(root)
                        results.append(si.name)
        return results

    def _parse_line(self, header, line, nrun):
        nisotopes = self.nisotopes
        niso = nisotopes * 5
        series = []

        if self.with_results:
            line = line[2:-7]
        else:
            line = line[2:-2]

        nline = array(line)
        try:
            nline = nline.reshape(len(line) / niso, niso)
        except ValueError:
            warning(None, 'Invalid number (%i) of isotope measurements for this file' % nisotopes)
            return None

        nline = hsplit(nline, nisotopes)

        for i, si in enumerate(nline):

            '''
                si is a 2d array
                each row is a cycle
            '''
            ind = i * 5 + 2
            name = '%03i_%s' % (nrun, '_'.join(header[ind].split(':')[1:]))

            s = XYSeries(name)
            s.parse_raw_data(si)

            series.append(s)

        return series

class XYSeries(object):
    def __init__(self, name):
        self.name = name
        self.xs = []
        self.ys = []

    def parse_raw_data(self, data):
        for cycle in data:
            self.xs.append(float(cycle[2]))
            self.ys.append(float(cycle[1]))

    def dump(self, root):

        p = os.path.join(root, '%s.txt' % self.name)

        with open(p, 'w') as f:
            writer = csv.writer(f, delimiter='\t')

            #write a header row
            header = ['Time (s)', 'Intensity (fA)']
            writer.writerow(header)
            for x, y in zip(self.xs, self.ys):
                row = [x, y, 1]
                writer.writerow(row)

if __name__ == '__main__':
    a = QtegraFilter()
    a.filter()
#============= EOF ====================================

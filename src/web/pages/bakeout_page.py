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
#============= standard library imports ========================
from twisted.web.resource import Resource
import os, csv
from src.helpers.datetime_tools import diff_timestamp
from src.web.charts.annotated_timeline_chart import annotated_timeline
from src.helpers.paths import data_dir
#============= local library imports  ==========================
import cgi

class BakeoutPage(Resource):
#    isLeaf = True
    def get_datafile(self):
        base = os.path.join(data_dir, 'bakeouts')
        p = os.listdir(base)[-1]
        return os.path.join(base, p), p

    def render_GET(self, request):

        #get the data

        p, name = self.get_datafile()

        data = []
        nbytes = os.path.getsize(p)
        ndownsample = 0
        if nbytes > 1e5:
            percent = 25
            ndownsample = int(100 / float(percent))

        with open(p, 'rb') as f:
            #build the chart cols and data
            reader = csv.reader(f)
            header = reader.next()

            for line in reader:

                td, h, m, s = diff_timestamp(float(line[0]), 0)

                if td.days:
                    tstamp = 'new Date(2011,1,{0.days},{1},{2},{3})'.format(td, h, m, s)
                else:
                    tstamp = 'new Date(2011,1,1,{0},{1},{2})'.format(h, m, s)

                d = [line[i] for i in range(1, len(header), 2)]
                data.append('[{}]'.format(','.join([tstamp] + d)))
                for i in range(ndownsample):
                    try:
                        reader.next()
                    except StopIteration:
                        break

        data = '[{}]'.format(',\n'.join(data))

        cols = ',\n'.join(['data.addColumn("datetime","Date")'] + ['data.addColumn("number","{}")'.format(header[i].split('_')[0])
                                                                   for i in range(1, len(header), 2)])

        return annotated_timeline(title=name,
                                  data_path=p,
                                  data=data,
                                  columns=cols,
                                  width=75
                                  )

    def render_POST(self, request):

        return '<html><body>%s</body></html>' % cgi.escape(request.args["te"][0])






#============= EOF =====================================

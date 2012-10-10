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
#============= local library imports  ==========================
def annotated_timeline(title=None, width=None, height=None, **kw):
    if title is None:
        title = 'Foo'

    if height is None:
        height = 300

    if width is None:
        width = 75

    kw['height'] = height
    kw['width'] = width
    kw['title'] = title
    s = '''
<html>
    <head>
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        <script type="text/javascript">
        google.load("visualization","1",{"packages":['annotatedtimeline']});
        google.setOnLoadCallback(drawChart);
        function drawChart(){
            var data = new google.visualization.DataTable();
            %(columns)s;
            data.addRows(%(data)s);
            var options={};
            var chart = new google.visualization.AnnotatedTimeLine(document.getElementById("chart_div"));
            chart.draw(data,options);
        }
        </script>    
    </head>
    
    <body>
        <h1>%(title)s</h1>
        <div id="chart_div" style='width: %(width)s%%; height: %(height)spx;'></div>
        <p>
        data path: %(data_path)s
        </p>

    </body>
</html>
'''

    return s % kw
#============= EOF =====================================

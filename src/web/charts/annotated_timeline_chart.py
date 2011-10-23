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

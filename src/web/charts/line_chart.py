#=============enthought library imports=======================

#============= standard library imports ========================
#============= local library imports  ==========================
def line(width=None, height=None, line_width=None, **kw):
    if height is None:
        height = 300
        
    if width is None:
        width = 75
    
    if line_width is None:
        line_width = 1
        
    kw['height'] = height
    kw['width'] = width
    kw['line_width'] = line_width
        
    s = '''
<html>
    <head>
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        <script type="text/javascript">
        google.load("visualization","1",{"packages":['corechart']});
        google.setOnLoadCallback(drawChart);
        function drawChart(){
            var data = new google.visualization.DataTable();
            %(columns)s;
            data.addRows(%(data)s);
            var options={"title":"%(title)s",
                          "lineWidth":"%(line_width)s",
                          "pointSize":"0"
                            };
            var chart = new google.visualization.ScatterChart(document.getElementById("chart_div"));
            chart.draw(data,options);
        }
        </script>    
    </head>
    
    <body>
    <div id="chart_div" style='width: 700px; height: %(height)spx;'></div>
    </body>
</html>
'''
     
    return s % kw   
#============= EOF =====================================

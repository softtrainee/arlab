'''
RossLabs 2009
Ross  Jake Ross   jirhiker@gmail.com

Nov 11, 2009
'''

#=============enthought library imports=======================

#=============standard library imports ========================
import os
import logging
import csv
log = logging.getLogger('kmlwriter')
#=============local library imports  ==========================
def color_generator():
    i = 0
    colors = ['FFF00014', #blue
            'FF1478FF', #orange

            'FF1400FF', #red
            'FF14F000', #green

            'FF14F0FF', #yellow
            'FF7800F0',
            
            'FF780078',#purple 120,0,120
            'FF783CF0',#pink 240,60,120
            
            ]
    while 1:
        yield colors[i]
        i += 1
        if i > len(colors):
            i = 0
color_gen = color_generator()

def make_style_from_source(srcpath, style_dir):
    #sf=open(srcpath,'r')
    style_name = '%s_style' % os.path.basename(srcpath).split('.')[0]
    log.info('adding %s' % style_name)
    style_path = os.path.join(style_dir, '%s.txt' % style_name)
    stf = open(style_path, 'w')
    icon = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
    stf.write('''<Style id="%s">
    <LabelStyle>
    <color>FF14F0FF</color>
    <scale>0.8</scale>
    </LabelStyle>
    <IconStyle>
        <color>%s</color>
        <scale>%i</scale>
        <Icon>
            <href>%s</href>
        </Icon>
    </IconStyle>
</Style>
''' % (style_name, color_gen.next(), 1, icon)
)
    return style_name, style_path
def make_schema_from_source(srcpath, schema_dir, display_figure):
    sf = open(srcpath, 'U')
    reader = csv.reader(sf)
    schema_name = '%s_schema' % os.path.basename(srcpath).split('.')[0]
    log.info('adding %s' % schema_name)
    schema_path = os.path.join(schema_dir, '%s.txt' % schema_name)
    scf = open(schema_path, 'w')

    header = reader.next()
    scf.write('<Schema id="%s">' % schema_name)
    for item in header:
        if '\n' in item:
            item = item[:-1]
        field = '''<SimpleField type="string" name="%s">
    <displayName>%s</displayName>
</SimpleField>
''' % (item, item)


        scf.write(field)
    if display_figure:
        scf.write('''<SimpleField type="string" name="figure">
        </SimpleField>
''')
    scf.write('</Schema>')
    scf.close()
    sf.close()
    return schema_name, schema_path
def make_placemarker_from_source(srcpath, placemarker_dir, display_figure):
    sf = open(srcpath, 'U')
    header = csv.reader(sf).next()

    pmname = '%s_placemarker' % os.path.basename(srcpath).split('.')[0]
    log.info('adding %s' % pmname)
    pmpath = os.path.join(placemarker_dir, '%s.txt' % pmname)
    pmf = open(pmpath, 'w')

    pmf.write('''<Placemark>
    <name>%s</name>
    
    <styleUrl>#<![CDATA[%s]]></styleUrl>
        <ExtendedData>
        
'''
)

    for item in header:
        if '\n' in item:
            item = item[:-1]
        pmf.write('''<Data name="%s">
        <displayName>%s</displayName>
        <value>%%s</value>
        </Data>
    ''' % (item,item))
    if display_figure:
        pmf.write('''<Data name="figure">
        <![CDATA[<img src="%s"></img>]]>
        </Data>
''')
    pmf.write('''
    </ExtendedData>
''')
    pmf.write('''<Point>
    <coordinates>
    %s,%s,0
    </coordinates>
</Point>
</Placemark>
'''
)
    sf.close()
    pmf.close()
    return pmname, pmpath
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

Nov 11, 2009
'''

#=============enthought library imports=======================

#=============standard library imports ========================
import logging
import os
import csv
#=============local library imports  ==========================
from taghelper import *
from filetools.import_file_tools import find_col, flatten
from kml_writer_configuration import *

log = logging.getLogger('kmlwriter')

names = flatten([(x.capitalize(), x.upper(), x) for x in ['sample name', 'sample_name', 'name', 'Sample Name', 'Sample_Name']])

def display_available(li):
    p = [key for key in li]
    s = ''
    for pp in p:
        s += ' %s ' % pp
    print s
def parse_for_schema(placemarker, sample, conf, source_header):
    arguments = []
    def start_element(name, attrs):
        if name == 'Data':
            n = attrs['name']
            if n != 'figure':
                arguments.append(str(n))

    placemarkerfile = open(conf.placemarker_dict[placemarker], 'r')
    s = placemarkerfile.read()

    import xml.parsers.expat as xmlp
    parser = xmlp.ParserCreate()
    parser.StartElementHandler = start_element

    parser.Parse(s)
    if conf.display_figure:
        arguments.append('figure')

    arguments.append('Longitude')
    arguments.append('Latitude')
    arguments.append('Lon')
    arguments.append('Lat')
    args = ()
    #print 'arg', arguments
    for item in arguments:
       # print item
        if item == 'figure':
            item = conf.image_tag
            i = source_header.index(item)

            arg = '%s/%s/%s.png' % (conf.source_dir, conf.image_dir, sample[i])
        else:

            try:
                i = source_header.index(item)
                arg = sample[i]
                args += (arg,)
            except ValueError:
                pass

    return args

def parse_source(conf):
    header = conf.header
    #names = flatten([(x.capitalize(), x.upper(), x) for x in ['sample name', 'sample_name', 'name', 'Sample Name', 'Sample_Name']])
    name_index = find_col(names, source_header)
    ages = ['age', 'Age']
    age_index = find_col(ages, source_header)

    for s in conf.data:
        print s

def parse_src(scrname, src_file, output_file, placemarker, style, schema, conf):

    #samples=[i.split(',') for i in src_file]

    output_file.write(folder(scrname))

    pmf = open(conf.placemarker_dict[placemarker], 'r')
    placemarker_template = pmf.read()
    pmf.close()

    reader = csv.reader(src_file)
    source_header = reader.next()

    #names = ['Sample Name', 'Sample_Name', 'sample', 'Sample', 'name', 'Name']
    name_index = find_col(names, source_header)
    ages = ['age', 'Age']
    age_index = find_col(ages, source_header)


    for s in reader:
        if conf.age_only:
            pname = s[age_index]
        elif conf.name_only:
            pname = s[name_index]
        elif conf.age_in_name:
           # print 'agi', age_index, name_index
            pname = '%s, %s' % (s[name_index], s[age_index])
        elif conf.no_name:
            pname = ''
        else:
            pname = s[name_index]


        #baseargs = (pname, style, schema)
        baseargs = (pname, style)
        args = parse_for_schema(placemarker, s, conf, source_header)


        args = baseargs + args
        #print placemarker_template,len(args)
        placemark = placemarker_template % args
        output_file.write(placemark)
    output_file.write(endfolder())

def load_schemas(of, schema_list, log):
    log.info('=====loading schemas=======')
    for schema in schema_list:
        schema = schema_list[schema]
        log.info('loading schema %s' % os.path.basename(schema))

        f = open(schema, 'r')
        s = f.read()
        of.write(s)
        f.close()

def build_kml_file(conf):
    kmlheader = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
'''
    kmlfooter = '''
</Document>
</kml>
    '''
    if isinstance(conf, KMLWriterConfigurationStream):
        kml = []
        header = [kmlheader]
        kml += header
        kml += conf.schema
        kml += conf.style
        kml += parse_source(conf.data)
        footer = [kmlfooter]
    else:

        scps = conf.schema_dict
        stps = conf.style_dict
        pmps = conf.placemarker_dict
        srcps = conf.source_paths
        output = conf.output_path

        of = open(output, 'w')
        of.write(kmlheader)
        #load_schemas(of,scps,log)

        of.write('''<LookAt>
        <longitude>166.2</longitude>
        <latitude>-78.535</latitude>
        <altitude>45000</altitude>
        <altitudeMode>absolute</altitudeMode>
        <heading>0</heading>
        </LookAt>
        
''')
        for style in stps:
            style = stps[style]
            log.info('loading style %s' % os.path.basename(style))

            f = open(style, 'r')
            s = f.read()
            of.write(s)
            f.close()

        use_default = conf.use_default
        for src in srcps:
            log.info('loading placemarks for %s' % os.path.basename(src))

            n = os.path.basename(src).split('.')[0]
            if use_default:
                schema = '%s_schema' % n
                style = '%s_style' % n
                placemarker = '%s_placemarker' % n

            else:
            #===========user input=============
                schema = raw_input('schema for %s (l to list available) >> ' % n)
                if not schema in scps:
                    print 'invalid schema'
                    schema = 'l'
                while schema == 'l':
                    display_available(scps)
                    schema = raw_input('schema for %s (l to list available) >> ' % n)
                    if not schema in scps:
                        print 'invalid schema'
                        schema = 'l'
                style = raw_input('style for %s (l to list available) >> ' % n)
                if not style in stps:
                    print 'invalid schema'
                    style = 'l'
                while style == 'l':
                    display_available(stps)
                    style = raw_input('style for %s (l to list available) >> ' % n)
                    if not style in stps:
                        style = 'l'
                placemarker = raw_input('placemark name for %s (l to list available) >> ' % n)
                if not placemarker in pmps:
                        placemarker = 'l'
                while placemarker == 'l':
                    display_available(pmps)
                    placemarker = raw_input('placemark name for %s (l to list available) >> ' % n)
                    if not placemarker in pmps:
                        placemarker = 'l'

           # log.info('using %s' % schema)
            log.info('using %s' % style)
            log.info('using %s' % placemarker)
            f = open(src, 'U')
            parse_src(n, f, of, placemarker, style, schema, conf)
        of.write(kmlfooter)
        of.close()
        log.info('build of %s successful' % os.path.basename(output))
        print '''Your KML file is located at 
        %s
    ''' % conf.output_path

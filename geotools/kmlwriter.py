'''
RossLabs 2009
Ross  Jake Ross   jirhiker@gmail.com

Nov 10, 2009
'''

#=============enthought library imports=======================

#=============standard library imports ========================
import os
import logging
import pickle
import sys
#=============local library imports  ==========================
from kmltools.kml_writer_configuration import KMLWriterConfiguration
from kmltools.taghelper import folder, endfolder
from kmltools.standard_builders import *
from kmltools.kml_builder import build_kml_file

from filetools.utm_latlong_converter import convert_utm_ll
'''
KML Writer

takes a text file and parses it into a KML file
'''
#=============== set up logger==============
logdir = os.path.join(os.getcwd(), 'logs')
if not os.path.isdir(logdir):
    os.mkdir(logdir)
logpath = os.path.join(logdir, 'kmlwriter.log')
if sys.version.split(' ')[0] < '2.4.0':
    logging.basicConfig()
else:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=logpath,
                    filemode='w'
                  )
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format 
console.setFormatter(formatter)

log = logging.getLogger('kmlwriter')
log.addHandler(console)
#===========================================
def get_number(name):
    n = None
    while n is None:
        n = raw_input('number of %s files >> ' % name)
        try:
            n = int(n)
        except ValueError:
            n = None
    return n
def check_dir(dir, make=False):

    if not os.path.isdir(dir):
        if make:
            log.info('creating %s directory' % os.path.basename(dir))
            os.mkdir(dir)
            return True
        else:
            log.info('%s directory does not exist' % os.path.basename(dir))
            return False
    else:
        return True

def build_placemarkers(source_paths, placemarker_dir, display_figure):
    placemarker_dict = {}
    for src in source_paths:
        n, p = make_placemarker_from_source(src, placemarker_dir, display_figure)
        placemarker_dict[n] = p
    return placemarker_dict

def build_styles(source_paths, style_dir):
    style_dict = {}
    for srcpath in source_paths:
        n, p = make_style_from_source(srcpath, style_dir)
        style_dict[n] = p
    return style_dict

def build_schemas(source_paths, schema_dir, display_figure):
    schema_dict = {}
    for srcpath in source_paths:
        n, p = make_schema_from_source(srcpath, schema_dir, display_figure)
        schema_dict[n] = p
    return schema_dict

def build_csv(items):
    l = ''
    c = 0
    for i in items:
        if c < len(items) - 2:
            l += '%s,' % i
        else:
            l += '%s' % i
        c += 1
    return l

def load_placemarkers(source_dir, source_paths, use_default, display_figure):
    #specify placemark files   

    if use_default:
        dir = 'placemarkers'
        dir = os.path.join(source_dir, dir)
        check_dir(dir, make=True)
    else:
        while 1:
            dir = raw_input('placemarker dir >> ')
            dir = os.path.join(source_dir, dir)
            if dir == '':
                log.info('using default placemarker directory')
                dir = 'placemarkers'
                dir = os.path.join(source_dir, dir)
                check_dir(dir, make=True)
            elif check_dir(dir):
                break


    placemarker_dir = dir
    log.info('placemarker dir = %s' % dir)

    placemarker_dict = {}
    if use_default:
        placemarker_dict = build_placemarkers(source_paths, placemarker_dir, display_figure)
    elif raw_input('build placemarkers from source (y/n)? >> ') == 'y':
        placemarker_dict = build_placemarkers(source_paths, placemarker_dir, display_figure)
    else:
        nplacemarkers = get_number('placemarkers')
        for i in range(nplacemarkers):
            p = raw_input('placemarker file >> ')
            n = raw_input('placemarker name >> ')
            p = 'placemarker1.txt'
            n = 'circle'
            placemarker_dict[n] = os.path.join(placemarker_dir, p)
    return placemarker_dict

def load_style(source_dir, source_paths, use_default):
     #specify style files
    if use_default:
        dir = 'styles'
        dir = os.path.join(source_dir, dir)
        check_dir(dir, make=True)
    else:
        while 1:
            dir = raw_input('style directory >> ')
            dir = os.path.join(source_dir, dir)
            if dir == '':
                log.info('using default style directory')
                dir = 'styles'
                dir = os.path.join(source_dir, dir)
                check_dir(dir, make=True)
            elif check_dir(dir):
                break


    style_dir = dir
    log.info('style dir = %s' % dir)

    style_dict = {}
    if use_default:
        style_dict = build_styles(source_paths, style_dir)
    elif raw_input('make default styles from sources (y/n)? >> ') == 'y':
        style_dict = build_styles(source_paths, style_dir)
    else:
        nstyles = get_number('styles')
        style_dir = os.path.join(source_dir, style_dir)
        for i in range(nstyles):
            p = raw_input('style file >> ')
            n = raw_input('style name >> ')
            style_dict[n] = os.path.join(style_dir, p)
    return style_dict

def load_schema(source_dir, source_paths, use_default, display_figure):
    #specifiy the schema files
    if use_default:
        dir = 'schemas'
        dir = os.path.join(source_dir, dir)
        check_dir(dir, make=True)
    else:
        while 1:
            dir = raw_input('schema directory >> ')
            dir = os.path.join(source_dir, dir)
            if dir == '':
                log.info('using default schema directory')
                dir = 'schemas'
                dir = os.path.join(source_dir, dir)
                check_dir(dir, make=True)
            elif check_dir(dir):
                break

    schema_dir = dir
    log.info('schema dir = %s' % dir)

    schema_dict = {}
    if use_default:
        schema_dict = build_schemas(source_paths, schema_dir, display_figure)
    elif raw_input('make standard schema from source y/n? >> ') == 'y':
        schema_dict = build_schemas(source_paths, schema_dir, display_figure)
    else:
        nschema = get_number('schema')
        for i in range(nschema):
            p = raw_input('schema file >> ')
            n = raw_input('schema name >> ')
            schema_dict[n] = os.path.join(schema_dir, p)

    return schema_dict
def load_source_paths(nfiles, source_dir, log):
    source_paths = []
    for i in range(nfiles):
        p = raw_input('source file >> ')
        p = os.path.join(source_dir, p)

        while not os.path.isfile(p):
            print '%s is not a valid file' % p
            p = raw_input('source file >> ')
            p = os.path.join(source_dir, p)

        log.info('adding source_file %s' % p)
        if raw_input('convert source file (y/n)? >> ') == 'y':
            zone = raw_input('UTM zone ? >> ')
            p = convert_utm_ll(p, zone)

        source_paths.append(p)
    return source_paths
def bootstrap_configuration():
    log.info('bootstrap configuration')
    print '''
===========================================
    Create a new configuration file
===========================================

'''
    #do configuration 
    #specify source files
    #source_paths = []
    source_dir = raw_input('source directory >> ')
    if source_dir == '':
        log.info('using default')
        source_dir = os.path.join(os.getcwd(), 'data')


    else:
        while not os.path.isdir(source_dir):
            source_dir = raw_input('source directory >> ')
            if source_dir == '':
                log.info('using default')
                source_dir = os.path.join(os.getcwd(), 'data',)

    check_dir(source_dir, make=True)
    log.info('source directory = %s' % source_dir)

    nfiles = get_number('source')
    #nfiles=2
    source_paths = load_source_paths(nfiles, source_dir, log)
    #source_paths=[os.path.join(source_dir,'%s.txt'%i) for i in range(nfiles)]
   # p1=os.path.join(source_dir,'trachyte_samples_dated.csv')
    #p2=os.path.join(source_dir,'trachyte_samples_nondated.csv')
    #zone='58C'
    #source_paths=[convert_utm_ll(p1, zone),convert_utm_ll(p2, zone)]
    use_default = raw_input('use default placemarkers (y/n)? >> ') == 'y'
    if use_default:
        display_figure = False
        name_only = True
        age_in_name = False

        age_only = False
        no_name = False

        image_tag = 'L#'
        image_dir = 'images'
    else:
        age_in_name = raw_input('display name as name and age (y/n)? >> ') == 'y'
        age_only = False
        if not age_in_name:
            age_only = raw_input('display name as age only (y/n)? >> ') == 'y'
            if not age_only:
                no_name = raw_input('dont display a name (y/n)> >>') == 'y'
        image_dir = None
        display_figure = raw_input('display a figure with placemarker (y/n)? >> ') == 'y'
        if display_figure:
            image_dir = raw_input('image dir >> ')
            #image_dir=os.path.join(source_dir,image_dir)
            image_tag = raw_input('column name the contains image name >> ')

  #  schema_dict = load_schema(source_dir, source_paths, use_default, display_figure)
    style_dict = load_style(source_dir, source_paths, use_default)
    placemarker_dict = load_placemarkers(source_dir, source_paths, use_default, display_figure)

    #specify output path
    output_path = raw_input('output file >> ')
    #output_path='trachyte_samples.kml'
    output_path = os.path.join(os.getcwd(), 'data', output_path)

    conf = KMLWriterConfiguration()
    conf.source_dir = source_dir
    conf.image_dir = image_dir

    conf.source_paths = source_paths
    conf.output_path = output_path

    #conf.schema_dict = schema_dict
    conf.style_dict = style_dict
    conf.output_path = output_path
    conf.placemarker_dict = placemarker_dict

    conf.use_default = use_default
    conf.display_figure = display_figure
    conf.age_in_name = age_in_name
    conf.age_only = age_only
    conf.no_name = no_name
    conf.name_only = name_only
    conf.image_tag = image_tag
#    if raw_input('save this configuration (y/n)? >> ') == 'y':
#        conf_file = open(os.path.join(os.getcwd(), 'conf.cfg'), 'wb')
#        pickle.dump(conf, conf_file)
#        conf_file.close()
    return conf

def main():
    print '''
===========================================
Welcome to KML Writer
Jake Ross 2009
jirhiker@gmail.com
NMGRL

A simple script to create customizable kml files for Google Earth from a text (csv) file 

Source Files:
    source files must be comma separated value (csv) files
    the first line in the file should be a header ie column name
    
    sources files need at least the 3 following columns
    Name,Latitude,Longitude

    
TIP:
    if you do not know a value to enter simple hit return
    
    return after >> will yield the default value
    
    !WILL NOT WORK FOR SOURCE FILES!
    currently source files must be located in the source directory
    and are the only files the you need to specify during configuration
    
see Jake for help
===========================================
'''


    conf_exists = False
    p = os.path.join(os.getcwd(), 'conf.cfg')
    if os.path.isfile(p):
        conf_exists = True

    if not conf_exists:
        conf = bootstrap_configuration()
    elif raw_input('load conf file (y/n)? >> ') == 'n':
         conf = bootstrap_configuration()
    else:
        cf = open(p, 'rb')
        conf = pickle.load(cf)

        if raw_input('edit output file (y/n)? >> ') == 'y':
            o = raw_input('output file name >> ')
            o = os.path.join(conf.source_dir, o)
            conf.output_path = o


    #build the kml file 
    build_kml_file(conf)

if __name__ == '__main__':

    main()

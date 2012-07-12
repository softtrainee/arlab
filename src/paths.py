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
Global path structure

add a path verification function
make sure directory exists and build if not
'''
from os import path, mkdir



#host_url = 'https://arlab.googlecode.com/svn'
#project_root = 'trunk'

#if beta:
#    home = '{}_beta{}'.format(home, version)
#    project_root = 'branches/pychron'
#
#project_home = path.join(host_url, project_root)

class Paths():
    root = None
    pychron_src_root = None
    doc_html_root = None

    #_dir suffix ensures the path is checked for existence
    root_dir = root
    stable_root = None
    #==============================================================================
    # #database
    #==============================================================================
    device_scan_root = device_scan_root = None
    device_scan_db = None

    bakeout_db_root = bakeout_db_root = None
    bakeout_db = None
    co2laser_db_root = None
    co2laser_db = None

    diodelaser_db_root = None
    diodelaser_db = None

    isotope_db_root = None
    isotope_db = None
    #==============================================================================
    # root
    #==============================================================================
    scripts_dir = scripts_dir = None
    experiment_dir = None
    plugins_dir = None
    hidden_dir = hidden_dir = None
    test_dir = None
    #==============================================================================
    # setup
    #==============================================================================
    setup_dir = setup_dir = None
    device_dir = device_dir = None
    canvas2D_dir = None
    canvas3D_dir = None
    extraction_line_dir = None
    monitors_dir = None
    jog_dir = None
    pattern_dir = None

    bakeout_config_dir = None
    bakeout = None

    heating_schedule_dir = None
    map_dir = map_dir = None
    user_points_dir = None
    #==============================================================================
    # data
    #==============================================================================
    data_dir = data_dir = None
    modeling_data_dir = None
    argus_data_dir = None
    positioning_error_dir = None
    snapshot_dir = None
    video_dir = None
    stage_visualizer_dir = None
    #initialization_dir = None
    #device_creator_dir = None

    #==============================================================================
    # lovera exectuables
    #==============================================================================
    clovera_root = None

    def build(self, version):
        HOME = path.expanduser('~')

        home = 'Pychrondata{}'.format(version)

        self.root = root = path.join(HOME, home)
        src_repo_name = 'pychron{}'.format(version)
        self.pychron_src_root = pychron_src_root = path.join(HOME, 'Programming', 'mercurial', src_repo_name)
        self.doc_html_root = path.join(pychron_src_root, 'docs', '_build', 'html')

        #_dir suffix ensures the path is checked for existence
        self.root_dir = root
        stable_root = path.join(HOME, 'Pychrondata')

        #==============================================================================
        # #database
        #==============================================================================
        db_path = '/usr/local/pychron'
        self.device_scan_root = device_scan_root = path.join(db_path, 'device_scans')
        self.device_scan_db = path.join(device_scan_root, 'device_scans.sqlite')

        self.bakeout_db_root = bakeout_db_root = path.join(db_path, 'bakeoutdb')
        self.bakeout_db = path.join(bakeout_db_root, 'bakeouts.sqlite')
        self.co2laser_db_root = path.join(db_path, 'co2laserdb')
        self.co2laser_db = path.join(db_path, 'co2.sqlite')

        self.diodelaser_db_root = path.join(db_path, 'diodelaserdb')
        self.diodelaser_db = path.join(db_path, 'diode.sqlite')
        self.isotope_db_root = path.join(db_path, 'isotopedb')
        self.isotope_db = path.join(db_path, 'isotope.sqlite')
        #==============================================================================
        # root
        #==============================================================================
        self.scripts_dir = scripts_dir = path.join(root, 'scripts')
        experiment_dir = path.join(root, 'experiments')
        plugins_dir = path.join(root, 'plugins')
        self.hidden_dir = path.join(root, '.hidden')
        self.test_dir = path.join(root, 'testing')
        #==============================================================================
        # setup
        #==============================================================================
        self.setup_dir = setup_dir = path.join(root, 'setupfiles')
        self.device_dir = device_dir = path.join(setup_dir, 'devices')
        self.canvas2D_dir = path.join(setup_dir, 'canvas2D')
        self.canvas3D_dir = path.join(setup_dir, 'canvas3D')
        self.extraction_line_dir = path.join(setup_dir, 'extractionline')
        self.monitors_dir = path.join(setup_dir, 'monitors')
        self.jog_dir = path.join(setup_dir, 'jogs')
        self.pattern_dir = path.join(setup_dir, 'patterns')

        self.bakeout_config_dir = path.join(setup_dir, 'bakeout_configurations')
        self.bakeout = path.join(device_dir, 'bakeout')

        self.heating_schedule_dir = path.join(setup_dir, 'heating_schedules')
        self.map_dir = map_dir = path.join(setup_dir, 'tray_maps')
        self.user_points_dir = path.join(map_dir, 'user_points')
        #==============================================================================
        # data
        #==============================================================================
        self.data_dir = data_dir = path.join(stable_root, 'data')
        self.modeling_data_dir = path.join(data_dir, 'modeling')
        self.argus_data_dir = path.join(data_dir, 'argusVI')
        self.positioning_error_dir = path.join(data_dir, 'positioning_error')
        self.snapshot_dir = path.join(data_dir, 'snapshots')
        self.video_dir = path.join(data_dir, 'videos')
        self.stage_visualizer_dir = path.join(data_dir, 'stage_visualizer')
        #initialization_dir = path.join(setup_dir, 'initializations')
        #device_creator_dir = path.join(device_dir, 'device_creator')

        #==============================================================================
        # lovera exectuables
        #==============================================================================
        self.clovera_root = path.join(pychron_src_root, 'src', 'modeling', 'lovera', 'bin')


paths = Paths()
paths.build('_beta')

def rec_make(pi):
    if pi and not path.exists(pi):
        try:
            mkdir(pi)
        except OSError:
            rec_make(path.split(pi)[0])
            mkdir(pi)

def build_directories():
    global paths
    #verify paths
#    import copy
    for l in dir(paths):
        if l.endswith('_dir'):
            rec_make(getattr(paths, l))


#def build_initialization_file(root):
#    p = path.join(root, 'initialization.xml')
#    if os.path.isfile(p):
#        from src.helpers.initialization_parser import InitializationParser
#        parser = InitializationParser()
#
#        DEFAULT_GENERAL_PLUGINS = ['Database', 'SVN']
#        DEFAULT_HARDWARE_PLUGINS = ['ExtractionLine',
#                                    'FusionsCO2', 'FusionsDiode',
#                                    'SynradCO2',
#                                    'Spectrometer',
#                                    ]
#        DEFAULT_DATA_PLUGINS = ['Graph', 'MDDModeler']
#        DEFAULT_SOCIAL_PLUGINS = ['Twitter', 'Email']
#
#        DEFAULT_PLUGINS = (DEFAULT_GENERAL_PLUGINS +
#                            DEFAULT_HARDWARE_PLUGINS +
#                            DEFAULT_DATA_PLUGINS +
#                            DEFAULT_SOCIAL_PLUGINS
#                            )
#
#        DEFAULT_PLUGINS.sort()
#        plugins = parser.get_plugins(all=True)
#        plugins.sort()
#
#        #add any default plugin not defined already
#        uptodate = DEFAULT_PLUGINS == plugins
#        if not uptodate:
#            diff = list(set(DEFAULT_PLUGINS) - set(plugins))
#            for grp, plist in [('general', DEFAULT_GENERAL_PLUGINS),
#                          ('hardware', DEFAULT_HARDWARE_PLUGINS),
#                          ('data', DEFAULT_DATA_PLUGINS),
#                          ('social', DEFAULT_SOCIAL_PLUGINS)
#                          ]:
#                for di in diff:
#                    if di in plist:
#                        parser.add_plugin(grp, di)
#                        #@todo add child elements such as managers and devices to this plugin
#    else:
#        with open(p, 'w') as f:
#            f.write('''
#<!--
#This is the initialization file. It defines the plugins and the associated managers and devices
#that should be bootstrapped (load, open, initialize) on startup.
#
#load means read configuration values
#open means create and error check communication handles
#initialize is a hook for object specific tasks directly after communications is established
#
#plugins
#general
#  database
#  svn @depecretated
#  script
#hardware
#  extractionline
#  bakeout
#  fusionsCO2
#  fusionsDiode
#  synradCO2
#  spectrometer
#data
#  graph
#social
#  email
#  twitter
#-->
#
#<root>
#  <general>
#    <plugin enabled="false">Database</plugin>
#    <plugin enabled="false">SVN</plugin>
#  </general>
#  <hardware>
#    <plugin enabled="false">ExtractionLine
#      <manager enabled="true">valve_manager
#        <device enabled="true">valve_controller</device>
#        <device enabled="true" klass="ValveController">argus_valve_controller</device>
#      </manager>
#      <manager enabled="false">gauge_manager</manager>
#      <manager enabled="false">bakeout_manager</manager>
#    </plugin>
#    <plugin enabled="false">FusionsCO2
#      <manager enabled="true">stage_manager
#       <device enabled="true">stage_controller</device>
#      </manager>
#      <device enabled="true">logic_board</device>
#    </plugin>
#    <plugin enabled="false">FusionsDiode
#      <manager enabled="true">stage_manager
#        <device enabled="true">stage_controller</device>
#      </manager>
#      <manager enabled="true">control_module
#        <device enabled="true">control</device>
#      </manager>
#      <device enabled="true">logic_board</device>
#      <device enabled="true">temperature_controller</device>
#      <device enabled="true">pyrometer</device>
#      <device enabled="true">subsystem</device>
#    </plugin>
#    <plugin enabled="false">SynradCO2</plugin>
#    <plugin enabled="false">Spectrometer
#      <device enabled="true" klass="ArgusController">spectrometer_microcontroller</device>
#    </plugin>
#  </hardware>
#  <data>
#    <plugin enabled="false">Graph</plugin>
#    <plugin enabled="false">MDDModeler</plugin>
#  </data>
#  <social>
#      <plugin enabled="false">Twitter</plugin>
#      <plugin enabled="false">Email</plugin>
#  </social>
#</root>
#''')



#            #ensure plugins dir is a valid python package
#            if l == 'plugins_dir':
#                p = path.join(pi, '__init__.py')
#                if not os.path.isfile(p):
#                    with open(p, 'w') as _f:
#                        pass
#            elif l == 'setup_dir':
#                #build initialization file
#                build_initialization_file(pi)

#============= EOF ==============================================

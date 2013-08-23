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
from os import path, mkdir, getcwd



# host_url = 'https://arlab.googlecode.com/svn'
# project_root = 'trunk'

# if beta:
#    home = '{}_beta{}'.format(home, version)
#    project_root = 'branches/pychron'
#
# project_home = join(host_url, project_root)

class Paths():
    version = None
    root = None
    bundle_root = None
    # pychron_src_root = None
    # doc_html_root = None
    icons = None
    splashes = None
    abouts = None
    sounds = None
    app_resources = None
    # _dir suffix ensures the path is checked for existence
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
    generic_experiment_dir = None
    plugins_dir = None
    hidden_dir = None
    preferences_dir = None
    plotter_options_dir = None
    test_dir = None
    custom_queries_dir = None
    #===========================================================================
    # scripts
    #===========================================================================
    procedures_dir = None
    measurement_dir = None
    post_measurement_dir = None
    extraction_dir = None
    post_equilibration_dir = None
    #==============================================================================
    # setup
    #==============================================================================
    setup_dir = setup_dir = None
    device_dir = None
    spectrometer_dir = None
    canvas2D_dir = None
    canvas3D_dir = None
    extraction_line_dir = None
    monitors_dir = None
    jog_dir = None
    pattern_dir = None
    incremental_heat_template_dir = None

    bakeout_config_dir = None
    bakeout = None

    block_dir = None
    heating_schedule_dir = None
    map_dir = map_dir = None
    user_points_dir = None
    #==============================================================================
    # data
    #==============================================================================
    data_dir = None
    modeling_data_dir = None
    argus_data_dir = None
    positioning_error_dir = None
    snapshot_dir = None
    video_dir = None
    stage_visualizer_dir = None
    default_workspace_dir = None
    workspace_root_dir = None
    spectrometer_scans_dir = None
    processed_dir = None
    image_cache_dir = None
    default_cache = None
    loading_dir = None
    power_map_dir = None
    # initialization_dir = None
    # device_creator_dir = None

    #==============================================================================
    # lovera exectuables
    #==============================================================================
    clovera_root = None

    #===========================================================================
    # files
    #===========================================================================
    backup_recovery_file = None

    def build(self, version):
        self.version = version

        HOME = path.expanduser('~')

        home = 'Pychrondata{}'.format(version)
        join = path.join

        self.root = root = join(HOME, home)
#        self.resources = join('..', '..', '..', 'resources',)

        self.resources = join(path.dirname(path.dirname(__file__)), 'resources')
        self.icons = join(self.resources, 'icons')
        self.splashes = join(self.resources, 'splashes')

        self.abouts = join(self.resources, 'abouts')
        self.sounds = join(self.resources, 'sounds')
        self.bullets = join(self.resources, 'bullets')
#        src_repo_name = 'pychron{}'.format(version)
#        self.pychron_src_root = pychron_src_root = join('.', 'pychron.app', 'Contents', 'Resources')
#        self.pychron_dev_src_root = join(HOME, 'Programming', 'mercurial',
#                                             'pychron{}'.format(version),
#                                             'resources'
#                                            )
        # _dir suffix ensures the path is checked for existence
        self.root_dir = root
        stable_root = join(HOME, 'Pychrondata')


        #==============================================================================
        # #database
        #==============================================================================
#        db_path = '/usr/local/pychron
        db_path = stable_root
        self.device_scan_root = device_scan_root = join(db_path, 'device_scans')
        self.device_scan_db = join(device_scan_root, 'device_scans.sqlite')
        self.bakeout_db_root = join(db_path, 'bakeoutdb')
        self.bakeout_db = join(db_path, 'bakeouts.db')
        self.co2laser_db_root = join(db_path, 'co2laserdb')
        self.co2laser_db = join(db_path, 'co2.sqlite')
        self.uvlaser_db_root = join(db_path, 'uvlaserdb')
        self.uvlaser_db = join(db_path, 'uv.sqlite')

        self.powermap_db_root = join(db_path, 'powermap')
        self.powermap_db = join(db_path, 'powermap.sqlite')

        self.diodelaser_db_root = join(db_path, 'diodelaserdb')
        self.diodelaser_db = join(db_path, 'diode.sqlite')
        self.isotope_db_root = join(db_path, 'isotopedb')

        ROOT = '/Users/ross/Sandbox/pychron_test_data/data'
        self.isotope_db = join(ROOT, 'isotopedb.sqlite')
        #==============================================================================
        # root
        #==============================================================================
        self.scripts_dir = scripts_dir = join(root, 'scripts')
#        self.procedures_dir = join(scripts_dir, 'procedures')
        self.measurement_dir = join(scripts_dir, 'measurement')
        self.post_measurement_dir = join(scripts_dir, 'post_measurement')
        self.extraction_dir = join(scripts_dir, 'extraction')
        self.post_equilibration_dir = join(scripts_dir, 'post_equilibration')


        self.experiment_dir = join(root, 'experiments')
        self.generic_experiment_dir = join(self.experiment_dir, 'generic')
        self.hidden_dir = join(root, '.hidden')
        self.preferences_dir = join(root, 'preferences')
        self.plotter_options_dir = join(self.hidden_dir, 'plotter_options')
        self.test_dir = join(root, 'testing')
        self.custom_queries_dir = join(root, 'custom_queries')
        #==============================================================================
        # setup
        #==============================================================================
        self.setup_dir = setup_dir = join(root, 'setupfiles')
        self.spectrometer_dir = join(setup_dir, 'spectrometer')
        self.device_dir = device_dir = join(setup_dir, 'devices')
        self.canvas2D_dir = join(setup_dir, 'canvas2D')
        self.canvas3D_dir = join(setup_dir, 'canvas3D')
        self.extraction_line_dir = join(setup_dir, 'extractionline')
        self.monitors_dir = join(setup_dir, 'monitors')
        self.pattern_dir = join(setup_dir, 'patterns')
        self.incremental_heat_template_dir = join(setup_dir, 'incremental_heat_templates')

        self.bakeout_config_dir = join(setup_dir, 'bakeout_configurations')
        self.bakeout = join(device_dir, 'bakeout')

        self.block_dir = join(setup_dir, 'blocks')
        self.map_dir = map_dir = join(setup_dir, 'tray_maps')
        self.user_points_dir = join(map_dir, 'user_points')
        #==============================================================================
        # data
        #==============================================================================
        self.data_dir = data_dir = join(root, 'data')
        self.spectrometer_scans_dir = join(data_dir, 'spectrometer_scans')
        self.modeling_data_dir = join(data_dir, 'modeling')
        self.argus_data_dir = join(data_dir, 'argusVI')
        self.positioning_error_dir = join(data_dir, 'positioning_error')
        self.snapshot_dir = join(data_dir, 'snapshots')
        self.video_dir = join(data_dir, 'videos')
        self.stage_visualizer_dir = join(data_dir, 'stage_visualizer')

        self.arar_dir = join(data_dir, 'arar')

        self.isotope_dir = join(self.data_dir, 'isotopes')
        self.workspace_root_dir = join(self.data_dir, 'workspaces')
        self.default_workspace_dir = join(self.workspace_root_dir, 'collection')
        self.processed_dir = join(self.data_dir, 'processed')
        # initialization_dir = join(setup_dir, 'initializations')
        # device_creator_dir = join(device_dir, 'device_creator')
        self.image_cache_dir = join(self.data_dir, 'image_cache')
        self.default_cache = join(self.data_dir, 'cache')
        self.loading_dir = join(self.data_dir, 'loads')
        self.power_map_dir = join(self.data_dir, 'power_maps')
        #==============================================================================
        # lovera exectuables
        #==============================================================================
#        self.clovera_root = join(pychron_src_root, 'src', 'modeling', 'lovera', 'bin')


        #=======================================================================
        # files
        #=======================================================================
        self.backup_recovery_file = join(self.hidden_dir, 'backup_recovery')


paths = Paths()
paths.build('_beta')

def rec_make(pi):
    if pi and not path.exists(pi):
        try:
            mkdir(pi)
        except OSError:
            rec_make(path.split(pi)[0])
            mkdir(pi)

def build_directories(paths):
#    global paths
    # verify paths
#    import copy
    for l in dir(paths):
        if l.endswith('_dir'):
            rec_make(getattr(paths, l))


# def build_initialization_file(root):
#    p = join(root, 'initialization.xml')
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
# <!--
# This is the initialization file. It defines the plugins and the associated managers and devices
# that should be bootstrapped (load, open, initialize) on startup.
#
# load means read configuration values
# open means create and error check communication handles
# initialize is a hook for object specific tasks directly after communications is established
#
# plugins
# general
#  database
#  svn @depecretated
#  script
# hardware
#  extractionline
#  bakeout
#  fusionsCO2
#  fusionsDiode
#  synradCO2
#  spectrometer
# data
#  graph
# social
#  email
#  twitter
# -->
#
# <root>
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
# </root>
# ''')



#            #ensure plugins dir is a valid python package
#            if l == 'plugins_dir':
#                p = join(pi, '__init__.py')
#                if not os.path.isfile(p):
#                    with open(p, 'w') as _f:
#                        pass
#            elif l == 'setup_dir':
#                #build initialization file
#                build_initialization_file(pi)

#============= EOF ==============================================

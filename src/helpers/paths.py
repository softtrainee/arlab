'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
'''
Global path structure

add a path verification function
make sure directory exists and build if not
'''
import os
from src.helpers.initialization_parser import InitializationParser

HOME = os.path.expanduser('~')
home = 'Pychrondata'

version = '1.4'

from globals import beta

host_url = 'https://arlab.googlecode.com/svn'
project_root = 'trunk'

if beta:
    home = '{}_beta{}'.format(home, version)
    project_root = 'branches/pychron'

project_home = os.path.join(host_url, project_root)
root = os.path.join(HOME, home)
src_repo_name = 'pychron_beta'
pychron_src_dir = os.path.join(HOME, 'Programming', 'mercurial', src_repo_name)

#_dir suffix ensures the path is checked for existence
root_dir = root

src_root = os.getcwd()

#directories directly under root
setup_dir = os.path.join(root, 'setupfiles')
device_dir = os.path.join(setup_dir, 'devices')
canvas2D_dir = os.path.join(setup_dir, 'canvas2D')
canvas3D_dir = os.path.join(setup_dir, 'canvas3D')
data_dir = os.path.join(root, 'data')
extraction_line_dir = os.path.join(setup_dir, 'extractionline')
#initialization_dir = os.path.join(setup_dir, 'initializations')
scripts_dir = os.path.join(root, 'scripts')

#device_creator_dir = os.path.join(device_dir, 'device_creator')
modeling_data_dir = os.path.join(data_dir, 'modeling')
monitors_dir = os.path.join(setup_dir, 'monitors')
jog_dir = os.path.join(setup_dir, 'jogs')
pattern_dir = os.path.join(setup_dir, 'patterns')

bakeout = os.path.join(device_dir, 'bakeout')
bakeout_config_dir = os.path.join(setup_dir, 'bakeout_configurations')

clovera_root = os.path.join(src_root, 'src', 'data_processing', 'modeling', 'lovera')
#clovera_root = '/usr/local/clovera'

argus_data_dir = os.path.join(data_dir, 'argusVI')
heating_schedule_dir = os.path.join(setup_dir, 'heating_schedules')
experiment_dir = os.path.join(root, 'experiments')
plugins_dir = os.path.join(root, 'plugins')
map_dir = os.path.join(setup_dir, 'tray_maps')
user_points_dir = os.path.join(map_dir, 'user_points')

positioning_error_dir = os.path.join(data_dir, 'positioning_error')
snapshot_dir = os.path.join(data_dir, 'snapshots')
video_dir = os.path.join(data_dir, 'videos')

hidden_dir = os.path.join(root, '.hidden')



def rec_make(pi):
    if not os.path.exists(pi):
        try:
            os.mkdir(pi)
        except OSError:
            rec_make(os.path.split(pi)[0])
            os.mkdir(pi)

def build_initialization_file(root):
    p = os.path.join(root, 'initialization.xml')
    if os.path.isfile(p):
        parser = InitializationParser(p)

        DEFAULT_GENERAL_PLUGINS = ['Database', 'SVN']
        DEFAULT_HARDWARE_PLUGINS = ['ExtractionLine',
                                    'FusionsCO2', 'FusionsDiode',
                                    'SynradCO2',
                                    'Spectrometer',
                                    ]
        DEFAULT_DATA_PLUGINS = ['Graph', 'MDDModeler']
        DEFAULT_SOCIAL_PLUGINS = ['Twitter', 'Email']

        DEFAULT_PLUGINS = (DEFAULT_GENERAL_PLUGINS +
                            DEFAULT_HARDWARE_PLUGINS +
                            DEFAULT_DATA_PLUGINS +
                            DEFAULT_SOCIAL_PLUGINS
                            )

        DEFAULT_PLUGINS.sort()
        plugins = parser.get_plugins(all=True)
        plugins.sort()

        #add any default plugin not defined already
        uptodate = DEFAULT_PLUGINS == plugins
        if not uptodate:
            diff = list(set(DEFAULT_PLUGINS) - set(plugins))
            for grp, plist in [('general', DEFAULT_GENERAL_PLUGINS),
                          ('hardware', DEFAULT_HARDWARE_PLUGINS),
                          ('data', DEFAULT_DATA_PLUGINS),
                          ('social', DEFAULT_SOCIAL_PLUGINS)
                          ]:
                for di in diff:
                    if di in plist:
                        parser.add_plugin(grp, di)
                        #@todo add child elements such as managers and devices to this plugin
    else:
        with open(p, 'w') as f:
            f.write('''
<!--
This is the initialization file. It defines the plugins and the associated managers and devices
that should be bootstrapped (load, open, initialize) on startup.

load means read configuration values
open means create and error check communication handles
initialize is a hook for object specific tasks directly after communications is established

plugins
general
  database
  svn @depecretated
  script
hardware
  extractionline
  bakeout
  fusionsCO2
  fusionsDiode
  synradCO2
  spectrometer
data
  graph
social
  email
  twitter
-->

<root>
  <general>
    <plugin enabled="false">Database</plugin>
    <plugin enabled="false">SVN</plugin>
  </general>
  <hardware>
    <plugin enabled="false">ExtractionLine
      <manager enabled="true">valve_manager
        <device enabled="true">valve_controller</device>
        <device enabled="true" klass="ValveController">argus_valve_controller</device>
      </manager>
      <manager enabled="false">gauge_manager</manager>
      <manager enabled="false">bakeout_manager</manager>
    </plugin>
    <plugin enabled="false">FusionsCO2
      <manager enabled="true">stage_manager
       <device enabled="true">stage_controller</device>
      </manager>
      <device enabled="true">logic_board</device>
    </plugin>
    <plugin enabled="false">FusionsDiode
      <manager enabled="true">stage_manager
        <device enabled="true">stage_controller</device>
      </manager>
      <manager enabled="true">control_module
        <device enabled="true">control</device>
      </manager>
      <device enabled="true">logic_board</device>
      <device enabled="true">temperature_controller</device>
      <device enabled="true">pyrometer</device>
      <device enabled="true">subsystem</device>
    </plugin>
    <plugin enabled="false">SynradCO2</plugin>
    <plugin enabled="false">Spectrometer
      <device enabled="true" klass="ArgusController">spectrometer_microcontroller</device>
    </plugin>
  </hardware>
  <data>
    <plugin enabled="false">Graph</plugin>
    <plugin enabled="false">MDDModeler</plugin>
  </data>
  <social>
      <plugin enabled="false">Twitter</plugin>
      <plugin enabled="false">Email</plugin>
  </social>
</root>
''')

def build_directories():
    #verify paths
    import copy
    local = copy.copy(globals())
    for l in local:

        if l[-4:] == '_dir':
            pi = local[l]

            rec_make(pi)

            #ensure plugins dir is a valid python package
            if l == 'plugins_dir':
                p = os.path.join(pi, '__init__.py')
                if not os.path.isfile(p):
                    with open(p, 'w') as _f:
                        pass
            elif l == 'setup_dir':
                #build initialization file
                build_initialization_file(pi)

#============= EOF ==============================================

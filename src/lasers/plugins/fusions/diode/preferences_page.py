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



#============= enthought library imports =======================
#from traits.api import HasTraits, Str, Password, Bool, Button, Enum, Float, List, on_trait_change
#
#from traitsui.table_column import ObjectColumn
#from traitsui.extras.checkbox_column import CheckboxColumn
#from src.helpers.paths import initialization_dir
#import os
#from ConfigParser import ConfigParser
#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.fusions.fusions_laser_preferences_page import FusionsLaserPreferencesPage

class FusionsDiodePreferencesPage(FusionsLaserPreferencesPage):
    id = 'pychron.fusions.diode.preferences_page'
    preferences_path = 'pychron.fusions.diode'
    name = 'Fusions Diode'
    plugin_name = 'FusionsDiode'
#    def traits_view(self):
#        v = View('width',
#               'height')
#        return v
#    width = Float
#    height = Float

#class CItem(HasTraits):
#    enabled = Bool
#    name = Str
#
#class ExtractionLinePreferencesPage(PreferencesPage):
#    '''
#        G{classtree}
#    '''
#    id = 'pychron.extraction_line.preferences_page'
#    name = 'Extraction Line'
#    preferences_path = 'pychron.extraction_line'
#    style = Enum('2D', '3D')
#    width = Float
#    height = Float
#    devices = List(transient = True)
#    managers = List(transient = True)
#
#    @on_trait_change('managers.enabled, devices.enabled')
#    def _managers_changed(self, obj, name, old, new):
#        p = os.path.join(initialization_dir, 'extraction_line_initialization.cfg')
#        #overwrite the extracton_line_initialization file
#        with open(p, 'r') as f:
#
#            config = ConfigParser()
#            config.readfp(f)
#
#            #write the managers
#            ms = []
#            for m in self.managers:
#                t = m.name
#                if not m.enabled:
#                    t = '_%s' % m.name
#                ms.append(t)
#
#            config.set('General', 'managers', ','.join(ms))
#
#            #write the devices
#            ds = []
#            for d in self.devices:
#                t = d.name
#                if not d.enabled:
#                    t = '_%s' % d.name
#                ds.append(t)
#            config.set('General', 'devices', ','.join(ds))
#
#
#        with open(p, 'w') as f:
#            config.write(f)
#
#    def _managers_default(self):
#        # read the config file
#        p = os.path.join(initialization_dir, 'extraction_line_initialization.cfg')
#
#        r = []
#        with open(p, 'r') as f:
#
#            config = ConfigParser()
#            config.readfp(f)
#            managers = config.get('General', 'managers')
#            for m in managers.split(','):
#                m = m.strip()
#                enabled = not m.startswith('_')
#                if not enabled:
#                    #strip off enabled flag char
#                    m = m[1:]
#                r.append(CItem(enabled = enabled,
#
#                                name = m))
#
#        return r
#
#    def _devices_default(self):
#        # read the config file
#        p = os.path.join(initialization_dir, 'extraction_line_initialization.cfg')
#
#        r = []
#        with open(p, 'r') as f:
#
#            config = ConfigParser()
#            config.readfp(f)
#            devices = config.get('General', 'devices')
#            for d in devices.split(','):
#                d = d.strip()
#                enabled = not d.startswith('_')
#                if not enabled:
#                    #strip off enabled flag char
#                    d = d[1:]
#                r.append(CItem(enabled = enabled,
#
#                                name = d))
#
#        return r
#
#    def traits_view(self):
#        '''
#        '''
#        canvas_group = VGroup(Item('style', show_label = False),
#                              'width',
#                              'height',
#                              label = 'Canvas', show_border = True)
#
#        cols = [CheckboxColumn(name = 'enabled',
#                             ),
#                ObjectColumn(name = 'name')
#                             ]
#        table_editor = TableEditor(columns = cols)
#
#        devices_group = VGroup(Item('devices', show_label = False,
#                                    editor = table_editor
#                                    ),
#                                label = 'Devices'
#                              )
#        manager_group = VGroup(Item('managers', show_label = False,
#                                    editor = table_editor
#                                    ),
#                                label = 'Managers'
#                              )
#        v = View(
#                 manager_group,
#                 devices_group,
#                 canvas_group,
#                 )
#        return v
#============= views ===================================
#============= EOF ====================================

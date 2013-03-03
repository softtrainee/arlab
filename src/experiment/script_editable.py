#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, Str, Property
from traitsui.api import View, Item, VGroup, EnumEditor
from src.saveable import Saveable
import os
from src.paths import paths
from src.constants import NULL_STR
#============= standard library imports ========================
#============= local library imports  ==========================

class ScriptEditable(Saveable):
    mass_spectrometer = Str(NULL_STR)
    extract_device = Str(NULL_STR)

    measurement_script = Str
    measurement_scripts = Property(depends_on='mass_spectrometer')
    post_measurement_script = Str
    post_measurement_scripts = Property(depends_on='mass_spectrometer')
    post_equilibration_script = Str
    post_equilibration_scripts = Property(depends_on='mass_spectrometer,extract_device')
    extraction_script = Str
    extraction_scripts = Property(depends_on='mass_spectrometer')

    def _load_script_names(self, name):
        p = os.path.join(paths.scripts_dir, name)
#        print 'fff', name, p
        if os.path.isdir(p):
            prep = lambda x:x
    #        prep = lambda x: os.path.split(x)[0]

            return [prep(s)
                    for s in os.listdir(p)
                        if not s.startswith('.') and s.endswith('.py')
                        ]
        else:
            self.warning_dialog('{} script directory does not exist!'.format(p))

    def _get_scripts(self, es):
        if self.mass_spectrometer != '---':
            k = '{}_'.format(self.mass_spectrometer)
            es = [self._clean_script_name(ei) for ei in es if ei.startswith(k)]

        es = [NULL_STR] + es
        return es

    def _clean_script_name(self, name):
        name = self._remove_mass_spectrometer_name(name)
        return self._remove_file_extension(name)

    def _remove_file_extension(self, name, ext='.py'):
        if name is NULL_STR:
            return NULL_STR

        if name.endswith('.py'):
            name = name[:-3]

        return name

    def _remove_mass_spectrometer_name(self, name):
        if self.mass_spectrometer:
            name = name.replace('{}_'.format(self.mass_spectrometer), '')
        return name

    def _add_mass_spectromter_name(self, name):
        if self.mass_spectrometer:
            name = '{}_{}'.format(self.mass_spectrometer, name)
        return name

    def _update_run_script(self, run, sname):
        if run.state == 'not run':
            ssname = '{}_script'.format(sname)
            name = getattr(self, ssname)
            if name:
                setattr(run.script_info, '{}_script_name'.format(sname), name)
                setattr(run, '{}_dirty'.format(ssname), True)
#===============================================================================
# property get/set
#===============================================================================
    def _get_extraction_scripts(self):
        ms = self._load_script_names('extraction')
        ms = self._get_scripts(ms)
        return ms

    def _get_measurement_scripts(self):
        ms = self._load_script_names('measurement')
        ms = self._get_scripts(ms)
        return ms

    def _get_post_measurement_scripts(self):
        ms = self._load_script_names('post_measurement')
        ms = self._get_scripts(ms)
        return ms

    def _get_post_equilibration_scripts(self):
        ms = self._load_script_names('post_equilibration')
        ms = self._get_scripts(ms)
        return ms

    def _get_script_group(self):
        script_grp = VGroup(
                        Item('extraction_script',
                             label='Extraction',
                             editor=EnumEditor(name='extraction_scripts')),
                        Item('measurement_script',
                             label='Measurement',
                             editor=EnumEditor(name='measurement_scripts')),
                        Item('post_equilibration_script',
                             label='Post Equilibration',
                             editor=EnumEditor(name='post_equilibration_scripts')),
                        Item('post_measurement_script',
                             label='Post Measurement',
                             editor=EnumEditor(name='post_measurement_scripts')),
                        show_border=True,
                        label='Scripts'
                        )
        return script_grp
#============= EOF =============================================

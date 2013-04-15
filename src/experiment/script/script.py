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
from traits.api import HasTraits, Str, Any, Property, Button, cached_property, \
    String, Bool
from traitsui.api import View, Item, HGroup, Label, spring, EnumEditor
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.paths import paths
from src.pyscripts.editor import PyScriptEditor
from src.pyscripts.measurement_editor import MeasurementPyScriptEditor
from src.constants import NULL_STR
from src.loggable import Loggable

class Script(Loggable):
    application = Any
    label = Str
    mass_spectrometer = String

    name = Str(NULL_STR)
    names = Property(depends_on='mass_spectrometer')
    edit = Button
    kind = 'ExtractionLine'
    can_edit = Bool(False)

    def _edit_fired(self):
        p = os.path.join(paths.scripts_dir, self.label.lower(), '{}_{}.py'.format(self.mass_spectrometer,
                                                                                  self.name))
        if self.kind == 'ExtractionLine':
            editor = PyScriptEditor(application=self.application)
        else:
            editor = MeasurementPyScriptEditor(application=self.application)

        editor.open_script(p)
        editor.open_view(editor)

    def traits_view(self):
        return View(HGroup(
                           Label(self.label),
                           spring,
                           Item('name',
                                show_label=False,
                                width= -150,
                                editor=EnumEditor(name='names')),
                           Item('edit',
                                enabled_when='name and name!="---" and can_edit',
                                show_label=False)
                           )
                    )

#    def _get_scripts(self, es):
# #        if self.mass_spectrometer != '---':
#        es = [self._clean_script_name(ei) for ei in es]
# #            k = '{}_'.format(self.mass_spectrometer)
# #            es = [self._clean_script_name(ei) for ei in es if ei.startswith(k)]
#
#        es = [NULL_STR] + es
#        return es

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
            name = name.replace('{}_'.format(self.mass_spectrometer.lower()), '')
        return name

    def _load_script_names(self):
        d = self.label.lower().replace(' ', '_')
        p = os.path.join(paths.scripts_dir, d)
        if os.path.isdir(p):
            return [s for s in os.listdir(p)
                        if not s.startswith('.') and s.endswith('.py')]
        else:
            self.warning_dialog('{} script directory does not exist!'.format(p))

    @cached_property
    def _get_names(self):
        names = [NULL_STR]
        ms = self._load_script_names()
        if ms:
            msn = '{}_'.format(self.mass_spectrometer.lower())
            names.extend([self._clean_script_name(ei) for ei in ms if ei.startswith(msn)])

        return names

#============= EOF =============================================

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
from traits.api import HasTraits, Str, Property, List, Button, Instance, Any, cached_property
from traitsui.api import View, Item, VGroup, EnumEditor, HGroup, spring, Label
from src.saveable import Saveable
import os
from src.paths import paths
from src.constants import NULL_STR, SCRIPT_KEYS
from src.pyscripts.pyscript_editor import PyScriptManager
from src.loggable import Loggable
import yaml
#============= standard library imports ========================
#============= local library imports  ==========================
# class ScriptMixin(object):
#    def _clean_script_name(self, name):
#        name = self._remove_mass_spectrometer_name(name)
#        return self._remove_file_extension(name)
#
#    def _remove_file_extension(self, name, ext='.py'):
#        if name is NULL_STR:
#            return NULL_STR
#
#        if name.endswith('.py'):
#            name = name[:-3]
#
#        return name
#
#    def _remove_mass_spectrometer_name(self, name):
#        if self.mass_spectrometer:
#            name = name.replace('{}_'.format(self.mass_spectrometer), '')
#        return name

# class Script(Loggable, ScriptMixin):
#    application = Any
#    label = Str
#    name = Str
#    mass_spectrometer = Str
#    names = Property(depends_on='mass_spectrometer')
#    edit = Button
#    kind = 'ExtractionLine'
#
#    def _edit_fired(self):
#        p = os.path.join(paths.scripts_dir, self.label.lower(), '{}_{}.py'.format(self.mass_spectrometer,
#                                                                                  self.name))
#        editor = PyScriptManager(kind=self.kind, application=self.application)
#        editor.open_script(p)
#        editor.open_view(editor)
#
#    def traits_view(self):
#        return View(HGroup(
#                           Label(self.label),
#                           spring,
#                           Item('name',
#                                show_label=False,
#                                width= -150,
#                                editor=EnumEditor(name='names')),
#                           Item('edit',
#                                enabled_when='name and name!="---"',
#                                show_label=False)
#                           )
#                    )
#
# #    def _get_scripts(self, es):
# # #        if self.mass_spectrometer != '---':
# #        es = [self._clean_script_name(ei) for ei in es]
# # #            k = '{}_'.format(self.mass_spectrometer)
# # #            es = [self._clean_script_name(ei) for ei in es if ei.startswith(k)]
# #
# #        es = [NULL_STR] + es
# #        return es
#
#
#
#    def _load_script_names(self):
#        d = self.label.lower().replace(' ', '_')
#        p = os.path.join(paths.scripts_dir, d)
# #        print 'fff', name, p
#        if os.path.isdir(p):
#            return [s for s in os.listdir(p)
#                        if not s.startswith('.') and s.endswith('.py')]
#        else:
#            self.warning_dialog('{} script directory does not exist!'.format(p))
#
#    @cached_property
#    def _get_names(self):
#        names = [NULL_STR]
#        ms = self._load_script_names()
#
#        if ms:
#            msn = '{}_'.format(self.mass_spectrometer)
#            names.extend([self._clean_script_name(ei) for ei in ms if ei.startswith(msn)])
#
#        return names

class ScriptEditable(Saveable, ScriptMixin):
    application = Any
    mass_spectrometer = Str(NULL_STR)
    extract_device = Str(NULL_STR)

    extraction_script = Instance(Script)
    measurement_script = Instance(Script)
    post_measurement_script = Instance(Script)
    post_equilibration_script = Instance(Script)

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

    def _script_factory(self, label, name, kind='ExtractionLine'):
        return Script(label=label,
#                      names=getattr(self, '{}_scripts'.format(name)),
                      application=self.application,
                      mass_spectrometer=self.mass_spectrometer,
                      kind=kind
                      )

    def _extraction_script_default(self):
        return self._script_factory('Extraction', 'extraction')

    def _measurement_script_default(self):
        return self._script_factory('Measurement', 'measurement', kind='Measurement')

    def _post_measurement_script_default(self):
        return self._script_factory('Post Measurement', 'post_measurement')

    def _post_equilibration_script_default(self):
        return self._script_factory('Post Equilibration', 'post_equilibration')

    def clear_script_names(self):
        self.measurement_script.name = NULL_STR
        self.extraction_script.name = NULL_STR
        self.post_measurement_script.name = NULL_STR
        self.post_equilibration_script.name = NULL_STR

    def set_scripts_mass_spectrometer(self):
        self.extraction_script.mass_spectrometer = self.mass_spectrometer
        self.measurement_script.mass_spectrometer = self.mass_spectrometer
        self.post_measurement_script.mass_spectrometer = self.mass_spectrometer
        self.post_equilibration_script.mass_spectrometer = self.mass_spectrometer

    def _add_mass_spectromter_name(self, name):
        if self.mass_spectrometer:
            name = '{}_{}'.format(self.mass_spectrometer, name)
        return name

    def _update_run_script(self, run, sname, name):
        if run.state == 'not run':
#            ssname = '{}_script'.format(sname)
#            script = getattr(self, ssname)
#            print script, script.name
#            if script:
            setattr(run.script_info, '{}_script_name'.format(sname), name)

#                setattr(run, '{}_dirty'.format(ssname), True)

    def _load_default_scripts(self, setter=None, key=None):
        if key is None:
            if self.automated_run is None:
                return
            key = self.automated_run.labnumber

        if setter is None:
#            def setter(ski, sci):
#                v = getattr(self, '{}_script'.format(ski))

            setter = lambda ski, sci:setattr(getattr(self, '{}_script'.format(ski)), 'name', sci)

        # open the yaml config file
#        import yaml
        p = os.path.join(paths.scripts_dir, 'defaults.yaml')
        if not os.path.isfile(p):
            self.warning('Script defaults file does not exist {}'.format(p))
            return

        with open(p, 'r') as fp:
            defaults = yaml.load(fp)

        # convert keys to lowercase
        defaults = dict([(k.lower(), v) for k, v in defaults.iteritems()])

        # if labnumber is int use key='U'
        try:
            _ = int(key)
            key = 'u'
        except ValueError:
            pass

        key = key.lower()

        if not key in defaults:
            return

        scripts = defaults[key]
        for sk in SCRIPT_KEYS:
            sc = NULL_STR
            try:
                sc = scripts[sk]
                sc = sc if sc else NULL_STR
            except KeyError:
                pass

            sc = self._remove_file_extension(sc)
            if key.lower() in ('u', 'bu') and self.extract_device != NULL_STR:
                e = self.extract_device.split(' ')[1].lower()
                if sk == 'extraction':
                    sc = e
                elif sk == 'post_equilibration':
                    sc = 'pump_{}'.format(e)

            script = getattr(self, '{}_script'.format(sk))
            if not sc in script.names:
#            if not sc in getattr(self, '{}_scripts'.format(sk)):
                sc = NULL_STR
#            print setter, sk, sc
            setter(sk, sc)
#===============================================================================
# property get/set
#===============================================================================
    def _get_script_group(self):
        script_grp = VGroup(
                        Item('extraction_script', style='custom', show_label=False),
                        Item('measurement_script', style='custom', show_label=False),
                        Item('post_equilibration_script', style='custom', show_label=False),
                        Item('post_measurement_script', style='custom', show_label=False),
                        show_border=True,
                        label='Scripts'
                        )
        return script_grp
#============= EOF =============================================

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
from traits.api import Any, Instance, List, Str, Property, Button, Dict
from traitsui.api import Item, EnumEditor, VGroup, HGroup
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.automated_run import AutomatedRun
from src.experiment.automated_run_tabular_adapter import AutomatedRunAdapter
from src.constants import NULL_STR, SCRIPT_KEYS
import os
from src.paths import paths
import yaml
from src.helpers.filetools import str_to_bool
from src.experiment.script_editable import ScriptEditable


class RunAdapter(AutomatedRunAdapter):
    can_edit = True
    def _columns_default(self):
        cf = self._columns_factory()
        #remove state
        cf.pop(0)

        cf.remove(('Aliquot', 'aliquot'))
        cf.remove(('Sample', 'sample'))
        return cf

    def _set_float(self, attr, v):
        try:
            setattr(self.item, attr, float(v))
        except ValueError:
            pass

    def _set_position_text(self, v):
        self._set_float('position', v)

    def _set_duration_text(self, v):
        self._set_float('position', v)

    def _set_cleanup_text(self, v):
        self._set_float('position', v)

#class BaseSchedule(Saveable):
class BaseSchedule(ScriptEditable):
    automated_runs = List(AutomatedRun)
    automated_run = Instance(AutomatedRun, ())

    tray = Str(NULL_STR)

#    measurement_script = Str
#    measurement_scripts = Property(depends_on='mass_spectrometer')
#    post_measurement_script = Str
#    post_measurement_scripts = Property(depends_on='mass_spectrometer')
#    post_equilibration_script = Str
#    post_equilibration_scripts = Property(depends_on='mass_spectrometer,extract_device')
#    extraction_script = Str
#    extraction_scripts = Property(depends_on='mass_spectrometer')

    loaded_scripts = Dict

    add = Button
    copy_button = Button('copy')
    paste_button = Button('paste')

    selected = Any
    _copy_cache = Any

    def update_loaded_scripts(self, new):
        if new:
            self.loaded_scripts[new.name] = new
            for ai in self.automated_runs:
                ai.scripts = self.loaded_scripts
            if self.automated_run:
                self.automated_run.scripts = self.loaded_scripts

    def _load_default_scripts(self, setter=None, key=None):
        if key is None:
            if self.automated_run is None:
                return
            key = self.automated_run.labnumber

        if setter is None:
            setter = lambda ski, sci:setattr(self, '{}_script'.format(ski), sci)

        # open the yaml config file
#        import yaml
        p = os.path.join(paths.scripts_dir, 'defaults.yaml')
        if not os.path.isfile(p):
            return

        with open(p, 'r') as fp:
            defaults = yaml.load(fp)

        #convert keys to lowercase
        defaults = dict([(k.lower(), v) for k, v in defaults.iteritems()])

        #if labnumber is int use key='U'
        try:
            _ = int(key)
            key = 'u'
        except ValueError:
            pass

        key = key.lower()

#        print key, defaults
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
            if sk == 'extraction' and key.lower() in ['u', 'bu']:
                if self.extract_device != NULL_STR:
                    sc = self.extract_device.split(' ')[1].lower()
            if not sc in getattr(self, '{}_scripts'.format(sk)):
                sc = NULL_STR
#            print setter, sk, sc
            setter(sk, sc)

#===============================================================================
# persistence
#===============================================================================
    def dump(self, stream):
        header, attrs = self._get_dump_attrs()

        writeline = lambda m: stream.write(m + '\n')

        tab = lambda l: writeline('\t'.join(map(str, l)))

        #write metadata
        self._meta_dumper(stream)
        writeline('#' + '=' * 80)

        tab(header)

        def isNotNull(vi):
            if vi and vi != NULL_STR:
                try:
                    vi = int(vi)
                    return vi != 0
                except ValueError:
                    return True
            else:
                return False

        for arun in self.automated_runs:
            vs = arun.to_string_attrs(attrs)
            vals = [v if isNotNull(v) else '' for v in vs]
            tab(vals)

        return stream
#               
    def _get_dump_attrs(self):
        header = ['labnumber',
                  'pattern',
                  'position',
                  'overlap',
                  'extract_group',
                  'extract_value',
                  'extract_units',
                  'duration',
                  'cleanup',
                  'autocenter',
                  'extraction', 'measurement', 'post_equilibration', 'post_measurement',
                  'disable_between_positions'
                  ]
        attrs = ['labnumber',
                  'pattern',
                  'position',
                  'overlap',
                  'extract_group',
                  'extract_value',
                  'extract_units',
                  'duration',
                  'cleanup',
                  'autocenter',
                  'extraction_script', 'measurement_script',
                  'post_equilibration_script', 'post_measurement_script',
                  'disable_between_positions']

        return header, attrs

    def _meta_dumper(self, fp=None):
        pass

    @classmethod
    def _run_parser(cls, header, line, meta, delim='\t'):
        params = dict()
        if not isinstance(line, list):
            line = line.split(delim)

        args = map(str.strip, line)

        #load strings
        for attr in ['labnumber',
                     'measurement', 'extraction', 'post_measurement',
                     'post_equilibration',
                     'pattern',
                     'position'
                     ]:
            params[attr] = args[header.index(attr)]

        #load booleans
        for attr in ['autocenter', 'disable_between_positions']:
            try:
                param = args[header.index(attr)]
                if param.strip():
                    bo = str_to_bool(param)
                    if bo is not None:
                        params[attr] = bo
                    else:
                        params[attr] = False
            except (IndexError, ValueError):
                params[attr] = False

        #load numbers
        for attr in ['duration', 'overlap', 'cleanup',
                     'extract_group'
                     ]:
            try:
                param = args[header.index(attr)].strip()
                if param:
                    params[attr] = float(param)
            except IndexError:
                pass

        #default extract_units to watts
        extract_value = args[header.index('extract_value')]
        extract_units = args[header.index('extract_units')]
        if not extract_units:
            extract_units = '---'

        params['extract_value'] = extract_value
        params['extract_units'] = extract_units

        def make_script_name(n):
            na = args[header.index(n)]
            if na.startswith('_'):
                if meta:
                    na = meta['mass_spectrometer'] + na

            if na and not na.endswith('.py'):
                na = na + '.py'
            return na

        params['configuration'] = cls._build_configuration(make_script_name)
        return params
#===============================================================================
# handlers
#===============================================================================
    def _copy_button_fired(self):
        self._copy_cache = [a.clone_traits() for a in self.selected]

    def _paste_button_fired(self):
        ind = None
        if self.selected:
            ind = self.automated_runs.index(self.selected[-1])

        if ind is None:
            self.automated_runs.extend(self._copy_cache[:])
        else:
            _rcopy_cache = reversed(self._copy_cache)
            for ri in _rcopy_cache:
                self.automated_runs.insert(ind + 1, ri)
        self.selected = []

#===============================================================================
# views
#===============================================================================


#===============================================================================
# scripts
#===============================================================================
    @classmethod
    def _build_configuration(cls, make_script_name):
        def make_path(dname, name):
            return os.path.join(getattr(paths, '{}_dir'.format(dname)), name)
        args = [('{}_script'.format(ni), make_path(ni, make_script_name(ni)))
                for ni in SCRIPT_KEYS]
        return dict(args)

    def _bind_automated_run(self, a):
        a.on_trait_change(self.update_loaded_scripts, '_measurement_script')
        a.on_trait_change(self.update_loaded_scripts, '_extraction_script')
        a.on_trait_change(self.update_loaded_scripts, '_post_measurement_script')
        a.on_trait_change(self.update_loaded_scripts, '_post_equilibration_script')


#===============================================================================
# views
#===============================================================================
    def _get_copy_paste_group(self):
        return HGroup(
             Item('copy_button', enabled_when='object.selected'),
             Item('paste_button', enabled_when='object._copy_cache'),
              show_labels=False)

#============= EOF =============================================

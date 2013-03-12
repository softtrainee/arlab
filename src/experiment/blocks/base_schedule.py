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
from traits.api import Any, Instance, List, Str, Property, Button, Dict, \
    DelegatesTo, on_trait_change, Event
from traitsui.api import Item, EnumEditor, VGroup, HGroup
#============= standard library imports ========================
import yaml
import os
#============= local library imports  ==========================
from src.experiment.automated_run import AutomatedRun
from src.experiment.automated_run_tabular_adapter import AutomatedRunAdapter
from src.constants import NULL_STR, SCRIPT_KEYS
from src.paths import paths
from src.experiment.script_editable import ScriptEditable
from src.experiment.runs_table import RunsTable
from src.experiment.blocks.parser import RunParser, UVRunParser
from src.experiment.identifier import SPECIAL_NAMES, SPECIAL_MAPPING


class RunAdapter(AutomatedRunAdapter):
    can_edit = True
    def _columns_default(self):
        cf = self._columns_factory()
        # remove state
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


class BaseSchedule(ScriptEditable):
    automated_run = Instance(AutomatedRun, ())
    runs_table = Instance(RunsTable, ())
    automated_runs = DelegatesTo('runs_table')
    selected = DelegatesTo('runs_table')
    rearranged = DelegatesTo('runs_table')
    selected_runs = List(AutomatedRun)

    tray = Str(NULL_STR)

    loaded_scripts = Dict

    add = Button
    copy_button = Button('copy')
    paste_button = Button('paste')

    _copy_cache = Any
    parser = None
    update_aliquots_needed = Event
    def _rearranged_fired(self):
        self.update_aliquots_needed = True

    @on_trait_change('''extraction_script, measurement_script,
post_measurement_script, post_equilibration_script''')
    def _script_changed(self, name, new):
        name = name[:-7]
        if self.selected_runs is not None:
            for si in self.selected_runs:
                self._update_run_script(si, name)

        if self.automated_run is not None:
            self._update_run_script(self.automated_run, name)

    def _selected_changed(self, new):
#        print new
        self.selected_runs = new
        if len(new) == 1:
            run = new[0]
            if run.state == 'not run':
                self.automated_run = run.clone_traits()
                for si in SCRIPT_KEYS:
                    try:
                        n = self._clean_script_name(getattr(run.script_info, '{}_script_name'.format(si)))
#                        n = self._clean_script_name(getattr(run, '{}_script'.format(si)).name)
                        setattr(self, '{}_script'.format(si), n)
                    except AttributeError:
                        pass

    @on_trait_change('''automated_run:[_position, extract_+, cleanup, 
    duration, autocenter, overlap, ramp_rate, weight, comment, pattern]''')
    def _sync_selected_runs(self, name, new):
        if self.selected_runs:
            for si in self.selected_runs:
                si.trait_set(**{name:new})

#    def make_configuration(self):
#        extraction = self.extraction_script
#        measurement = self.measurement_script
#        post_measurement = self.post_measurement_script
#        post_equilibration = self.post_equilibration_script
#
#        if not extraction:
#            extraction = self.extraction_scripts[0]
#        if not measurement:
#            measurement = self.measurement_scripts[0]
#        if not post_measurement:
#            post_measurement = self.post_measurement_scripts[0]
#        if not post_equilibration:
#            post_equilibration = self.post_equilibration_scripts[0]
#
#        names = dict(extraction=extraction,
#                           measurement=measurement,
#                           post_measurement=post_measurement,
#                           post_equilibration=post_equilibration
#                           )
#        def make_script_name(ni):
#            na = names[ni]
#            if na is NULL_STR:
#                return na
#            if not na.startswith(self.mass_spectrometer):
#                na = '{}_{}'.format(self.mass_spectrometer, na)
#            return na
#        return self._build_configuration(make_script_name)

    def _set_script_info(self, info):
        for sn in SCRIPT_KEYS:
            v = getattr(self, '{}_script'.format(sn))
            setattr(info, '{}_script_name'.format(sn), v.name)

    def _add_hook(self, ar, **kw):
        self._set_script_info(ar.script_info)
        self.automated_run = ar.clone_traits()
        # if analysis type is bg, b- or a overwrite a few defaults
        if not ar.analysis_type == 'unknown':
            kw['position'] = ''
            kw['extract_value'] = 0

        if not 'labnumber' in kw:
            keys = SPECIAL_MAPPING.values()
            if not ar.labnumber in keys:
                kw['special_labnumber'] = NULL_STR
            else:
                kw['special_labnumber'] = ar.special_labnumber

            kw['labnumber'] = ar.labnumber
            kw['_labnumber'] = ar._labnumber

        self.automated_run.trait_set(**kw)
        self._bind_automated_run(self.automated_run)

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
#            def setter(ski, sci):
#                v = getattr(self, '{}_script'.format(ski))

            setter = lambda ski, sci:setattr(getattr(self, '{}_script'.format(ski)), 'name', sci)

        # open the yaml config file
#        import yaml
        p = os.path.join(paths.scripts_dir, 'defaults.yaml')
        if not os.path.isfile(p):
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
            if key.lower() in ['u', 'bu'] and self.extract_device != NULL_STR:
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
# persistence
#===============================================================================
    def dump(self, stream):
        header, attrs = self._get_dump_attrs()

        writeline = lambda m: stream.write(m + '\n')

        tab = lambda l: writeline('\t'.join(map(str, l)))

        # write metadata
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
                  'disable_between_positions',
                  'weight', 'comment'
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
                  'disable_between_positions',
                  'weight', 'comment'
                  ]

        if self.extract_device == 'Fusions UV':
            header.extend(('reprate', 'mask', 'attenuator'))
            attrs.extend(('reprate', 'mask', 'attenuator'))
#        else:
#            header.extend(['beam'])
#            attrs.extend(['beam'])

        return header, attrs

    def _meta_dumper(self, fp=None):
        pass

#    @classmethod
#    def _run_parser(cls, header, line, meta, delim='\t'):
#        params = dict()

    def parse_line(self, *args, **kw):
        if self.parser is None:
            pklass = RunParser
            if self.extract_device == 'Fusions UV':
                pklass = UVRunParser
            parser = pklass()
            self.parser = parser

        return self.parser.parse(*args, **kw)

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
#    @classmethod
#    def _build_configuration(cls, make_script_name):
#        def make_path(dname, name):
#            return os.path.join(getattr(paths, '{}_dir'.format(dname)), name)
#        args = [('{}_script'.format(ni), make_path(ni, make_script_name(ni)))
#                for ni in SCRIPT_KEYS]
#        return dict(args)

    def _bind_automated_run(self, a, remove=False):
        a.on_trait_change(self.update_loaded_scripts, '_measurement_script', remove=remove)
        a.on_trait_change(self.update_loaded_scripts, '_extraction_script', remove=remove)
        a.on_trait_change(self.update_loaded_scripts, '_post_measurement_script', remove=remove)
        a.on_trait_change(self.update_loaded_scripts, '_post_equilibration_script', remove=remove)
#        a.on_trait_change(self.update_loaded_scripts, 'scripts', remove=remove)



#===============================================================================
# views
#===============================================================================
    def _get_copy_paste_group(self):
        return HGroup(
             Item('copy_button', enabled_when='object.selected'),
             Item('paste_button', enabled_when='object._copy_cache'),
              show_labels=False)

#============= EOF =============================================

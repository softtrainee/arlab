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
from traits.api import HasTraits, List, Instance, DelegatesTo, Str, Int, \
    Property, Event, on_trait_change
from traitsui.api import View, Item, VGroup, HGroup
# from src.experiment.runs_table import RunsTable
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.automated_run.table import AutomatedRunsTable
from src.constants import NULL_STR
from src.experiment.stats import ExperimentStats
import yaml
import os
from src.paths import paths
from src.experiment.automated_run.spec import AutomatedRunSpec
from src.loggable import Loggable
from src.experiment.queue.parser import RunParser, UVRunParser
from src.experiment.automated_run.uv.table import UVAutomatedRunsTable


class BaseExperimentQueue(Loggable):
    runs_table = Instance(AutomatedRunsTable, ())
    automated_runs = DelegatesTo('runs_table')
    selected = DelegatesTo('runs_table')
    rearranged = DelegatesTo('runs_table')
    pasted = DelegatesTo('runs_table')

    cleaned_automated_runs = Property(depends_on='automated_runs[]')

    mass_spectrometer = Str
    extract_device = Str
    tray = Str
    delay_before_analyses = Int
    delay_between_analyses = Int

    stats = Instance(ExperimentStats, ())

    _suppress_aliquot_update = False
    update_aliquots_needed = Event

    def test(self):
        self.info('testing')
        return True

    def add_runs(self, runviews):
        self.automated_runs.extend(runviews)
        self.update_aliquots_needed = True

    def set_extract_device(self, ed):
        self.extract_device = ed
        runs = self.automated_runs
        if self.extract_device == 'Fusions UV':
            klass = UVAutomatedRunsTable
        else:
            klass = AutomatedRunsTable

        self.runs_table = klass()
        self.runs_table.set_runs(runs)
#===============================================================================
# persistence
#===============================================================================
    def load(self, txt):
#        if self.automated_runs is not None:
#            self._cached_runs = self.automated_runs
        self.stats.delay_between_analyses = self.delay_between_analyses

        aruns = self._load_runs(txt)
        if aruns:
#            self.executable = any([ai.executable for ai in aruns])
            self.automated_runs = aruns

#            lm = self.sample_map
#            if lm:
#                for ai in self.automated_runs:
#                    if ai.position:
#                        lm.set_hole_labnumber(ai)

            return True

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

        for arun in self.runs_table.automated_runs:
            vs = arun.to_string_attrs(attrs)
            vals = [v if isNotNull(v) else '' for v in vs]
            tab(vals)

        return stream

    def _load_runs(self, txt):
        aruns = []
        f = (l for l in txt.split('\n'))
        metastr = ''
        # read until break
        for line in f:
            if line.startswith('#====='):
                break
            metastr += '{}\n'.format(line)

        meta = yaml.load(metastr)
        if meta is None:
            self.warning_dialog('Invalid experiment set file. Poorly formatted metadata {}'.format(metastr))

        # load sample map
        self._load_map(meta)

        default = lambda x: x if x else '---'
        default_int = lambda x: x if x is not None else 1

        self._set_meta_param('tray', meta, default)
        self._set_meta_param('extract_device', meta, default)
        self._set_meta_param('mass_spectrometer', meta, default)
        self._set_meta_param('delay_between_analyses', meta, default_int)
        self._set_meta_param('delay_before_analyses', meta, default_int)

        delim = '\t'

        header = map(str.strip, f.next().split(delim))

        pklass = RunParser
        if self.extract_device == 'Fusions UV':
            pklass = UVRunParser
        parser = pklass()
        for linenum, line in enumerate(f):
            if line.startswith('#'):
                continue

            line = line.strip()
            if not line:
                continue

            try:

                script_info, params = parser.parse(header, line, meta)
#                script_info, params = self._parse_line(header, line, meta)
                params['mass_spectrometer'] = self.mass_spectrometer
                params['extract_device'] = self.extract_device
                params['tray'] = self.tray
#                params['db'] = self.db

                arun = self._automated_run_factory(script_info, params)

                aruns.append(arun)

            except Exception, e:
                import traceback
                print traceback.print_exc()
                self.warning_dialog('Invalid Experiment file {}\nlinenum= {}\nline= {}'.format(e, linenum, line))

                return

#        aruns = self._add_frequency_runs(meta, aruns)
        return aruns

    def _automated_run_factory(self, script_info, params):
        arv = AutomatedRunSpec()
        arv.load(script_info, params)
        return arv

    def _load_map(self, meta):
        from src.lasers.stage_managers.stage_map import StageMap
        from src.experiment.map_view import MapView

        def create_map(name):
            if name:
                if not name.endswith('.txt'):
                    name = '{}.txt'.format(name)
                name = os.path.join(paths.map_dir, name)

                if os.path.isfile(name):
                    sm = StageMap(file_path=name)
                    mv = MapView(stage_map=sm)
                    return mv

        self._set_meta_param('sample_map', meta, create_map, metaname='tray')

    def _set_meta_param(self, attr, meta, func, metaname=None):
        if metaname is None:
            metaname = attr

        v = None
        try:
            v = meta[metaname]
        except KeyError:
            pass

        setattr(self, attr, func(v))

    def _get_dump_attrs(self):
        header = ['labnumber',
                  'pattern',
                  'position',
                  'overlap',
                  'e_group',
                  'e_value',
                  'e_units',
                  'duration',
                  'cleanup',
                  'autocenter',
                  'extraction', 'measurement', 'post_eq', 'post_meas',
                  'dis_btw_pos',
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
            header.extend(('reprate', 'mask', 'attenuator', 'image'))
            attrs.extend(('reprate', 'mask', 'attenuator', 'image'))

        return header, attrs

    def _meta_dumper(self, fp):
        s = '''mass_spectrometer: {}
delay_before_analyses: {}
delay_between_analyses: {}
extract_device: {}
tray: {} 
'''.format(self.mass_spectrometer,
           self.delay_before_analyses,
           self.delay_between_analyses,
           self.extract_device,
           self.tray if self.tray else '',
#           make_frequency_runs('blanks'),
#           make_frequency_runs('airs'),
#           make_frequency_runs('cocktails'),
#           make_frequency_runs('backgrounds'),
           )

        if fp:
            fp.write(s)
        else:
            return s

#===============================================================================
# handlers
#===============================================================================
    def _pasted_changed(self):
        sel = self.runs_table.selected

        idx = self.automated_runs.index(sel[0])
        self._suppress_aliquot_update = True
        for si in self.runs_table.copy_cache[::-1]:
            ci = si.clone_traits()
            self.automated_runs.insert(idx, ci)
        self._suppress_aliquot_update = False

        self.update_aliquots_needed = True

    @on_trait_change('automated_runs[]')
    def _update_runs(self):
        if not self._suppress_aliquot_update:
            self.update_aliquots_needed = True
#===============================================================================
# property get/set
#===============================================================================
    def _get_cleaned_automated_runs(self):
        return [ci for ci in self.automated_runs if not ci.skip]

#===============================================================================
# groups
#===============================================================================
    def _get_copy_paste_group(self):
        return HGroup(
             Item('copy_button', enabled_when='object.selected'),
             Item('paste_button', enabled_when='object._copy_cache'),
             Item('update_aliquots'),
              show_labels=False)
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        analysis_table = VGroup(
#                                self._get_copy_paste_group(),
                                Item('runs_table', show_label=False, style='custom'),
                                show_border=True,
                                label='Analyses',
                                )
        v = View(analysis_table)
        return v
#============= EOF =============================================

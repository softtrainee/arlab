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
from traits.api import HasTraits, List, Instance, Str, Button, Any, \
    Bool, Property, Float, Int, on_trait_change, Dict, String, cached_property, \
    Event, DelegatesTo
from traitsui.api import View, Item, TabularEditor, VGroup, HGroup, spring, \
    EnumEditor
#============= standard library imports ========================
import os
#import time
#import datetime
import yaml
#import sha
#============= local library imports  ==========================
from src.experiment.automated_run import AutomatedRun
from src.experiment.extract_schedule import ExtractSchedule
from src.paths import paths
from src.loggable import Loggable
from src.experiment.batch_edit import BatchEdit
from src.experiment.stats import ExperimentStats
from src.helpers.filetools import str_to_bool
from src.experiment.automated_run_tabular_adapter import AutomatedRunAdapter
from src.traits_editors.tabular_editor import myTabularEditor
#from src.experiment.file_listener import FileListener
from src.experiment.identifier import convert_identifier, convert_labnumber
from src.experiment.blocks.schedule_block import ScheduleBlock
from constants import NULL_STR, SCRIPT_KEYS


def extraction_path(name):
    return os.path.join(paths.extraction_dir , name)

def measurement_path(name):
#    return os.path.join(paths.scripts_dir, 'measurement', name)
    return os.path.join(paths.measurement_dir , name)

def post_measurement_path(name):
    return os.path.join(paths.post_measurement_dir, name)

def post_equilibration_path(name):
    return os.path.join(paths.post_equilibration_dir, name)


class ExperimentSet(ScheduleBlock):
#    automated_runs = List(AutomatedRun)
#    automated_run = Instance(AutomatedRun)
    current_run = Instance(AutomatedRun)
    selected_runs = Instance(AutomatedRun)
    extract_schedule = Instance(ExtractSchedule, ())
    stats = Instance(ExperimentStats, ())

    sample_map = Any
    db = Any

    measuring = Property(depends_on='current_run.measuring')

    apply = Button
    add = Button

    delay_between_analyses = Float(1)
    name = Property(depends_on='path')
    path = Str
    ok_to_add = Bool(False)

#    dirty = Property(depends_on='_dirty,path')
#    _dirty = Bool(False)

    dirty = Bool(False)

#    isediting = False
    executable = Bool(True)
    auto_increment = Bool(True)
    update_aliquots_needed = Event

    loaded_scripts = Dict

    measurement_script = String
    measurement_scripts = Property(depends_on='mass_spectrometer')

    post_measurement_script = String
    post_measurement_scripts = Property(depends_on='mass_spectrometer')

    post_equilibration_script = String
    post_equilibration_scripts = Property(depends_on='mass_spectrometer,extract_device')

    extraction_script = String
    extraction_scripts = Property(depends_on='mass_spectrometer')

#    mass_spectrometer = Str('jan')
    mass_spectrometer = Str(NULL_STR)
    mass_spectrometers = Property
    tray = Str
    trays = Property
    extract_device = Str(NULL_STR)
    extract_devices = Property

    selected = Any
    right_clicked = Any

    copy_button = Button
    duplicate_button = Button('duplicate')

#    _text = None
    _cached_runs = None
    _alive = False

    _current_group_id = 0
    _warned_labnumbers = List

#===============================================================================
# persistence
#===============================================================================
    def dump(self, stream):
        self.dirty = False

        header = ['labnumber',
                  'sample',
                  'position',
                  'overlap',
                  'extract_group',
                  'extract_value',
                  'extract_units',
                  'duration',
                  'cleanup',
                  'autocenter',
                  'extraction', 'measurement', 'post_equilibration', 'post_measurement']

        attrs = ['labnumber',
                  'sample',
                  'position',
                  'overlap',
                  'extract_group',
                  'extract_value',
                  'extract_units',
                  'duration',
                  'cleanup',
                  'autocenter',
                  'extraction_script', 'measurement_script',
                  'post_equilibration_script', 'post_measurement_script']

        writeline = lambda m: stream.write(m + '\n')

#        with open(p, 'wb') as f:
        tab = lambda l: writeline('\t'.join(map(str, l)))

        #write metadata

        self._meta_dumper(stream)
        writeline('#' + '=' * 80)

        tab(header)
        for arun in self.automated_runs:
            vs = arun.to_string_attrs(attrs)
#            vs = [getattr(arun, ai) for ai in attrs]
            vals = [v if v and v != NULL_STR else '' for v in vs]
            tab(vals)

        return stream
#               
    def _meta_dumper(self, fp=None):
        def make_frequency_runs(name):
            tmp = '''{}:
 frequency: {{}}
 scripts:
  extraction: {{}}
  measurement: {{}}
  post_equilibration: {{}}
  post_measurement: {{}}'''.format(name)
            s = tmp.format(0, '', '', '', '')
            return s


        s = '''mass_spectrometer: {}
delay_between_analyses: {}
extract_device: {}
tray: {} 
{}
{}
{}
{}
'''.format(self.mass_spectrometer,
           self.delay_between_analyses,
           self.extract_device,
           self.sample_map if self.sample_map else '',
           make_frequency_runs('blanks'),
           make_frequency_runs('airs'),
           make_frequency_runs('cocktails'),
           make_frequency_runs('backgrounds'),
           )

        if fp:
            fp.write(s)
        else:
            return s

    def truncate_run(self, style):
        self.current_run.truncate(style)

    def new_runs_generator(self, last_ran=None):
        runs = [ai for ai in self.automated_runs if ai.executable]

        n = len(runs)
        rgen = (r for r in runs)
        if last_ran is not None:
            #get index of last run in self.automated_runs
#            startid = next((i for i, r in enumerate(runs) if r.runid == last_ran.runid), None)
#            if startid is not None:
            if self._cached_runs:
                startid = self._cached_runs.index(last_ran) + 1
                #for graphic clarity load the finished runs back in
                cached = self._cached_runs[:startid]

                for ai in self.automated_runs:
                    crun = next((r for r in cached if r.labnumber == ai.labnumber and ai.aliquot == 0), None)
                    if crun is not None:
                        ai.state = crun.state
                        ai.aliquot = crun.aliquot
#                        print 'setting ', crun.aliquot

                newruns = runs[startid:]
                self.info('starting at analysis {} (startid={} of {})'.format(newruns[0].runid, startid + 1, n))
                n = len(newruns)
                rgen = (r for r in newruns)
            else:
                self.info('last ran analysis {} does not exist in modified experiment set. starting from the beginning')

        return rgen, n

    def load_automated_runs(self, text):
        if self.automated_runs is not None:
            self._cached_runs = self.automated_runs

        self.stats.delay_between_analyses = self.delay_between_analyses

        aruns = self._load_runs(text)
        if aruns:
#            self.update_aliquots_needed = True
            self.executable = any([ai.executable for ai in aruns])
            self.automated_runs = aruns

            lm = self.sample_map
            if lm:
                for ai in self.automated_runs:
                    if ai.position:
                        lm.set_hole_labnumber(ai.position, ai.labnumber)

            return True

    def _set_meta_param(self, attr, meta, func, metaname=None):
        if metaname is None:
            metaname = attr

        v = None
        try:
            v = meta[metaname]
        except KeyError:
            pass

        setattr(self, attr, func(v))

    def _load_runs(self, text):
        aruns = []

        f = (l for l in text.split('\n'))
        metastr = ''
        #read until break
        for line in f:
            if line.startswith('#====='):
                break
            metastr += '{}\n'.format(line)

        meta = yaml.load(metastr)

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

        default = lambda x: x if x else '---'
        default_int = lambda x: x if x is not None else 1
        self._set_meta_param('extract_device', meta, default)
        self._set_meta_param('mass_spectrometer', meta, default)
        self._set_meta_param('delay_between_analyses', meta, default_int)

        delim = '\t'

        header = map(str.strip, f.next().split(delim))

        for linenum, line in enumerate(f):
            if line.startswith('#'):
                continue

            line = line.strip()
            if not line:
                continue

            try:
                params = self._run_parser(header, line, meta)

                params['mass_spectrometer'] = self.mass_spectrometer
                params['extract_device'] = self.extract_device

                arun = self._automated_run_factory(**params)
                aruns.append(arun)

            except Exception, e:
                import traceback
                print traceback.print_exc()
                self.warning_dialog('Invalid Experiment file {}\nlinenum= {}\nline= {}'.format(e, linenum, line))

                return

        aruns = self._add_frequency_runs(meta, aruns)

        return aruns

    def _add_frequency_runs(self, meta, runs):
        nruns = []
        i = 0

        names = dict()
        setter = lambda sk, sc:names.__setitem__(sk, sc)
        def _make_script_name(_meta, li, name):
            na = _meta['scripts'][name]
            if na is None:
                na = ''
            elif na.startswith('_'):
                na = meta['mass_spectrometer'] + na

            if not na:
                self._load_default_scripts(setter=setter, key=li)
#                print names, name
                ni = names[name]
                if ni != NULL_STR:
                    na = self._add_mass_spectromter_name(ni)
#                print na
#                na = names[name] if names[name] != NULL_STR else ''


            if na and not na.endswith('.py'):
                na = na + '.py'


            return na

        cextract_group = None
        for ai in runs:
            nruns.append(ai)
#            print ai.labnumber
            try:
                int(ai.labnumber)
                i += 1
            except ValueError:
                continue
#            index_mapping = dict(before=lambda n:-1, after=lambda n: n)
            for name, ln in [('blanks', 'Bu'), ('airs', 'A'), ('cocktails', 'C'), ('backgrounds', 'Bg')]:
                try:
                    _meta = meta[name]
                    freq = _meta['frequency']
                    if not freq:
                        continue
                except KeyError:
                    continue

                make_script_name = lambda x: _make_script_name(_meta, ln, x)
                params = dict()
                params['labnumber'] = '{}'.format(ln)
                params['configuration'] = self._build_configuration(make_script_name)

#                print name, arun.labnumber, arun.aliquot
                if isinstance(freq, int):
                    freq = [freq]

                for fi in freq:
                    arun = self._automated_run_factory(**params)
                    if isinstance(fi, int):
                        if i % freq == 0:
#                            arun = self._automated_run_factory(**params)
                            nruns.append(arun)
                    else:
                        if ai.extract_group:
                            if cextract_group == ai.extract_group:
                                #if this is the last run dont continue
                                if ai != runs[-1]:
                                    continue
                            else:
                                cextract_group = ai.extract_group

                        if fi.lower() == 'before' and ai != runs[-1]:
                            if len(nruns) >= 2:
#                                print nruns[-2].labnumber, ln, 'fff'
                                if nruns[-2].labnumber != ln:
                                    nruns.insert(-1, arun)
                            else:
                                nruns.insert(-1, arun)
                        elif fi.lower() == 'after':
                            nruns.append(arun)

        return nruns

    def _build_configuration(self, make_script_name):
        gdict = globals()
        args = [('{}_script'.format(ni), gdict['{}_path'.format(ni)](make_script_name(ni)))
              for ni in SCRIPT_KEYS]
#              ['extraction', 'measurement', 'post_measurement', 'post_equilibration']
#              ]
        return dict(args)

    def _right_clicked_changed(self):
        selected = self.selected
        if selected:
            selected = selected[0]
            ms = selected.measurement_script.name
            es = selected.extraction_script.name
            be = BatchEdit(
                           batch=len(self.selected) > 1,
                           measurement_scripts=self.measurement_scripts,
                           measurement_script=ms,
                           orig_measurement_script=ms,

                           extraction_scripts=self.extraction_scripts,
                           extraction_script=es,
                           orig_extraction_script=es,

                           power=selected.extract_value,
                           orig_power=selected.extract_value,

                           duration=selected.duration,
                           orig_duration=selected.duration,

                           position=selected.position,
                           orig_position=selected.position
                           )

            be.reset()
            info = be.edit_traits()
            if info.result:
                be.apply_edits(self.selected)
                self.automated_run.update = True

    def _run_parser(self, header, line, meta, delim='\t'):
        params = dict()
        args = map(str.strip, line.split(delim))

        #load strings
        for attr in ['labnumber',
                     'sample',
                     'measurement', 'extraction', 'post_measurement',
                     'post_equilibration',
                     ]:
            params[attr] = args[header.index(attr)]

        #load booleans
        for attr in ['autocenter']:
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

        for attr in ['duration', 'position', 'overlap', 'cleanup', 'extract_group']:
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
#        heat = args[header.index('extract_value')]
#        if heat:
#            if ',' in heat:
#                v, u = heat.split(',')
#                v = float(v)
#            else:
#                v = float(heat)
#                u = 'w'
#
#            params['extract_value'] = v
#            params['extract_units'] = u

        def make_script_name(n):
            na = args[header.index(n)]
            if na.startswith('_'):
                na = meta['mass_spectrometer'] + na

            if na and not na.endswith('.py'):
                na = na + '.py'
            return na

        params['configuration'] = self._build_configuration(make_script_name)
        return params

    def _load_script_names(self, name):
        p = os.path.join(paths.scripts_dir, name)
        if os.path.isdir(p):
            prep = lambda x:x
    #        prep = lambda x: os.path.split(x)[0]

            return [prep(s)
                    for s in os.listdir(p)
                        if not s.startswith('.') and s.endswith('.py')
                        ]
        else:
            self.warning_dialog('{} script directory does not exist!'.format(p))

#    def _build_configuration(self, extraction, measurement, post_measurement, post_equilibration):
#        c = dict(extraction_script=extraction_path(extraction),
#                  measurement_script=measurement_path(measurement),
#                  post_measurement_script=post_measurement_path(post_measurement),
#                  post_equilibration_script=post_equilibration_path(post_equilibration)
#                  )
#        return c

    def save_to_db(self):
        self.info('saving experiment {} to database'.format(self.name))
        db = self.db
        db.add_experiment(self.name)
        db.commit()

    def update_loaded_scripts(self, new):
#        print self.loaded_scripts, 'loadded scripts'
        if new:
            self.loaded_scripts[new.name] = new
            self.automated_run.scripts = self.loaded_scripts
#    def reset_stats(self):
#        self._alive = True
#        self.stats.start_timer()
#
#    def stop_stats_timer(self):
#        self._alive = False
#        self.stats.stop_timer()

    def _auto_increment(self, m):

        try:
            m = str(int(m) + 1)
        except ValueError:
            pass

        return m

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
        with open(p, 'r') as fp:
            defaults = yaml.load(fp)

        #if labnumber is int use key='U'
        try:
            _ = int(key)
            key = 'U'
        except ValueError:
            pass

#        print key, defaults
        if not key in defaults:
            return

        scripts = defaults[key]
        for sk in ['extraction', 'measurement', 'post_equilibration', 'post_measurement']:

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
#                    print sc
            if not sc in getattr(self, '{}_scripts'.format(sk)):
                sc = NULL_STR
#            print setter, sk, sc
            setter(sk, sc)


#===============================================================================
# handlers
#===============================================================================
    def _duplicate_button_fired(self):

        for si in self.selected:
            self.automated_runs.append(si.clone_traits())
        self.update_aliquots_needed = True

    def _add_fired(self):
        ars = self.automated_runs
        ar = self.automated_run
        rid = self._auto_increment(ar.labnumber)

        position = None
        if ar.position:
            position = self._auto_increment(ar.position)

        def make_script_name(ni):
            na = getattr(self, '{}_script'.format(ni))
            if na == NULL_STR:
                return na
            if not na.startswith(self.mass_spectrometer):
                na = '{}_{}'.format(self.mass_spectrometer, na)

            if na and not na.endswith('.py'):
                na = na + '.py'
            return na

        ar.configuration = self._build_configuration(make_script_name)
        ar.extraction_script_dirty = True
        ar.measurement_script_dirty = True
        ar.post_measurement_script_dirty = True
        ar.post_equilibration_script_dirty = True

        ars.append(ar)

        kw = dict()
        if self.auto_increment:
            if rid:
                nrid = rid
#                kw['labnumber'] = rid
            npos = position
            if npos:
                npos = position

#                kw['position'] = position
        else:
            nrid = ar.labnumber
            npos = ar.position
#            kw['labnumber'] = self.automated_run.labnumber
#            kw['position'] = self.automated_run.position

#        kw['_extract_value'] = ar._extract_value
#        kw['_extract_units'] = ar._extract_units
#        kw['_duration'] = ar._duration
#        kw['configuration'] = ar.configuration
#        kw['mass_spectrometer'] = self.mass_spectrometer

        self.automated_run = ar.clone_traits()
        kw['labnumber'] = nrid
        if npos:
            kw['position'] = npos
        self.automated_run.trait_set(**kw)
#        self.automated_run = self.automated_run_factory(copy_automated_run=False, **kw)

        self.update_aliquots_needed = True

    def _apply_fired(self):
        hs = self.extract_schedule
        for _i, s in enumerate(hs.steps):
            if s.duration:
                a = self.automated_run.clone_traits()
                a._extract_value = s.extract_value
                a._duration = s.duration
                a._extract_units = hs.units
                a.extract_group = self._current_group_id
#                a._nominal_step = i
                self.automated_runs.append(a)

        self._current_group_id += 1
        self.update_aliquots_needed = True

    def _extraction_script_changed(self):
        self._script_changed('extraction')

    def _measurement_script_changed(self):
        self._script_changed('measurement')

    def _post_measurement_script_changed(self):
        self._script_changed('post_measurement')

    def _post_equilibration_script_changed(self):
        self._script_changed('post_equilibration')

    def _script_changed(self, name):
        if self.selected_runs is not None:
            for si in self.selected_runs:
                self._update_run_script(self.selected_runs, name)

        if self.automated_run is not None:
            self._update_run_script(self.automated_run, name)

    def _update_run_script(self, run, sname):
        ssname = '{}_script'.format(sname)
        name = getattr(self, ssname)
        name = self._add_mass_spectromter_name(name)
        run.configuration[ssname] = os.path.join(paths.scripts_dir,
                                                    sname,
                                                    name
                                                    )
        setattr(run, '{}_script_dirty'.format(sname), True)

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

    @on_trait_change('current_run,automated_runs[]')
    def _update_stats(self, obj, name, old, new):
        if self.automated_runs:
            self.dirty = True
        else:
            self.dirty = False
#        self.stats.calculate_etf(self.automated_runs)

    @on_trait_change('automated_run:labnumber')
    def _update_labnumber(self, labnumber):
#        if not self.isediting:
#            return

        arun = self.automated_run
        #check for id in labtable
        self.ok_to_add = False
        db = self.db

        arun.sample = ''
        arun.aliquot = 1
        arun.irrad_level = ''

        if labnumber:
            if isinstance(convert_identifier(labnumber), int):
                self.ok_to_add = True
                arun.sample = convert_labnumber(convert_identifier(labnumber))
                self._load_default_scripts()
                return

            ln = db.get_labnumber(labnumber)
            if ln:
                self.ok_to_add = True
                #set sample and irrad info
                try:
                    arun.sample = ln.sample.name
                except AttributeError:
                    pass

                ipos = ln.irradiation_position
                if not ipos is None:
                    level = ipos.level
                    irrad = level.irradiation
#                    irrad = ipos.irradiation
                    arun.irrad_level = '{}{}'.format(irrad.name, level.name)

                #set default scripts
                self._load_default_scripts()

#            elif self.confirmation_dialog('{} does not exist. Add to database?'.format(labnumber)):
#                db.add_labnumber(labnumber, 1, commit=True)
#                self.ok_to_add = True
            else:
                self.warning_dialog('{} does not exist'.format(labnumber))

    def _mass_spectrometer_changed(self):
        if self.automated_run is None:
            return

        for ai in self.automated_runs:
            ai.mass_spectrometer = self.mass_spectrometer

        if self.automated_run.labnumber:
            self._load_default_scripts()
        else:
            self.post_equilibration_script = NULL_STR
            self.post_measurement_script = NULL_STR
            self.measurement_script = NULL_STR
            self.extraction_script = NULL_STR


    def _extract_device_changed(self):
        if self.mass_spectrometer:
            self._load_default_scripts()
#        self.automated_run.mass_spectrometer = self.mass_spectrometer

    def _selected_changed(self, new):
#        print new
        self.selected_runs = new
        if len(new) == 1:
            self.automated_run = new[0].clone_traits()

            for si in SCRIPT_KEYS:
                try:
                    n = self._clean_script_name(getattr(new[0], '{}_script'.format(si)).name)
                    setattr(self, '{}_script'.format(si), n)
                except AttributeError:
                    pass

#===============================================================================
# property get/set
#===============================================================================
#    def _set_dirty(self, d):
#        self._dirty = d
#
#    def _get_dirty(self):
#        return self._dirty and os.path.isfile(self.path)

    def _get_name(self):
        if self.path:
            return os.path.splitext(os.path.basename(self.path))[0]
        else:
            return ''
#        else:
#            return 'New ExperimentSet'

    def _get_measuring(self):
        if self.current_run:
            return self.current_run.measuring

    def _get_scripts(self, es):
        if self.mass_spectrometer != '---':
            k = '{}_'.format(self.mass_spectrometer)
#            es = [ei.replace(k, '').replace('.py', '') for ei in es if ei.startswith(k)]
            es = [self._clean_script_name(ei) for ei in es if ei.startswith(k)]

        es = [NULL_STR] + es
        return es

    def _get_extraction_scripts(self):
        ms = self._load_script_names('extraction')
        ms = self._get_scripts(ms)
#        self.extraction_script = '---'
#        if not self.extraction_script in ms:

        return ms

    def _get_measurement_scripts(self):
        ms = self._load_script_names('measurement')
        ms = self._get_scripts(ms)
#        self.measurement_script = '---'

#        name = self.automated_run.measurement_script.name
#        name = self._remove_mass_spectrometer_name(name)
#        if self.mass_spectrometer:
#            msi = msi.name.replace('{}_'.format(self.mass_spectrometer), '')

#        if name in ms:
#            self.measurement_script = name
##            if self.mass_spectrometer:
##                msi = '{}_{}'.format(self.mass_spectrometer, msi)
#            self.measurement_script = msi
#            print self.measurement_script
#        print self.automated_run.measurement_script
        return ms

    def _get_post_measurement_scripts(self):
        ms = self._load_script_names('post_measurement')
        ms = self._get_scripts(ms)
#        self.post_measurement_script = '---'
#        if not self.post_measurement_script in ms:
#        self.post_measurement_script = 'pump_ms.py'
        return ms

    def _get_post_equilibration_scripts(self):
        ms = self._load_script_names('post_equilibration')
        ms = self._get_scripts(ms)
#        self.post_equilibration_script = '---'
#        if not self.post_equilibration_script in ms:
        return ms

    def set_script_names(self):
        arun = self.automated_run
#        keys = ['measurement', 'post_measurement', 'extraction', 'post_equilibration']

        def get_name(si):
            script = getattr(arun, '{}_script'.format(si))
            if script:
                scripts = getattr(self, '{}_scripts'.format(si))
                name = self._clean_script_name(script.name)
#                name = self._remove_mass_spectrometer_name(script.name)
                if not name in scripts:
                    name = NULL_STR
            else:
                name = NULL_STR

            return name
#        print 'setting script names'
        traits = dict([('{}_script'.format(k), get_name(k)) for k in SCRIPT_KEYS])
        self.trait_set(**traits)

    @cached_property
    def _get_mass_spectrometers(self):
        db = self.db
        ms = [NULL_STR] + [mi.name for mi in db.get_mass_spectrometers()]
        return ms

    def _get_trays(self):
        ts = ['---'] + [s for s in os.listdir(paths.map_dir)
                if not s.startswith('.') and s.endswith('.txt')]
        return ts

    def _get_extract_devices(self):
        return [NULL_STR, 'Fusions CO2', 'Fusions Diode']

#    def _set_dirty(self, d):
#        self._dirty = d
#
#    def _get_dirty(self):
#        return self._dirty and os.path.isfile(self.path)
#===============================================================================
# factories
#===============================================================================
    def automated_run_factory(self, copy_automated_run=False, ** params):
        extraction = self.extraction_script
        measurement = self.measurement_script
        post_measurement = self.post_measurement_script
        post_equilibration = self.post_equilibration_script

        if not extraction:
            extraction = self.extraction_scripts[0]
        if not measurement:
            measurement = self.measurement_scripts[0]
        if not post_measurement:
            post_measurement = self.post_measurement_scripts[0]
        if not post_equilibration:
            post_equilibration = self.post_equilibration_scripts[0]

        names = dict(extraction=extraction,
                           measurement=measurement,
                           post_measurement=post_measurement,
                           post_equilibration=post_equilibration
                           )

        def make_script_name(ni):
            na = names[ni]
            if na is NULL_STR:
                return na
            if not na.startswith(self.mass_spectrometer):
                na = '{}_{}'.format(self.mass_spectrometer, na)
            return na

#        make_script_name = lambda x: names[x]
        configuration = self._build_configuration(make_script_name)

        arun = self.automated_run
        if arun and copy_automated_run:
            params.update(dict(
                               labnumber=arun.labnumber,
                               position=arun.position,
                               aliquot=arun.aliquot))

        params['configuration'] = configuration

        return self._automated_run_factory(**params)

    def _automated_run_factory(self, labnumber=None, **kw):
        '''
             always use this factory for new AutomatedRuns
             it sets the configuration, loaded scripts and binds our update_loaded_script
             handler so we are aware of scripts that have been tested
        '''



        #copy some of the last runs values
        if self.automated_runs:
            pa = self.automated_runs[-1]
            for k in ['extract_device', 'autocenter']:
                if not k in kw:
                    kw[k] = getattr(pa, k)

        a = AutomatedRun(
                         scripts=self.loaded_scripts,
                         labnumber=labnumber if labnumber else '',
                         **kw
                         )
        if labnumber:
            ln = self.db.get_labnumber(labnumber)

            if ln is None:
                #check to see if we have already warned for this labnumber
                if not labnumber in self._warned_labnumbers:
                    self.warning_dialog('Invalid labnumber {}'.format(labnumber))
                    self._warned_labnumbers.append(labnumber)
                a._executable = False
            else:
                self._bind_automated_run(a)
                a.create_scripts()
        else:
            self._bind_automated_run(a)
            a.create_scripts()

        return a

    def _bind_automated_run(self, a):
        a.on_trait_change(self.update_loaded_scripts, '_measurement_script')
        a.on_trait_change(self.update_loaded_scripts, '_extraction_script')
        a.on_trait_change(self.update_loaded_scripts, '_post_measurement_script')
        a.on_trait_change(self.update_loaded_scripts, '_post_equilibration_script')

#===============================================================================
# defaults
#===============================================================================
#    def _automated_run_default(self):
#
#        es = self.extraction_scripts[0]
#        ms = self.measurement_scripts[0]
#
#
#        return self._automated_run_factory(extraction=es, measurement=ms)
    def _stats_default(self):
        return ExperimentStats(experiment_set=self)
#===============================================================================
# views
#===============================================================================
    def _automated_run_editor(self, update=''):
        r = myTabularEditor(adapter=AutomatedRunAdapter(),
                             update=update,
                             right_clicked='object.right_clicked',
                             selected='object.selected',
#                             refresh='object.refresh',
#                             activated_row='object.activated_row',
                            operations=['delete', 'edit'],
#                            editable=False,
                             auto_resize=True,
                             multi_select=True,
                             auto_update=True,
                             scroll_to_bottom=False
                            )
        self.tabular_editor = r
        return r

    def traits_view(self):
        new_analysis = VGroup(
                              Item('automated_run',
                                   show_label=False,
                                   style='custom',
                                   ),
                              enabled_when='mass_spectrometer and mass_spectrometer!="---"'
                              )

        analysis_table = VGroup(
                                HGroup(
#                                       Item('copy_button'), 
                                       Item('duplicate_button'), show_labels=False),
                                Item('automated_runs', show_label=False,
                                    editor=self._automated_run_editor(),
                                    height=0.75,
#                                    width=400,
                                    ), show_border=True,

                                label='Analyses'
                                )


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

#        schedule_grp = Item('extract_schedule',
#                                   style='custom',
#                                   show_label=False,
#                                   height=0.25,
#                                   )

#        VGroup(
#                                Item('extract_schedule',
#                                   style='custom',
#                                   show_label=False,
#                                   height=0.25,
#                                   width=0.1,
#                                   ),
#                                   HGroup(spring, Item('apply', enabled_when='ok_to_add'),
#                                     show_labels=False),
#                              springy=False
#                              )
        gparameters_grp = VGroup(
              Item('mass_spectrometer',
                   editor=EnumEditor(name='mass_spectrometers'),
#                                           show_label=False
                   ),
              Item('extract_device',
                   editor=EnumEditor(name='extract_devices'),
#                                           show_label=False,
                   ),
              Item('tray',
                   editor=EnumEditor(name='trays'),
#                                           show_label=False,
                   )
              )
        v = View(
                 HGroup(
                        VGroup(
                               gparameters_grp,
                               new_analysis,
                               script_grp,
                               HGroup(Item('auto_increment'),
                                     spring,
                                     Item('add', show_label=False, enabled_when='ok_to_add'),
                                     ),
                               ),

                        VGroup(
#                               schedule_grp,
                               analysis_table
                               )

                        )
                 )

        return v


#===============================================================================
# debugging
#===============================================================================
#    def add_run(self):
#        a = self._automated_run_factory('B-1')
#        self.automated_runs.append(a)
#        print a.measurement_script
#
#        a = self._automated_run_factory('B-2')
#        self.automated_runs.append(a)
#        a = AutomatedRun(identifier='B-dd12',
#                         scripts=self.loaded_scripts,
#                         configuration=self.test_configuration
#                         )
#        self.automated_runs.append(a)
#        self.automated_runs.append(a)
#    def _automated_runs_default(self):
#        return [
#
#                AutomatedRun(identifier='B-01'),
#                AutomatedRun(identifier='A-01'),
#                AutomatedRun(identifier='A-02'),
#                AutomatedRun(identifier='A-03'),
#                AutomatedRun(identifier='A-04'),
#                AutomatedRun(identifier='B-02'),
#                AutomatedRun(identifier='A-05'),
#                AutomatedRun(identifier='A-06'),
#                AutomatedRun(identifier='A-07'),
#                AutomatedRun(identifier='A-08'),
#                AutomatedRun(identifier='A-09'),
#                AutomatedRun(identifier='A-10'),
#                AutomatedRun(identifier='B-03'),
#                ]
#    @on_trait_change('automated_runs[]')
#    def _automated_runs_changed(self, obj, name, old, new):
#        if old:
#            old = old[0]
#
#            if self.automated_run:
#                if old.identifier == self.automated_run.identifier:
#                    self.automated_run.aliquot -= 1
#
#            fo = dict()
#            pi = None
#
#            for ai in self.automated_runs:
#                try:
#                    pi = fo[ai.identifier]
#                    if ai.aliquot != pi + 1:
#                        ai.aliquot -= 1
#                except KeyError:
#                    pass
#
#                fo[ai.identifier] = ai.aliquot
#============= EOF =============================================


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
from src.experiment.heat_schedule import HeatSchedule
from src.paths import paths
from src.loggable import Loggable
from src.experiment.batch_edit import BatchEdit
from src.experiment.stats import ExperimentStats
from src.helpers.filetools import str_to_bool
from src.experiment.automated_run_tabular_adapter import AutomatedRunAdapter
from src.traits_editors.tabular_editor import myTabularEditor
#from src.experiment.file_listener import FileListener
from src.experiment.identifier import convert_identifier, convert_labnumber


def extraction_path(name):
    return os.path.join(paths.scripts_dir, 'extraction', name)

def measurement_path(name):
    return os.path.join(paths.scripts_dir, 'measurement', name)

def post_measurement_path(name):
    return os.path.join(paths.scripts_dir, 'post_measurement', name)

def post_equilibration_path(name):
    return os.path.join(paths.scripts_dir, 'post_equilibration', name)


class ExperimentSet(Loggable):
    automated_runs = List(AutomatedRun)
    automated_run = Instance(AutomatedRun)
    current_run = Instance(AutomatedRun)
    heat_schedule = Instance(HeatSchedule, ())
    stats = Instance(ExperimentStats, ())

    lab_map = Any
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
    post_equilibration_scripts = Property(depends_on='mass_spectrometer')

    extraction_script = String
    extraction_scripts = Property(depends_on='mass_spectrometer')

#    mass_spectrometer = Str('jan')
    mass_spectrometer = Str
    mass_spectrometers = Property
    tray = Str
    trays = Property
    heat_device = Str
    heat_devices = Property

    selected = Any
    right_clicked = Any

    copy_button = Button
    duplicate_button = Button('duplicate')

#    _text = None
    _cached_runs = None
    _alive = False
#===============================================================================
# persistence
#===============================================================================
    def dump(self, stream):
        self.dirty = False

        header = ['labnumber',
                  'sample',
                  'position',
                  'overlap',
                  'heat_value',
                  'heat_units',
                  'duration',
                  'cleanup',
                  'autocenter',
                  'extraction', 'measurement', 'post_equilibration', 'post_measurement']

        attrs = ['labnumber',
                  'sample',
                  'position',
                  'overlap',
                  'heat_value',
                  'heat_units',
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
            vals = [v if v and v != '---' else '' for v in vs]
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
heat_device: {}
tray: {} 
{}
{}
{}
{}
'''.format(self.mass_spectrometer,
           self.delay_between_analyses,
           self.heat_device,
           self.lab_map if self.lab_map else '',
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
            startid = next((i for i, r in enumerate(runs) if r.runid == last_ran.runid), None)
            if startid is not None:
                if self._cached_runs:
                    #for graphic clarity load the finished runs back in
                    cached = self._cached_runs[:startid - 1]
                    for ai in self.automated_runs:
                        crun = next((r for r in cached if r.runid == ai.runid), None)
                        if crun is not None:
                            ai.state = crun.state

                newruns = runs[startid + 1:]
                self.info('starting at analysis {} (startid={} of {})'.format(newruns[0].runid, startid + 2, n))
                n = len(newruns)
                rgen = (r for r in newruns)
            else:
                self.info('last ran analysis {} does not exist in modified experiment set. starting from the beginning')

        return rgen, n

    def load_automated_runs(self, text):
        if self.automated_runs is not None:
            self._cached_runs = self.automated_runs

        self.stats.delay_between_analyses = self.delay_between_analyses

        if text is None:
            with open(self.path, 'r') as fp:
                text = fp.read()

        aruns = self._load_runs(text)
        if aruns:
            self.automated_runs = aruns
#            self._update_aliquots()
            lm = self.lab_map

            for ai in self.automated_runs:
                if ai.position:
                    lm.set_hole_labnumber(ai.position, ai.labnumber)

            return True

    def _load_runs(self, text):
        aruns = []

#        if text is None:
#            with open(self.path, 'r') as fp:
#                text = fp.read()
#
#        self._text = text

        f = (l for l in text.split('\n'))
        metastr = ''
        #read until break
        for line in f:
            if line.startswith('#====='):
                break
            metastr += '{}\n'.format(line)

#        print metastr
        meta = yaml.load(metastr)

        from src.lasers.stage_managers.stage_map import StageMap
        from src.experiment.map_view import MapView
        try:
            sm = meta['tray']
            sm = StageMap(file_path=os.path.join(paths.map_dir, '{}.txt'.format(sm)))
            mv = MapView(stage_map=sm)
            self.lab_map = mv
            hd = meta['heat_device']
            self.heat_device = hd if hd else '---'
        except KeyError:
            pass

        delim = '\t'

        header = map(str.strip, f.next().split(delim))
        self.executable = True
        for linenum, line in enumerate(f):
            if line.startswith('#'):
                continue

            line = line.strip()
            if not line:
                continue

            try:
                self.delay_between_analyses = meta['delay_between_analyses']
                params = self._run_parser(header, line, meta)
                params['mass_spec_name'] = meta['mass_spectrometer']
                params['heat_device'] = self.heat_device
                arun = self._automated_run_factory(**params)
                aruns.append(arun)

            except Exception, e:
                import traceback
                print traceback.print_exc()
                self.warning_dialog('Invalid Experiment file {}\nlinenum= {}\nline= {}'.format(e, linenum, line))
                self.executable = False
                return

        aruns = self._add_frequency_runs(meta, aruns)

        return aruns

    def _add_frequency_runs(self, meta, runs):
        nruns = []
        i = 0
        def _make_script_name(_meta, na):
            na = _meta['scripts'][na]
            if na is None:
                na = ''
            elif na.startswith('_'):
                na = meta['mass_spectrometer'] + na

            if na and not na.endswith('.py'):
                na = na + '.py'
            return na

        for ai in runs:
            nruns.append(ai)
            try:
                int(ai.labnumber)
                i += 1
            except ValueError:
                continue

            for name, ln in [('blanks', 'Bu'), ('airs', 'A'), ('cocktails', 'C'), ('backgrounds', 'Bg')]:
                try:
                    _meta = meta[name]
                    freq = _meta['frequency']
                    if not freq:
                        continue
                except KeyError:
                    continue

                make_script_name = lambda x: _make_script_name(_meta, x)
                params = dict()
                params['labnumber'] = '{}'.format(ln)
                params['configuration'] = self._build_configuration(make_script_name)

                if i % freq == 0:
                    arun = self._automated_run_factory(**params)
                    nruns.append(arun)

        return nruns

    def _build_configuration(self, make_script_name):
        gdict = globals()
        args = [('{}_script'.format(ni), gdict['{}_path'.format(ni)](make_script_name(ni)))
              for ni in ['extraction', 'measurement', 'post_measurement', 'post_equilibration']]
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

                           power=selected.heat_value,
                           orig_power=selected.heat_value,

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
#                     'heat_device'
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
        for attr in ['duration', 'position', 'overlap', 'cleanup']:
            try:
                param = args[header.index(attr)].strip()
                if param:
                    params[attr] = float(param)
            except IndexError:
                pass

        #default heat_units to watts
        heat_value = args[header.index('heat_value')]
        heat_units = args[header.index('heat_units')]
        if not heat_units:
            heat_units = '---'

        params['heat_value'] = heat_value
        params['heat_units'] = heat_units
#        heat = args[header.index('heat_value')]
#        if heat:
#            if ',' in heat:
#                v, u = heat.split(',')
#                v = float(v)
#            else:
#                v = float(heat)
#                u = 'w'
#
#            params['heat_value'] = v
#            params['heat_units'] = u

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
        if new:
            self.loaded_scripts[new.name] = new

    def reset_stats(self):
        self._alive = True
        self.stats.start_timer()

    def stop_stats_timer(self):
        self._alive = False
        self.stats.stop_timer()

    def _auto_increment(self, m):

        try:
            m = str(int(m) + 1)
        except ValueError:
            pass

        return m

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
            if na == '---':
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
        kw['labnumber'] = nrid
        if npos:
            kw['position'] = npos

        kw['_heat_value'] = ar._heat_value
        kw['_heat_units'] = ar._heat_units
        kw['_duration'] = ar._duration
        kw['configuration'] = ar.configuration
        kw['mass_spec_name'] = self.mass_spectrometer
        self.automated_run = self.automated_run_factory(copy_automated_run=False, **kw)
        self.update_aliquots_needed = True

    def _apply_fired(self):
        hs = self.heat_schedule
        for _i, s in enumerate(hs.steps):
            if s.duration:
                a = self.automated_run.clone_traits()
                a._heat_value = s.heat_value
                a._duration = s.duration
                a._heat_units = hs.units
                self.automated_runs.append(a)

        self.update_aliquots_needed = True

    def _extraction_script_changed(self):
#        print self.extraction_script
        if self.automated_run:
            self.automated_run.configuration['extraction_script'] = os.path.join(paths.scripts_dir,
                                                        'extraction',
                                                        self.extraction_script)

            self.automated_run.extraction_script_dirty = True

    def _measurement_script_changed(self):
#        print self.measurement_script
        if self.automated_run:
            self.automated_run.configuration['measurement_script'] = os.path.join(paths.scripts_dir,
                                                        'measurement',
                                                        self.measurement_script)
            self.automated_run.measurement_script_dirty = True
    def _post_measurement_script_changed(self):
#        print self.post_measurement_script
        if self.automated_run:
            self.automated_run.configuration['post_measurement_script'] = os.path.join(paths.scripts_dir,
                                                        'post_measurement',
                                                        self.post_measurement_script)
            self.automated_run.post_measurement_script_dirty = True

    def _post_equilibration_script_changed(self):
#        print self.post_equilibration_script
        if self.automated_run:
            self.automated_run.configuration['post_equilibration_script'] = os.path.join(paths.scripts_dir,
                                                        'post_equilibration',
                                                        self.post_equilibration_script)
            self.automated_run.post_equilibration_script_dirty = True

    def increment_nruns_finished(self):
        self.stats.nruns_finished += 1

    @on_trait_change('current_run,automated_runs[]')
    def _update_stats(self, obj, name, old, new):
        if self.automated_runs:
            self.dirty = True
        else:
            self.dirty = False
        self.stats.calculate_etf(self.automated_runs)

    @on_trait_change('automated_run.labnumber')
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
                return

            def _add_info(li):
                try:
                    arun.sample = li.sample.name
                except AttributeError:
                    pass
#                    self.warning_dialog('{} does not have sample info'.format(li.labnumber))

                ipos = li.irradiation_position
                if not ipos is None:
                    irrad = ipos.irradiation
                    arun.irrad_level = '{}{}'.format(irrad.name, irrad.level)
#                else:
#                    self.warning_dialog('{} does not have irradiation info'.format(li.labnumber))

            ln = db.get_labnumber(labnumber)
            if ln:
                _add_info(ln)
                self.ok_to_add = True
#            elif self.confirmation_dialog('{} does not exist. Add to database?'.format(labnumber)):
#                db.add_labnumber(labnumber, 1, commit=True)
#                self.ok_to_add = True
            else:
                self.warning_dialog('{} does not exist'.format(labnumber))

    def _mass_spectrometer_changed(self):
        for ai in self.automated_runs:
            ai.mass_spec_name = self.mass_spectrometer

#        self.automated_run.mass_spec_name = self.mass_spectrometer

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
            es = [ei.replace(k, '') for ei in es if ei.startswith(k)]

        es = ['---'] + es
        return es

    def _get_extraction_scripts(self):
        ms = self._load_script_names('extraction')
        ms = self._get_scripts(ms)
        if not self.extraction_script in ms:
            self.extraction_script = '---'

        return ms

    def _get_measurement_scripts(self):
        ms = self._load_script_names('measurement')
        ms = self._get_scripts(ms)
        if not self.measurement_script in ms:
            self.measurement_script = '---'
        return ms

    def _get_post_measurement_scripts(self):
        ms = self._load_script_names('post_measurement')
        ms = self._get_scripts(ms)
#        if not self.post_measurement_script in ms:
#            self.post_measurement_script = '---'
        self.post_measurement_script = 'pump_ms.py'
        return ms

    def _get_post_equilibration_scripts(self):
        ms = self._load_script_names('post_equilibration')
        ms = self._get_scripts(ms)
        if not self.post_equilibration_script in ms:
            self.post_equilibration_script = '---'
        return ms

    @cached_property
    def _get_mass_spectrometers(self):
        db = self.db
        ms = ['---'] + [mi.name for mi in db.get_mass_spectrometers()]
        return ms

    def _get_trays(self):
        ts = ['---'] + [s for s in os.listdir(paths.map_dir)
                if not s.startswith('.') and s.endswith('.txt')]
        return ts

    def _get_heat_devices(self):
        return ['---', 'Fusions CO2', 'Fusions Diode']

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
            if na == '---':
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

    def _automated_run_factory(self, **kw):
        '''
             always use this factory for new AutomatedRuns
             it sets the configuration, loaded scripts and binds our update_loaded_script
             handler so we are aware of scripts that have been tested
        '''

        #copy some of the last runs values
        if self.automated_runs:
            pa = self.automated_runs[-1]
            for k in ['heat_device', 'autocenter']:
                if not k in kw:
                    kw[k] = getattr(pa, k)

        a = AutomatedRun(
                         scripts=self.loaded_scripts,
                         **kw
                         )

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
                                   style='custom'
                                   ),
                              enabled_when='mass_spectrometer and mass_spectrometer!="---"'
                              )

        analysis_table = VGroup(
                                HGroup(
#                                       Item('copy_button'), 
                                       Item('duplicate_button'), show_labels=False),
                                Item('automated_runs', show_label=False,
                                    editor=self._automated_run_editor(),
#                                    height=0.5
                                    ), show_border=True,

                                label='Analyses'
                                )

        heat_schedule_table = Item('heat_schedule', style='custom',
                                   show_label=False,
                                   height=0.35
                                   )

        script_grp = VGroup(
                        Item('extraction_script',
                             label='Extraction',
                             editor=EnumEditor(name='extraction_scripts')),
                        Item('measurement_script',
                             label='Measurement',
                             editor=EnumEditor(name='measurement_scripts')),
                        Item('post_measurement_script',
                             label='Post Measurement',
                             editor=EnumEditor(name='post_measurement_scripts')),
                        Item('post_equilibration_script',
                             label='Post Equilibration',
                             editor=EnumEditor(name='post_equilibration_scripts')),
                        show_border=True,
                        label='Scripts'
                        )

        v = View(
                 HGroup(
                        VGroup(VGroup(
                                      Item('mass_spectrometer',
                                           editor=EnumEditor(name='mass_spectrometers'),
#                                           show_label=False
                                           ),
                                      Item('heat_device',
                                           editor=EnumEditor(name='heat_devices'),
#                                           show_label=False,
                                           ),
                                      Item('tray',
                                           editor=EnumEditor(name='trays'),
#                                           show_label=False,
                                           )
                                      ),
                               new_analysis,
                               script_grp,
                               HGroup(Item('auto_increment'),
                                     spring,
                                     Item('add', show_label=False, enabled_when='ok_to_add'),
                                     ),
                               ),

                         VGroup(
                                 heat_schedule_table,
                                 HGroup(spring, Item('apply', enabled_when='ok_to_add'),
                                        show_labels=False),
                                analysis_table,
        #                        stats
                                ),
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


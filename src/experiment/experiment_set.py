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
from traits.api import  List, Instance, Str, Button, Any, \
    Bool, Property, Float, on_trait_change, cached_property, \
    Event
from traitsui.api import View, Item, VGroup, HGroup, spring, \
    EnumEditor
#============= standard library imports ========================
import os
import yaml
#============= local library imports  ==========================
from src.experiment.automated_run import AutomatedRun
from src.experiment.extract_schedule import ExtractSchedule
from src.paths import paths
from src.experiment.batch_edit import BatchEdit
from src.experiment.stats import ExperimentStats
from src.experiment.automated_run_tabular_adapter import AutomatedRunAdapter
from src.traits_editors.tabular_editor import myTabularEditor
from src.experiment.identifier import convert_identifier, convert_labnumber
from src.constants import NULL_STR, SCRIPT_KEYS
from src.experiment.blocks.base_schedule import BaseSchedule
from src.experiment.blocks.block import Block


class ExperimentSet(BaseSchedule):
    current_run = Instance(AutomatedRun)
    selected_runs = List(AutomatedRun)
    extract_schedule = Instance(ExtractSchedule, ())
    stats = Instance(ExperimentStats, ())

    sample_map = Any
    db = Any

    measuring = Property(depends_on='current_run.measuring')

    delay_between_analyses = Float(1)
    delay_before_analyses = Float(1)
    name = Property(depends_on='path')
    path = Str
    ok_to_add = Property
    _ok_to_add = Bool(False)

    dirty = Bool(False)

    executable = Bool(True)
    auto_increment = Bool(True)
    update_aliquots_needed = Event

    mass_spectrometer = Str('obama')
#    mass_spectrometer = Str(NULL_STR)
    mass_spectrometers = Property
#    tray = Str(NULL_STR)
    trays = Property
    extract_device = Str('Fusions CO2')
#    extract_device = Str(NULL_STR)
    extract_devices = Property

    right_clicked = Any
    dclicked = Any

    _cached_runs = None
    _alive = False

    _current_group_id = 0
    _warned_labnumbers = List

    schedule_block = Str(NULL_STR)
    schedule_blocks = Property(depends_on='schedule_block_added')
    schedule_block_added = Event
    edit_schedule_block = Button('Edit')
    new_schedule_block = Button('New')
#===============================================================================
# persistence
#===============================================================================
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
# execution
#===============================================================================
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

#===============================================================================
# load runs
#===============================================================================
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
        if meta is None:
            self.warning_dialog('Invalid experiment set file. Poorly formatted metadata {}'.format(metastr))

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

        self._set_meta_param('tray', meta, default)
        self._set_meta_param('extract_device', meta, default)
        self._set_meta_param('mass_spectrometer', meta, default)
        self._set_meta_param('delay_between_analyses', meta, default_int)
        self._set_meta_param('delay_before_analyses', meta, default_int)

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
                params['db'] = self.db
                params['tray'] = self.tray
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
                ni = names[name]
                if ni != NULL_STR:
                    na = self._add_mass_spectromter_name(ni)

            if na and not na.endswith('.py'):
                na = na + '.py'

            return na

        cextract_group = None
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

                make_script_name = lambda x: _make_script_name(_meta, ln, x)
                params = dict()
                params['labnumber'] = '{}'.format(ln)
                params['configuration'] = self._build_configuration(make_script_name)

                if isinstance(freq, int):
                    freq = [freq]

                for fi in freq:
                    arun = self._automated_run_factory(**params)
                    if isinstance(fi, int):
                        if i % freq == 0:
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
                                if nruns[-2].labnumber != ln:
                                    nruns.insert(-1, arun)
                            else:
                                nruns.insert(-1, arun)
                        elif fi.lower() == 'after':
                            nruns.append(arun)

        return nruns

    def _dclicked_changed(self):
        self._right_clicked_changed()

    def _right_clicked_changed(self):
#        self.debug('Right click currently disabled')
#        return

        selected = self.selected
        if selected:
            selected = selected[0]

            if selected.state == 'success':
                #recall the analysis and display

                db = self.db
                print selected.uuid
#                dbrecord = db.get_analysis_uuid(selected.uuid)
                db.selector.open_record(selected.uuid)

    def _batch_edit(self, selected):
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

    def save_to_db(self):
        self.info('saving experiment {} to database'.format(self.name))
        db = self.db
        db.add_experiment(self.name)
        db.commit()

    def _auto_increment(self, m):

        try:
            m = str(int(m) + 1)
        except ValueError:
            pass

        return m

    def _block_factory(self, name=None):
        s = Block(mass_spectrometer=self.mass_spectrometer,
                  extract_device=self.extract_device
                  )

        if name is not None:
            s.load(os.path.join(paths.block_dir, name))

        return s

#===============================================================================
# handlers
#===============================================================================
    def _new_schedule_block_fired(self):
        b = self._block_factory()
        info = b.edit_traits(kind='livemodal')
        if info.result:
            self.schedule_block = b.name
            self.schedule_block_added = True

    def _edit_schedule_block_fired(self):
        b = self._block_factory(name=self.schedule_block)
        info = b.edit_traits(kind='livemodal')

    def _add_fired(self):

        ars = self.automated_runs
        ar = self.automated_run
        if self.schedule_block and self.schedule_block != NULL_STR:
#            print self.schedule_block
            block = self._block_factory(self.schedule_block)
            nruns = block.render(ar, self._current_group_id)
            ars.extend(nruns)
            self._current_group_id += 1

        else:
#            rid = self._auto_increment(ar.labnumber)
#            position = None
#            if ar.position:
#                position = self._auto_increment(ar.position)

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
            rid = self._auto_increment(ar.labnumber)
            npos = self._auto_increment(ar.position)
            if rid:
                kw['labnumber'] = rid
            if npos:
                kw['position'] = npos

        self.automated_run = ar.clone_traits()
        #if analysis type is bg, b- or a overwrite a few defaults
        if not ar.analysis_type == 'unknown':
            kw['position'] = 0
            kw['extract_value'] = 0

        self.automated_run.trait_set(**kw)
        self._bind_automated_run(self.automated_run)

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

    def _update_run_script(self, run, sname):
        if run.state == 'not run':
            ssname = '{}_script'.format(sname)
            name = getattr(self, ssname)
            name = self._add_mass_spectromter_name(name)
            if run.configuration:
                run.configuration[ssname] = os.path.join(paths.scripts_dir,
                                                            sname,
                                                            name
                                                            )
                setattr(run, '{}_script_dirty'.format(sname), True)

    @on_trait_change('current_run,automated_runs[]')
    def _update_stats(self, obj, name, old, new):
        if self.automated_runs:
            self.dirty = True
        else:
            self.dirty = False

#    @on_trait_change('automated_runs:dirty')
#    def _update_dirty(self, dirty):
#        if dirty:
#            self.dirty = dirty

    @on_trait_change('automated_run:labnumber')
    def _update_labnumber(self, labnumber):

        arun = self.automated_run
        #check for id in labtable
        self._ok_to_add = False
        db = self.db

        arun.sample = ''
        arun.aliquot = 1
        arun.irrad_level = ''

        if labnumber:
            if isinstance(convert_identifier(labnumber), int):
                self._ok_to_add = True
                arun.sample = convert_labnumber(convert_identifier(labnumber))
                self._load_default_scripts()
                return

            ln = db.get_labnumber(labnumber)
            if ln:
                self._ok_to_add = True
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
#                self._ok_to_add = True
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
            run = new[0]
            if run.state == 'not run':
                self.automated_run = run.clone_traits()

                for si in SCRIPT_KEYS:
                    try:
                        n = self._clean_script_name(getattr(run, '{}_script'.format(si)).name)
                        setattr(self, '{}_script'.format(si), n)
                    except AttributeError:
                        pass

#===============================================================================
# property get/set
#===============================================================================
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

    def set_script_names(self):
        arun = self.automated_run

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

    def _list_dir(self, d, condition=None):
        if condition is None:
            condition = lambda x: True

        return [s for s in os.listdir(d) if not s.startswith('.') and condition(s)]

    @cached_property
    def _get_mass_spectrometers(self):
        db = self.db
        ms = [NULL_STR] + [mi.name for mi in db.get_mass_spectrometers()]
        return ms

    def _get_trays(self):
        condition = lambda x: x.endswith('.txt')
        ts = [NULL_STR] + self._list_dir(paths.map_dir, condition)
#        ts = [NULL_STR] + [s for s in os.listdir(paths.map_dir)
#                if not s.startswith('.') and s.endswith('.txt')]
        return ts

    def _get_extract_devices(self):
        return [NULL_STR, 'Fusions CO2', 'Fusions Diode']

    @cached_property
    def _get_schedule_blocks(self):
        return [NULL_STR] + self._list_dir(os.path.join(paths.block_dir),
                                           )
    def _get_ok_to_add(self):
        b = False
        if self.schedule_block != NULL_STR:
            if not Block.is_template(self.schedule_block):
                b = True

        return self._ok_to_add or b

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

        configuration = self._build_configuration(make_script_name)

        arun = self.automated_run
        if arun and copy_automated_run:
            params.update(dict(
                               labnumber=arun.labnumber,
                               position=arun.position,
                               aliquot=arun.aliquot))

        params['configuration'] = configuration
        params['db'] = self.db
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
                            operations=['delete',
                                        'move',
                                        'edit'],
#                            editable=False,
                             auto_resize=True,
                             multi_select=True,
                             auto_update=True,
                             scroll_to_bottom=False
                            )
        self.tabular_editor = r
        return r

    def _get_global_parameters_group(self):
        gparams_grp = VGroup(
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
                   ),
              Item('delay_between_analyses', label='Delay between Analyses (s)')
              )
        return gparams_grp

    def traits_view(self):
        new_analysis = VGroup(
                              Item('automated_run',
                                   show_label=False,
                                   style='custom',
                                   ),
                              enabled_when='mass_spectrometer and mass_spectrometer!="---"'
                              )

        analysis_table = VGroup(
                                self._get_copy_paste_group(),
                                Item('automated_runs', show_label=False,
                                    editor=self._automated_run_editor(),
                                    height=0.75,
#                                    width=400,
                                    ), show_border=True,

                                label='Analyses'
                                )

        script_grp = self._get_script_group()
        gparams_grp = self._get_global_parameters_group()
        block_grp = HGroup(Item('schedule_block',
                                label='Block',
                                editor=EnumEditor(name='schedule_blocks')),
                          Item('edit_schedule_block',
                               enabled_when='object.schedule_block!="---"',
                                show_label=False),
                          Item('new_schedule_block', show_label=False)
                          )
        v = View(
                 HGroup(
                        VGroup(
                               gparams_grp,
                               block_grp,
                               new_analysis,
                               script_grp,
                               HGroup(Item('auto_increment'),
                                     spring,
                                     Item('add', show_label=False,
                                          enabled_when='ok_to_add'),
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


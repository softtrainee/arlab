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
from src.experiment.stats import ExperimentStats
# from src.experiment.automated_run_tabular_adapter import AutomatedRunAdapter
# from src.traits_editors.tabular_editor import myTabularEditor
from src.experiment.identifier import convert_identifier
from src.constants import NULL_STR, SCRIPT_KEYS
from src.experiment.blocks.base_schedule import BaseSchedule
from src.experiment.blocks.parser import RunParser, UVRunParser
from src.experiment.blocks.block import Block
from src.experiment.runs_table import RunsTable


class ExperimentSet(BaseSchedule):
    current_run = Instance(AutomatedRun)
    extract_schedule = Instance(ExtractSchedule, ())
    stats = Instance(ExperimentStats, ())
    cleaned_automated_runs = Property(depends_on='automated_runs[]')

    sample_map = Any
    db = Any

    measuring = Property(depends_on='current_run.measuring')

    delay_between_analyses = Float(25)
    delay_before_analyses = Float(5)
    name = Property(depends_on='path')
    path = Str
    ok_to_add = Property(depends_on='_ok_to_add')
    _ok_to_add = Bool(False)

    dirty = Bool(False)

    executable = Bool(True)
    auto_increment = Bool(False)

#    mass_spectrometer = Str('jan')
    mass_spectrometer = Str(NULL_STR)
    mass_spectrometers = Property
#    tray = Str(NULL_STR)
    trays = Property
#    extract_device = Str('Fusions Diode')
    extract_device = Str(NULL_STR)
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
    def test(self):
        for ai in self.automated_runs:
            if not ai.test():
                return
        return True

    def automated_run_factory(self, copy_automated_run=False, **params):
        arun = self.automated_run
        if arun and copy_automated_run:
            params.update(dict(
                               labnumber=arun.labnumber,
                               position=arun.position,
                               aliquot=arun.aliquot))

        params['db'] = self.db
        params['mass_spectrometer'] = self.mass_spectrometer
        return self._automated_run_factory({}, params)

    def save_to_db(self):
        self.info('saving experiment {} to database'.format(self.name))
        db = self.db
        db.add_experiment(self.name)
        db.commit()

    def set_script_names(self):
        arun = self.automated_run

        def get_name(si):
            scriptname = getattr(arun.script_info, '{}_script_name'.format(si))
            if scriptname:
                name = self._clean_script_name(scriptname)
                script = getattr(self, '{}_script'.format(si))
                if not name in script.names:
                    name = NULL_STR
            else:
                name = NULL_STR

            return name

        traits = dict([('{}_script'.format(k), get_name(k)) for k in SCRIPT_KEYS])
        self.trait_set(**traits)

#===============================================================================
# execution
#===============================================================================
    def truncate_run(self, style):
        self.current_run.truncate(style)

    def new_runs_generator(self, last_ran=None):
#        runs = [ai for ai in self.automated_runs if ai.executable and not ai.skip]
        runs = [ai for ai in self.cleaned_automated_runs]

        n = len(runs)
        rgen = (r for r in runs)
        if last_ran is not None:
            # get index of last run in self.automated_runs
#            startid = next((i for i, r in enumerate(runs) if r.runid == last_ran.runid), None)
#            if startid is not None:
            if self._cached_runs:
                startid = self._cached_runs.index(last_ran) + 1
                # for graphic clarity load the finished runs back in
                cached = self._cached_runs[:startid]

                cnts = {}
                for ai in self.automated_runs:
                    if ai.skip:
                        continue
                    crun = next((r for r in cached if r.labnumber == ai.labnumber and ai.aliquot == 0), None)
                    if crun is not None:
                        ai.state = crun.state
                        cnt = 0
                        if ai.labnumber in cnts:
                            cnt = cnts[ai.labnumber] + 1

                        ai.aliquot = crun.aliquot + cnt
                        cnts[ai.labnumber] = cnt
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
            self.executable = any([ai.executable for ai in aruns])
            self.automated_runs = aruns

            lm = self.sample_map
            if lm:
                for ai in self.automated_runs:
                    if ai.position:
                        lm.set_hole_labnumber(ai)

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
        # read until break
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

                script_info, params = self.parse_line(header, line, meta)
                params['mass_spectrometer'] = self.mass_spectrometer
                params['extract_device'] = self.extract_device
                params['db'] = self.db
                params['tray'] = self.tray

                arun = self._automated_run_factory(script_info, params)
                aruns.append(arun)

            except Exception, e:
                import traceback
                print traceback.print_exc()
                self.warning_dialog('Invalid Experiment file {}\nlinenum= {}\nline= {}'.format(e, linenum, line))

                return

#        aruns = self._add_frequency_runs(meta, aruns)
        return aruns

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
# handlers
#===============================================================================
    def _new_schedule_block_fired(self):
        b = self._block_factory()
        info = b.edit_traits(kind='livemodal')
        if info.result:
            if b.name:
                self.schedule_block = b.name
                self.schedule_block_added = True

    def _edit_schedule_block_fired(self):
        b = self._block_factory(name=self.schedule_block)
        b.edit_traits(kind='livemodal')

    def _add_fired(self):


        ars = self.automated_runs
        ar = self.automated_run
        nar = ar.clone_traits()

        # labnumber is a property so its not cloned by clone_traits
        nar.labnumber = ar.labnumber
        nar.position=ar.position
#        nar.aliquot=ar.aliquot

        if ar.analysis_type.startswith('blank') or ar.analysis_type == 'background':
            nar.extract_value = 0
            nar.extract_units = ''

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

#            if not self._add_new_run(ar):
#                return
#            else:
            if self.selected:
                ind = self.automated_runs.index(self.selected[-1])
                ars.insert(ind + 1, nar)
            else:
                ars.append(nar)

        kw = dict()
        if self.auto_increment:
            rid = self._auto_increment(ar.labnumber)
            npos = self._auto_increment(ar.position)
            if rid:
                kw['labnumber'] = rid
            if npos:
                kw['position'] = npos
#        else:
#            self._ok_to_add = False

        self._add_hook(ar, **kw)
        self.update_aliquots_needed = True

    @on_trait_change('current_run,automated_runs[]')
    def _update_stats(self, obj, name, old, new):
        if self.automated_runs:
            self.dirty = True
        else:
            self.dirty = False

#    @on_trait_change('automated_runs:')
#    def _update_skip(self):
#        self.update_aliquots_needed = True

    @on_trait_change('automated_run:labnumber')
    def _update_labnumber(self, labnumber):

        arun = self.automated_run
        # check for id in labtable
        self._ok_to_add = False
        db = self.db

        arun.run_info.sample = ''
        arun.aliquot = 1
        arun.irrad_level = ''
        if labnumber:

            # convert labnumber (a, bg, or 10034 etc)
            labnumber = convert_identifier(labnumber)
#            if isinstance(convert_identifier(labnumber), int):
#                self._ok_to_add = True
# #                arun.sample = convert_labnumber(convert_identifier(labnumber))
#                self._load_default_scripts()
#                return

            ln = db.get_labnumber(labnumber)
            if ln:
                self._ok_to_add = True
                # set sample and irrad info
                try:
                    arun.run_info.sample = ln.sample.name
                except AttributeError:
                    pass

                arun.run_info.irrad_level = self._make_irrad_level(ln)

                # set default scripts
                self._load_default_scripts()
            else:
                self.warning_dialog('{} does not exist. Add using "Labnumber Entry" or "Utilities>>Import"'.format(labnumber))

    def _make_irrad_level(self, ln):
        il = ''
        ipos = ln.irradiation_position
        if not ipos is None:
            level = ipos.level
            irrad = level.irradiation
            il = '{}{}'.format(irrad.name, level.name)
        return il

    def _mass_spectrometer_changed(self):
        if self.automated_run is None:
            return

        for ai in self.automated_runs:
            ai.mass_spectrometer = self.mass_spectrometer

        if self.automated_run.labnumber:
            self._load_default_scripts()
        else:
            self.clear_script_names()

        self.set_scripts_mass_spectrometer()

    def _extract_device_changed(self):

        if self.extract_device != NULL_STR:

            runs = self.automated_runs
            self.runs_table = RunsTable(extract_device=self.extract_device)
            self.runs_table.set_runs(runs)

            self.automated_run = self.automated_run_factory(copy_automated_run=False)

            if self.mass_spectrometer:
                self._load_default_scripts()

#        self.automated_run.mass_spectrometer = self.mass_spectrometer

#    def _selected_changed(self, new):
# #        print new
#        self.selected_runs = new
#        if len(new) == 1:
#            run = new[0]
#            if run.state == 'not run':
#                self.automated_run = run.clone_traits()
#                for si in SCRIPT_KEYS:
#                    try:
#                        n = self._clean_script_name(getattr(run, '{}_script'.format(si)).name)
#                        setattr(self, '{}_script'.format(si), n)
#                    except AttributeError:
#                        pass
#
#    @on_trait_change('''automated_run:[_position, extract_+, cleanup,
#    duration, autocenter, overlap, ramp_rate, weight, comment, pattern]''')
#    def _sync_selected_runs(self, name, new):
#        if self.selected_runs:
#            for si in self.selected_runs:
#                si.trait_set(**{name:new})

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
        return [NULL_STR, 'Fusions CO2', 'Fusions Diode', 'Fusions UV']

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

    def _get_cleaned_automated_runs(self):
        return [ci for ci in self.automated_runs if not ci.skip]

#===============================================================================
# factories
#===============================================================================

    def _automated_run_factory(self, script_params, params):
        '''
             always use this factory for new AutomatedRuns
             it sets the configuration, loaded scripts and binds our update_loaded_script
             handler so we are aware of scripts that have been tested
        '''
        # copy some of the last runs values
        if self.automated_runs:
            pa = self.automated_runs[-1]
            for k in ['extract_device', 'autocenter']:
                if not k in params:
                    params[k] = getattr(pa, k)

        if self.extract_device == 'Fusions UV':
            from src.experiment.uv_automated_run import UVAutomatedRun
            klass = UVAutomatedRun
        else:
            klass = AutomatedRun

        a = klass(scripts=self.loaded_scripts,
                  application=self.application,
                  **params)

        for k, v in script_params.iteritems():
            setattr(a.script_info, '{}_script_name'.format(k), v)


#        a = klass(scripts=self.loaded_scripts,
#                  labnumber=labnumber if labnumber else '',
#                  **kw)
        if 'labnumber' in params:
            labnumber = params['labnumber']
        else:
            labnumber = ''

        if labnumber:
            ln = self.db.get_labnumber(labnumber)

            if ln is None:
                # check to see if we have already warned for this labnumber
                if not labnumber in self._warned_labnumbers:
                    self.warning_dialog('Invalid labnumber {}. Add it using "Labnumber Entry" or "Utilities>>Impprt"'.format(labnumber))
                    self._warned_labnumbers.append(labnumber)
                a._executable = False
            else:
                a.run_info.sample = ln.sample.name
                a.run_info.irrad_level = self._make_irrad_level(ln)
#            else:
#                self._bind_automated_run(a)
#                a.create_scripts()
#        else:
        self._bind_automated_run(a)
#            a.create_scripts()

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
    def _get_global_parameters_group(self):
        gparams_grp = VGroup(
              Item('mass_spectrometer',
                   editor=EnumEditor(name='mass_spectrometers'),
                   tooltip='Select a mass spectrometer for this set'
                   ),
              Item('extract_device',
                   editor=EnumEditor(name='extract_devices'),
                   tooltip='Select an extraction device for this set'
                   ),
              Item('tray',
                   editor=EnumEditor(name='trays'),
                   tooltip='Select an sample tray for this set'
                   ),
              Item('delay_between_analyses',
                   tooltip='Set the delay between analysis in seconds',
                   label='Delay between Analyses (s)')
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
                                Item('runs_table', show_label=False, style='custom'),
                                show_border=True,
                                label='Analyses',
                                )

        script_grp = self._get_script_group()
        gparams_grp = self._get_global_parameters_group()
        block_grp = HGroup(Item('schedule_block',
                                label='Block',
                                editor=EnumEditor(name='schedule_blocks')),
                          Item('edit_schedule_block',
                               enabled_when='object.schedule_block!="---"',
                                show_label=False),
                          Item('new_schedule_block', show_label=False),
                          enabled_when='mass_spectrometer and mass_spectrometer!="---"'
                          )
        v = View(
                 HGroup(
                        VGroup(
                               gparams_grp,
#                               block_grp,
                               new_analysis,
                               script_grp,
                               HGroup(Item('auto_increment'),
                                     spring,
                                     Item('add', show_label=False,
                                          enabled_when='ok_to_add'),
                                     ),
                               ),
                        analysis_table

#                        VGroup(
#                               schedule_grp,
#                               analysis_table
#                               )

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
#    def _add_frequency_runs(self, meta, runs):
#        nruns = []
#        i = 0
#
#        names = dict()
#        setter = lambda sk, sc:names.__setitem__(sk, sc)
#        def _make_script_name(_meta, li, name):
#            na = _meta['scripts'][name]
#            if na is None:
#                na = ''
#            elif na.startswith('_'):
#                na = meta['mass_spectrometer'] + na
#
#            if not na:
#                self._load_default_scripts(setter=setter, key=li)
#                ni = names[name]
#                if ni != NULL_STR:
#                    na = self._add_mass_spectromter_name(ni)
#
#            if na and not na.endswith('.py'):
#                na = na + '.py'
#
#            return na
#
#        cextract_group = None
#        for ai in runs:
#            nruns.append(ai)
#            try:
#                int(ai.labnumber)
#                i += 1
#            except ValueError:
#                continue
#
#            for name, ln in [('blanks', 'Bu'), ('airs', 'A'), ('cocktails', 'C'), ('backgrounds', 'Bg')]:
#                try:
#                    _meta = meta[name]
#                    freq = _meta['frequency']
#                    if not freq:
#                        continue
#                except KeyError:
#                    continue
#
#                make_script_name = lambda x: _make_script_name(_meta, ln, x)
#                params = dict()
#                params['labnumber'] = '{}'.format(ln)
#                params['configuration'] = self._build_configuration(make_script_name)
#
#                if isinstance(freq, int):
#                    freq = [freq]
#
#                for fi in freq:
#                    arun = self._automated_run_factory(**params)
#                    if isinstance(fi, int):
#                        if i % freq == 0:
#                            nruns.append(arun)
#                    else:
#                        if ai.extract_group:
#                            if cextract_group == ai.extract_group:
#                                # if this is the last run dont continue
#                                if ai != runs[-1]:
#                                    continue
#                            else:
#                                cextract_group = ai.extract_group
#
#                        if fi.lower() == 'before' and ai != runs[-1]:
#                            if len(nruns) >= 2:
#                                if nruns[-2].labnumber != ln:
#                                    nruns.insert(-1, arun)
#                            else:
#                                nruns.insert(-1, arun)
#                        elif fi.lower() == 'after':
#                            nruns.append(arun)
#
#        return nruns
# def _automated_run_editor(self, update=''):
#        r = myTabularEditor(adapter=AutomatedRunAdapter(),
#                            operations=['delete',
#                                        'move',
#                                        'edit'],
# #                            editable=False,
# #                             auto_resize=True,
#                             multi_select=True,
# #                             auto_update=True,
#                             scroll_to_bottom=False
#                            )
#        return r
#    def _dclicked_changed(self):
#        self._right_clicked_changed()
#
#    def _right_clicked_changed(self):
# #        self.debug('Right click currently disabled')
# #        return
#
#        selected = self.selected
#        if selected:
#            selected = selected[0]
#
#            if selected.state == 'success':
#                #recall the analysis and display
#
#                db = self.db
#                db.selector.open_record(selected.uuid)
#

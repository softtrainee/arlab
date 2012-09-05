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
    Bool, Property, Float, Int, on_trait_change, Dict, String, cached_property
from traitsui.api import View, Item, TabularEditor, VGroup, HGroup, spring, \
    EnumEditor
#============= standard library imports ========================
import os
#import time
#import datetime
#============= local library imports  ==========================
from src.experiment.automated_run import AutomatedRun, AutomatedRunAdapter
from src.experiment.heat_schedule import HeatSchedule
from src.paths import paths
from src.loggable import Loggable
from src.experiment.batch_edit import BatchEdit
from src.experiment.stats import ExperimentStats
from src.helpers.filetools import str_to_bool


def extraction_path(name):
    return os.path.join(paths.scripts_dir, 'extraction', name)

def measurement_path(name):
    return os.path.join(paths.scripts_dir, 'measurement', name)


class ExperimentSet(Loggable):
    automated_runs = List(AutomatedRun)
    automated_run = Instance(AutomatedRun)
    current_run = Instance(AutomatedRun)
    heat_schedule = Instance(HeatSchedule, ())
    db = Any

    ok_to_add = Bool(False)
    apply = Button
    add = Button

    name = Property(depends_on='path')
    path = Str
    stats = Instance(ExperimentStats, ())

    loaded_scripts = Dict

    measurement_script = String
    measurement_scripts = Property#(depends_on='_measurement_scripts')
#    _measurement_scripts = List

    extraction_script = String
    extraction_scripts = Property#(depends_on='_extraction_scripts')
#    _extraction_scripts = List

    delay_between_runs = Float(1)

    dirty = Property(depends_on='_dirty,path')
    _dirty = Bool(False)

    selected = Any
    right_clicked = Any

    executable = Bool(True)

    def _run_parser(self, header, line, delim='\t'):
        params = dict()
        args = map(str.strip, line.split(delim))


        #load strings
        for attr in ['identifier', 'measurement', 'extraction', 'heat_device']:
            params[attr] = args[header.index(attr)]

        #load booleans
        for attr in ['autocenter']:
            param = args[header.index(attr)]
            if param.strip():
                params[attr] = str_to_bool(param)

        #load numbers
        for attr in ['duration', 'temp_or_power', 'position']:
            param = args[header.index(attr)].strip()
            if param:
                params[attr] = float(param)

        extraction = args[header.index('extraction')]
        measurement = args[header.index('measurement')]

        params['configuration'] = self._build_configuration(extraction, measurement)
        return params

    def load_automated_runs(self):
        with open(self.path, 'rb') as f:
            #read meta
            #read until break
            for line in f:
                if line.startswith('#====='):
                    break

            delim = '\t'
            header = map(str.strip, f.next().split(delim))
            self.executable = True
            for line in f:
                if line.startswith('#'):
                    continue
#                args = map(str.strip, ai.split(delim))
#                identifier = args[header.index('identifier')]

#                extraction = args[header.index('extraction')]
#                measurement = args[header.index('measurement')]

#                hd = args[header.index('heat_device')]
#                autocenter = str_to_bool(args[header.index('autocenter')])

#                position = int(args[header.index('position')])

                params = self._run_parser(header, line)
                arun = self._automated_run_factory(**params)
                self.automated_runs.append(arun)

#                arun.extraction_script
#                arun.measurement_script

                if not arun.executable:
                    self.executable = False
                    print self.executable

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

                           power=selected.temp_or_power,
                           orig_power=selected.temp_or_power,

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

    def _build_configuration(self, extraction, measurement):
        c = dict(extraction_script=extraction_path(extraction),
                  measurement_script=measurement_path(measurement)
                  )
        return c

    def save_to_db(self):
        db = self.db
        db.add_experiment(self.name)
        db.commit()

    def update_loaded_scripts(self, new):
        if new:
            self.loaded_scripts[new.name] = new

    def reset_stats(self):
        self.stats.start_timer()

    def stop_stats_timer(self):
        self.stats.stop_timer()

    def _auto_increment_runid(self, rid):

        try:
            rid = str(int(rid) + 1)
        except ValueError:
            pass

        return rid

#===============================================================================
# handlers
#===============================================================================
    def _add_fired(self):
        ars = self.automated_runs
        ar = self.automated_run

        rid = self._auto_increment_runid(ar.identifier)

        ars.append(ar)
        self.automated_run = self._automated_run_factory(self.extraction_script,
                                                         self.measurement_script,
                                                         identifier=rid,
                                                         )


    @on_trait_change('automated_runs[]')
    def _automated_runs_changed(self, obj, name, old, new):
        print  old, new
        if old:
            old = old[0]

            if self.automated_run:
                if old.identifier == self.automated_run.identifier:
                    self.automated_run.aliquot -= 1

            fo = dict()
            pi = None

            for ai in self.automated_runs:
                try:
                    pi = fo[ai.identifier]
                    if ai.aliquot != pi + 1:
                        ai.aliquot -= 1
                except KeyError:
                    pass

                fo[ai.identifier] = ai.aliquot

    def _apply_fired(self):
        for i, s in enumerate(self.heat_schedule.steps):
            a = self.automated_run_factory(temp_or_power=s.temp_or_power,
                                         duration=s.duration,
                                         )
            a.aliquot += i
            self.automated_runs.append(a)

        self.automated_run.aliquot = a.aliquot + 1



    def _extraction_script_changed(self):
        print self.extraction_script
        self.automated_run.configuration['extraction_script'] = os.path.join(paths.scripts_dir,
                                                        'extraction',
                                                        self.extraction_script)

    def _measurement_script_changed(self):
        print self.measurement_script
        self.automated_run.configuration['measurement_script'] = os.path.join(paths.scripts_dir,
                                                        'measurement',
                                                        self.measurement_script)

    @on_trait_change('current_run,automated_runs[]')
    def _update_stats(self, obj, name, old, new):
        self.dirty = True
        #updated the experiments stats
        if name == 'current_run':
            if not new is self.automated_runs[0]:
                #skip the first update 
                self.stats.nruns_finished += 1

        elif name == 'automated_runs_items':
            self.stats.calculate_etf(self.automated_runs)

    @on_trait_change('automated_run.identifier')
    def _update_identifier(self, identifier):
        arun = self.automated_run
        #check for id in labtable
        self.ok_to_add = False
        db = self.db

        arun.sample = ''
        arun.aliquot = 1
        arun.irrad_level = ''

        if identifier:
            oidentifier = identifier
            if identifier == 'B':
                identifier = 1
            elif identifier == 'A':
                identifier = 2

            ln = db.get_labnumber(identifier)
            if ln:
                arun.sample = ln.sample.name

                noccurrences = len([ai for ai in self.automated_runs
                                  if ai.identifier == oidentifier
                                  ])
                arun.aliquot = ln.aliquot + noccurrences + 1

                ipos = ln.irradiation_position
                irrad = ipos.irradiation
                arun.irrad_level = '{}{}'.format(irrad.name, irrad.level)

                self.ok_to_add = True

#===============================================================================
# property get/set
#===============================================================================
    def _set_dirty(self, d):
        self._dirty = d

    def _get_dirty(self):
        return self._dirty and os.path.isfile(self.path)

    def _get_name(self):
        if self.path:
            return os.path.splitext(os.path.basename(self.path))[0]
        else:
            return 'New ExperimentSet'

    @cached_property
    def _get_extraction_scripts(self):
        es = self._load_script_names('extraction')
        if es:
            self.extraction_script = es[0]
        return es

    @cached_property
    def _get_measurement_scripts(self):
        ms = self._load_script_names('measurement')
        if ms:
            self.measurement_script = ms[0]
        return ms
#===============================================================================
# factories
#===============================================================================
    def automated_run_factory(self, **kw):
        extraction = self.extraction_script
        measurement = self.measurement_script

        configuration = self._build_configuration(extraction, measurement)

        params = dict()
        arun = self.automated_run
        if arun:
            params = dict(
                          identifier=arun.identifier,
                          position=arun.position,
                          aliquot=arun.aliquot)

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
                kw[k] = getattr(pa, k)

        a = AutomatedRun(
                         executable=True,
                         scripts=self.loaded_scripts,
                         **kw
                         )
        self._bind_automated_run(a)
        return a

    def _bind_automated_run(self, a):
        a.on_trait_change(self.update_loaded_scripts, '_measurement_script')
        a.on_trait_change(self.update_loaded_scripts, '_extraction_script')

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
        return TabularEditor(adapter=AutomatedRunAdapter(),
                             update=update,
                             right_clicked='object.right_clicked',
                             selected='object.selected',
                             multi_select=True,
                             auto_update=True
                                )
    def traits_view(self):
        new_analysis = VGroup(
                              Item('automated_run',
                                   show_label=False,
                                   style='custom'
                                   ),
                              HGroup(
                                     spring,
                                     Item('add', show_label=False, enabled_when='ok_to_add'),
                                     )
                              )


        analysis_table = VGroup(Item('automated_runs', show_label=False,
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
                        show_border=True,
                        label='Scripts'
                        )

        v = View(
                 HGroup(
                        VGroup(new_analysis,
                               script_grp
                               ),

                 VGroup(
                         heat_schedule_table,
                         HGroup(spring, Item('apply', enabled_when='ok_to_add'),
                                show_labels=False),
                        analysis_table,
#                        stats
                        ),
                 ))

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
#============= EOF =============================================


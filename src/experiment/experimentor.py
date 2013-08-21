#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import Instance, List, on_trait_change, Bool, Event
# from traitsui.api import View, Item
# from src.loggable import Loggable
#============= standard library imports ========================
from itertools import groupby
#============= local library imports  ==========================
# from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.experiment.queue.experiment_queue import ExperimentQueue

from src.experiment.factory import ExperimentFactory
from src.constants import ALPHAS, NULL_STR
from src.experiment.stats import StatsGroup
from src.experiment.executor import ExperimentExecutor
from src.experiment.utilities.file_listener import FileListener
from src.experiment.utilities.identifier import convert_identifier, \
    ANALYSIS_MAPPING
from src.deprecate import deprecated
from src.experiment.isotope_database_manager import IsotopeDatabaseManager
LAlphas = list(ALPHAS)

from itertools import tee

def partition(seq, predicate):
    '''
        http://stackoverflow.com/questions/949098/python-split-a-list-based-on-a-condition
        partition seqeunce based on evaluation of predicate(i)
        
        returns 2 generators
        True_eval, False_eval
    '''

    l1, l2 = tee((predicate(item), item) for item in seq)
    return (i for p, i in l1 if p), (i for p, i in l2 if not p)

# class Experimentor(Experimentable):
class Experimentor(IsotopeDatabaseManager):
    experiment_factory = Instance(ExperimentFactory)
    experiment_queue = Instance(ExperimentQueue)
    executor = Instance(ExperimentExecutor)
    experiment_queues = List
    stats = Instance(StatsGroup, ())

    mode = None
    unique_executor_db = True

    save_enabled = Bool

    #===========================================================================
    # permissions
    #===========================================================================
#    max_allowable_runs = 10000
#    can_edit_scripts = True
#    _last_ver_time = None
#    _ver_timeout = 10

    #===========================================================================
    # task events
    #===========================================================================
    execute_event = Event

    activate_editor_event = Event
    save_event = Event
#    clear_display_event = Event
    def reset_run_generator(self):
        if self.executor.isAlive():
            self.debug('Queue modified. Reset run generator')
#             self.executor.queue_modified = True
            self.executor.reset_queue()

    def refresh_executable(self, qs=None):
        if qs is None:
            qs = self.experiment_queues
        self.executor.executable = all([ei.isExecutable() for ei in qs])

    def update_queues(self):
        self._update_queues()

#     def test_queues(self, qs=None):
#         if qs is None:
#             qs = self.experiment_queues
#
#         self.refresh_executable(qs)

    def test_connections(self):
        if not self.db:
            return

        if not self.db.connect():
            self.warning_dialog('Failed connecting to database. {}'.format(self.db.url))
            return

        return True

    @deprecated
    def start_file_listener(self, path):
        fl = FileListener(
                          path,
                          callback=self._reload_from_disk,
                          check=self._check_for_file_mods
                          )
        self.filelistener = fl

    @deprecated
    def stop_file_listener(self):
        if self.filelistener:
            self.filelistener.stop()

    def update_info(self, reset_db=False):
        if reset_db:
            self.db.reset()

        self._update()
#===============================================================================
# info update
#===============================================================================
    def _get_all_automated_runs(self, queues=None):
        if queues is None:
            queues = self.experiment_queues

        return [ai for ei in self.experiment_queues
                    for ai in ei.executed_runs + ei.automated_runs
                        if ai.executable
                        ]

    def _update(self, queues=None):
        if queues is None:
            queues = self.experiment_queues

        queues = [qi for qi in queues if qi.isUpdateable()]
        if not queues:
            return

        self.debug('update runs')
        self.debug('updating stats')
        self.stats.calculate()

        ans = self._get_all_automated_runs(queues)
#         print len([i for i in ans])
        exclude = ('dg', 'pa')
#        timethis(self._modify_aliquots_steps, args=(ans,), kwargs=dict(exclude=exclude))
        self._modify_aliquots_steps(ans, exclude=exclude)

        self.debug('info updated')
        for qi in queues:
            qi.refresh_table_needed = True

    def _get_labnumber(self, ln):
        '''
            dont use cache
            cache labnumbers for quick retrieval
        '''
        db = self.db
        ln = convert_identifier(ln)
        dbln = db.get_labnumber(ln)

        return dbln

    def _group_analyses(self, ans, exclude=None):
        '''
        sort, group and filter by labnumber
        '''
        if exclude is None:
            exclude = tuple()
        key = lambda x: x.labnumber

        return ((ln, group) for ln, group in groupby(sorted(ans, key=key), key)
                                if ln not in exclude)

    def _modify_aliquots_steps(self, ans, exclude=None):
        '''
        '''

        def get_is_special(ln):
            special = False
            if '-' in ln:
                special = ln.split('-')[0] in ANALYSIS_MAPPING
            return ln, special

        def get_analysis_info(li):
            sample, irradiationpos = '', ''

#            analysis = db.get_last_analysis(li)
#            if analysis:
#                dbln = analysis.labnumber
            dbln = db.get_labnumber(li)
            if dbln:
                sample = dbln.sample
                if sample:
                    sample = sample.name

                irradiationpos = dbln.irradiation_position
                if irradiationpos:
                    level = irradiationpos.level
                    irradiationpos = '{}{}'.format(level.irradiation.name,
                                                   level.name)
#            self.debug('{} {} {}'.format(li, analysis, sample))
            return sample, irradiationpos

        db = self.db
        groups = self._group_analyses(ans, exclude=exclude)
        for ln, analyses in groups:
            ln, special = get_is_special(ln)
            cln = convert_identifier(ln)

            sample, irradiationpos = get_analysis_info(cln)

            aliquot_key = lambda x: x._aliquot
            egroup_key = lambda x: x.extract_group
            if not special:
                a = sorted(analyses, key=aliquot_key)
                for aliquot, aa in groupby(a, key=aliquot_key):
                    aa = sorted(aa, key=egroup_key)
                    aliquot_start = None

                    for egroup, ais in groupby(aa, key=egroup_key):
                        ast = self._set_aliquot_step(ais, special, cln,
                                                    aliquot,
                                                    aliquot_start,
                                                    egroup,
                                                    sample,
                                                    irradiationpos
                                                )
                        aliquot_start = ast + 1

            else:
                aliquot_start = None
                egroup = 0
                ans = sorted(analyses, key=aliquot_key)
                for aliquot, ais in groupby(ans, key=aliquot_key):
                    self._set_aliquot_step(ais, special, cln, aliquot,
                                           aliquot_start,
                                           egroup,
                                           sample, irradiationpos)
#




    def _set_aliquot_step(self, ais, special, cln,
                          aliquot,
                          aliquot_start,
                          egroup,
                          sample, irradiationpos):
        db = self.db

#         step_start = 0
        if aliquot_start is None:
            an = db.get_last_analysis(cln, aliquot=aliquot)
            aliquot_start = 0
            if an:
                aliquot_start = an.aliquot
#                 print an.aliquot, aliquot
#                 if an.step and an.aliquot == aliquot:
#                     step_start = LAlphas.index(an.step) + 1

        step_cnt = 0
        aliquot_cnt = 0
        for arun in ais:
#             for arun in aruns:
            arun.trait_set(sample=sample or '', irradiation=irradiationpos or '')
            if arun.skip:
                arun.aliquot = 0
                continue

            if arun.state in ('failed', 'canceled'):
                continue

            if not arun.user_defined_aliquot:
                if arun.state in ('not run', 'extraction', 'measurement'):
#                     print arun.runid, egroup, aliquot_start, aliquot_cnt
                    arun.assigned_aliquot = int(aliquot_start + aliquot_cnt + 1)
                    if special or not egroup:
                        aliquot_cnt += 1

            if not special and egroup:
                step_start = 0
                an = db.get_last_analysis(cln, aliquot=aliquot)
                if an and an.step and an.aliquot == arun.aliquot:
                    step_start = LAlphas.index(an.step) + 1

                arun.step = int(step_start + step_cnt)
#                 print arun.aliquot, arun.step, step_start, step_cnt
                step_cnt += 1

        return aliquot_start

#     def execute_queues(self, queues, path, text, text_hash):
    def execute_queues(self, queues):
        self.debug('setup executor')

        self.executor.trait_set(
                                experiment_queues=queues,
                                experiment_queue=queues[0],
#                                 path=path,
                                stats=self.stats,
#                                 text=text,
#                                 text_hash=text_hash,
                                )

        return self.executor.execute()

#===============================================================================
# handlers
#===============================================================================
    @on_trait_change('executor:experiment_queue')
    def _activate_editor(self, eq):
        self.activate_editor_event = id(eq)

    @on_trait_change('executor:execute_button')
    def _execute(self):
        '''
            trigger the experiment task to assemble current queues.
            the queues are then passed back to execute_queues()
        '''
        self.debug('%%%%%%%%%%%%%%%%%% Execute fired')
        if self.executor.isAlive():
            self.info('stop execution')
            '''
                if the executor is delaying then stop but dont cancel
                otherwise cancel
            '''
            self.executor.stop()
        else:
#             self.update_info()

            self.debug('%%%%%%%%%%%%%%%%%% Execute event true')
            self.execute_event = True

    @on_trait_change('experiment_queues[]')
    def _update_queues(self):
        qs = self.experiment_queues
        self.stats.experiment_queues = qs
        self.stats.calculate()
        self.refresh_executable(qs)

        self.debug('executor executable {}'.format(self.executor.executable))

    @on_trait_change('experiment_factory:run_factory:changed')
    def _queue_dirty(self):
        self.experiment_queue.changed = True
#         executor = self.executor
#         executor.executable = False

#         if executor.isAlive():
#             executor.prev_end_at_run_completion = executor.end_at_run_completion
#             executor.end_at_run_completion = True
#             executor.changed_flag = True

    @on_trait_change('experiment_queue:dclicked')
    def _dclicked_changed(self, new):
        self.experiment_factory.run_factory.edit_mode = True
        self._set_factory_runs(self.experiment_queue.selected)

    @on_trait_change('executor:update_needed')
    def _refresh1(self):
        self.debug('update needed fired')

        self.executor.clear_run_states()
        self.update_info()

    @on_trait_change('executor:non_clear_update_needed')
    def _refresh2(self):
        self.debug('non clear update needed fired')

        self.update_info()

    @on_trait_change('experiment_factory:run_factory:update_info_needed')
    def _refresh3(self):
        self.debug('update info needed fired')

        self.update_info()
        executor = self.executor
        executor.clear_run_states()
#         if executor.isAlive():
#             executor.end_at_run_completion = True
#             executor.changed_flag = True
    @on_trait_change('experiment_factory:run_factory:refresh_table_needed')
    def _refresh4(self):
        for qi in self.experiment_queues:
            qi.refresh_table_needed = True

    @on_trait_change('experiment_factory:save_button')
    def _save_update(self):
        self.save_event = True

    def _experiment_queue_changed(self, eq):
        if eq:
            self.experiment_factory.queue = eq
            qf = self.experiment_factory.queue_factory
            for a in ('username', 'mass_spectrometer', 'extract_device',
                      'load_name',
                      'delay_before_analyses', 'delay_between_analyses'
                      ):
                v = getattr(eq, a)
                if v is not None:
                    if isinstance(v, str):
                        v = v.strip()
                        if v:
                            setattr(qf, a, v)
                    else:
                        setattr(qf, a, v)

    @on_trait_change('experiment_queue:selected')
    def _selected_changed(self, new):
        ef = self.experiment_factory
        rf = ef.run_factory
        rf.edit_mode = False
        if new:
            if len(new) > 1:
                self._set_factory_runs(new)

    def _set_factory_runs(self, new):
        ef = self.experiment_factory
        rf = ef.run_factory
        rf.special_labnumber = 'Special Labnumber'
        rf._labnumber = NULL_STR
        rf.labnumber = ''
        rf.edit_mode = True

        rf.suppress_update = True
        rf.set_selected_runs(new)
#        rf.suppress_update = True

#===============================================================================
# property get/set
#===============================================================================
#     def _get_title(self):
#         if self.experiment_queue:
#             return 'Experiment {}'.format(self.experiment_queue.name)

    def _executor_factory(self):
        p1 = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
        p2 = 'src.spectrometer.spectrometer_manager.SpectrometerManager'
        p3 = 'src.spectrometer.ion_optics_manager.IonOpticsManager'
        kw = dict()
        if self.application:
            kw = dict(extraction_line_manager=self.application.get_service(p1),
                      spectrometer_manager=self.application.get_service(p2),
                      ion_optics_manager=self.application.get_service(p3),)

        if not self.unique_executor_db:
            kw['db'] = self.db

        e = ExperimentExecutor(
                               mode=self.mode,
                               application=self.application,
                               **kw
                               )
        return e

#===============================================================================
# defaults
#===============================================================================
    def _executor_default(self):
        return self._executor_factory()

    def _experiment_factory_default(self):
        e = ExperimentFactory(db=self.db,
                              application=self.application,
#                               queue=self.experiment_queue,
#                              max_allowable_runs=self.max_allowable_runs,
#                              can_edit_scripts=self.can_edit_scripts
                              )

#        from src.globals import globalv
#        if globalv.experiment_debug:
#            e.queue_factory.mass_spectrometer = 'Jan'
#            e.queue_factory.extract_device = 'Fusions Diode'

        return e

#============= EOF =============================================
#    def _update_run_info(self, ans, exclude=None):
#        self.debug('update run info')
#
#        for ln, aruns in self._group_analyses(ans, exclude=exclude):
#            dbln = self._get_labnumber(ln)
#            if dbln:
#
#                sample = dbln.sample
#                if sample:
#                    sample = sample.name
#
#                irradiationpos = dbln.irradiation_position
#                if irradiationpos:
#                    level = irradiationpos.level
#                    irradiationpos = '{}{}'.format(level.irradiation.name, level.name)
#
#                for ai in aruns:
#                    ai.trait_set(sample=sample or '',
#                                 irradiation=irradiationpos or ''
#                                 )

#    def _modify_aliquots2(self, ans, exclude=None):
#        if exclude is None:
#            exclude = tuple()
#        self.debug('modifying aliquots')
# #        print ans
#        offset = 0
#
#        # update the aliquots
#        idcnt_dict = dict()
#        stdict = dict()
#        fixed_dict = dict()
#
#        for arun in ans:
#            arunid = arun.labnumber
#
#            if arun.skip:
#                arun.aliquot = 0
#                continue
#
#            if arun.state in ('failed', 'canceled'):
#                continue
#
#            # dont set degas or pause aliquot
#            if arunid in exclude:
#                continue
#
#            c = 1
#            st = 0
#
#            if arunid in fixed_dict:
#                st = fixed_dict[arunid]
#
#            if arunid in idcnt_dict:
#                c = idcnt_dict[arunid]
#                if not arun.extract_group:
#                    c += 1
#                st = stdict[arunid] if arunid in stdict else 0
#            else:
#                ln = self._get_labnumber(arun.labnumber)
#                if ln is not None:
#                    try:
#                        st = ln.analyses[-1].aliquot
#                    except IndexError:
#                        st = 0
#                else:
#                    st = stdict[arunid] if arunid in stdict else 0
#
#            if not arun.user_defined_aliquot:
#                if arun.state == 'not run':
#                    arun.aliquot = int(st + c - offset)
#            else:
#                c = 0
#                fixed_dict[arunid] = arun.aliquot
#                st = arun.aliquot
#
# #            print '{:<20s}'.format(str(arun.labnumber)), arun.aliquot, st, c
#            idcnt_dict[arunid] = c
#            stdict[arunid] = st

#    def _modify_steps(self, ans, exclude=None):
#        if exclude is None:
#            exclude = tuple()
#        self.debug('modifying steps')
#
#        idcnt_dict = dict()
#        stdict = dict()
#        extract_group = -1
#        aoffs = dict()
#        for arun in ans:
#            arunid = arun.labnumber
#            if arun.skip:
#                continue
#
#            if arun.state in ('canceled', 'failed'):
#                continue
# #            if arun.state == 'canceled':
# #                continue
# #            if arun.aliquot == '##':
# #                continue
#
#            # dont set degas or pause aliquot
#            if arunid in exclude:
#                continue
#
#            if arun.extract_group:
#                if not arun.extract_group == extract_group:
#                    if arunid in aoffs:
#                        aoffs[arunid] += 1
#                    else:
#                        aoffs[arunid] = 0
#
# #                    aoff += 1
#                    idcnt_dict, stdict = dict(), dict()
#                    c = 1
#                else:
#                    if arunid in idcnt_dict:
#                        c = idcnt_dict[arunid]
#                        c += 1
#                    else:
#                        c = 1
#
#                ln = self._get_labnumber(arun.labnumber)
#                if ln is not None:
#                    st = 0
#                    if ln.analyses:
#                        an = next((ai for ai in ln.analyses if ai.aliquot == arun.aliquot), None)
#                        if not an:
#                            st = 0
#                        else:
#                            try:
#                                st = an.step
#                                st = list(ALPHAS).index(st) + 1
#                            except (IndexError, ValueError):
#                                st = 0
#                else:
#                    st = stdict[arunid] if arunid in stdict else 0
#
#                arun._step = st + c
#                idcnt_dict[arunid] = c
#                stdict[arunid] = st
#                extract_group = arun.extract_group
#
#            if arunid in aoffs:
#                aoff = aoffs[arunid]
#            else:
#                aoff = 0
# #             print arun.labnumber, aoff
#
#            if arun.state == 'not run':
#                arun.aliquot += aoff
#     def _clear_cache(self):
#         for di in dir(self):
#             if di.startswith('_cached'):
#                 setattr(self, di, None)
#    def _load_experiment_queue_hook(self):
#
#        for ei in self.experiment_queues:
#            self.debug('ei executable={}'.format(ei.executable))
#        self.executor.executable = all([ei.executable
#                                        for ei in self.experiment_queues])
#        self.debug('setting executor executable={}'.format(self.executor.executable))

#    def _validate_experiment_queues(self, eq):
#        for exp in eq:
#            if exp.test_runs():
#                return
#
#        return True
#
#    def _dump_experiment_queues(self, p, queues):
#
#        if not p:
#            return
#        if not p.endswith('.txt'):
#            p += '.txt'
#
#        self.info('saving experiment to {}'.format(p))
#        with open(p, 'wb') as fp:
#            n = len(queues)
#            for i, exp in enumerate(queues):
#                exp.path = p
#                exp.dump(fp)
#                if i < (n - 1):
#                    fp.write('\n')
#                    fp.write('*' * 80)
#
#        return p
#    @on_trait_change('selected')
#    def _update_selected(self, new):
#        self.experiment_factory.run_factory.suppress_update = True
#        self.experiment_factory.set_selected_runs(new)

#    def _pasted_changed(self):
#        self._update()
#    @on_trait_change('can_edit_script, max_allowable_runs')
#    def _update_value(self, name, value):
#        setattr(self.experiment_factory, name, value)
    #    @on_trait_change('experiment_factory:run_factory:clear_selection')
#    def _on_clear_selection(self):
#        self.selected = []
#    def _experiment_queue_factory(self, add=True, **kw):
#        exp = ExperimentQueue(
#                             db=self.db,
#                             application=self.application,
#                             **kw)
#        exp.on_trait_change(self._update, 'update_needed')
#        if add:
#            self.experiment_queues.append(exp)
# #        exp.on_trait_change(self._update_dirty, 'dirty')
#        return exp

#    def _experiment_queue_default(self):
#        return self._experiment_queue_factory()
#    def new_experiment_queue(self):
#        exp = self._experiment_queue_factory()
#        self.experiment_queue = exp
#    @deprecated
#    def load_experiment_queue(self, path=None, edit=True, saveable=False):
#
# #        self.bind_preferences()
#        # make sure we have a database connection
#        if not self.test_connections():
#            return
#
#        if path is None:
#            dlg = FileDialog(default_directory=paths.experiment_dir)
#            if dlg.open():
#                path = dlg.path
# #            path = self.open_file_dialog(default_directory=paths.experiment_dir)
#
#        if path:
#
# #            self.experiment_queue = None
# #            self.experiment_queues = []
#
#            # parse the file into individual experiment sets
#            ts = self._parse_experiment_file(path)
#            ws = []
#            for text in ts:
#                exp = self._experiment_queue_factory(path=path, add=False)
#
#                exp._warned_labnumbers = ws
#                if exp.load(text):
#                    self.experiment_queues.append(exp)
#                ws = exp._warned_labnumbers
#
#            self._update(all_info=True, stats=False)
#            if self.experiment_queues:
#                self.test_runs()
#                self.experiment_queue = self.experiment_queues[0]
#                self.start_file_listener(self.experiment_queue.path)
#
#                self._load_experiment_queue_hook()
#                self.save_enabled = True
#
#                return True

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
from traits.api import HasTraits, Str, Instance, List, Property, \
    on_trait_change, Bool, Any, Event, Button
from pyface.file_dialog import FileDialog
# from traitsui.api import View, Item
# from src.loggable import Loggable
#============= standard library imports ========================
#============= local library imports  ==========================
# from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.experiment.queue.experiment_queue import ExperimentQueue

from src.experiment.factory import ExperimentFactory
from src.constants import ALPHAS
from src.experiment.stats import StatsGroup
from src.experiment.executor import ExperimentExecutor
from src.paths import paths
from src.experiment.utilities.file_listener import FileListener
from src.experiment.experimentable import Experimentable
from src.experiment.utilities.identifier import convert_identifier
from src.deprecate import deprecated


class Experimentor(Experimentable):
    experiment_factory = Instance(ExperimentFactory)
    experiment_queue = Instance(ExperimentQueue)
    executor = Instance(ExperimentExecutor)

    stats = Instance(StatsGroup, ())

    title = Property(depends_on='experiment_queue')  # DelegatesTo('experiment_set', prefix='name')
    filelistener = None
    username = Str

    save_enabled = Bool

    #===========================================================================
    # permissions
    #===========================================================================
    max_allowable_runs = 10000
    can_edit_scripts = True
    _last_ver_time = None
    _ver_timeout = 10

#    selected = Any
#    pasted = Event
#    refresh = Button
#    dclicked = Any
    #===========================================================================
    # task events
    #===========================================================================
    execute_event = Event
    activate_editor_event = Event
    clear_display_event = Event

    def test_queues(self, qs=None):
        if qs is None:
            qs = self.experiment_queues

        for qi in qs:
            qi.test_runs()
        self.executor.executable = all([ei.executable for ei in qs])

#    def test_runs(self):
#        for ei in self.experiment_queues:
#            ei.test_runs()

    def test_connections(self):
        if not self.db:
            return

        if not self.db.connect():
            self.warning_dialog('Failed connecting to database. {}'.format(self.db.url))
            return

#        if not self.repository.connect():
#            self.warning_dialog('Failed connecting to repository {}'.format(self.repository.url))
#            return

        return True

    def start_file_listener(self, path):
        fl = FileListener(
                          path,
                          callback=self._reload_from_disk,
                          check=self._check_for_file_mods
                          )
        self.filelistener = fl

    def stop_file_listener(self):
        if self.filelistener:
            self.filelistener.stop()

    def update_info(self):
        self._update(all_info=True, stats=True)
#===============================================================================
# info update
#===============================================================================
    def _update(self, all_info=False, stats=True):
        self.debug('update runs')

        if stats:
            self.debug('updating stats')
            self.stats.calculate()

#        print len(self.experiment_queues)
        ans = self._get_all_automated_runs()
        # update the aliquots

        self._modify_aliquots(ans)

        # update the steps
        self._modify_steps(ans)

        # update run info
        if not all_info:
            ans = ans[-1:]

        self._update_info(ans)
        self.debug('info updated')

    def _get_labnumber(self, arun):
        '''
            cache labnumbers for quick retrieval
        '''
        ca = '_cached_{}'.format(arun.labnumber)
#         print ca, hasattr(self,ca)
        dbln = None
        if hasattr(self, ca):
            dbln = getattr(self, ca)

        if not dbln:
            db = self.db
            ln = arun.labnumber
            ln = convert_identifier(ln)
            dbln = db.get_labnumber(ln)
            setattr(self, ca, dbln)

        return dbln

    def _update_info(self, ans):
        self.debug('update run info')

        for ai in ans:
            self.debug('ln {}'.format(ai.labnumber))
            if ai.labnumber and not ai.labnumber in ('dg',):
                dbln = self._get_labnumber(ai)
                if dbln:
                    sample = dbln.sample
                    if sample:
                        ai.sample = sample.name
                        self.debug('sample {}'.format(ai.sample))

                    ipos = dbln.irradiation_position
                    if not ipos is None:
                        level = ipos.level
                        irrad = level.irradiation
                        ai.irradiation = '{}{}'.format(irrad.name, level.name)
                        self.debug('irrad {}'.format(ai.irradiation))

    def _modify_steps(self, ans):
        self.debug('modifying steps')

        idcnt_dict = dict()
        stdict = dict()
        extract_group = -1
        aoffs = dict()
        for arun in ans:
            arunid = arun.labnumber
            if arun.skip:
                continue

            if arun.extract_group:
                if not arun.extract_group == extract_group:
                    if arunid in aoffs:
                        aoffs[arunid] += 1
                    else:
                        aoffs[arunid] = 0

#                    aoff += 1
                    idcnt_dict, stdict = dict(), dict()
                    c = 1
                else:
                    if arunid in idcnt_dict:
                        c = idcnt_dict[arunid]
                        c += 1
                    else:
                        c = 1

                ln = self._get_labnumber(arun)
#                 ln = db.get_labnumber(arunid)
                if ln is not None:
                    st = 0
                    if ln.analyses:
                        an = ln.analyses[-1]
                        if an.aliquot != arun.aliquot:
                            st = 0
                        else:
                            try:
                                st = an.step
                                st = list(ALPHAS).index(st) + 1
                            except (IndexError, ValueError):
                                st = 0
                else:
                    st = stdict[arunid] if arunid in stdict else 0

                arun._step = st + c
                idcnt_dict[arunid] = c
                stdict[arunid] = st
                extract_group = arun.extract_group

            if arunid in aoffs:
                aoff = aoffs[arunid]
            else:
                aoff = 0
#             print arun.labnumber, aoff
            arun.aliquot += aoff

    def _modify_aliquots(self, ans):
        self.debug('modifying aliquots')
#        print ans
        offset = 0

        # update the aliquots
        idcnt_dict = dict()
        stdict = dict()
        fixed_dict = dict()
        for arun in ans:
            if arun.skip:
                arun.aliquot = 0
                continue

            arunid = arun.labnumber
            c = 1
            st = 0
            if arunid in fixed_dict:
                st = fixed_dict[arunid]

            if arunid in idcnt_dict:
                c = idcnt_dict[arunid]
                if not arun.extract_group:
                    c += 1
                st = stdict[arunid] if arunid in stdict else 0
            else:
                ln = self._get_labnumber(arun)
                if ln is not None:
                    try:
                        st = ln.analyses[-1].aliquot
                    except IndexError:
                        st = 0
                else:
                    st = stdict[arunid] if arunid in stdict else 0

            if not arun.user_defined_aliquot:
                arun.aliquot = int(st + c - offset)
            else:
                c = 0
                fixed_dict[arunid] = arun.aliquot

            # print '{:<20s}'.format(str(arun.labnumber)), arun.aliquot, st, c
            idcnt_dict[arunid] = c
            stdict[arunid] = st

    def execute_queues(self, queues, text, text_hash):
        if self.executor.isAlive():
            self.debug('cancel execution')
            self.executor.cancel()
        else:
            self.debug('stop file listener')
            self.stop_file_listener()

            self.debug('setup executor')
            self.executor.trait_set(experiment_queues=queues,
                                    experiment_queue=queues[0],
                                    text=text,
                                    text_hash=text_hash,
                                    stats=self.stats
                                    )

            self.executor.execute()

#===============================================================================
# handlers
#===============================================================================
    def _refresh_fired(self):
        self._update(all_info=True, stats=True)

    @on_trait_change('executor:experiment_queue')
    def _activate_editor(self, eq):
        self.activate_editor_event = id(eq)

    @on_trait_change('executor:execute_button')
    def _execute(self):
        '''
            trigger the experiment task to assemble current queues.
            the queues are then passed back to execute_queues()
        '''
        self.execute_event = True

    @on_trait_change('experiment_queues[]')
    def _update_stats(self):

        self.stats.experiment_queues = self.experiment_queues
        self.stats.calculate()

#    @on_trait_change('experiment_queues')
#    def _update_queues(self, new):
#        self.executor.set_experiment_queues(new)

    @on_trait_change('experiment_queue:dclicked')
    def _dclicked_changed(self, new):
        self.experiment_factory.run_factory.edit_mode = True

    @on_trait_change('''experiment_queue:refresh_button,
experiment_factory:run_factory:update_info_needed''')
    def _refresh(self):
        self.update_info()

    def _experiment_queue_changed(self, eq):
        if eq:
            self.experiment_factory.queue = eq
            qf = self.experiment_factory.queue_factory
            for a in ('username', 'mass_spectrometer', 'extract_device', 'username',
                      'delay_before_analyses', 'delay_between_analyses'
                      ):
                setattr(qf, a, getattr(eq, a))

    @on_trait_change('experiment_queue:selected')
    def _selected_changed(self, new):
        ef = self.experiment_factory
        rf = ef.run_factory
        rf.edit_mode = False
        if new:
#            self.selected = new
            rf.special_labnumber = '---'
            rf._labnumber = '---'
            rf.labnumber = ''
            if len(new) > 1:
                rf.edit_mode = True

        rf.suppress_update = True
        ef.set_selected_runs(new)

#===============================================================================
# property get/set
#===============================================================================
    def _get_title(self):
        if self.experiment_queue:
            return 'Experiment {}'.format(self.experiment_queue.name)

#===============================================================================
# defaults
#===============================================================================
    def _executor_default(self):
        e = ExperimentExecutor(db=self.db,
                               application=self.application
                               )

#        pfunc = lambda *args, **kw: self._update(all_info=True)
#        e.on_trait_change(pfunc, 'update_needed')
        return e

    def _experiment_factory_default(self):
        e = ExperimentFactory(db=self.db,
                              application=self.application,
                              queue=self.experiment_queue,
                              max_allowable_runs=self.max_allowable_runs,
                              can_edit_scripts=self.can_edit_scripts
                              )

        from src.globals import globalv
        if globalv.experiment_debug:
            e.queue_factory.mass_spectrometer = 'Jan'
            e.queue_factory.extract_device = 'Fusions Diode'

        return e

#============= EOF =============================================
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

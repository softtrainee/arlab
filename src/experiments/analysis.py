#===============================================================================
# Copyright 2011 Jake Ross
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



from __future__ import with_statement
#============= enthought library imports =======================
from traits.api import List, Property, Enum, Str, String, Float, Int, Button, Bool, Instance, Any, Long
from traitsui.api import View, Item, Group, VGroup, HGroup, EnumEditor, spring
import apptools.sweet_pickle as pickle

#============= standard library imports ========================
import os
import time
#============= local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
from src.helpers.paths import heating_schedule_dir, scripts_dir
from heating_schedule import HeatingSchedule, HeatingScheduleEditor
from src.graph.graph import Graph
from src.scripts.extraction_line_script import ExtractionLineScript
from src.loggable import Loggable
from time_series_helper import parse_time_series_blob, \
    build_time_series_blob
from src.extraction_line.extraction_line_manager import ExtractionLineManager
from threading import Condition
prep_script_dir = os.path.join(scripts_dir, 'prep_scripts')

class AutomatedRun(Loggable):
    '''
    '''
    kind = Enum('analysis', 'blank')

    sample_id = Long
    experiment_id = Long

    runid = String(enter_set=True, auto_set=False)
    power = Float
    hole = Int

    getter_time = Float
    time_at_temp = Float

    prep_script = Str
    _active_prep_script = Any(transient=True)

    database = Instance(DatabaseAdapter, transient=True)
    extraction_line_manager = Instance(ExtractionLineManager, transient=True)

#===============================================================================
# setup parameters
#===============================================================================
    heating_schedule = Property(depends_on='_heating_schedule')
    heating_schedules = Property(depends_on='_heating_schedules')

    _heating_schedule = Instance(HeatingSchedule)
    _heating_schedules = List
    edit_hs = Button('Edit')
    new_hs = Button('New')

    assign = Button

    _valid_sample = Bool(False)
    use_schedule = Property(depends_on='power')

    _prep_scripts = List

    _alive = Bool(False, transient=True)
#===============================================================================
# graph
#===============================================================================
    graph = Instance(Graph, transient=True)

#===============================================================================
# experiment
#===============================================================================
    experiment = Any

#===============================================================================
# database parameters
#===============================================================================
    db_session = Any(transient=True)
    db_analysis = Any(transient=True)
    db_detectors = Any(transient=True)
    db_signals = Any(transient=True)

    def _graph_default(self):
        '''
        '''
        return self._graph_factory()

    def _graph_factory(self):
        g = Graph(container_dict=dict(type='g', shape=[2, 3],
                                       padding=0,
                                       fill_padding=True,
                                       spacing=(5, 5)
                                       ))

        return g



    def __init__(self, *args, **kw):
        '''
           
        '''
        super(AutomatedRun, self).__init__(*args, **kw)
        self.load_heating_schedules()
        self.load_prep_scripts()

    def _dummy_execute(self, spectrometer):
        self.save_analysis()
        self.save_detectors()
        #do an analysis
        spectrometer.move_to_mass(40, detector='ax')

#        colors = ['red', 'green', 'blue', 'yellow', 'purple']
        for i, di in enumerate(['l2', 'l1', 'ax', 'h1', 'h2']):
            self.graph.new_plot(**dict(padding=[25, 0, 0, 25],
                                       ))
            self.graph.new_series(type='scatter', plotid=i, marker_size=1.25)

        x = dict(l1=[], l2=[], ax=[], h1=[], h2=[])
        y = dict(l1=[], l2=[], ax=[], h1=[], h2=[])
        realtime_view = False
        db_save = True
        for _j in range(60):
            for i, di in enumerate(['l2', 'l1', 'ax', 'h1', 'h2']):
                datum = spectrometer.get_signal(di)

                if db_save:
                    self.save_signal(di, datum)

                if realtime_view:
                    self.graph.add_datum(datum, plotid=i)
                    time.sleep(0.1)
                else:
                    x[di].append(datum[0])
                    y[di].append(datum[1])

        if not realtime_view:
            for i, di in enumerate(['l2', 'l1', 'ax', 'h1', 'h2']):
                self.graph.set_data(x[di], plotid=i, axis=0)
                self.graph.set_data(y[di], plotid=i, axis=1)

    def isAlive(self):
        return self._alive

    def kill(self):
        self._alive = False
        if self._active_prep_script is not None:
            self._active_prep_script.kill_script()

    def load_prep_scripts(self):
        for p in os.listdir(prep_script_dir):
            if p.endswith('.rs'):
                self._prep_scripts.append(p)
        if self._prep_scripts:
            self.prep_script = self._prep_scripts[0]

    def load_heating_schedules(self):
        #load the heating schedules
        for p in os.listdir(heating_schedule_dir):
            with open(os.path.join(heating_schedule_dir, p), 'r') as f:
                s = pickle.load(f)
                self._heating_schedules.append(s)

        if self._heating_schedules:
            s = self._heating_schedules[0]
            self.heating_schedule = s.name
            self._heating_schedule = s

    def save_signal(self, detector_key, datum):
        '''
       
        '''
        db_detector = self.db_detectors[detector_key]
        db_analysis = self.db_analysis
        if self.db_signals is None:
            self.db_signals = dict()

        if detector_key in self.db_signals:
            dbdet = self.db_signals[detector_key]
            ts = dbdet.time_series
            t, v = parse_time_series_blob(ts)
            t.append(datum[0])
            v.append(datum[1])
            dbdet.time_series = build_time_series_blob(t, v)
        else:
            ts = build_time_series_blob(*datum)
            args = dict(time_series=ts)
            dbs, _sess = self.database.add_signal(args, dbanalysis=db_analysis,
                                        dbdetector=db_detector,
                                        sess=self.db_session
                                        )
            self.db_signals[detector_key] = dbs

        self.db_session.flush()

    def save_detectors(self):
        '''
        '''
        if self.database is not None:
            db = self.database
            detectors = ['l2', 'l1', 'ax', 'h1', 'h2']
            axial_mass = 38
            self.db_detectors = dict()
            for i, d in enumerate(detectors):
                db_detector, sess = db.add_detector(dict(mass=axial_mass - 2 + i , label=d),
                                                    sess=self.db_session)
                self.db_session = sess
                self.db_detectors[d] = db_detector

        self.db_session.flush()

    def save_analysis(self):
        '''
        '''
        db = self.database
        if db is not None:
            args = dict(args=dict(kind=self.kind),
                      dbexperiment=self.experiment_id,
                      sess=self.db_session
                      )

            if self.sample_id:
                args['dbsample'] = self.sample_id
            dba, sess = db.add_analysis(**args)

            self.db_session = sess
            self.db_analysis = dba
        else:
            self.warning('no database')

        self.db_session.flush()

    def execute(self, kw):
        self._alive = True
        spectrometer = kw['spectrometer']
        self.experiment_id = kw['experiment_id']

        self.pre_execute(kw)
        self._dummy_execute(spectrometer)
        self.post_execute()



    def pre_execute(self, kw):
        '''
            @type hardware_dict: C{str}
            @param hardware_dict:
        '''
        if self.isAlive():
            #sdir = os.path.join(scripts_dir, 'prep_scripts')
            fullpath = os.path.join(prep_script_dir, self.prep_script)

            self.info('execute the prep script %s' % self.prep_script)
            #execute the prep script

            manager = kw['extraction_line_manager']
            #use a condition to wait until prep script is finished
            c = Condition()
            c.acquire()

            if os.path.isfile(fullpath):
                e = ExtractionLineScript(source_dir=prep_script_dir ,
                                     file_name=self.prep_script,
                                     manager=manager,
                                     getter_time=self.getter_time,
                                     power=self.power,
                                     kind=self.kind,
                                     time_at_temp=self.time_at_temp,
                                     hole=self.hole
                                     )

                e.bootstrap(condition=c)
                self._active_prep_script = e

                #condition released by script.kill_script
                c.wait()

            else:
                self.warning('not a valid prep script  %s' % fullpath)

    def post_execute(self):
        '''
        '''
        if self.isAlive():
            self.info('post execute clean up')

            #finish saving to db 
            if self.db_session is not None:
                self.db_session.commit()
                self.db_session.close()

                #clear db instances
                self.db_analysis = None
                self.db_detectors = None
                self.db_signals = None

    def _assign_fired(self):
        '''
        '''

        self._add_logger()

        if not self.experiment.analyses and self.experiment.start_with_blank:
            #if the is the first analysis prepend a blank
            b = self.clone_traits(traits=['prep_script'])
            print b.runid
            b.name = 'Blank %i' % len(self.experiment.blanks)
            b.kind = 'blank'
            self.experiment.blanks.append(b)
            self.experiment.analyses.append(b)


        self.name = 'AutomatedRun %i' % len(self.experiment.analyses)
        if self.use_schedule:
            for s in self._heating_schedule.steps:
                nobj = self.clone_traits()
                nobj.power = s.power
                nobj.name = 'AutomatedRun %i' % len(self.experiment.analyses)
                nobj.database = self.database
                self.experiment.analyses.append(nobj)

        else:
            self.experiment.analyses.append(self.clone_traits())

    def _edit_hs_fired(self):
        '''
        '''
        if self.heating_schedule:
            s = self._heating_schedule
            s.load_from_pickle()
            ss = HeatingScheduleEditor(schedule=s,
                                       _allow_save_as=True)

            info = ss.edit_traits(kind='livemodal')
            if info.result:
                if ss.schedule.save_as:
                    self._heating_schedules.append(ss.schedule)
                    self._heating_schedule = ss.schedule

    def _new_hs_fired(self):
        '''
        '''
        s = HeatingScheduleEditor()
        info = s.edit_traits(kind='livemodal')
        if info.result:
            self._heating_schedules.append(s.schedule)
            self._heating_schedule = s.schedule

    def _runid_changed(self):
        '''
        '''
        if self.database is not None:
            sample, sess = self.database.get_samples(dict(name=self.runid))
            if sample is not None:
                self._valid_sample = True
                self.sample_id = sample.id
                #print sample.id, sample.name, sample.irradiation_id
            if sess is not None:
                sess.close()

    def traits_view(self):
        '''
        '''
        hg = Group(
                   HGroup(
                          Item('prep_script', editor=EnumEditor(name='_prep_scripts'))
                          ),
                   HGroup(
                          Item('heating_schedule',
                               editor=EnumEditor(name='object.heating_schedules'),
                               ),
                          Item('edit_hs', enabled_when='object.heating_schedules'),
                          Item('new_hs'),
                          Item('assign'),
                          show_labels=False,
                        ),
                 visible_when='_valid_sample',
                 show_border=True,
                 label='Heating Schedule')

        analysis_group = Group(
                 Item('runid'),
                 Item('power'),
                 Item('hole'),
                 Item('time_at_temp'),
                 Item('getter_time'),
                 hg,
                 #enabled_when = 'kind=="analysis"'
                 )

        kind_group = HGroup(Item('kind', show_label=False), spring),
        v = View(VGroup(
                    kind_group,
                    analysis_group,
                    ),
                 buttons=['OK', 'Cancel'],
                 width=500,
                 height=500,
                 )
        return v

    def _get_use_schedule(self):
        '''
        '''
        return True if self._heating_schedules and self.power == 0 else False

    def _get_heating_schedules(self):
        '''
        '''
        return [s.name for s in self._heating_schedules]

    def _get_heating_schedule(self):
        '''
        '''
        return self._heating_schedule.name

    def _set_heating_schedule(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        for s in self._heating_schedules:
            if s.name == v:
                self._heating_schedule = s
                break

#============= views ===================================

#============= EOF ====================================

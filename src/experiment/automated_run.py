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

#============= enthought library imports =======================
from traits.api import Any, Str, String, Int, CInt, List, Enum, Property, \
     Event, Float, Instance, Bool, cached_property, Dict, on_trait_change, DelegatesTo
from traitsui.api import View, Item, VGroup, EnumEditor, HGroup, Group
from traitsui.tabular_adapter import TabularAdapter
from pyface.timer.do_later import do_later
#============= standard library imports ========================
import os
import time
import random
from threading import Thread
from threading import Event as TEvent
#============= local library imports  ==========================
from src.loggable import Loggable
from src.experiment.heat_schedule import HeatStep
from src.graph.stacked_graph import StackedGraph
from src.data_processing.regression.regressor import Regressor
#from src.scripts.extraction_line_script import ExtractionLineScript
from src.pyscripts.measurement_pyscript import MeasurementPyScript
from src.pyscripts.extraction_line_pyscript import ExtractionLinePyScript
#from src.database.adapters.isotope_adapter import IsotopeAdapter
#from src.paths import paths
from src.data_processing.mass_spec_database_importer import MassSpecDatabaseImporter
from src.helpers.datetime_tools import get_datetime
from src.database.sync.repository import Repository
from src.experiment.plot_panel import PlotPanel


HEATDEVICENAMES = ['Fusions Diode', 'Fusions CO2']

class AutomatedRunAdapter(TabularAdapter):

    state_image = Property
    state_text = Property
    extraction_script_text = Property
    measurement_script_text = Property
    post_measurement_script_text = Property
    post_equilibration_script_text = Property
    position_text = Property
    heat_value_text = Property
    duration_text = Property
    autocenter_text = Property
    overlap_text = Property

    can_edit = False
#    def get_can_edit(self, obj, trait, row):
#        if self.item:
#            if self.item.state == 'not run':
#                return True

    def _columns_default(self):
#        hp = ('Temp', 'heat_value')
#        if self.kind == 'watts':
#            hp =

        return  [('', 'state'), ('RunID', 'identifier'), ('Aliquot', 'aliquot'),

                 ('Sample', 'sample'),
                 ('Position', 'position'),
                 ('Autocenter', 'autocenter'),
                 ('HeatDevice', 'heat_device'),
                 ('Overlap', 'overlap'),
                 ('Heat', 'heat_value'),
                 ('Duration', 'duration'),
                 ('Extraction', 'extraction_script'),
                 ('Measurement', 'measurement_script'),
                 ('Post Measurement', 'post_measurement_script'),
                 ('Post equilibration', 'post_equilibration_script'),
                 ]

    def _get_heat_value_text(self, trait, item):
        _, u = self.item.heat_value
        if u:
            return '{:0.2f},{}'.format(*self.item.heat_value)
        else:
            return ''

    def _get_duration_text(self, trait, item):
        return self._get_number('duration')

    def _get_overlap_text(self, trait, item):
        return self._get_number('overlap')

    def _get_position_text(self, trait, item):
        return self._get_number('position')

    def _get_number(self, attr):
        v = getattr(self.item, attr)
        if v:
            return v
        else:
            return ''

    def _get_autocenter_text(self, trait, item):
        return 'yes' if self.item.autocenter else ''

#    def _set_autocenter_text(self, trait, value):
#        self.item.autocenter = value == 'yes'

    def _get_extraction_script_text(self, trait, item):
        if self.item.extraction_script:
            return self.item.extraction_script.name

    def _get_measurement_script_text(self, trait, item):
        if self.item.measurement_script:
            return self.item.measurement_script.name

    def _get_post_measurement_script_text(self, trait, item):
        if self.item.post_measurement_script:
            return self.item.post_measurement_script.name

    def _get_post_equilibration_script_text(self, trait, item):
        if self.item.post_equilibration_script:
            return self.item.post_equilibration_script.name

    def _get_state_text(self):
        return ''

    def _get_state_image(self):
        if self.item:
            im = 'gray'
            if self.item.state == 'extraction':
                im = 'yellow'
            elif self.item.state == 'measurement':
                im = 'orange'
            elif self.item.state == 'success':
                im = 'green'
            elif self.item.state == 'fail':
                im = 'red'

            #get the source path
            root = os.path.split(__file__)[0]
            while not root.endswith('src'):
                root = os.path.split(root)[0]
            root = os.path.split(root)[0]
            root = os.path.join(root, 'resources')
            return os.path.join(root, '{}_ball.png'.format(im))


class AutomatedRun(Loggable):
    spectrometer_manager = Any
    extraction_line_manager = Any
    experiment_manager = Any
    ion_optics_manager = Any
    data_manager = Any

    db = Any
    massspec_importer = Instance(MassSpecDatabaseImporter)
    repository = Instance(Repository)
    runner = Any
    plot_panel = Any

    sample = Str

    experiment_name = Str
    identifier = String(enter_set=True, auto_set=False)
    aliquot = Int
    state = Enum('not run', 'extraction', 'measurement', 'success', 'fail')
#    runtype = Enum('Blank', 'Air')
    irrad_level = Str

    heat_step = Instance(HeatStep)
    duration = Property(depends_on='heat_step,_duration')

#    temp_or_power = Property(depends_on='heat_step,_temp_or_power')
    _duration = Float

    heat_value = Property(depends_on='heat_step,_heat_value,_heat_units')
    _heat_value = Float

    heat_units = Property(depends_on='heat_step,_heat_units')
    _heat_units = Str#Enum('watts', 'temp', 'percent')

    heat_device = Str

    position = CInt
    endposition = Int
    multiposition = Bool
    autocenter = Bool


    weight = Float
    comment = Str

    scripts = Dict
    signals = Dict
    sample_data_record = Any

    update = Event

    overlap = CInt

    measurement_script_dirty = Event
    measurement_script = Property(depends_on='measurement_script_dirty')
    _measurement_script = Any

    post_measurement_script_dirty = Event
    post_measurement_script = Property(depends_on='post_measurement_script_dirty')
    _post_measurement_script = Any

    post_equilibration_script_dirty = Event
    post_equilibration_script = Property(depends_on='post_equilibration_script_dirty')
    _post_equilibration_script = Any

    extraction_script_dirty = Event
    extraction_script = Property(depends_on='extraction_script_dirty')
    _extraction_script = Any

    _active_detectors = List
    _debug = False
    _loaded = False
    configuration = None

    _rundate = None
    _runtime = None

    executable = Bool(False)
    _alive = False

    regression_results = None
    peak_center = None
#    info_display = DelegatesTo('experiment_manager')
    info_display = None#DelegatesTo('experiment_manager')

    @property
    def compound_name(self):
        return '{}-{}'.format(self.identifier, self.aliquot)

    @property
    def runtype(self):
        if self.identifier.startswith('B'):
            return 'blank'
        elif self.identifier.startswith('A'):
            return 'air'

    def finish(self):
        del self.info_display
        if self.plot_panel:
            self.plot_panel.close_ui()
        if self.peak_center:
            self.peak_center.graph.close()

    def info(self, msg, *args, **kw):
        super(AutomatedRun, self).info(msg, *args, **kw)
        if self.info_display:
            do_later(self.info_display.add_text, msg)

    def get_estimated_duration(self):
        '''
            use the pyscripts to calculate etd
        '''
        s = self.duration

        for si in [self.measurement_script,
                   self.extraction_script,
                   self.post_equilibration_script,
                   self.post_measurement_script]:
            if si is not None:
                s += si.get_estimated_duration()

        return s

    def get_measurement_parameter(self, key, default=None):
        ms = self.measurement_script
        import ast
        import yaml
        m = ast.parse(ms._text)
        docstr = ast.get_docstring(m)
        if docstr is not None:
            params = yaml.load(ast.get_docstring(m))
            try:
                return params[key]
            except KeyError:
                pass
            except TypeError:
                self.warning('Invalid yaml docstring in {}. Could not retrieve {}'.format(ms.name, key))

        return default


    def measurement_script_factory(self, ec):
        ec = self.configuration
        mname = os.path.basename(ec['measurement_script'])

        ms = MeasurementPyScript(root=os.path.dirname(ec['measurement_script']),
            name=mname,
            automated_run=self
            )
        return ms
#
    def extraction_script_factory(self, ec):
        key = 'extraction_script'
        return self._extraction_script_factory(ec, key)

    def post_measurement_script_factory(self, ec):
        key = 'post_measurement_script'
        return self._extraction_script_factory(ec, key)

    def post_equilibration_script_factory(self, ec):
        key = 'post_equilibration_script'
        return self._extraction_script_factory(ec, key)

    def _extraction_script_factory(self, ec, key):
        #get the klass

        path = os.path

        source_dir = path.dirname(ec[key])
        file_name = path.basename(ec[key])

        if file_name.endswith('.py'):
            klass = ExtractionLinePyScript
            hdn = self.heat_device.replace(' ', '_').lower()
            return klass(
                    root=source_dir,
                    name=file_name,

                    hole=self.position,

                    duration=self.duration,
                    heat_value=self._heat_value,
                    heat_units=self._heat_units,
#                    watts=self.watts,
#                    temp_or_power=self.temp_or_power,

                    runner=self.runner,
                    heat_device=hdn,
                    runtype=self.runtype
                    )
    def cancel(self):
        self._alive = False
        self.extraction_script.cancel()
        self.post_equilibration_script.cancel()
        self.measurement_script.cancel()
        self.post_measurement_script.cancel()

    def wait_for_overlap(self):
        self.info('waiting for overlap signal')
        evt = self.overlap_evt
        evt.wait()

        self.info('starting overlap delay {}'.format(self.overlap))
        starttime = time.time()
        while self._alive:
            if time.time() - starttime > self.overlap:
                break
            time.sleep(0.5)

#===============================================================================
# doers
#===============================================================================
    def start(self):
        self.overlap_evt = TEvent()
        self.info('Start automated run {}'.format(self.name))
        self._alive = True

    def do_extraction(self):
        if not self._alive:
            return

        self.info('======== Extraction Started ========')
        self.state = 'extraction'
        self.extraction_script.manager = self.experiment_manager

#        self._pre_extraction_save()
        if self.extraction_script.execute():
            self._post_extraction_save()
            self.info('======== Extraction Finished ========')
            return True
        else:
            self.info('======== Extraction Finished unsuccessfully ========')
            return False

    def do_measurement(self):
        if not self._alive:
            return

        self.measurement_script.manager = self.experiment_manager
        #use a measurement_script to explicitly define 
        #measurement sequence
        self.info('======== Measurement Started ========')
        self._pre_measurement_save()
        if self.measurement_script.execute():
            self._post_measurement_save()

            self.info('======== Measurement Finished ========')
            return True
        else:
            self.info('======== Measurement Finished unsuccessfully ========')
            return False

    def do_post_measurement(self):
        if not self._alive:
            return

        self.info('======== Post Measurement Started ========')
        self.state = 'extraction'
        self.post_measurement_script.manager = self.experiment_manager

        if self.post_measurement_script.execute():
            self.info('======== Post Measurement Finished ========')
            return True
        else:
            self.info('======== Post Measurement Finished unsuccessfully ========')
            return False

    def do_equilibration(self):
        event = TEvent()
        if not self._alive:
            event.set()
            return event

        self.info('====== Equilibration Started ======')
        t = Thread(name='equilibration', target=self._equilibrate, args=(event,))
        t.start()
        return event

    def _equilibrate(self, evt):
        eqtime = self.get_measurement_parameter('equilibration_time', default=15)
        inlet = self.get_measurement_parameter('inlet_valve')
        outlet = self.get_measurement_parameter('outlet_valve')
        elm = self.extraction_line_manager
        if elm:
            if outlet:
                #close mass spec ion pump
                elm.close_valve(outlet, mode='script')
                time.sleep(1)

            if inlet:
                #open inlet
                elm.open_valve(inlet, mode='script')

        evt.set()

        #delay for eq time
        self.info('equilibrating for {}sec'.format(eqtime))
        time.sleep(eqtime)

        self.info('====== Equilibration Finished ======')
        if elm and inlet:
            elm.close_valve(inlet)

        self.do_post_equilibration()
        self.overlap_evt.set()

    def do_post_equilibration(self):
        if not self._alive:
            return

        self.info('======== Post Equilibration Started ========')
        self.post_equilibration_script.manager = self.experiment_manager

        if self.post_equilibration_script.execute():
            self.info('======== Post Equilibration Finished ========')
#            return True
        else:
            self.info('======== Post Equilibration Finished unsuccessfully ========')
#            return False

    def do_data_collection(self, ncounts, starttime, series=0):
        if not self._alive:
            return
        if self.plot_panel:
            self.plot_panel._ncounts = ncounts

        gn = 'signals'
        self._build_tables(gn)
        return self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series)

    def do_sniff(self, ncounts, starttime, series=0):
        if not self._alive:
            return

        if self.plot_panel:
            self.plot_panel._ncounts = ncounts
        gn = 'sniffs'
        self._build_tables(gn)

        return self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series)

    def do_baselines(self, ncounts, starttime, mass, detector,
                     mode, series=0):
        if not self._alive:
            return

        if self.plot_panel:
            self.plot_panel._ncounts = ncounts
        if mass:
            ion = self.ion_optics_manager
            if ion is not None:
                ion.position(mass, detector, False)
                time.sleep(2)

        gn = 'baselines'
        self._build_tables(gn)
        if mode == 'multicollect':
            return self._measure_iteration(gn,
                                self._get_data_writer(gn),
                                ncounts, starttime, series)
##        else:
##            masses = [1, 2]
##            self._peak_hop(gn, detector, masses, ncounts, starttime, series)

    def do_peak_hop(self, detector, isotopes, cycles, starttime, series):
        if not self._alive:
            return
        self._peak_hop('signals', detector,
                       isotopes, cycles, starttime, series)


    def do_peak_center(self, **kw):
        if not self._alive:
            return
        ion = self.ion_optics_manager
        if ion is not None:

            t = ion.do_peak_center(**kw)

            #block until finished
            t.join()

            pc = ion.peak_center
            self.peak_center = pc
            if pc.result:
                dm = self.data_manager
                tab = dm.new_table('/', 'peakcenter')
                for xi, yi in zip(*pc.data):
                    nrow = tab.row
                    nrow['time'] = xi
                    nrow['value'] = yi
                    nrow.append()

                xs, ys, _mx, _my = pc.result
                attrs = tab.attrs
                attrs.low_dac = xs[0]
                attrs.center_dac = xs[1]
                attrs.high_dac = xs[2]

                attrs.low_signal = ys[0]
                attrs.center_signal = ys[1]
                attrs.high_signal = ys[2]
                tab.flush()

    def set_spectrometer_parameter(self, name, v):
        self.info('setting spectrometer parameter {} {}'.format(name, v))
        sm = self.spectrometer_manager
        if sm is not None:
            sm.spectrometer.set_parameter(name, v)

    def set_position(self, pos, detector, dac=False):
        if not self._alive:
            return

        ion = self.ion_optics_manager

        if ion is not None:
            ion.position(pos, detector, dac)
            try:
                #update the plot_panel labels
                for det, pi in zip(self._active_detectors, self.plot_panel.graph.plots):
                    pi.y_axis.title = '{} {} Signal (fA)'.format(det.name, det.isotope)
            except Exception, e:
                print 'set_position exception', e


    def set_isotopes(self, isotopes):
        for di, iso in zip(isotopes, self._active_detectors):
            di.isotope = iso

    def activate_detectors(self, dets):
        if not self._alive:
            return
        p = self.plot_panel
        if p is not None:
            p.ui.dispose()

        p = PlotPanel(
                         window_y=0.05 + 0.01 * self.index,
                         window_x=0.6 + 0.01 * self.index,
                         window_title='Plot Panel {}-{}'.format(self.identifier, self.aliquot)
                         )
        p.graph.clear()

        self.plot_panel = p
        self.experiment_manager.open_view(p)
        dets.reverse()

        spec = self.spectrometer_manager.spectrometer
        g = p.graph
        for l in dets:
            det = spec.get_detector(l)
            g.new_plot(ytitle='{} {} Signal (fA)'.format(det.name, det.isotope))
            g.new_series(type='scatter',
                         marker='circle',
                         marker_size=1.25,
                         label=l)

        g.set_x_limits(min=0, max=400)
#        dets.reverse()

#            g.new_series(type='scatter',
#                         marker='circle',
#                         marker_size=1.25,
#                         label=l, plotid=i)

#        dets =
        self._active_detectors = [spec.get_detector(n) for n in dets]
#        do_later(self.experiment_manager.ui.control.Raise)

    def do_regress(self, fits, series=0):
        if not self._alive:
            return

        n = len(self._active_detectors)
        if isinstance(fits, str) or len(fits) < n:
            fits = [fits[0], ] * n

        r = Regressor()
        g = self.plot_panel.graph

        time_zero_offset = 0#int(self.experiment_manager.equilibration_time * 2 / 3.)
        self.regression_results = dict()
        for pi, (dn, fi) in enumerate(zip(self._active_detectors, fits)):

            x = g.get_data(plotid=pi, series=series)[time_zero_offset:]
            y = g.get_data(plotid=pi, series=series, axis=1)[time_zero_offset:]
            x, y = zip(*zip(x, y))
            rdict = r._regress_(x, y, fi)
            self.regression_results[dn.name] = rdict
            self.info('{}-{} intercept {}+/-{}'.format(dn.name, fi,
                                                    rdict['coefficients'][-1],
                                                 rdict['coeff_errors'][-1]
                                                 ))
            g.new_series(rdict['x'],
                         rdict['y'],
                         plotid=pi, color='black')
            kw = dict(color='red',
                         line_style='dash',
                         plotid=pi)

            g.new_series(rdict['upper_x'],
                         rdict['upper_y'],
                         **kw
                         )
            g.new_series(rdict['lower_x'],
                         rdict['lower_y'],
                         **kw
                         )
            g.redraw()

    def _build_tables(self, gn):
        dm = self.data_manager
        #build tables
        for di in self._active_detectors:
            dm.new_table('/{}'.format(gn), di.name)

    def _peak_hop(self, name, detector, isotopes, ncounts, starttime, series):
        self.info('peak hopping {} detector={}'.format(name, detector))
        spec = None
        sm = self.spectrometer_manager
        if sm:
            spec = sm.spectrometer
        graph = self.plot_panel.graph
        for i in xrange(0, ncounts, 1):
            for mi, iso in enumerate(isotopes):
                ti = self.integration_time * 0.99 if not self._debug else 0.01
                time.sleep(ti)
                if spec is not None:
                    #position isotope onto detector
                    self.set_position(iso, detector)

                x = time.time() - starttime

                signals = [1200 * (1 + random.random()),
                        3.5 * (1 + random.random())]

                v = signals[mi]

                kw = dict(series=series, do_after=1,)
                if len(graph.series[mi]) < series + 1:
                    kw['marker'] = 'circle'
                    kw['type'] = 'scatter'
                    kw['marker_size'] = 1.25
                    graph.new_series(x=[x], y=[v], plotid=mi, **kw)
                else:
                    graph.add_datum((x, v), plotid=mi, ** kw)

                if x > graph.get_x_limits()[1]:
                    graph.set_x_limits(0, x + 10)

    def _measure_iteration(self, grpname, data_write_hook,
                           ncounts, starttime, series):

        self.info('measuring {}'.format(grpname))

        spec = self.spectrometer_manager.spectrometer
        graph = self.plot_panel.graph
        for i in xrange(0, ncounts, 1):
            if i > self.plot_panel.ncounts:
                break

            if not self._alive:
                return False

            if i % 50 == 0:
                self.info('collecting point {}'.format(i + 1))

            m = self.integration_time * 0.99 if not self._debug else 0.1
            time.sleep(m)

            if not self._debug:
                data = spec.get_intensities(tagged=True)
                if data is not None:
                    keys, signals = data
#                keys, signals = zip(*data)
            else:
                keys = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']

                if series == 0:
                    signals = [10, 1000, 8, 8, 8, 3]
                elif series == 1:
                    r = random.randint(0, 75)
                    signals = [0.1, (0.015 * (i - 2800 + r)) ** 2,
                               0.1, 1, 0.1, (0.001 * (i - 2000 + r)) ** 2
                               ]
                else:
                    signals = [1, 2, 3, 4, 5, 6]

            x = time.time() - starttime# if not self._debug else i + starttime
            data_write_hook(x, keys, signals)

            self.signals = dict(zip(keys, signals))

            kw = dict(series=series, do_after=1, update_y_limits=True)
            if len(graph.series[0]) < series + 1:
                kw['marker'] = 'circle'
                kw['type'] = 'scatter'
                kw['marker_size'] = 1.25
                func = lambda x, signal, kw: graph.new_series(x=[x],
                                                                 y=[signal],
                                                                 **kw
                                                                 )
            else:
                func = lambda x, signal, kw: graph.add_datum((x, signal), **kw)

            dets = self._active_detectors
            for pi, dn in enumerate(dets):
                signal = signals[keys.index(dn.name)]
                kw['plotid'] = pi
                func(x, signal, kw)

            if (i and i % 100 == 0) or x > graph.get_x_limits()[1]:
                graph.set_x_limits(0, x + 10)

        return True

    def _load_script(self, name):
        ec = self.configuration
        fname = os.path.basename(ec['{}_script'.format(name)])
        if fname in self.scripts:
            self.info('script "{}" already loaded... cloning'.format(fname))
            s = self.scripts[fname]
            if s is not None:
                s = s.clone_traits()
                s.automated_run = self
                s.runtype = self.runtype
        else:
            self.info('loading script "{}"'.format(fname))
            func = getattr(self, '{}_script_factory'.format(name))
            s = func(ec)

            setattr(self, '_{}_script'.format(name), s)
            if s.bootstrap():
                try:
                    s._test()
                except Exception, e:
                    self.warning(e)
                    self.executable = False
        return s

    def pre_extraction_save(self):
        # set our aliquot
        db = self.db
        identifier = self.identifier
        if identifier == 'B':
            identifier = 1
        elif identifier == 'A':
            identifier = 2

        ln = db.get_labnumber(identifier)
        if ln is not None:
            aliquot = ln.aliquot + 1
            self.aliquot = aliquot
        else:
            self.warning('invalid lab number {}'.format(self.identifier))

        d = get_datetime()
        self._runtime = d.time()
        self.info('analysis started at {}'.format(self._runtime))
        self._rundate = d.date()

    def _post_extraction_save(self):
        pass

    def _pre_measurement_save(self):
        self.info('pre measurement save')
        dm = self.data_manager
        #make a new frame for saving data

        #the new frame is untracked and will be added to the git repo
        #at post_measurement_save
        dm.new_frame(
                     path=os.path.join(self.repository.root,
                                       '{}-{}.h5'.format(self.identifier, self.aliquot)
                                       )
#                     directory=self.repository.root,
#                     directory='automated_runs',
#                     base_frame_name='{}-{}'.format(self.identifier, self.aliquot)

                     )


        #create initial structure
        dm.new_group('baselines')
        dm.new_group('sniffs')
        dm.new_group('signals')

    def _post_measurement_save(self):
        self.info('post measurement save')
        db = self.db
        if db:
        #save to a database
#            self.labnumber = 1
            identifier = self.identifier
            aliquot = self.aliquot

            sample = self.sample
            if identifier == 'B':
                identifier = 1
                sample = 'BoneBlank'
            elif identifier == 'A':
                identifier = 2
                sample = 'Air'
            else:
                identifier = int(identifier)

            lab = db.add_labnumber(identifier, aliquot, sample=sample)

            self.info(self.experiment_name)
            experiment = db.get_experiment(self.experiment_name)
            d = get_datetime()

            self.info('analysis finished at {}'.format(d.time()))
            a = db.add_analysis(lab, runtime=self._runtime,
                                    rundate=self._rundate,
                                    endtime=d.time()
                                )
            experiment.analyses.append(a)

            db.add_extraction(
                              a,
                              self.extraction_script.name,
                              script_blob=self.measurement_script.toblob()
                              )
            db.add_measurement(
                              a,
                              self.measurement_script.name,
                              script_blob=self.measurement_script.toblob()
                              )

            p = self.data_manager.get_current_path()

            #use a path relative to the repo repo
            p = './' + os.path.relpath(p, self.repository.root)
            db.add_analysis_path(p, analysis=a)
            db.commit()

        #save to massspec
        self._save_to_massspec()

        #close h5 file
        self.data_manager.close()

        #version control new analysis
#        self._version_control_analysis(p, a)


    def _version_control_analysis(self, apath, analysis):
        repo = self.repository

        ln = analysis.labnumber
        identifier = '{}-{}'.format(ln.labnumber, ln.aliquot)

        #add files to repo and commit
        repo.add(os.path.basename(apath))
        dbname = os.path.basename(self.db.dbname)
        repo.add(dbname)
        repo.commit('added analysis {}, updated isotopedb'.format(identifier))
        repo.push()

    def _save_to_massspec(self):
        self.info('saving to massspec database')
#        #save to mass spec database
        dm = self.data_manager
        baselines = []
        signals = []
        detectors = []
        for det in self._active_detectors:
            ai = det.name
            detectors.append((ai, det.isotope))

            table = dm.get_table(ai, '/baselines')
            if table:
                bi = [(row['time'], row['value']) for row in table.iterrows()]
                baselines.append(bi)

            table = dm.get_table(ai, '/signals')
            if table:
                si = [(row['time'], row['value']) for row in table.iterrows()]
                signals.append(si)

        self.massspec_importer.add_analysis(self.identifier,
                                            self.aliquot,
                                            self.identifier,
                                            baselines,
                                            signals,
                                            detectors,
                                            self.regression_results
#                                            self.irrad_level,
#                                            self.sample,
#                                            self.runtype
                                            )
#===============================================================================
# property get/set
#===============================================================================
    def _get_data_writer(self, grpname):
        dm = self.data_manager
        def write_data(x, keys, signals):
#            print x, keys, signals
#            print grpname
            for det in self._active_detectors:
                k = det.name
                t = dm.get_table(k, '/{}'.format(grpname))
                nrow = t.row
                nrow['time'] = x
                nrow['value'] = signals[keys.index(k)]
                nrow.append()
                t.flush()

        return write_data

    @cached_property
    def _get_post_measurement_script(self):
        self._post_measurement_script = self._load_script('post_measurement')
        return self._post_measurement_script

    @cached_property
    def _get_post_equilibration_script(self):
        self._post_equilibration_script = self._load_script('post_equilibration')
        return self._post_equilibration_script

    @cached_property
    def _get_measurement_script(self):
        self._measurement_script = self._load_script('measurement')
        return self._measurement_script

    @cached_property
    def _get_extraction_script(self):
        self._extraction_script = self._load_script('extraction')
        return self._extraction_script

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, v):
        self._index = v

    def _get_duration(self):
        if self.heat_step:
            d = self.heat_step.duration
        else:
            d = self._duration
        return d

#    def _get_temp_or_power(self):
#        if self.heat_step:
#
#            t = self.heat_step.temp_or_power
#        else:
#            t = self._temp_or_power
#        return t
#    def _get_temp_or_power(self):
#        if self.heat_step:
#
#            t = self.heat_step.temp_or_power
#        else:
#            t = self._temp_or_power
#        return t
    def _get_heat_units(self):
        units = dict(t='temp', w='watts', p='percent')
        return units[self._heat_units]

    def _set_heat_units(self, v):
        self._heat_units = v

    def _get_heat_value(self):
        if self.heat_step:
            v = self.heat_step.heat_value
            u = self.heat_step.heat_units
        else:
            v = self._heat_value
            u = self._heat_units
        return (v, u)

    def _validate_duration(self, d):
        return self._validate_float(d)

#    def _validate_temp_or_power(self, d):
#        return self._validate_float(d)
    def _validate_heat_value(self, d):
        return self._validate_float(d)
    def _validate_float(self, d):
        try:
            return float(d)
        except ValueError:
            pass

    def _set_duration(self, d):
        if d is not None:
            if self.heat_step:
                self.heat_step.duration = d
            else:
                self._duration = d

    def _set_heat_value(self, t):
        if t is not None:
            if self.heat_step:
                self.heat_step.heat_value = t
            else:
                self._heat_value = t

#===============================================================================
# views
#===============================================================================
    def traits_view(self):

#        scripts = VGroup(
#                       Item('extraction_line_script_name',
#                        editor=EnumEditor(name='extraction_line_scripts'),
#                        label='Extraction'
#                        ),
#                       Item('measurement_script_name',
#                            editor=EnumEditor(name='measurement_scripts'),
#                            label='Measurement'
#                            ),
#                       label='Scripts',
#                       show_border=True
#                       )
        def readonly(n, **kw):
            return Item(n, style='readonly', **kw)

        v = View(
                 VGroup(
                     Group(
                     HGroup(Item('identifier'),
                            readonly('aliquot')
                            ),
                     readonly('sample'),
                     readonly('irrad_level', label='Iradiation'),
                     Item('weight'),
                     Item('comment'),
                     show_border=True,
                     label='Info'
                     ),
                     Group(
                         Item('heat_device', editor=EnumEditor(values=HEATDEVICENAMES)),
                         Item('autocenter'),
                         Item('position'),
                         Item('multiposition', label='Multi. position run'),
                         Item('endposition'),
                         show_border=True,
                         label='Position'
                     ),
#                     scripts,
                     )
                 )
        return v
#============= EOF =============================================

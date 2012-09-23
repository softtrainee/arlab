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
from traits.api import Instance, Enum, Any, DelegatesTo, List, Property, Str, \
     on_trait_change, Bool, Int
from traitsui.api import View, VGroup, HGroup, Group, Item, Spring, spring, Label, \
     ListEditor, InstanceEditor, EnumEditor
from traits.api import HasTraits, Range, Float
from pyface.timer.api import Timer
#============= standard library imports ========================
import random
import os
import pickle
#============= local library imports  ==========================
#'black', 'red', 'violet', 'maroon', 'yellow',
from src.managers.manager import Manager
from src.graph.time_series_graph import TimeSeriesStreamGraph
#from src.helpers.timer import Timer

from src.spectrometer.detector import Detector
from src.spectrometer.tasks.magnet_scan import MagnetScan
from src.spectrometer.tasks.rise_rate import RiseRate
from src.paths import paths
from chaco.log_mapper import LogMapper
from chaco.linear_mapper import LinearMapper
from src.graph.tools.data_tool import DataTool, DataToolOverlay
from chaco.data_range_1d import DataRange1D

class Magnet(HasTraits):
    dac = Range(0.0, 6.0)
    def map_mass_to_dac(self, d):
        return d

class Source(HasTraits):
    y_symmetry = Float

class DummySpectrometer(HasTraits):
    detectors = List
    magnet = Instance(Magnet, ())
    source = Instance(Source, ())
    def get_intensities(self):
        return [d.name for d in self.detectors], [random.random() + (i * 12.3) for i in range(len(self.detectors))]

    def get_intensity(self, *args, **kw):
        return 1

class ScanManager(Manager):
    spectrometer = Any

    graph = Instance(TimeSeriesStreamGraph)
    integration_time = Enum(0.065536, 0.131072, 0.262144, 0.524288,
                            1.048576, 2.097152, 4.194304, 8.388608,
                            16.777216, 33.554432, 67.108864)

    detectors = DelegatesTo('spectrometer')
    detector = Instance(Detector)
    magnet = DelegatesTo('spectrometer')
    source = DelegatesTo('spectrometer')
    scanner = Instance(MagnetScan)
    rise_rate = Instance(RiseRate)
    isotope = Str
    isotopes = Property

    graph_scale = Enum('linear', 'log')
    graph_ymin_auto = Bool(True)
    graph_ymax_auto = Bool(True)

    graph_ymin = Property(Float, depends_on='_graph_ymin')
    graph_ymax = Property(Float, depends_on='_graph_ymax')
    _graph_ymin = Float
    _graph_ymax = Float
    graph_scan_width = Int(1000) #in secs

    def _update_graph_limits(self, name, new):
#        print name, new
        if 'high' in name:
            self._graph_ymax = new
        else:
            self._graph_ymin = new

    def _toggle_detector(self, obj, name, old, new):
        self.graph.set_series_visiblity(new, series=obj.name)

    def opened(self):

        self.graph = self._graph_factory()

        self._start_timer()

        #listen to detector for enabling 
        self.on_trait_change(self._toggle_detector, 'detectors.active')

        #force update
        self.load_settings()

    def load_settings(self):
        self.info('load scan settings')
        spec = self.spectrometer
        p = os.path.join(paths.hidden_dir, 'scan_settings')
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                try:
                    params = pickle.load(f)
                    self.detector = spec.get_detector(params['detector'])
                    self.isotope = params['isotope']

                    for pi in self.graph_attr_keys:
                        try:
                            setattr(self, pi, params[pi])
                        except KeyError, e:
                            print pi, e
#                    self.graph_scale = params['graph_scale']
#                    self.graph_scale = params['graph_scale']
#                    self.graph_scale = params['graph_scale']
#                    for pi in ['graph_ymin','graph_ymax']:


                except (pickle.PickleError, EOFError, KeyError):
                    self.detector = self.detectors[-1]
                    self.isotope = self.isotopes[-1]

    def dump_settings(self):
        self.info('dump scan settings')
        p = os.path.join(paths.hidden_dir, 'scan_settings')
        with open(p, 'wb') as f:
            iso=self.isotope
            if not iso:
                iso=self.isotopes[0]
                
            det=self.detector
            if not det:
                det=self.detectors[0]
                
            d = dict(isotope=iso,
                     detector=det.name)
#            print type(det), type(iso)
#            d=dict()
            for ki in self.graph_attr_keys:
                d[ki] = getattr(self, ki)
#            
#            print d
            pickle.dump(d, f)

    @property
    def graph_attr_keys(self):
        return ['graph_scale',
                'graph_ymin', 'graph_ymax',
                'graph_ymin_auto', 'graph_ymax_auto',
                ]
    def close(self, isok):
        self._stop_timer()
        self.dump_settings()

        #clear our graph settings so on reopen events will fire
        del self.graph_scale

#    @on_trait_change('spectrometer:intensity_dirty')
#    def _update_scan_graph(self, new):
    def _update_scan_graph(self):
        data = self.spectrometer.get_intensities()
        if data:
            _, signals = data
#            _, signals = zip(*[(k, v) for k, v in new.iteritems()])
#            _, signals = zip(*new.iteritems())
            self.graph.record_multiple(signals,
                                       track_y=False,
#                                       track_y=s,
                                       #track_y_pad=1
                                       )

    def _start_timer(self):
        self._first_iteration = True

        self.info('starting scan timer')
        self.integration_time = 1.048576
        self.timer = self._timer_factory()

    def _stop_timer(self):
        self.info('stopping scan timer')
        self.timer.Stop()
#===============================================================================
# handlers
#===============================================================================
    def _set_position(self):
        if self.isotope and self.detector:
            self.info('set position {} on {}'.format(self.isotope, self.detector))
            self.ion_optics_manager.position(self.isotope, self.detector.name)

    def _isotope_changed(self):
        self._set_position()

    def _graph_changed(self):
        self.rise_rate.graph = self.graph

        plot = self.graph.plots[0]
        plot.value_range.on_trait_change(self._update_graph_limits, '_low_value, _high_value')
#        plot.value_range.on_trait_change(self._update_graph_limits, '_high_value')

    def _detector_changed(self):
        if self.detector:
            self.scanner.detector = self.detector
            self.rise_rate.detector = self.detector
            nominal_width = 1
            emphasize_width = 2
            for name, plot in self.graph.plots[0].plots.iteritems():
                plot = plot[0]
                plot.line_width = emphasize_width if name == self.detector.name else nominal_width

            self._set_position()

    def _graph_ymin_auto_changed(self, new):
        p = self.graph.plots[0]
        if new:
            p.value_range.low_setting = 'auto'
        else:
            p.value_range.low_setting = self.graph_ymin
        self.graph.redraw()

    def _graph_ymax_auto_changed(self, new):
        p = self.graph.plots[0]
        if new:
            p.value_range.high_setting = 'auto'
        else:
            p.value_range.high_setting = self.graph_ymax
        self.graph.redraw()

    def _graph_scale_changed(self, new):
        p = self.graph.plots[0]
        dr = p.value_range
        hp = p.value_mapper.high_pos
        lp = p.value_mapper.low_pos
        d = dict(high_pos=hp, low_pos=lp)
        if new == 'log':
            klass = LogMapper
            d['range']=DataRange1D(low_setting=max(0.01,dr.low), high_setting=dr.high_setting)
        else:
            klass = LinearMapper
            d['range']=dr
            
#        for pi in p.plots.itervalues():
#            pi[0].value_mapper=klass(**d)
            
        p.value_mapper = klass(**d)
        self.graph.redraw()

    def _graph_scan_width_changed(self):
        g = self.graph
        n = self.graph_scan_width
        n = max(n, 1)
        g.data_limits[0] = n
        g.set_x_tracking(n * 1.01)

#===============================================================================
# factories
#===============================================================================
    def _timer_factory(self, func=None):

        if func is None:
            func = self._update_scan_graph

        mult = 1000

        return Timer((self.integration_time + 0.025) * mult, self._update_scan_graph)

    def _graph_factory(self):
        g = TimeSeriesStreamGraph(container_dict=dict(bgcolor='gray',
                                                      padding=5
                                                      )

                                  )
        n = 1000
        g.new_plot(padding=[50, 5, 5, 50],
                   data_limit=n,
                   xtitle='Time',
                   ytitle='Signal',
                   scale=self.graph_scale
                   )

        g.set_x_tracking(n * 1.01)
        for i, det in enumerate(self.detectors):
#            if not det.active:
            g.new_series(visible=det.active, color=det.color)
            g.set_series_label(det.name)
            det.series_id = i

        p = g.plots[0]
#        print p, p.plots
        cp = p.plots[det.name][0]
#        print cp
        dt = DataTool(plot=cp, component=p,
                      normalize_time=True,
                      use_date_str=False)
        dto = DataToolOverlay(
                              component=p,
                              tool=dt)
        p.tools.append(dt)
        p.overlays.append(dto)
#        for det in self.detectors:
#            g.set_series_visiblity(det.active, series=det.name, do_later=10)

        return g

#===============================================================================
# property get/set
#===============================================================================
    def _get_isotopes(self):
        molweights = self.spectrometer.molecular_weights
        return sorted(molweights.keys(), key=lambda x: int(x[2:]))

    def _validate_graph_ymin(self, v):
        try:
            v = float(v)
            if v < self.graph_ymax:
                return v
        except ValueError:
            pass

    def _validate_graph_ymax(self, v):
        try:
            v = float(v)
            if v > self.graph_ymin:
                return v
        except ValueError:
            pass

    def _get_graph_ymin(self):
        return self._graph_ymin

    def _get_graph_ymax(self):
        return self._graph_ymax

    def _set_graph_ymin(self, v):
        if v is not None:
            self._graph_ymin = v
            p = self.graph.plots[0]
            p.value_range.low_setting = v
            self.graph.redraw()

    def _set_graph_ymax(self, v):
        if v is not None:
            self._graph_ymax = v
            p = self.graph.plots[0]
            p.value_range.high_setting = v
            self.graph.redraw()

#===============================================================================
# defaults
#===============================================================================
    def _graph_default(self):
        return self._graph_factory()

    def _rise_rate_default(self):
        r = RiseRate(spectrometer=self.spectrometer,
                     graph=self.graph)
        return r

    def _scanner_default(self):
        s = MagnetScan(spectrometer=self.spectrometer)
        return s
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        custom = lambda n:Item(n, style='custom', show_label=False)
        magnet_grp = VGroup(
                            HGroup(
                                Item('detector',
                                     show_label=False,
                                     editor=EnumEditor(name='detectors')),
                                Item('isotope',
                                     show_label=False,
                                     editor=EnumEditor(name='isotopes')
                                     )),
                            custom('magnet'),
                            custom('scanner'),
                            label='Magnet'
                            )
        detector_grp = VGroup(
                              HGroup(Spring(springy=False, width=120), Label('Deflection')),
                              Item('detectors',
                                   show_label=False,
                                   editor=ListEditor(style='custom', mutable=False, editor=InstanceEditor())),
                              label='Detectors'
                              )

        rise_grp = custom('rise_rate')
        source_grp = custom('source')
        graph_cntrl_grp = VGroup(
                                 HGroup(Item('graph_scan_width', label='Scan Width'), spring),
                                 HGroup(Item('graph_scale', show_label=False,), spring),
                                 HGroup(spring, Label('Auto')),
                                 HGroup(
                                        Item('graph_ymax',
                                             enabled_when='not graph_ymax_auto',
                                             format_str='%0.3f', label='Y max'),
                                        spring,
                                        Item('graph_ymax_auto', show_label=False)
                                        ),
                                 HGroup(
                                        Item('graph_ymin',
                                             enabled_when='not graph_ymin_auto',
                                             format_str='%0.3f', label='Y min'),
                                        spring,
                                        Item('graph_ymin_auto', show_label=False)
                                        ),

#                                 Item('graph_ymin', label='Y min')
                                 )
        control_grp = Group(
                          graph_cntrl_grp,
                          detector_grp,
                          source_grp,
                          rise_grp,
                          magnet_grp,
                          layout='tabbed')
        intensity_grp = VGroup(
                               HGroup(spring, Label('Intensity'),
                                      Spring(springy=False, width=23),
                                      Label(u'1\u03c3'),
                                      Spring(springy=False, width=87)),
                               Item('detectors',
                                   show_label=False,
                                   editor=ListEditor(style='custom', mutable=False,
                                                     editor=InstanceEditor(view='intensity_view'))))
        graph_grp = custom('graph')
        v = View(
                    HGroup(
                           VGroup(control_grp, intensity_grp),
                           graph_grp,
                           ),
                    title='Scan',
                    resizable=True,
                    handler=self.handler_klass,
                    width=0.8,
                    height=0.6
                    )
        return v


if __name__ == '__main__':

    detectors = [
             Detector(name='H2',
                      color='black',
                      isheader=True
                      ),
             Detector(name='H1',
                      color='red'
                      ),
             Detector(name='AX',
                      color='violet'
                      ),
             Detector(name='L1',
                      color='maroon'
                      ),
             Detector(name='L2',
                      color='yellow'
                      ),
             Detector(name='CDD',
                      color='lime green',
                      active=False
                      ),

             ]
    sm = ScanManager(
#                     detectors=detectors,
                     spectrometer=DummySpectrometer(detectors=detectors))
#    sm.load_detectors()
    sm.configure_traits()
#============= EOF =============================================

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

#=============enthought library imports=======================
from traits.api import Bool, Any, Instance, Button, Property, Event, on_trait_change
from traitsui.api import View, Item, Handler, HGroup
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
from threading import Thread
from threading import Event as TEvent
from numpy import linspace, argmin, argmax, random
import time
import os
#============= local library imports  ==========================
from src.data_processing.time_series.time_series import smooth
from src.image.cvwrapper import grayspace, get_focus_measure, crop, resize
from scipy.ndimage.measurements import variance
from scipy.ndimage.filters import generic_gradient_magnitude, sobel
from scipy.ndimage import sum as ndsum
from src.paths import paths
from src.managers.manager import Manager
from src.image.image import Image
from src.machine_vision.focus_parameters import FocusParameters
from src.image.image_editor import ImageEditor
from src.graph.graph import Graph
from pyface.timer.do_later import do_later


class ConfigureHandler(Handler):
    def closed(self, info, isok):
        if isok:
            info.object.dump_parameters()


class AutofocusManager(Manager):
    '''
        currently uses passive focus techniques
        see

        http://en.wikipedia.org/wiki/Autofocus

    '''

    video = Any
    laser_manager = Any
    stage_controller = Any
    canvas = Any
    parameters = Instance(FocusParameters)
    configure_button = Button('configure')

    autofocus_button = Event
    autofocus_label = Property(depends_on='autofocusing')
    autofocusing = Bool

    #threading event for cancel signal
    _evt_autofocusing = None

    image = Instance(Image, ())

    graph = None

    def dump_parameters(self):
        p = os.path.join(paths.hidden_dir, 'autofocus_configure')
        self.info('dumping parameters to {}'.format(p))
        with open(p, 'wb') as f:
            pickle.dump(self.parameters, f)

    def load_parameter(self):
        p = os.path.join(paths.hidden_dir, 'autofocus_configure')
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                try:
                    params = pickle.load(f)
                    self.info('loading parameters from {}'.format(p))
                    return params
                except Exception:
                    return FocusParameters()
        else:
            return FocusParameters()

    def passive_focus(self):
#        manager = self.laser_manager
        oper = self.parameters.operator
        self.info('passive focus. operator = {}'.format(oper))

#        if '2step' in oper:
#            target = self._passive_focus_2step
#            kw = dict(operator=oper.split('-')[1])
#        else:
#            target = self._passive_focus_1step
#            kw = dict(operator=oper,
#                      )
#            try:
#                kw['zoom'] = self.parameters.zoom
#            except AttributeError:
#                pass

        g = Graph(plotcontainer_dict=dict(padding=10),
                  window_x=0.70,
                  window_y=20,
                  window_width=325,
                  window_height=325,
                  window_title='Autofocus'
                  )
        g.new_plot(padding=[40, 10, 10, 40],
                   xtitle='Z (mm)',
                   ytitle='Focus Measure ({})'.format(oper)
                   )
        g.new_series()
        g.new_series()
        self.graph = g
        do_later(self._open_graph)

        target = self._passive_focus
        self._passive_focus_thread = Thread(name='autofocus', target=target,
                                            args=(self._evt_autofocusing)
                                            )
        self._passive_focus_thread.start()

    def _open_graph(self):
        ui = self.graph.edit_traits()
        self.add_window(ui)

    def stop_focus(self):

        if self.stage_controller:
            self.stage_controller.stop()

        self.info('autofocusing stopped by user')

    def _passive_focus(self, stop_signal):
        '''
            sweep z looking for max focus measure
            FMgrad= roberts or sobel (sobel removes noise)
            FMvar = intensity variance
        '''

        self.autofocusing = True

        manager = self.laser_manager
        fstart = self.parameters.fstart
        fend = self.parameters.fend
        step_scalar = self.parameters.step_scalar
        zoom = self.parameters.zoom
        operator = self.parameters.operator

        steps = step_scalar * (max(fend, fstart) - min(fend, fstart)) + 1

        prev_zoom = None
        if manager is not None:
            if zoom:
                prev_zoom = manager.zoom
                self.info('setting zoom: {}'.format(zoom))
                manager.set_zoom(zoom, block=True)

        args = self._do_focusing(fstart, fend, steps, operator)

        if manager is not None:
            if prev_zoom is not None:
                self.info('returning to previous zoom: {}'.format(prev_zoom))
                manager.set_zoom(prev_zoom, block=True)

        if args:
            mi, fmi, ma, fma = args

            self.info('''passive focus results:Operator={}
ImageGradmin={} (z={})
ImageGradmax={}, (z={})'''.format(operator, mi, fmi, ma, fma))
            self.info('calculated focus z= {}'.format(fma))

#            if set_z:
            controller = self.stage_controller
            if controller is not None:
                if not stop_signal.isSet():
                    controller.single_axis_move('z', fma, block=True)
                    controller._z_position = fma
                    controller.z_progress = fma

        self.autofocusing = False

    def _cancel_sweep(self, vo):
        if self._evt_autofocusing.isSet():
            #return to original velocity
            self.autofocusing = False
            self._reset_velocity(vo)
            return True

    def _reset_velocity(self, vo):
        if self.stage_controller:
            pdict = dict(velocity=vo, key='z')
            self.stage_controller._set_single_axis_motion_parameters(pdict=pdict)

    def _do_focusing(self, start, end, steps, operator):
        roi = self._get_roi()
        self._add_focus_area_rect(*roi)


        '''
            start the z in motion and take pictures as you go
            query stage_controller to get current z
        '''

        self.info('focus sweep start={} end={}'.format(start, end))
        #move to start position
        controller = self.stage_controller
        if controller:
            vo = controller.axes['z'].velocity
            if self._cancel_sweep(vo):
                return
            self.graph.set_x_limits(min(start, end), max(start, end), pad=2)
            #sweep 1 and velocity 1
            self._do_sweep(start, end, velocity=self.parameters.velocity_scalar1)
            fms, focussteps = self._collect_focus_measures(operator, roi)

            #reached end of sweep
            #calculate a nominal focal point    
            args = self._calculate_nominal_focal_point(fms, focussteps)
            nfocal = args[3]

            nwin = self.parameters.negative_window
            pwin = self.parameters.positive_window

            if self._cancel_sweep(vo):
                return
            nstart, nend = max(0, nfocal - nwin), nfocal + pwin
            mi = min(min(nstart, nend), min(start, end))
            ma = max(max(nstart, nend), max(start, end))
            self.graph.set_x_limits(mi, ma, pad=2)
            # do a slow tight sweep around the nominal focal point
            self._do_sweep(nstart, nend, velocity=self.parameters.velocity_scalar2)
            fms, focussteps = self._collect_focus_measures(operator, roi, series=1)

            self._reset_velocity(vo)

        else:
            focussteps = linspace(0, 10, 11)
            fms = -(focussteps - 5) ** 2 + 10 + random.random(11)

        self.info('frames analyzed {}'.format(len(fms)))

        self.canvas.markupcontainer.pop('croprect')
        return self._calculate_nominal_focal_point(fms, focussteps)

    def _do_sweep(self, start, end, velocity=None):
        controller = self.stage_controller
        controller.single_axis_move('z', start, block=True)
        time.sleep(0.05)
        #explicitly check for motion
        controller.block(axis='z')

        if velocity:
            vo = controller.axes['z'].velocity
            controller._set_single_axis_motion_parameters(pdict=dict(velocity=vo * velocity,
                                                    key='z'))

        controller.single_axis_move('z', end)

    def _collect_focus_measures(self, operator, roi, series=0):
        controller = self.stage_controller
        focussteps = []
        fms = []
        while controller.timer.IsRunning() and not self._evt_autofocusing.isSet():
            src = self._load_source()
            x = controller.get_current_position('z')
            y = self._calculate_focus_measure(src, operator, roi)
            focussteps.append(x)
            fms.append(y)
            self.graph.add_datum((x, y), series=series, do_after=1)
            time.sleep(0.05)
        return fms, focussteps

    def _calculate_nominal_focal_point(self, fms, focussteps):

        sfms = smooth(fms)
        fmi = focussteps[argmin(sfms)]
        fma = focussteps[argmax(sfms)]

        mi = min(sfms)
        ma = max(sfms)

        return mi, fmi, ma, fma

    def _calculate_focus_measure(self, src, operator, roi):
        '''
            see
            IMPLEMENTATION OF A PASSIVE AUTOMATIC FOCUSING ALGORITHM
            FOR DIGITAL STILL CAMERA
            DOI 10.1109/30.468047
            and
            http://cybertron.cg.tu-berlin.de/pdci10/frankencam/#autofocus
        '''

        #need to resize to 640,480. this is the space the roi is in
        s = resize(grayspace(src), 640, 480)
        v = crop(s, *roi, mat=False)

        di = dict(var=lambda x:variance(x),
                  laplace=lambda x: get_focus_measure(x, 'laplace'),
                  sobel=lambda x: ndsum(generic_gradient_magnitude(x, sobel, mode='nearest'))
                  )

        func = di[operator]
        return func(v)
#        if operator == 'var':
#            '''
#                slow version. use scipy.ndimage... variance for fast computation 2x speedup
#                ni, nj = v.shape
#                genx = xrange(ni)
#                geny = xrange(nj)
#
#                mu = 1 / float(ni * nj) * sum([v[i, j] for i in genx for j in geny])
#                func = lambda g, i, j:abs(g[i, j] - mu) ** 2
#                fm = 1 / float(ni * nj) * sum([func(v, i, j) for i in genx for j in geny])
#            '''
#            fm = variance(v)
#        elif operator == 'laplace':
#            fm = get_focus_measure(v, 'laplace')
#        else:
#            fm = ndsum(generic_gradient_magnitude(v, sobel, mode='nearest'))
#        return fm

    def image_view(self):
        v = View(Item('image', show_label=False, editor=ImageEditor(),
                      width=640,
                      height=480,
                       style='custom'))
        return v

    def traits_view(self):
        v = View(
               HGroup(self._button_factory('autofocus_button', 'autofocus_label'),
                      Item('configure_button', show_label=False),
                      show_border=True,
                      label='Autofocus'
                      )
               )
        return v

    def configure_view(self):
        v = View(Item('parameters', style='custom', show_label=False),
               handler=ConfigureHandler,
               buttons=['OK', 'Cancel'],
               kind='livemodal',
               title='Configure Autofocus',
               x=0.80,
               y=0.05
               )
        return v

    def _load_source(self):
        src = self.video._frame
        if src:
            self.image.load(src)

        return self.image.source_frame

    def _get_roi(self):
        w = self.parameters.crop_width
        h = self.parameters.crop_height

        cx = (640 * self.canvas.scaling - w) / 2
        cy = (480 * self.canvas.scaling - h) / 2
        roi = cx, cy, w, h

        return roi

    def _add_focus_area_rect(self, cx, cy, w, h):
        pl = self.canvas.padding_left
        pb = self.canvas.padding_bottom
        self.canvas.add_markup_rect(cx + pl, cy + pb, w, h)

    def _autofocus_button_fired(self):
        if not self.autofocusing:
            self.autofocusing = True
            self._evt_autofocusing = TEvent()
            self._evt_autofocusing.clear()
            self.passive_focus()
        else:
            self.autofocusing = False
            self._evt_autofocusing.Set()
            self.stop_focus()

    def _configure_button_fired(self):
        self._crop_rect_update()
        self.edit_traits(view='configure_view', kind='livemodal')
        try:
            self.canvas.markupcontainer.pop('croprect')
        except KeyError:
            pass

    @on_trait_change('parameters:[_crop_width,_crop_height]')
    def _crop_rect_update(self):
        roi = self._get_roi()
        self._add_focus_area_rect(*roi)

    def _get_autofocus_label(self):
        return 'Autofocus' if not self.autofocusing else 'Stop'


    def _parameters_default(self):
        return self.load_parameter()
#===============================================================================
# Deprecated
#===============================================================================
#    def discrete_sweep(self):
#        if self.parameters.discrete:
#            self.info_later('focus sweep start={} end={} steps={}'.format(start, end, steps))
#            focussteps = linspace(start, end, steps)
#            for fi in focussteps:
#                if controller is not None:
#                    controller.single_axis_move('z', fi, block=True)
#
#                s = self._load_source()
#                grads.append(self._calculate_focus_measure(operator, roi, src=s))
#
##            sgrads = smooth(grads)
##            fmi = focussteps[argmin(sgrads)]
##            fma = focussteps[argmax(sgrads)]
#        else:
#    def _passive_focus_2step(self, operator='laplace'):
#        '''
#            see
#            IMPLEMENTATION OF A PASSIVE AUTOMATIC FOCUSING ALGORITHM
#            FOR DIGITAL STILL CAMERA
#            DOI 10.1109/30.468047
#            and
#            http://cybertron.cg.tu-berlin.de/pdci10/frankencam/#autofocus
#        '''
#        args = self._passive_focus(operator=operator, set_z=False,
#                             velocity_scalar=self.parameters.velocity_scalar1
#                            )
#
#        if args:
#            nominal_focus1, fs1, gs1, sgs1 = args
#
#        fstart = nominal_focus1 - self.parameters.negative_window
#        fend = nominal_focus1 + self.parameters.positive_window
#
#        args = self._passive_focus(operator=operator,
#                             fstart=fstart,
#                             fend=fend,
#                             velocity_scalar=self.parameters.velocity_scalar2
#                             )
#
#        if args:
#            nominal_focus2, fs2, gs2, sgs2 = args
#            g = Graph()
#            g.new_plot(padding_top=30)
#            g.new_series(fs1, gs1)
#            g.new_series(fs1, sgs1)
#            g.new_plot(padding_top=30)
#            g.new_series(fs2, gs2, plotid=1)
#            g.new_series(fs2, sgs2, plotid=1)
#
#            g.set_x_title('Z', plotid=1)
#            g.set_x_title('Z', plotid=0)
#            g.set_y_title('FMsob', plotid=0)
#            g.set_y_title('FMsob', plotid=1)
#
#            g.add_vertical_rule(nominal_focus1)
#            g.add_vertical_rule(nominal_focus2, plotid=1)
#            g.add_vertical_rule(fstart, color=(0, 0, 1))
#            g.add_vertical_rule(fend, color=(0, 0, 1))
#            g.window_title = 'Autofocus'
#
#            #g.set_plot_title('Sobel', plotid=1)
#            #g.set_plot_title('Sobel')
#            do_later(g.edit_traits)
#        self.autofocusing = False
#
#    def _passive_focus_1step(self, operator, **kw):
#        nominal_focus, fs, gs, sgs = self._passive_focus(operator, **kw)
#
#        self.autofocusing = False
#
#        if self.graph is not None:
#            self.graph.close()
#
#        g = Graph()
#        g.new_plot(padding_top=20)
#        g.new_series(fs, gs)
#        g.new_series(fs, sgs)
#        g.add_vertical_rule(nominal_focus)
#        g.set_x_title('Z')
#        g.set_y_title('FM{}'.format(operator[:3]))
#        g.window_title = 'Autofocus'
#        g.window_x = 20
#        g.window_y = 400
#        do_later(g.edit_traits)
#        self.graph = g
#        self.autofocusing = False
#============= EOF =====================================

#        else:
#            '''
#             currently the slowest
#            '''
#            
##            fmx = _fm_(v, oper=operator)
##            fmy = _fm_(v, x=False, oper=operator)
##            fmh=hypot(fmx,fmy)
##            fms=fmx+fmy
##            print 'roberts slow',fmh, fms
###            
#            def roberts(input, axis = -1, output = None, mode = "constant", cval = 0.0):
#                output, return_value = _ni_support._get_output(output, input)
#                correlate1d(input, [1, 0], 0, output, mode, cval, 0)
#                correlate1d(input, [0, -1], 1, output, mode, cval, 0)
#                
#                correlate1d(input, [0, -1], 0, output, mode, cval, 0)
#                correlate1d(input, [1, 0], 1, output, mode, cval, 0)
#                
#                return return_value
#                
#                
#            fm =ndsum(generic_gradient_magnitude(v, roberts, mode='constant'))
#            
#            print 'roberts fast', fm
#        print operator, fm

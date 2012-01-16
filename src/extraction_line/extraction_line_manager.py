'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================
from traits.api import  Instance, Str
from traitsui.api import View, Item, HGroup
#=============standard library imports ========================
import os
import time
from threading import Thread
#=============local library imports  ==========================

from src.extraction_line.explanation.extraction_line_explanation import ExtractionLineExplanation
from src.extraction_line.extraction_line_canvas import ExtractionLineCanvas
#from src.monitors.pumping_monitor import PumpingMonitor
from src.helpers.paths import canvas2D_dir, scripts_dir
from src.scripts.extraction_line_script import ExtractionLineScript

from view_controller import ViewController
from src.managers.manager import Manager

#from src.managers.multruns_report_manager import MultrunsReportManager

#Macro = None
#start_recording = None
#stop_recording = None
#play_macro = None


class ExtractionLineManager(Manager):
    '''
    Manager for interacting with the extraction line
    contains 2 interaction canvases, 2D and 3D
    contains reference to valve manager, gauge manager and laser manager
    
    '''
    canvas = Instance(ExtractionLineCanvas)
    explanation = Instance(ExtractionLineExplanation)

    valve_manager = Instance(Manager)
    gauge_manager = Instance(Manager)
    environmental_manager = Instance(Manager)
    device_stream_manager = Instance(Manager)

    multruns_report_manager = Instance(Manager)
#    multruns_report_manager = Instance(MultrunsReportManager)

    view_controller = Instance(ViewController)

#    pumping_monitor = Instance(PumpingMonitor)

    runscript = None

    def get_subsystem_module(self, subsystem, module):
        '''
        '''
        try:
            ss = getattr(self, subsystem)
            return ss.get_module(module)
        except AttributeError:
            self.warning('{} not initialized'.format(subsystem))

    def create_manager(self, manager):
        '''
        '''
        klass = self.convert_config_name(manager)
        kw = dict(name=manager)

        kw['parent'] = self

        gdict = globals()
        if klass in gdict:

            class_factory = gdict[klass]

        else:
            #try a lazy load of the required module
            if 'fusions' in manager:
                package = 'src.managers.laser_managers.{}'.format(manager)
                self.laser_manager_id = manager
            else:
                package = 'src.managers.{}'.format(manager)

            class_factory = self.get_manager_factory(package, klass)

        if class_factory:
            kw['application'] = self.application
            m = class_factory(**kw)

            if manager in ['gauge_manager', 'valve_manager',
                           'environmental_manager', 'device_stream_manager',
                           'multruns_report_manager'
                           ]:
                self.trait_set(**{manager:m})
            else:
                self.add_trait(manager, m)

            #m.exit_on_close = False

            return m

    def finish_loading(self):
        '''
        '''
        pass
#        if self.gauge_manager is not None:
#            self.gauge_manager.on_trait_change(self.pressure_update, 'gauges.pressure')

    def opened(self):
        super(ExtractionLineManager, self).opened()
        self.reload_scene_graph()

#    def _view_controller(self):
#        print self.ui.control
#        self.view_controller.edit_traits(kind = 'livemodal',
#                                      parent = self.ui.control)

#    def show_device_streamer(self):
#        self.device_stream_manager.edit_traits(parent=self.window.control)
    def bind_preferences(self):
        from apptools.preferences.preference_binding import bind_preference
        bind_preference(self.canvas, 'style', 'pychron.extraction_line.style')
        bind_preference(self.canvas, 'width', 'pychron.extraction_line.width')
        bind_preference(self.canvas, 'height', 'pychron.extraction_line.height')

        bind_preference(self, 'enable_close_after', 'pychron.extraction_line.enable_close_after')
        bind_preference(self, 'close_after_minutes', 'pychron.extraction_line.close_after')

        from src.extraction_line.plugins.extraction_line_preferences_page import get_valve_group_names

        for name in get_valve_group_names():
            self.add_trait(name, Str(''))
            self.on_trait_change(self._owner_change, name)
            bind_preference(self, name, 'pychron.extraction_line.{}'.format(name))

    def _owner_change(self, name, value):
        self.valve_manager.claim_section(name.split('_')[0], value.lower)

    def reload_scene_graph(self):

        #remember the explanation settings
        iddict = dict()
        for ev in self.explanation.explanable_items:
            i = ev.identify
            iddict[ev.name] = i
        if self.canvas is not None:
            self.canvas.canvas3D.setup()#canvas3D_dir, 'extractionline3D.txt')

            #load state
            if self.valve_manager:
                for k, v in self.valve_manager.valves.iteritems():
                    vc = self.canvas.get_object(k)
                    if vc:
                        vc.soft_lock = v.software_lock
                        v.canvas_valve = vc
                        vc.identify = iddict[vc.name]

            self.view_controller = self._view_controller_factory()

    def load_canvas(self):
        '''
        '''
        p = self._file_dialog_('open', **dict(default_dir=canvas2D_dir))

        if p is not None:
            self.canvas.load_canvas(p)

#    def pressure_update(self, o, oo, n):
#        '''
#        on_trait_change handler for gauge_manager.gauges.pressure
#        
#        '''
#        if self.canvas:
#            self.canvas.update_pressure(o.name, n, o.state)
    def update_valve_state(self, *args, **kw):
        if self.canvas:
            self.canvas.update_valve_state(*args, **kw)

    def update_canvas2D(self, *args):
        if self.canvas:
            self.canvas.canvas2D.update_valve_state(*args)

#    def update_pumping_duration(self, name, val):
#        '''
#
#        '''
#        if self.canvas:
#            self.canvas.canvas3D.update_pumping_duration(name, val)

#    def update_idle_duration(self, name, val):
#        '''
# 
#        '''
#        if self.canvas:
#            self.canvas.update_idle_duration(name, val)

#    def set_interactor_state(self, state):
#        '''
#        '''
#        self.canvas.set_interactor_state(state)

    def show_valve_properties(self, name):
        if self.valve_manager is not None:
            self.valve_manager.show_valve_properties(name)

    def get_software_lock(self, name):
        if self.valve_manager is not None:
            return self.valve_manager.get_software_lock(name)

    def set_software_lock(self, name, lock):
        if self.valve_manager is not None:
            if lock:
                self.valve_manager.lock(name)
            else:
                self.valve_manager.unlock(name)

    def get_valve_states(self):
        if self.valve_manager is not None:
            return self.valve_manager.get_states()

    def get_valve_by_name(self, name):
        if self.valve_manager is not None:
            return self.valve_manager.get_valve_by_name(name)

    def open_valve(self, name, address=None, mode='remote', **kw):
        '''
        '''
        if self.valve_manager is not None:
            if address:
                name = self.valve_manager.get_name_by_address(address)
            return self._change_valve_state(name, mode, 'open', **kw)

    def close_valve(self, name, address=None, mode='remote', **kw):
        '''
        '''
        if self.valve_manager is not None:
            if address:
                name = self.valve_manager.get_name_by_address(address)
            return self._change_valve_state(name, mode, 'close', **kw)

    def sample(self, name, **kw):
        def sample():
            valve = self.valve_manager.get_valve_by_name(name)
            if valve is not None:
                self.info('start sample')
                self.open_valve(name, **kw)
                time.sleep(valve.sample_period)

                self.info('end sample')
                self.close_valve(name, **kw)

        t = Thread(target=sample)
        t.start()

    def cycle(self, name, **kw):
        def cycle():

            valve = self.valve_manager.get_valve_by_name(name)
            if valve is not None:
                n = valve.cycle_n
                period = valve.cycle_period

                self.info('start cycle n={} period={}'.format(n, period))
                for i in range(n):
                    self.info('valve cycling iteration ={}'.format(i + 1))
                    self.open_valve(name, **kw)
                    time.sleep(period)
                    self.close_valve(name, **kw)
                    time.sleep(period)

        t = Thread(target=cycle)
        t.start()

    def claim_group(self, *args):
        return self.valve_manager.claim_group(*args)

    def release_group(self, *args):
        return self.valve_manager.release_group(*args)

    def _change_valve_state(self, name, mode, action, sender_address=None):

        func = getattr(self.valve_manager, '{}_by_name'.format(action))

        claimer = self.valve_manager.get_system(sender_address)
        owned = False
        if claimer:
            owned = self.valve_manager.check_group_ownership(name, claimer)

        if not owned:
            result = func(name, mode=mode)
        else:
            result = '{} owned by {}'.format(name, claimer)
            self.warning(result)

#        system,f ok = self.valve_manager.check_ownership(name, sender_address)
##        ok = True
#        if ok:
#            critical = self.valve_manager.check_critical_section()
#            if not critical:
#                result = func(name, mode=mode)
#            else:
#                result = '{} critical section enabled'.format(name)
#                self.warning(result)
#        else:

        if isinstance(result, bool):
            self.canvas.update_valve_state(name, True if action == 'open' else False)
            result = True

        return result

    def execute_run_script(self, runscript_name):
        runscript_dir = os.path.join(scripts_dir, 'runscripts')
        if self.runscript is None:
            e = ExtractionLineScript(source_dir=runscript_dir ,
                                     file_name=runscript_name,
                                     manager=self,

                                     )

            e.bootstrap()
        elif self.runscript.isAlive():
            self.warning('{} already running'.format(runscript_name))
        else:
            self.runscript = None

    def set_selected_explanation_item(self, obj):

        selected = next((i for i in self.explanation.explanable_items if obj.name == i.name), None)
        if selected:
            self.explanation.selected = selected

    def traits_view(self):
        '''
        '''

        v = View(
                 HGroup(
                        Item('explanation', style='custom', show_label=False,
                             width=340
                             ),

                        Item('canvas', style='custom', show_label=False)
                        ),

               handler=self.handler_klass,
               title='Extraction Line Manager',
               resizable=True,
               x=self.window_x,
               y=self.window_y
               )
        return v


#=================== factories ==========================

    def _view_controller_factory(self):
        if self.canvas.canvas3D:
            v = ViewController(scene_graph=self.canvas.canvas3D.scene_graph)
            self.canvas.canvas3D.user_views = v.views
            return v

    def _valve_manager_changed(self):
        e = self.explanation
        if self.valve_manager is not None:
            e.load(self.valve_manager.explanable_items)
            self.valve_manager.on_trait_change(e.load_item, 'explanable_items[]')

#=================== defaults ===========================
#    def _view_controller_default(self):
#        return self._view_controller_factory()

    def _explanation_default(self):
        '''
        '''
        e = ExtractionLineExplanation()
        if self.valve_manager is not None:
            e.load(self.valve_manager.explanable_items)
            self.valve_manager.on_trait_change(e.load_item, 'explanable_items[]')

        return e

    def _canvas_default(self):
        '''
        '''
        return ExtractionLineCanvas(manager=self)

#    def _pumping_monitor_default(self):
#        '''
#        '''
#        return PumpingMonitor(gauge_manager=self.gauge_manager,
#                              parent=self)

#    def _multruns_report_manager_default(self):
#        return MultrunsReportManager(application=self.application)
if __name__ == '__main__':
    elm = ExtractionLineManager()
    elm.bootstrap()
    elm.canvas.style = '3D'
    elm.configure_traits()

#=================== EOF ================================
#    def add_extraction_line_macro_delay(self):
#        global Macro
#        if Macro is None:
#            from macro import _Macro_ as Macro
#
#        info = Macro.edit_traits()
#        if info.result:
#            Macro.record_action(('delay', Macro.delay))
#
#    def stop_extraction_line_macro_recording(self):
#        global stop_recording
#        if stop_recording is None:
#            from macro import stop_recording
#        stop_recording()
#
#    def start_extraction_line_macro_recording(self):
#        global start_recording
#        if start_recording is None:
#            from macro import start_recording
#        start_recording()
#
#    def play_extraction_line_macro_recording(self):
#        #lazy pre_start time and Thread
#        global time
#        if time is None:
#            import time
#
#        global Thread
#        if Thread is None:
#            from threading import Thread
#
#        global play_macro
#        if play_macro is None:
#            from macro import play_macro
#
#        def _play_():
#            for c in play_macro():
#                args = c[0]
#                kw = c[1]
#
#                if args == 'delay':
#
#                    time.sleep(kw)
#                else:
#                    action = args[3]
#                    name = args[1]
#
#                    func = getattr(self, '%s_valve' % action)
#                    func(name, mode = 'manual')
#
#        t = Thread(target = _play_)
#        t.start()

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
from src.hardware.gauges.base_gauge import BaseGauge
from src.hardware.gauges.mks.ion_gauge import IonGauge
from src.hardware.gauges.mks.pirani_gauge import MicroPirani1S, MicroPirani3S
'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import Str, List, Float, Button, on_trait_change, Property
from traitsui.api import View, Item, HGroup, VGroup, \
    TableEditor, spring, ListEditor
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
#from traitsui.wx.extra.led_editor import LEDEditor
from pyface.timer.api import Timer
#=============standard library imports ========================

import os

#=============local library imports  ==========================
#from src.hardware.gauges.base_gauge import BaseGauge, MicroPirani1S, MicroPirani3S, IonGauge
#from src.hardware.gauges.api import BaseGauge, IonGauge, MicroPirani1S, MicroPirani3S

from manager import Manager
#from stream_manager import StreamManager
##from managers.displays.rich_text_display import RichTextDisplay
#from src.managers.displays.messaging_display import MessagingDisplay

from src.helpers import paths
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.hardware.core.communicators.rs485_scheduler import RS485Scheduler
from pyface.timer.do_later import do_after
from src.hardware.core.i_core_device import ICoreDevice

prev_gauge = None

class Queue(object):
    '''
        G{classtree}
    '''
    data = None
    def __init__(self):
        '''
        '''
        self.data = []
    def put(self, obj):
        '''
            @type obj: C{str}
            @param obj:
        '''
        self.data.append(obj)
    def get(self):
        '''
        '''
        return self.data.pop(0)
    def empty(self):
        '''
        '''
        return len(self.data) == 0
#class GaugeManagerHandler(ManagerHandler):
#    def init(self, info):
#        '''
#            @type info: C{str}
#            @param info:
#        '''
#        object = info.object
#
#        object.opened()

class GaugeManager(Manager):
    '''
    This is the controller of gauges. 
    
    B{all gauge commands should be sent through the controllers scan queue} 
    
    G{classtree}
    '''

    gauges = List(BaseGauge)
    ion_gauges = List(IonGauge)

    pressure = Str

    simulation = Property
    scan_rate = Float
    scan_timer = None

    configure_setpoints = Button
    degas = Button
    #text_output = Instance(MessagingDisplay)

    auto_start = True
    prev_gauge = None

    data_manager = None
    def __init__(self, *args, **kw):
        '''
        create the queue
        
        '''
        super(GaugeManager, self).__init__(*args, **kw)

        self.queue = Queue()

    def _get_simulation(self):
        '''
        '''
        sim = False
        for g in self.gauges:
            if g.simulation:
                sim = True
                break

        return sim

    def kill(self):
        '''
        '''
        self.info('killing')
        if self.scan_timer is not None:
            self.info('stopping timer')
            self.scan_timer.Stop()

    def get_gauge_by_name(self, name):
        '''
        get the gauge by name

        @type name: C{str}
        @param name: str name of the gauge
        
        '''
        for g in self.gauges:
            if g.name == name:
                return g

    def load(self):
        '''
        '''

        '''     
        set up the gauge manager by loading a setup file
        
        '''
        scheduler = RS485Scheduler()
        self.gauges = []
        self.ion_gauges = []

        path = os.path.join(paths.device_dir, 'gauges.cfg')
        config = self.get_configuration(path)

        port = self.config_get(config, 'Communications', 'port', optional=False)
        baudrate = self.config_get(config, 'Communications', 'baudrate', optional=False)
        self.scan_rate = self.config_get(config, 'General', 'scan_rate', 'float', optional=False)
        for section in config.sections():
            _continue = False
            args = dict(name=section,
                        )
            for opt in ['address', 'kind']:
                if not config.has_option(section, opt):
                    _continue = True
                    break
                else:
                    args[opt] = self.config_get(config, section, opt)

            if _continue:
                continue

            g = self._gauge_factory(**args)
            g._communicator = g._communicator_factory('serial')
            #c.open(port = port, baudrate = baudrate)

            g.set_scheduler(scheduler)

            if g.open(port=port, baudrate=baudrate):
                self.info('%s opened' % g.name)

            if g.initialize():
                self.info('initialized %s' % g.name)

                #setup a datamanager for saving the gauge data
                self.data_manager = CSVDataManager()
                self.data_manager.new_frame(directory='gauges', base_frame_name=g.name)

            self.gauges.append(g)

            self.application.register_service(ICoreDevice, g)

            if isinstance(g, IonGauge):
                self.ion_gauges.append(g)


            do_after(3000, self.start_scan)
#    def opened(self):
#        '''
#        '''
#        if self.auto_start:
#            self.start_scan()

    def start_scan(self):
        '''
       
        '''
        if self.gauges:
            self.info('starting gauge scan')

#            #setup a datamanager for saving the gauge data
#            self.data_manager = dm = CSVDataManager()
#            #for g in self.gauges:
#                dm.new_frame(directory = 'gauges', base_frame_name = g.name)

            self.scan_timer = self.scan_timer_factory()

    def scan_timer_factory(self):
        '''
        '''
        self.repopulate()
        return Timer(self.scan_rate, self.pressure_scan)

    def pressure_scan(self):
        '''
        '''
        que = self.queue
        if not que.empty():
            self.do(*que.get())

        if que.empty():
            self.repopulate()

    def repopulate(self):
        '''
        repopulates by reloading the queue with commands
          
        '''
        #populate the queue with some commands 
        for g in self.gauges:
            if g.state:
                self.queue.put((g, 'pressure'))

    def do(self, gauge, cmd):
        '''
            @type gauge: C{str}
            @param gauge:

            @type cmd: C{str}
            @param cmd:
        '''
        prev_gauge = self.prev_gauge
        if prev_gauge is not None:
            prev_gauge.trait_set(indicator=False)

        if cmd == 'pressure':
            gauge.trait_set(indicator=True)
            gauge.get_transducer_pressure(verbose=False)
            self.prev_gauge = gauge

    def _gauge_factory(self, kind, **kw):
        '''
        private method to build a gauge
        '''
        if kind in ['MP3', 'MP']:
            state = True
    #        measure = True
            gauge = MicroPirani3S if kind == 'MP3' else MicroPirani1S
        else:
            state = False
            gauge = IonGauge

        kw['state'] = state

        return gauge(**kw)

    def _configure_setpoints_fired(self):
        '''
        '''
        self.edit_traits(view='gauge_configure_view')

    def _degas_fired(self):
        '''
        '''
        self.edit_traits(view='degas_configure_view')

    @on_trait_change('gauges.pressure')
    def pressure_handler(self, object, name, old, new):
        '''
 
        '''
        if self.data_manager is not None:
            self.data_manager.add_time_stamped_value(new, object.name)

    def degas_configure_view(self):
        '''
        '''
        v = View(Item('ion_gauges', show_label=False,
                    style='custom',
                    editor=TableEditor(columns=[ObjectColumn(name='name'),
                                                CheckboxColumn(name='degas')])
                    ),
                    title='Degas',
                    resizable=True,
                    width=150,
                    height=150
                    )
        return v

    def gauge_configure_view(self):
        '''
        '''
        v = View(Item('gauges',
                    show_label=False,
                    style='custom',
                    editor=ListEditor(use_notebook=True,
                                               dock_style='tab',
                                               page_name='.name',
                                               view='config_view')),
                resizable=True,
                width=415,
                height=200,
                title='Configure Setpoints'
                )
        return v

    def traits_view(self):
        '''
        default view for this class
        '''
        '''
        @rtype: C{View}
        @return: Traits View
        '''
        cols = [
                ObjectColumn(name='name', editable=False, width=75),
#                ObjectColumn(name = 'description', editable = False, width = 75),
                CheckboxColumn(name='indicator', label='-', width=25, editable=False),
                ObjectColumn(name='pressure', format='%0.2e', editable=False, width=75),
                CheckboxColumn(name='state', label='ON/OFF', width=50),
                ]
        table_editor = TableEditor(columns=cols)

        table = Item('gauges',
                            editor=table_editor,
                            show_label=False,
                            width=175,
                            height=175,

                            )
        config_button = HGroup(Item('configure_setpoints', show_label=False),
                             Item('degas', show_label=False),
                             spring)
        v = View(
                 VGroup(
                        config_button,
                        table,
                        #text_out
                        ),
                resizable=True,
               # handler = ManagerHandler
                )
        return v

if __name__ == '__main__':
    g = GaugeManager()
    g.start_loading()
    g.configure_traits()

#    @on_trait_change('gauges.error')
#    def error_handler(self, object, name, old, new):
#        error_map = ['',
#                   'Failed reading pressure',
#                   'Failed turning filament on',
#                   'Over pressure'
#                   ]
#
#        if isinstance(new, int) and new != 0:
#            self.text_output.add_text(msg = '%s - %s' % (object.name,
#                                                 error_map[new]), color = color_generators.colors8i['red'])
#============= defaults ===========
#    def _text_output_default(self):
#        r = MessagingDisplay(height = 175)
#        r.register('gauge')
#        return r
#============= EOF ================
#    @on_trait_change('gauges.identify')
#    def ilistener(self, object, name, old, new):
#        '''
#        handler for C{BaseGauge.identify}
#        
#        adds command to queue
#        
#        @type object: L{BaseGauge}
#        @param object: a gauge object
#        @type name: C{str}
#        @param name: trait name
#        @type old: C{boolean}
#        @param old: the previous value
#        @type new: C{boolean}
#        @param new: the new value
#        '''
#        of = 'OFF'
#        if nn:
#            of = 'ON'
#        command = '%s:pulse:%s' % (o.name, of)
#        self.queue.put(command)
#    @on_trait_change('gauges.flag')
#    def plistener(self, object, name, old, new):
#        '''
#        Handler for C{BaseGauge.flag} - provides a event for listeners listening for pressure changes
#        
#            1. update the gauge managers led editor with the new pressure
#            
#        @type object: L{BaseGauge}
#        @param object: a gauge object
#        @type name: C{str}
#        @param name: trait name
#        @type old: C{boolean}
#        @param old: the previous value
#        @type new: C{boolean}
#        @param new: the new value
#        '''
#        pass
#        #pressure_name = object.name + '_pressure'

#         self.trait_set(**{pressure_name:object.pressure })

#    @on_trait_change('gauges.setpoint.')
#    def slistener(self, object, name, old, new):
#        '''
#        Handler for changes to the setpoint value 
#        
#        adds command to the queue
#        
#        @type object: L{BaseGauge}
#        @param object: a gauge object
#        @type name: C{str}
#        @param name: trait name
#        @type old: C{float}
#        @param old: the previous value
#        @type new: C{float}
#        @param new: the new value
#        
#        '''
#        if len(new) == 9:
#            n = name[-1:]
#            command = '%s:set_point%i:%s' % (object.parent_gauge.name, int(n) + 1, new)
#            self.queue.put(command)
#    @on_trait_change('gauges.state')
#    def stlistener(self, object, name, old, new):
#        '''
#        Handler for changes to C{BaseGauge.state}
#        
#        @type object: L{BaseGauge}
#        @param object: a gauge object
#        @type name: C{str}
#        @param name: trait name
#        @type old: C{boolean}
#        @param old: the previous value
#        @type new: C{boolean}
#        @param new: the new value
#        '''
#        self.gauge_power(object, new)
#    @on_trait_change('gauges.show_data')
#    def dlistener(self, obj, name, old, new):
#        '''
#        Handler for C{BaseGauge.show_data}
#        
#        show the gauges data buffer
#        
#        @type obj: L{BaseGauge}
#        @param obj: a gauge object
#        @type name: C{str}
#        @param name: trait name
#        @type old: C{boolean}
#        @param old: the previous value
#        @type new: C{boolean}
#        @param new: the new value
#        '''
#        if new:
#            obj.show_data_buffer()

    #=================view methods =========================
#    def LED_pressure_indicator_factory(self):
#        '''
#        factory to add a LED widget to the view
#        
#        @rtype: L{LEDEditor}
#        @return: L{VGroup} 
#        '''
#        content = []
#        for i in self.gauges:
#            content.append(HGroup(
#                                  Item(i.name + '_indicator'),
#                                  Item(i.name + '_pressure',
#                                       height = 30,
#                                       width = 125,
#                                       editor = LEDEditor(format_str = '%0.2e')),
#
#                                  show_labels = False
#                                  )
#                            )
#
#        pv = VGroup(content = content)
#        return pv

#            self.stream_manager = sm = StreamManager()
#            dm = sm.data_manager
#
#            #generate a unigue path name
#            i = 0
#            path_gen = lambda i:os.path.join(paths.data_dir, 'gauges', 'gauges_data%i.h5' % i)
#            p = path_gen(i)
#            while os.path.exists(p):
#                i += 1
#                p = path_gen(i)
#
#            #create new date frame
#           # dm.new_frame(p)
#
#            #load the frames structure
#            #dm.add_group('analytical_gauges')
#            #dm.add_group('roughing_gauges')
#
#
#            d = []
#
#            gaugesA = self.grouped_gauges[0]
#            gaugesB = self.grouped_gauges[1]
#
#
#            for i, g in enumerate(gaugesA):
#                base = 'root.analytical_gauges'
#             #   dm.add_group(g.name, parent = base)
#                base += '.%s' % g.name
#              #  dm.add_table('pressure', parent = base)
#
#                g.stream_manager = sm
#
#                d.append(dict(parent = g, plotid = i, series = 0, delay = 200,
#                              tableid = base + '.pressure'
#                              )
#                        )
#
#            series = 0 if len(gaugesA) == 0 else 1
#            new_plot = True if len(gaugesA) == 0 else False
#
#
#            for j, g in enumerate(gaugesB):
#                base = 'root.roughing_gauges'
#               # dm.add_group(g.name, parent = base)
#                base += '.%s' % g.name
#                #dm.add_table('pressure', parent = base)
#
#                g.stream_manager = sm
#                d.append(dict(parent = g, plotid = j, series = series, delay = 200, new_plot = new_plot,
#                              tableid = base + '.pressure'
#                              )
#                        )
#            sm.load_streams(d)

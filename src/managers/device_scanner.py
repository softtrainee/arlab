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
from traits.api import HasTraits, List, Instance, Str, Any, Event, Property, Bool, Float, Int, Enum, Button
from traitsui.api import View, Item, Group, VGroup, HGroup, TableEditor, ButtonEditor, EnumEditor
from traitsui.table_column import ObjectColumn

#============= standard library imports ========================

#============= local library imports  ==========================
from src.graph.graph import Graph
from traitsui.extras.checkbox_column import CheckboxColumn
#from src.helpers.timer import Timer
from pyface.timer.timer import Timer
from src.graph.stream_graph import StreamGraph
from src.hardware import HW_PACKAGE_MAP
from traitsui.menu import ModalButtons
from src.hardware.core.communicators.serial_communicator import get_ports


class ScanDevice(HasTraits):
    name = Str('Device')
    scan = Bool
    _device = Any

    device_klass = Str
    dev_klasses = List

    port = Str
    ports = List

    communicator_type = Str('Serial')
    communicators = List(['Serial', 'Modbus', 'Ethernet', 'GPIB'])

    baudrate = Enum(9600, 19200, 38400, 57600, 115200)

    test = Button
    def _test_fired(self):
        print 'foo'
        self.create_device()
    def _ports_default(self):
        return get_ports()

    def _dev_klasses_default(self):
        ks = HW_PACKAGE_MAP.keys()
        self.device_klass = ks[0]
        return ks

    def get_scan_value(self):
        v = None
        if self._device:
            try:
                v = getattr(self._device, self._device.scan_func)()
            except TypeError:
                raise NotImplementedError('no scan func defined for {}'.format(self._device.__class__.__name__))
        return v

    def create_device(self):
        d = self._device_factory(self.device_klass)
        if d is not None:
            self._device = d
            return True

    def _device_factory(self, device_klass):
        try:
            name = HW_PACKAGE_MAP[device_klass]
        except KeyError:
            raise NotImplementedError('{} not in hardware package map. see src.hardware'.format(device_klass))

        d = __import__(name, fromlist=[device_klass])
        klass = getattr(d, device_klass)

        dev = klass(name=self.name)
        dev.create_communicator(self.communicator_type, self.port, self.baudrate)
        return dev

    def traits_view(self):
        dev_grp = Group(
                       'test',
                        Item('name'),
                        Item('device_klass', editor=EnumEditor(name='dev_klasses'))
                        )

        comms_grp = Group(
                       Item('communicator_type', editor=EnumEditor(name='communicators')),
                       Item('port', editor=EnumEditor(name='ports')),
                       Item('baudrate'),
                       label='Comms'
                       )
        v = View(
                 Group(
                       dev_grp,
                       comms_grp,
                       layout='tabbed'),
                 buttons=ModalButtons[2:]
                 )
        return v


class DeviceScanner(HasTraits):
    graph = Instance(Graph)
    devices = List

    application = Any

    execute = Event
    execute_label = Property(depends_on='alive')
    alive = Bool(False)

    interval = Float(1)
    def load_devices(self):
        ds = self.devices


        if self.application is not None:
            ics = self.application.service_registry.get_services('src.hardware.core.i_core_device.ICoreDevice')
            for ic in ics:
                ds.append(ScanDevice(name=ic.name))


    def _get_scanables(self):
        return [d for d in self.devices if d.scan]

    def _execute_fired(self):
        if not self.alive:
            scanables = self._get_scanables()
            if scanables:

                for _ in scanables:
                    self.graph.new_plot(scan_delay=self.interval,
                                        data_limit=10)
                    self.graph.new_series()

                self.timer = Timer(self.interval * 1000, self._scan_)
                self.alive = True


        else:
            print 'stop'
            self.timer.Stop()
            self.alive = False

    def _scan_(self):
        for d in self._get_scanables():
            v = d.get_scan_value()
            self.graph.record(v)

    def _get_execute_label(self):
        return 'Stop' if self.alive else 'Execute'
    def _graph_factory(self):
        g = StreamGraph(
                        )

        return g
    def _graph_default(self):
        return self._graph_factory()

    def _row_factory(self):
        s = ScanDevice(name='foo')
        info = s.edit_traits(kind='livemodal')
        if info.result:
            if s.create_device():
                s.scan = True
                return s

    def traits_view(self):

        cols = [ObjectColumn(name='name', editable=False, width=0.9),
                CheckboxColumn(name='scan', width=0.1)]
        editor = TableEditor(columns=cols,
                           editable=True,
                           #deletable=True,
                             show_toolbar=True,
                             auto_size=False,
                           row_factory=self._row_factory
                           )
        v = View(
                 HGroup(
                        VGroup(
                               Item('devices', show_label=False, editor=editor),
                               Group(Item('interval'),
                                     Item('execute', editor=ButtonEditor(label_value='execute_label'),
                                          show_label=False),
                                     show_border=True,
                                     label='Scan'

                                     )

                               ),

                        Item('graph', style='custom', show_label=False),
                        ),


                 )
        return v

if __name__ == '__main__':
    d = ScanDevice()

    d = DeviceScanner()
    d.load_devices()
    d.configure_traits()
#============= EOF =====================================

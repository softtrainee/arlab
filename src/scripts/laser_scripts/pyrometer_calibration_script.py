#@PydevCodeAnalysisIgnore

#=============enthought library imports=======================
from traits.api import HasTraits, Float, Instance
from traitsui.api import Item, View
#=============standard library imports ========================
import time
from threading import Thread, Event
from numpy import mean, array
#=============local library imports  ==========================
from src.scripts.file_script import FileScript
from src.graph.residuals_graph import ResidualsGraph
from src.scripts.core.script_helper import check_point
integral = 0
output = 0
previous_error = 0
class PIDLoop(HasTraits):
    '''
        G{classtree}
    '''
    dt = 0.02
    kp = Float(enter_set = True, auto_set = False)
    ki = Float(enter_set = True, auto_set = False)
    kd = Float(enter_set = True, auto_set = False)
    previous_error = 0
    integral = 0
    def __init__(self, p, i, d):
        '''
            @type p: C{str}
            @param p:

            @type i: C{str}
            @param i:

            @type d: C{str}
            @param d:
        '''
        self.kp = p
        self.ki = i
        self.kd = d
    def reset(self):
        '''
        '''
        self.previous_error = 0
        self.integral = 0
    def get_output(self, setpoint, process_value):
        '''
            @type setpoint: C{str}
            @param setpoint:

            @type process_value: C{str}
            @param process_value:
        '''
        #global integral
        #global output
        #global previous_error

        error = setpoint - process_value

        self.integral = self.integral + error * self.dt
        deriv = (error - self.previous_error) / self.dt
        output = self.kp * error + self.ki * self.integral + self.kd * deriv
        self.previous_error = error
        return output, error
    def traits_view(self):
        '''
        '''
        return View(Item('kp'),
                    Item('ki'),
                    Item('kd'))

class PyrometerCalibrationScript(FileScript):
    '''
        G{classtree}
    '''
    setpoint = 800
    update_interval = 3000
    #pid=Any
    nominal_emissivity = 90
    n = 3
    graph = Instance(ResidualsGraph)
    temperatures = None
    #scalibration_points=List
#    show_pid=Button

#    def _show_pid_fired(self):
#        self.pid.edit_traits()
#        
    def _graph_default(self):
        '''
        '''

        rg = ResidualsGraph(title = 'Pyrometer Calibration Curve')
        rg.new_plot()
        rg.new_series()
        return rg

    def load_file(self):
        '''
        '''
        self.update_interval = float(self._file_contents_.pop(0))
        #p,i,d=[float(i) for i in self.script[1].split(',')]
        self.n = float(self._file_contents_.pop(0))
        self.nominal_emissivity = float(self._file_contents_.pop(0))
        #self.pid=PIDLoop(p,i,d)


    def _run_(self):
        '''
        '''
        self.reload()

        manager = self.manager
        manager.stream_manager.start_streams()

        #fire laser
        self.progress.add_text('firing laser' , color = (255, 0, 0))
        manager.enable_laser()


        #set a nominal pyrometer emissivity
        self.progress.add_text('setting nominal emissivity %0.1f' % self.nominal_emissivity)
        manager.pyrometer.emissivity = self.nominal_emissivity


        for line in self._file_contents_:
            args = line.split(',')
            if len(args) == 3:

                self.calibration_points = []
                for si in range(int(args[0]), int(args[1]) + 1, int(args[2])):
                    t = Thread(target = self._execute_step, args = (si,))
                    t.start()
                    t.join()

            else:
                si = float(args[0])
                t = Thread(target = self._execute_step, args = (si,))
                t.start()
                t.join()


    def loop(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        manager = self.manager
        setpoint = self.setpoint

        if manager.simulation:
            temp = setpoint
        else:

            # read the watlow  process 1 value which corresponds to the
            # pyrometer temperature
            #temp=manager.stream_manager.sample_stream('%s_process1'%manager.temperature_controller.name)
            #read the ADC which corresponds to pyrometer temperature
            temp = manager.stream_manager.sample_stream(manager.pyrometer_temperature_monitor.name)

        emiss = manager.pyrometer.emissivity
        if self.at_setpoint(temp):
            self.progress.add_text('Emissivity calibration point e=%0.3f, temp=%0.3f' % (emiss, setpoint), color = (255, 100, 0))
            #if self.calibration_points is not None:
            #    self.calibration_points.append((setpoint,emiss))
            self.graph.add_datum((mean(self.temperatures), emiss))

            event.set()
        else:
            #output,error=self.pid.get_output(setpoint,temp)
            emiss += (temp - setpoint) / 10.0
            #print output,error
            manager.pyrometer._set_emissivity(emiss)

    def at_setpoint(self, temp):
        '''
            @type temp: C{str}
            @param temp:
        '''
        args = check_point(self.temperatures,
                               temp,
                               self.setpoint,
                               self.n)
        self.temperatures = args[1]

        return args[0]

    def _start_pid_loop(self):
        '''
        '''
        self.progress.add_text('starting PID loop', color = (255, 0, 0))

        event = Event()
        self.temperatures = array([])
        while not event.isSet():
            #self.pid.reset()
            Thread(target = self.loop, args = (event,)).start()
            time.sleep(self.update_interval / 1000.0)


    def kill_script(self):
        '''
        '''
        super(PyrometerCalibrationScript, self).kill_script()

        self.manager.disable_laser()
        self.manager.stream_manager.stop_streams()

    def reload(self):
        '''
        '''
        sm = self.manager.stream_manager
        sm.reload()

        #cm=self.diode_manager.control_module
        pytm = self.manager.pyrometer_temperature_monitor
        tc = self.manager.temperature_controller
        py = self.manager.pyrometer


        #cm.stream_manager=sm
        pytm.stream_manager = sm
        tc.stream_manager = sm
        py.stream_manager = sm


        s = [
           dict(parent = pytm, plotid = 0, delay = 1000, show_legend = True, label = 'pyrometer',
                tableid = 'root.pyrometer_tm.stream'
                ),
           dict(parent = tc, plotid = 0, series = 1, delay = 1000, new_plot = False, show_legend = True, label = 'thermocouple',
                tableid = 'root.temperature_controller.stream'
                ),
           dict(parent = py, plotid = 1, delay = 1000, type = 'line',
                tableid = 'root.emissivity.stream')]

        sm.load_streams(s, start = False)

        self.graph.clear()
        self.graph.new_plot()
        self.graph.new_series()

        self.progress.clear()


    def _execute_step(self, *args):
        '''
            @type *args: C{str}
            @param *args:
        '''

        self.setpoint = setpoint = args[0]

        manager = self.manager

        #set closed loop set point
        self.progress.add_text('setting closed loop setpoint %0.3f' % setpoint)
        manager.set_laser_power(setpoint, 'closed')

        #wait for thermocouple to reach a stable temperature
        at_temps = array([])
        while 1 and not manager.simulation:
            # sample the watlows process 1 value which corresponds
            # to the thermocouple temperature
            temp = manager.stream_manager.sample_stream(manager.temperature_controller.name)

            args = check_point(at_temps,
                                 temp,
                                 setpoint,
                                 10,
                                 )
            at_temps = args[1]
            if args[0]:
                break
            time.sleep(1)

        #start pid loop
        self._start_pid_loop()


#    def _button_group_factory(self):
#        grp=super(PyrometerCalibrationScript,self)._button_group_factory()
#        grp.content.append(Item('show_pid',enabled_when='pid is not None',
#                                 show_label=False))
#        return grp

    def _end_run_(self):
        '''
        '''
        super(PyrometerCalibrationScript, self)._end_run_()
        self.manager.stream_manager.stop_streams()
        self.manager.disable_laser()
#def open_execute(self, setpoint):
#        
#        manager=self.manager
#        
#        manager.temperature_controller.set_control_mode('open')
#        #set open loop set point
#        self.progress.add_text('setting open loop setpoint %0.3f'%setpoint)
#        manager.temperature_controller.set_open_loop_setpoint(setpoint)
#        
#        #wait for thermocouple to reach a stable temperature
#        at_temps=array([])
#        while 1 and not manager.simulation:
#            #temp=manager.temperature_monitor.read_temperature()
#            temp=manager.stream_manager.sample_stream(manager.temperature_monitor.name)
#            
#            
#            args=self._check_point(at_temps, 
#                                 temp,
#                                 None, 
#                                 20,
#                                 std_check=True                     
#                                 )
#            at_temps=args[1]
#            print at_temps,args[0]
#            if args[0]:
#            #if setpoint-temp<1:
#                break
#            time.sleep(1)
#            
#        self.setpoint_temp=mean(at_temps)
#        #start pid loop
#        self.progress.add_text('controlling to %0.3f'%self.setpoint_temp)
#
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
#@PydevCodeAnalysisIgnore

##============= enthought library imports =======================
#from traits.api import Float
#from traitsui.api import Item, HGroup, VGroup
##============= standard library imports ========================
#import time
##============= local library imports  ==========================
#from src.scripts.file_script import FileScript
#from src.scripts.core.script_helper import equilibrate
#from src.graph.api import BarGraph
#
#class DiodePowerScanScript(FileScript):
#    '''
#        G{classtree}
#    '''
#    mean = Float
#    std = Float
#    time = Float
#    def log(self, statsdict):
#        '''
#            @type statsdict: C{str}
#            @param statsdict:
#        '''
#        self.info('mean= %(mean)0.3f,  std= %(std)0.3f' % statsdict)
#        self.mean = statsdict['mean']
#        self.std = statsdict['std']
#
#    def _info_group_factory(self):
#        '''
#        '''
#        vg = VGroup(HGroup(Item('time', format_str = '%0.3f'),
#                              Item('mean', format_str = '%0.3f'), Item('std', format_str = '%0.3f')))
#        g = super(DiodePowerScanScript, self)._info_group_factory()
#        vg.content.append(g)
#        return vg
#
#    def load_file(self):
#        '''
#        '''
#        self.control_mode = self.script.pop(0)
#
#    def set_graph(self):
#        '''
#        '''
#        g = BarGraph()
#        g.new_plot()
#        g.set_y_limits(0, 120)
#        g.edit_traits()
#        self.graph = g
#
#    def _run_(self):
#        '''
#        '''
#        manager = self.manager
#
#        self.info('enabling laser for firing')
#        self.add_output('ENABLING LASER', color = 'red')
#        manager.enable_laser()
#        sp = 0
#        bd = 0
#        series = -1
#        tableid = 0
#        bar_width = 10
#        for line in self.script:
#
#            if line[0].upper() == 'G' and not self.kill:
#                bd = float(line[1:])
#                self.info('set beam diameter')
#                self.add_output('setting beam diameter %0.1f' % bd)
#                manager.logic_board.set_beam_diameter(bd, block = True)
#
#                self.graph.new_series(type = 'bar', bar_width = bar_width)
#                table = 'eq_times%02i' % tableid
#                self.data_manager.add_table(table,
#                                            parent = 'root', table_style = 'DiodePowerScan')
#                table = 'root.%s' % table
#                self.data_manager.set_table_attribute('beam_diameter', bd, table)
#
#                series += 1
#                tableid += 1
#                if series > 0:
#                    delay = 30
#                    self.add_output('Delay %i' % delay)
#                    self.info('delay %i(secs)' % delay)
#                    time.sleep(delay)
#            elif not self.kill:
#                sp = float(line)
#                self.info('set setpoint')
#                self.add_output('setting %s loop setpoint %0.1f' % (self.control_mode, sp))
#                manager.set_laser_power(sp, self.control_mode)
#
#
#                self.info('equilibrate')
#                self.add_output('Equilibrating', color = 'green')
#
#                if not manager.simulation:
#                    #wait until setpoint is reached
#                    eqt = equilibrate(self,
#                                manager.temperature_controller.get_temperature,
#                                sp,
#                                mean_tolerance = 5,
#                                std_tolerance = 2.5)
#
#                    if eqt:
#                        msg = 'EQ %0.3f' % eqt
#                        msgi = 'eq  %0.3f' % eqt
#                        color = 'black'
#                    else:
#                        msg = '***Failed equilibrating***'
#                        msgi = 'failed equilibration'
#                        color = 'red'
#                        eqt = 120
#                    self.add_output(msg, color = color)
#                    self.info(msgi)
#                else:
#                    time.sleep(1.0)
#                    eqt = 2.0 + series
#
#                self.data_manager.record(dict(setpoint = sp,
#                                              eq_time = eqt,
#                                              ),
#                                              table = table)
#                self.graph.add_datum((sp + series * bar_width, eqt), series = series)
#
#
#        manager.disable_laser()
#        self.add_output('Thread complete')
#        self.info('end thread')
#
##============= EOF ====================================

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

#============= enthought library imports =======================
#============= standard library imports ========================
#import os
import time
#============= local library imports  ==========================
from src.scripts.file_script import FileScript
#from preferences import preferences
from src.scripts.core.script_helper import equilibrate
class CameraScanScript(FileScript):
    def load(self):
        '''
        '''
        if self.set_data_frame():
            self.start()
            return True
    def load_file(self):
        '''
        '''
        self.zoom = float(self._file_contents_.pop(0))
        self.beam_diameter = float(self._file_contents_.pop(0))

    def set_data_frame(self):
        '''
        '''
        if super(CameraScanScript, self).set_data_frame():
            dm = self.data_manager
            dm.add_group('camera_scan')
            dm.add_table('scan', parent='root.camera_scan', table_style='CameraScan')
            return True

    def kill_script(self):
        '''
        '''
        super(CameraScanScript, self).kill_script()
        manager = self.manager

        self.info('disabling laser')
        manager.disable_laser()
        manager.video_manager.stop('camera_scan')
        self.info('end script')

    def _run_(self):
        '''
        '''
        manager = self.manager

        self.info('starting script')

        #open a video connection
        self.info('start camera')

        manager.video_manager.start('camera_scan')

        #set the zoom
        self.info('set zoom')
        self.add_output('setting zoom %0.1f' % self.zoom)
        manager.logic_board.set_zoom(self.zoom, block=True)

        self.info('set beam diameter')
        self.add_output('setting beam diameter %0.1f' % self.beam_diameter)
        manager.logic_board.set_beam_diameter(self.beam_diameter, block=True)

        delay = 1
        self.info('delay %i' % delay)
        time.sleep(delay)

        #turn laser on
        self.info('enabling laser for firing')
        self.add_output('ENABLING LASER', color='red')
        manager.enable_laser()

        for line in self._file_contents_:
            if self.isAlive():
                setpoint = float(line)
                #set laser power
                self.info('control to setpoint %s' % setpoint)
                manager.set_laser_power(setpoint, 'closed')

            if self.isAlive():
                #wait until setpoint is reached
                self.add_output('Equilbrating to %0.1f' % setpoint)
                self.info(' equilibrating to %0.1f ' % setpoint)
                if not manager.simulation:
                    equilibrate(self,
                                manager.temperature_controller.get_temperature,
                                setpoint)
                else:
                    time.sleep(2.0)

            if self.isAlive():

                #grab a frame and save it
                self.info('accumulate and save video frame')
                ta = manager.video_manager.process_current_frame()


                msg = ','.join(['%0.3f' % ta.val[i] for i in range(3)])
                self.add_output('Target value = (%s)' % msg)
#                manager.video_manager.accumulate_frames(setpoint,5,1)



#    def _equilibrate_(self,setpoint,n=5,**kw):
#        self.add_output('Equilbrating to %0.1f'%setpoint)
#        self.logger.info('====== equilibrating to %0.1f ======'%setpoint)

#        manager=self.manager
#        temps=[]
#        while not manager.simulation and not self.kill:
#            
#            temp=manager.temperature_controller.get_temperature()
#            args=check_point(temps,temp,setpoint,n,mean_tolerance=5,**kw)
#            
#            temps=args[1]
#            if args[0]:
#                break
#            else:
#                if len(args)>2:
#                    self.logger.info('====== mean= %(mean)0.3f,  std= %(std)0.3f ======'%args[2])
#            time.sleep(1.0)
#        else:
#            time.sleep(2.0)
#============= EOF ====================================

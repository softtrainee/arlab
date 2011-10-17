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
#============= enthought library imports =======================
from traits.api import Instance, String, DelegatesTo, Property, Button, Float, Bool
from traitsui.api import Group, Item, HGroup, spring, Spring
#============= standard library imports ========================

#============= local library imports  ==========================
from stage_manager import StageManager
from src.helpers.logger_setup import setup
from src.managers.videoable import Videoable
from video_component_editor import VideoComponentEditor
from src.managers.stage_managers.camera_calibration_manager import CameraCalibrationManager
import time
from threading import Thread, Condition
from pyface.timer.api import do_later
from src.managers.stage_managers.machine_vision.machine_vision_manager import MachineVisionManager

try:
    from src.canvas.canvas2D.video_laser_tray_canvas import VideoLaserTrayCanvas
except ImportError:
    from src.canvas.canvas2D.laser_tray_canvas import LaserTrayCanvas as VideoLaserTrayCanvas


#from calibration_manager import CalibrationManager
class VideoStageManager(StageManager, Videoable):
    '''
    '''

    canvas_editor_klass = VideoComponentEditor
#    calibration_manager = Instance(CalibrationManager)
    camera_xcoefficients = Property(String(enter_set=True, auto_set=False),
                                   depends_on='_camera_xcoefficients')
    _camera_xcoefficients = String

    camera_ycoefficients = Property(String(enter_set=True, auto_set=False),
                                   depends_on='_camera_ycoefficients')
    _camera_ycoefficients = String

    camera_calibration_manager = Instance(CameraCalibrationManager)
    calculate = Button

    calibrate_focus = Button
    focus_z = Float

    drive_xratio = Property(Float(enter_set=True,
                                   auto_set=False
                                   ), depends_on='_drive_xratio')
    _drive_xratio = Float

    drive_yratio = Property(Float(enter_set=True,
                                   auto_set=False
                                   ), depends_on='_drive_yratio')
    _drive_yratio = Float

    calculate_offsets = Bool

    pxpercmx = DelegatesTo('camera_calibration_manager')
    pxpercmy = DelegatesTo('camera_calibration_manager')
        
    auto_center = Bool(True)
    machine_vision_manager = Instance(MachineVisionManager)
        
    def update_camera_params(self, obj, name, old, new):
        if name == 'focus_z':
            self.focus_z = new
        elif 'y' in name:
            self._camera_ycoefficients = new
        elif 'x' in name:
            self._camera_xcoefficients = new

    def initialize_stage(self):
        super(VideoStageManager, self).initialize_stage()

        self.video.open(user='underlay')

        xa = self.stage_controller.axes['x'].drive_ratio
        ya = self.stage_controller.axes['y'].drive_ratio

        self._drive_xratio = xa
        self._drive_yratio = ya

    def kill(self):
        '''
        '''
        super(VideoStageManager, self).kill()
        self.canvas.camera.save_calibration()
        self.video.close(user='underlay')

    def _canvas_factory(self):
        '''
        '''
        try:
            video = self.video
        except AttributeError:
            self.warning('Video not Available')
            video = None

        v = VideoLaserTrayCanvas(parent=self,
                               padding=30,
                               video=video,
                               map=self._stage_map)
        return v

    def _canvas_editor_factory(self):
        w = self.canvas.camera.width * self.canvas.scaling
        h = self.canvas.camera.height * self.canvas.scaling
        l = self.canvas.padding_left
        r = self.canvas.padding_right
        t = self.canvas.padding_top
        b = self.canvas.padding_bottom
        return self.canvas_editor_klass(width=w + l + r,
                                        height=h + t + b)
    def _sconfig__group__(self):
        g = super(VideoStageManager, self)._sconfig__group__()
        g.content.append(Group(Item('camera_xcoefficients'),
                               Item('camera_ycoefficients'),
                               Item('drive_xratio'),
                               Item('drive_yratio'),
                               HGroup(Item('calculate', show_label=False), Item('calculate_offsets'), spring),
                               Item('pxpercmx'),
                               Item('pxpercmy'),

                               HGroup(Item('calibrate_focus', show_label=False), Spring(width=20,
                                                                                          springy=False),
                                      Item('focus_z',
                                            label='Focus',
                                            style='readonly'
                                            )),
                               label='Camera'))
        return g

    def _calculate_indicator_positions(self, shift=None):
        ccm = self.camera_calibration_manager

        zoom = self.parent.zoom
        src, name = self.video_manager.snapshot(identifier=zoom)
        ccm.image_factory(src=src)

        ccm.process_image()
        ccm.title = name

        cond = Condition()
        ccm.cond = cond
        cond.acquire()
        do_later(ccm.edit_traits, view='snapshot_view')
        if shift:
            self.stage_controller.linear_move(*shift, block=False)

        cond.wait()
        cond.release()

    def _calculate_camera_parameters(self):
        ccm = self.camera_calibration_manager
        self._calculate_indicator_positions()
        if ccm.result:
            if self.calculate_offsets:
                rdxmm = 5
                rdymm = 5

                x = self.stage_controller.x + rdxmm
                y = self.stage_controller.y + rdymm
                self.stage_controller.linear_move(x, y, block=True)

                time.sleep(2)

                polygons1 = ccm.polygons
                x = self.stage_controller.x - rdxmm
                y = self.stage_controller.y - rdymm
                self._calculate_indicator_positions(shift=(x, y))

                polygons2 = ccm.polygons

                #compare polygon sets
                #calculate pixel displacement
                dxpx = sum([sum([(pts1.x - pts2.x)
                                for pts1, pts2 in zip(p1.points, p2.points)]) / len(p1.points)
                                    for p1, p2 in zip(polygons1, polygons2)]) / len(polygons1)
                dypx = sum([sum([(pts1.y - pts2.y)
                                for pts1, pts2 in zip(p1.points, p2.points)]) / len(p1.points)
                                    for p1, p2 in zip(polygons1, polygons2)]) / len(polygons1)

                #convert pixel displacement to mm using defined mapping
                dxmm = dxpx / self.pxpercmx
                dymm = dypx / self.pxpercmy

                #calculate drive offset. ratio of request/actual
                try:
                    self.drive_xratio = rdxmm / dxmm
                    self.drive_yratio = rdymm / dymm
                except ZeroDivisionError:
                    self.drive_xratio = 100

    def _move_to_hole_hook(self):
        #use machine vision to calculate positioning error
        if self.auto_center:
            deviation = self.machine_vision_manager.calculate_positioning_error()
            if deviation:
                
                nx = self.stage_controller._x_position + deviation[0]
                ny = self.stage_controller._y_position + deviation[1]
                
                self.linear_move(nx, ny, calibrated_space=False)
            

#===============================================================================
# handlers
#===============================================================================
    def _calculate_fired(self):
        t = Thread(target=self._calculate_camera_parameters)
        t.start()

    def _calibrate_focus_fired(self):
        z = self.stage_controller.z
        self.info('setting focus posiition {}'.format(z))
        self.canvas.camera.focus_z = z
        self.canvas.camera.save_focus()
        
#===============================================================================
# Defaults 
#===============================================================================
    def _camera_calibration_manager_default(self):
        return CameraCalibrationManager()

    def _machine_vision_manager_default(self):
        return MachineVisionManager(video=self.video) 
    
#===============================================================================
# Property Get/Set
#===============================================================================
    def _get_drive_xratio(self):
        return self._drive_xratio

    def _set_drive_xratio(self, v):
        self._drive_xratio = v
        ax = self.stage_controller.axes['x']
        ax.drive_ratio = v
        ax.save()

    def _get_drive_yratio(self):
        return self._drive_yratio

    def _set_drive_yratio(self, v):
        self._drive_yratio = v
        ax = self.stage_controller.axes['y']
        ax.drive_ratio = v
        ax.save()
    
    def _get_camera_xcoefficients(self):
        return self._camera_xcoefficients

    def _set_camera_xcoefficients(self, v):
        self._camera_coefficients = v
        self.canvas.camera.calibration_data.xcoeff_str = v

        if self.parent is not None:
            z = self.parent.zoom
        else:
            z = 0
        self.canvas.camera.set_limits_by_zoom(z)

    def _get_camera_ycoefficients(self):
        return self._camera_ycoefficients

    def _set_camera_ycoefficients(self, v):
        self._camera_ycoefficients = v
        self.canvas.camera.calibration_data.ycoeff_str = v

        if self.parent is not None:
            z = self.parent.zoom
        else:
            z = 0
        print 'sety', z, v
        self.canvas.camera.set_limits_by_zoom(z)
    
if __name__ == '__main__':


    setup('stage_manager')
    s = VideoStageManager(name='co2stage',
                     configuration_dir_name='co2',
                     )

#    i = Initializer()
#    i.add_initialization(dict(name = 'stage_manager',
#                              manager = s
#                              ))
#    i.run()


    s.load()
    s.stage_controller.bootstrap()
    #s.update_axes()

    s.configure_traits()
#============= EOF ====================================
#    def _camera_coefficients_changed(self):
#        print self.camera_coefficients

#    def _calibration_manager_default(self):
#
##        self.video.open(user = 'calibration')
#        return CalibrationManager(parent = self,
#                                  laser_manager = self.parent,
#                               video_manager = self.video_manager,
#                               )

    #                adxs = []
    #                adys = []
    #                for p1, p2 in zip(polygons, polygons2):
    ##                    dxs = []
    ##                    dys = []
    ##                    for pts1, pts2 in zip(p1.points, p2.points):
    ##
    ##                        dx = pts1.x - pts2.x
    ##                        dy = pts1.y - pts2.y
    ##                        dxs.append(dx)
    ##                        dys.append(dy)
    ##                    dxs = [(pts1.x - pts2.x) for pts1, pts2 in zip(p1.points, p2.points)]
    ##                    dys = [(pts1.y - pts2.y) for pts1, pts2 in zip(p1.points, p2.points)]
    ##                    
    #                    adx = sum([(pts1.x - pts2.x) for pts1, pts2 in zip(p1.points, p2.points)]) / len(p1.points)
    #                    ady = sum([(pts1.y - pts2.y) for pts1, pts2 in zip(p1.points, p2.points)]) / len(p1.points)
    #
    ##                    adx = sum(dxs) / len(dxs)
    ##                    ady = sum(dys) / len(dys)
    #                    adxs.append(adx)
    #                    adys.append(ady)
    #                print 'xffset', sum(adxs) / len(adxs)
    #                print 'yffset', sum(adys) / len(adys)

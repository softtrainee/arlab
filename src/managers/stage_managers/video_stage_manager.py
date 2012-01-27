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
from traits.api import Instance, String, DelegatesTo, Property, Button, Float, Bool, on_trait_change
from traitsui.api import Group, Item, HGroup
from pyface.timer.api import do_later
from apptools.preferences.preference_binding import bind_preference
#============= standard library imports ========================
import time
from threading import Thread, Condition, Timer
#import sys
#import os

#sys.path.append(os.path.join(os.path.expanduser('~'), 'Programming', 'mercurial', 'pychron_beta'))
#============= local library imports  ==========================
from src.helpers.filetools import unique_path
from src.helpers.paths import video_dir, snapshot_dir
from src.helpers.logger_setup import setup
from src.managers.videoable import Videoable
from src.managers.stage_managers.camera_calibration_manager import CameraCalibrationManager
from src.managers.stage_managers.machine_vision.machine_vision_manager import MachineVisionManager
from src.managers.stage_managers.machine_vision.autofocus_manager import AutofocusManager

from stage_manager import StageManager
from video_component_editor import VideoComponentEditor

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

    autocenter_button = Button('AutoCenter')

    autofocus_manager = Instance(AutofocusManager)

    machine_vision_manager = Instance(MachineVisionManager)

    snapshot_button = Button('Snapshot')
    auto_save_snapshot = Bool(True)

    zoom_canvas_button = Button
    def _zoom_canvas_button_fired(self):
        print 'asdfsafd'
        self.canvas.set_image_zoom(10)
    def bind_preferences(self, pref_id):
        super(VideoStageManager, self).bind_preferences(pref_id)

        bind_preference(self, 'auto_center', '{}.auto_center'.format(pref_id))
        bind_preference(self.pattern_manager, 'record_patterning', '{}.record_patterning'.format(pref_id))
        bind_preference(self.pattern_manager, 'show_patterning', '{}.show_patterning'.format(pref_id))

    def start_recording(self, path=None, basename='vm_recording', use_dialog=False, user='remote'):
        '''
        '''
        self.info('start video recording ')
        if path is None:
            if use_dialog:
                path = self.save_file_dialog()
            else:
                path, _ = unique_path(video_dir, 'vm_recording', filetype='avi')

        self.info('saving recording to path {}'.format(path))

        self.video.open(user=user)

        self.video.start_recording(path)

    def stop_recording(self, user='remote'):
        '''
        '''
        self.info('stop video recording')
#        self.stop()
        self.video.stop_recording()

        #delay briefly before deleting the capture object
        t = Timer(4, self.video.close, kwargs=dict(user=user))
        t.start()
#        self.video.close(user=user)

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
        for s in self._stage_maps:
            s.dump_correction_file()

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
                               use_camera=True,
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
                               HGroup(Item('auto_center', label='Enabled'),
                                      Item('autocenter_button', show_label=False, enabled_when='auto_center')),
                               HGroup(Item('snapshot_button', show_label=False),
                                      Item('auto_save_snapshot')),
                               Item('autofocus_manager', show_label=False, style='custom'),
                               Item('zoom_canvas_button', show_label=False),
                               #HGroup(Item('calculate', show_label=False), Item('calculate_offsets'), spring),
#                               Item('pxpercmx'),
#                               Item('pxpercmy'),
#                               HGroup(Item('calibrate_focus', show_label=False), Spring(width=20,
#                                                                                          springy=False),
#                                      Item('focus_z',
#                                            label='Focus',
#                                            style='readonly'
#                                            )),
                               label='Camera')
                         )

        return g

    def _move_to_point_hook(self):
        if self._autocenter():
            self._point = 0

    def _move_to_hole_hook(self, holenum, correct):
        if correct:
            time.sleep(0.5)
            args = self._autocenter(holenum=holenum, ntries=3)
            if args:
                #add an adjustment value to the stage map
                self._stage_map.set_hole_correction(holenum, *args)
#            self._hole = 0


    @on_trait_change('autocenter_button')
    def _autocenter(self, holenum=None, ntries=1):
        #use machine vision to calculate positioning error
        if self.auto_center:
            for _t in range(ntries):
                newpos = self.machine_vision_manager.search(self.stage_controller._x_position,
                                                            self.stage_controller._y_position,
                                                            holenum=holenum
                                                            )
                if newpos:
                    #nx = self.stage_controller._x_position + newpos[0]
                    #ny = self.stage_controller._y_position + newpos[1]
    #                self._point = 0
                
                    #newpos=(newpos[0]+0.01, newpos[1]+0.01)
                    self.linear_move(*newpos, block=True, calibrated_space=False 
                                     #ratio_correct=False
                                 )
                    time.sleep(0.25)
            return newpos

#===============================================================================
# handlers
#===============================================================================
    def _snapshot_button_fired(self):

        if self.auto_save_snapshot:
            path, _cnt = unique_path(root=snapshot_dir, base='snapshot', filetype='jpg')
        else:
            path = self.save_file_dialog()
        if path:
            self.info('saving snapshot {}'.format(path))
            self.video.record_frame(path, swap_rb=False)

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

    def _autofocus_manager_default(self):
        return AutofocusManager(video=self.video,
                                manager=self.parent,
                                controller=self.stage_controller
                                )

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
        self.canvas.camera.set_limits_by_zoom(z)

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

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
#============= standard library imports ========================

#============= local library imports  ==========================
from src.remote_hardware.errors.system_errors import InvalidArgumentsErrorCode
from base_remote_hardware_handler import BaseRemoteHardwareHandler
from dummies import DummyLM

DIODE_PROTOCOL = 'src.managers.laser_managers.fusions_diode_manager.FusionsDiodeManager'
CO2_PROTOCOL = 'src.managers.laser_managers.fusions_co2_manager.FusionsCO2Manager'
SYNRAD_PROTOCOL = 'src.managers.laser_managers.synrad_co2_manager.SynradCO2Manager'


class LaserHandler(BaseRemoteHardwareHandler):

    def error_response(self, err):
        return 'OK' if (err is None or err is True) else err

    def get_manager(self):
        name = self.manager_name

        if self.application is not None:
            protocol = CO2_PROTOCOL
            if name == 'Diode':
                protocol = DIODE_PROTOCOL
            elif name == 'Synrad':
                protocol = SYNRAD_PROTOCOL

            lm = self.application.get_service(protocol)
        else:
            lm = DummyLM()

        return lm

    def ReadLaserPower(self, manager, *args):
        '''
            return watts
        '''
        result = manager.get_laser_watts()
        return result

    def GetLaserStatus(self, manager, *args):
        result = 'OK'
        return result

    def Enable(self, manager, *args):
        err = manager.enable_laser()

        if manager.record_lasing:
            
            #get the extraction line manager's current rid
            elm=self.application.get_service('src.extraction_line.extraction_line_manager.ExtractionLineManager')
            rid=elm.multruns_report_manager.get_current_rid()
            if rid is None:
                rid='testrid_001'
                
            manager.stage_manager.start_recording(basename=rid)

        return self.error_response(err)

    def Disable(self, manager, *args):
        err = manager.disable_laser()
        if manager.record_lasing:
            manager.stage_manager.stop_recording(delay=5)

        return self.error_response(err)

    def SetXY(self, manager, data, *args):
        try:
            x, y = data.split(',')
        except ValueError:
            return 'Invalid args: {}'.format(data)
        try:
            x = float(x)
        except ValueError:
            return 'Invalid args: {}  {}'.format(data, x)

        try:
            y = float(y)
        except ValueError:
            return 'Invalid args: {}  {}'.format(data, y)

        #need to remember x,y so we can fool mass spec that we are position
        manager.stage_manager._temp_position=x,y
        err=manager.stage_manager.set_xy(x,y)
        #err = manager.stage_manager.linear_move(x, y)

        return self.error_response(err)

    def _set_axis(self, manager, axis, value):
        try:
            d = float(value)
        except ValueError, err:
            return InvalidArgumentsErrorCode('Set{}'.format(axis.upper()), err)

        err = manager.stage_manager.single_axis_move(axis, d)
        return self.error_response(err)

    def SetX(self, manager, data, *args):
        return self._set_axis(manager, 'x', data)

    def SetY(self, manager, data, *args):
        return self._set_axis(manager, 'y', data)

    def SetZ(self, manager, data, *args):
        return self._set_axis(manager, 'z', data)

    def GetPosition(self, manager, *args):
        
        smanager = manager.stage_manager
        z = smanager.get_z()
        if smanager._temp_position is not None and not smanager.moving():
            x,y=smanager._temp_position
            smanager._temp_position=None
        else:
            x, y = smanager.get_uncalibrated_xy()

        result = ','.join(['{:0.2f}' .format(i) for i in (x, y, z)])

        return result

    def GetDriveMoving(self, manager, *args):
        return manager.stage_manager.moving()

    def GetXMoving(self, manager, *args):
        return manager.stage_manager.moving(axis='x')

    def GetYMoving(self, manager, *args):
        return manager.stage_manager.moving(axis='y')

    def GetZMoving(self, manager, *args):
        return manager.stage_manager.moving(axis='z')

    def StopDrive(self, manager, *args):
        manager.stage_manager.stop()
        return 'OK'

    def SetDriveHome(self, manager, *args):
        manager.stage_manager.define_home()
        return 'OK'

    def SetHomeX(self, manager, *args):
        return self._set_home_(manager, axis='x')

    def SetHomeY(self, manager, *args):
        return self._set_home_(manager, axis='y')

    def SetHomeZ(self, manager, *args):
        return self._set_home_(manager, axis='z')

    def _set_home_(self, manager, **kw):
        '''
        '''
        err = manager.stage_manager.define_home(**kw)
        return self.error_response(err)

    def GoToHole(self, manager, data, *args):
        try:
            data = int(data)
            err = manager.stage_manager._set_hole(data)
        except ValueError:
            err = InvalidArgumentsErrorCode('GoToHole', data)

        return self.error_response(err)

    def GetJogProcedures(self, manager, *args):
        jogs = manager.stage_manager.pattern_manager.get_pattern_names()
        return ','.join(jogs)

    def DoJog(self, manager, name, *args):
        err = manager.stage_manager.pattern_manager.execute_pattern(name)
        return self.error_response(err)

    def AbortJog(self, manager, *args):
        err = manager.stage_manager.pattern_manager.stop_pattern()
        return self.error_response(err)

    def SetBeamDiameter(self, manager, data, *args):
        try:
            bd = float(data)
        except ValueError:
            return InvalidArgumentsErrorCode('SetBeamDiameter', data, logger=self)

        if manager.set_beam_diameter(bd, block=False):
            return 'OK'
        else:
            return 'OK - beam disabled'

    def GetBeamDiameter(self, manager, *args):
        return manager.beam

    def SetZoom(self, manager, data, *args):
        try:
            zoom = float(data)
        except ValueError:
            return InvalidArgumentsErrorCode('SetZoom', data, logger=self)
        manager.zoom = zoom
        return 'OK'

    def GetZoom(self, manager, *args):
        return manager.zoom

    def SetSampleHolder(self, manager, name, *args):
        err = manager.stage_manager._set_stage_map(name)
        return self.error_response(err)

    def GetSampleHolder(self, manager, *args):
        return manager.stage_manager.stage_map

    def SetLaserPower(self, manager, data, *args):
        result = 'OK'
        try:
            p = float(data)
        except:
            return InvalidArgumentsErrorCode('SetLaserPower', data, logger=self)

        manager.set_laser_power(p)
        return result

#============= EOF ====================================

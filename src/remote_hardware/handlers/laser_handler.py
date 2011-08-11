#============= enthought library imports =======================
from base_remote_hardware_handler import BaseRemoteHardwareHandler

#============= standard library imports ========================

#============= local library imports  ==========================
#DIODE_PROTOCOL = 'src.managers.laser_managers.fusions_diode_manager.FusionDiodeManager'
#CO2_PROTOCOL = 'src.managers.laser_managers.fusions_co2_manager.FusionCO2Manager'
from src.managers.laser_managers.fusions_diode_manager import FusionsDiodeManager
from src.managers.laser_managers.fusions_co2_manager import FusionsCO2Manager
from src.managers.laser_managers.synrad_co2_manager import SynradCO2Manager

DIODE_PROTOCOL = FusionsDiodeManager
CO2_PROTOCOL = FusionsCO2Manager
SYNRAD_PROTOCOL = SynradCO2Manager
class DummyJM(object):
    def get_jogs(self):
        return 'JogA,JogB,JogC'

class DummySM(object):
    jog_manager = DummyJM()
    x = 1
    y = 2
    z = 3
    def linear_move_to(self, x, y):
        return 'OK'
    def moving(self, **kw):
        return True

    def stop(self):
        return True

    def define_home(self, *args, **kw):
        return True

    def do_jog(self, name):
        pass

class DummyLM(object):
    stage_manager = DummySM()
    zoom = 30
    beam = 1.5
    def set_beam_diameter(self, d):
        pass
    def set_laser_power(self, *args, **kw):
        pass
    def enable_laser(self):
        return True
    def disable_laser(self):
        return True
    def get_laser_watts(self):
        return 14.0

class LaserHandler(BaseRemoteHardwareHandler):
    manager_name = None
    def error_response(self, err):
        return 'OK' if (err is None or err is True) else err

    def get_laser_manager(self, name):
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

    def handle(self, data):
        result = 'error handling'

        args = self.split_data(data)
        if args:

            manager = self.get_laser_manager(self.manager_name)
            if manager is None:
                result = 'Laser not connected to system'
            else:

                func = self._get_func(args[0])
                if func is not None:

                    try:
                        if len(args) > 1:
                            result = func(manager, args[1])
                        else:
                            result = func(manager)
                    except TypeError, e:
                        self.warning('Invalid command {}, {}, {}'.format(args, data, e))

        return str(result)

    def ReadLaserPower(self, manager):
        '''
            return watts
        '''
        result = manager.get_laser_watts()
        return result

    def GetLaserStatus(self, manager):
        result = 'OK'
        return result

    def Enable(self, manager):
        err = manager.enable_laser()
        return self.error_response(err)

    def Disable(self, manager):
        err = manager.disable_laser()
        return self.error_response(err)

    def SetXY(self, manager, data):
        try:
            x, y = data.split(',')
        except ValueError:
            return 'Invalid args, {}'.format(data)
        x = float(x)
        y = float(y)

        err = manager.stage_manager.linear_move(x, y)

        return self.error_response(err)

    def _set_axis(self, manager, axis, value):
        try:
            d = float(value)
        except ValueError:
            return 'Invalid position value {}'.format(value)

        err = manager.stage_manager.stage_controller.single_axis_move(axis, d)
        return self.error_response(err)

    def SetX(self, manager, data):
        return self._set_axis(manager, 'x', data)

    def SetY(self, manager, data):
        return self._set_axis(manager, 'y', data)

    def SetZ(self, manager, data):
        return self._set_axis(manager, 'z', data)

    def GetPosition(self, manager):
        smanager = manager.stage_manager
        x, y = smanager.get_uncalibrated_xy()
        z = smanager.stage_controller._z_position
        result = ','.join(['{:0.2f}' .format(i) for i in (x, y, z)])

        return result

    def GetDriveMoving(self, manager):
        return manager.stage_manager.moving()

    def GetXMoving(self, manager):
        return manager.stage_manager.moving(axis = 'x')

    def GetYMoving(self, manager):
        return manager.stage_manager.moving(axis = 'y')

    def GetZMoving(self, manager):
        return manager.stage_manager.moving(axis = 'z')

    def StopDrive(self, manager):
        manager.stage_manager.stop()
        return 'OK'

    def SetDriveHome(self, manager):
        manager.stage_manager.define_home()
        return 'OK'

    def SetHomeX(self, manager):
        return self._set_home_(manager, axis = 'x')

    def SetHomeY(self, manager):
        return self._set_home_(manager, axis = 'y')

    def SetHomeZ(self, manager):
        return self._set_home_(manager, axis = 'z')

    def _set_home_(self, manager, **kw):
        '''
        '''
        err = manager.stage_manager.define_home(**kw)
        return self.error_response(err)

    def GoToHole(self, manager, data):
        err = manager.stage_manager._set_hole(data)

        return self.error_response(err)

    def GetJogProcedures(self, manager):
        jogs = manager.stage_manager.pattern_manager.get_pattern_names()
        return jogs

    def JogName(self, manager, name):
        err = manager.stage_manager.pattern_manager.execute_pattern(name)
        return self.error_response(err)

    def AbortJog(self, manager):
        err = manager.stage_manager.pattern_manager.stop_pattern()
        return self.error_response(err)

    def SetBeamDiameter(self, manager, data):
        bd = float(data)
        manager.set_beam_diameter(bd, block = False)
        return 'OK'

    def GetBeamDiameter(self, manager):
        return manager.beam

    def SetZoom(self, manager, data):
        zoom = float(data)
        manager.zoom = zoom
        return 'OK'

    def GetZoom(self, manager):
        return manager.zoom

    def SampleHolder(self, manager, name):
        err = manager.stage_manager._set_stage_map(name)
        return self.error_response(err)

    def GetSampleHolder(self, manager, name):
        return manager.stage_manager.stage_map

#============= views ===================================
#============= EOF ====================================

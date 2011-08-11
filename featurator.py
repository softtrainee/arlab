'''
test features of pychron using unittest



'''

import unittest
#===============================================================================
# ImportTest
#===============================================================================
#class ImportTest(unittest.TestCase):
#
#    def setUp(self):
#        pass
#    def testELM(self):
#        from src.managers.extraction_line_manager import ExtractionLineManager
#        e = ExtractionLineManager()
#        self.assertEqual(e.__class__, ExtractionLineManager)
#
#    def testFusionsCO2(self):
#        from src.managers.laser_managers.fusions_co2_manager import FusionsCO2Manager
#        e = FusionsCO2Manager()
#        self.assertEqual(e.__class__, FusionsCO2Manager)
#
#    def testFusionsDiode(self):
#        from src.managers.laser_managers.fusions_diode_manager import FusionsDiodeManager
#        e = FusionsDiodeManager()
#        self.assertEqual(e.__class__, FusionsDiodeManager)
#
#    def testStageManager(self):
#        from src.managers.stage_managers.stage_manager import StageManager
#        e = StageManager()
#        self.assertEqual(e.__class__, StageManager)
#
#    def testVideoStageManager(self):
#        from src.managers.stage_managers.video_stage_manager import VideoStageManager
#        e = VideoStageManager()
#        self.assertEqual(e.__class__, VideoStageManager)

#===============================================================================
# RemoteHardwareTest
#===============================================================================
from src.remote_hardware.remote_hardware_manager import RemoteHardwareManager
class RemoteHardwareTest(unittest.TestCase):

    def setUp(self):
        self.manager = RemoteHardwareManager()

    def testTest(self):

        request_type = 'test'
        data = 'data'
        result = self.manager.process_server_request(request_type, data)

        self.assertEqual(result, data)
    def testValveOpen(self):
        request_type = 'System'
        data = 'Open A'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testValveClose(self):
        request_type = 'System'
        data = 'Close A'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testValveGetValveState(self):
        request_type = 'System'
        data = 'GetValveState A'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'True')

    def testValveGetManualState(self):
        request_type = 'System'
        data = 'GetManualState A'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'True')

    def testSystemDeviceRead(self):
        request_type = 'System'
        data = 'Read bakeout1'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '0.1')

        data = 'Read "diode tr"'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '0.1')

    def testSystemDeviceSet(self):
        request_type = 'System'
        data = 'Set "bakeout1" 10'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

class RemoteLaserTest(unittest.TestCase):
    def setUp(self):
        self.manager = RemoteHardwareManager()
    def testNewportSet(self):
        request_type = 'Diode'
        data = 'SetXY 1,1'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'SetXY 1,1'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testNewportGet(self):
        request_type = 'Diode'
        data = 'GetPosition'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '1.00,2.00,3.00')

        request_type = 'CO2'
        data = 'GetPosition'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '1.00,2.00,3.00')

    def testNewportSetZ(self):
        request_type = 'Diode'
        data = 'SetZ 3'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'SetZ 3'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testNewportMoving(self):
        request_type = 'Diode'
        data = 'GetDriveMoving'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'True')

        request_type = 'CO2'
        data = 'GetDriveMoving'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'True')

    def testNewportGetXMoving(self):
        request_type = 'Diode'
        data = 'GetXMoving'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'True')

        request_type = 'CO2'
        data = 'GetXMoving'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'True')

    def testNewportGetYMoving(self):
        request_type = 'Diode'
        data = 'GetYMoving'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'True')

        request_type = 'CO2'
        data = 'GetYMoving'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'True')


    def testNewportStop(self):
        request_type = 'Diode'
        data = 'StopDrive'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'StopDrive'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testNewportSetDriveHome(self):
        request_type = 'Diode'
        data = 'SetDriveHome'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'SetDriveHome'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testNewportSetHomeX(self):
        request_type = 'Diode'
        data = 'SetHomeX'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'SetHomeX'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testNewportSetHomeY(self):
        request_type = 'Diode'
        data = 'SetHomeY'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'SetHomeY'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testNewportSetHomeZ(self):
        request_type = 'Diode'
        data = 'SetHomeZ'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'SetHomeZ'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testNewportGetJog(self):
        request_type = 'Diode'
        data = 'GetJogProcedures'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'JogA,JogB,JogC')

        request_type = 'CO2'
        data = 'GetJogProcedures'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'JogA,JogB,JogC')

    def testNewportDoJog(self):
        request_type = 'Diode'
        data = 'DoJog A'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'DoJog A'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testSetBeamDiameter(self):
        request_type = 'Diode'
        data = 'SetBeamExpander 1'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'SetBeamExpander 1'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testGetBeamDiameter(self):
        request_type = 'Diode'
        data = 'GetBeamExpander'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '1.5')

        request_type = 'CO2'
        data = 'GetBeamExpander'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '1.5')

    def testSetZoom(self):
        request_type = 'Diode'
        data = 'SetZoom 1'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'SetZoom 1'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testGetZoom(self):
        request_type = 'Diode'
        data = 'GetZoom'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '30')

        request_type = 'CO2'
        data = 'GetZoom'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '30')

    def testSetPower(self):
        request_type = 'Diode'
        data = 'SetLaserPower 1'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'SetLaserPower 1'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testLaserEnable(self):
        request_type = 'Diode'
        data = 'Enable'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'Enable'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testLaserDisable(self):
        request_type = 'Diode'
        data = 'Disable'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'Disable'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

    def testReadLaserPower(self):
        request_type = 'Diode'
        data = 'ReadLaserPower'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '14.0')

        request_type = 'CO2'
        data = 'ReadLaserPower'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, '14.0')

    def testGetLaserStatus(self):
        request_type = 'Diode'
        data = 'GetLaserStatus'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

        request_type = 'CO2'
        data = 'GetLaserStatus'
        result = self.manager.process_server_request(request_type, data)
        self.assertEqual(result, 'OK')

#class FooTest(unittest.TestCase):
#
#    def setUp(self):
#        pass
#    def runTest(self):
#        pass




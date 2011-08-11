#@PydevCodeAnalysisIgnore

#============= enthought library imports =======================

#============= standard library imports ========================
from tables import Float32Col, StringCol, IsDescription
#============= local library imports  ==========================


class CameraScanTableDescription(IsDescription):
    '''
    '''
    setpoint = Float32Col()
    frame_path = StringCol(140)
    ravg = Float32Col()
    gavg = Float32Col()
    bavg = Float32Col()

    #tc_temp=Float32Col()
class DiodePowerScanTableDescription(IsDescription):
    '''
    '''
    setpoint = Float32Col()
    eq_time = Float32Col()

class TimestampTableDescription(IsDescription):
    '''
        
    '''
    timestamp = StringCol(24)
    value = Float32Col()

class PowerScanTableDescription(IsDescription):
    '''
        
    '''
    power_requested = Float32Col()
    power_achieved = Float32Col()
    voltage = Float32Col()

class PowerMapTableDescription(IsDescription):
    '''
        
    '''
    row = Float32Col()
    col = Float32Col()
    x = Float32Col()
    y = Float32Col()
    power = Float32Col()


def table_description_factory(table_name):
    '''
    '''
    n = '{}TableDescription'.format(table_name)
    return globals()[n]
#============= EOF ====================================
#============= enthought library imports =======================
#============= standard library imports ========================
import os
import sys
#============= local library imports  ==========================
#add src to the path
root = os.path.basename(os.path.dirname(__file__))
if 'pychron' not in root:
    root = 'pychron'
src = os.path.join(os.path.expanduser('~'),
                   'Programming',
                   root
                   )
sys.path.append(src)

from src.helpers.logger_setup import setup

#===============================================================================
# stream manager is out of date
#===============================================================================
#from src.managers.device_stream_manager import DeviceStreamManager


from src.initializer import Initializer


#if __name__ == '__main__':
#    setup(name = 'device_streamer')
#    dsm = DeviceStreamManager(name = 'device_stream_manager')
#
#    i = Initializer()
#    i.add_initialization(dict(name = 'device_stream_manager',
#                              manager = dsm
#                              ))
#    i.run()
#    dsm.configure_traits()


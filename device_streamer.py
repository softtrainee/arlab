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


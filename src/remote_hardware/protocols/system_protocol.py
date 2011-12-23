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
from src.remote_hardware.protocols.protocol import Protocol

#=============enthought library imports=======================
#from traits.api import HasTraits
#from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================
class SystemProtocol(Protocol):
    commands = {'Open':'D', 'Close':'D',
              'GetValveState':'D', 'GetValveStates':None, 'GetManualState':'A',
              'Read':'foo', 'Set':'foo 1',
              #'RemoteLaunch':None,
              #'PychronReady':None,
              'StartMultRuns':'1254', 'CompleteMultRuns':'1254',
              'StartRun':'1', 'CompleteRun':'1'
              }
    
    
#============= EOF =====================================

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
from pyface.action.api import Action
from src.lasers.plugins.laser_actions import get_manager, open_manager
#from traits.api import on_trait_change

#============= standard library imports ========================

#============= local library imports  ==========================
class OpenCalibrationManagerAction(Action):
    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            man = manager.stage_manager.calibration_manager
            open_manager(man)
#============= EOF ====================================

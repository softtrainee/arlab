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
#@PydevCodeAnalysisIgnore

#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.scripts.file_script import FileScript

class LaserScript(FileScript):
    def clean_up(self):
        '''
        '''
        fr = self.manager.failure_reason
        if self.user_cancel:
            self.info('run canceled by user')
        elif fr is not None:
            self.info('%s' % fr)

        self.manager.disable_laser()
#============= EOF ====================================

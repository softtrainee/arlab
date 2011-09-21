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
#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
#============= enthought library imports =======================
#============= standard library imports ========================
import os
import sys
from src.managers.bakeout_manager import launch_bakeout

#============= local library imports  ==========================
#add src to the path
src = os.path.join(os.path.expanduser('~'),
                   'Programming',
                   'mercurial',
                   'pychron_beta'
                   )
sys.path.append(src)
from src.helpers.logger_setup import setup


if __name__ == '__main__':
    '''
       Launch a bakeout manager
    '''


    setup('bakeout')
    launch_bakeout()
    os._exit(0)

#============= EOF ====================================


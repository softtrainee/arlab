#===============================================================================
# Copyright 2012 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
#============= standard library imports ========================
import os
import sys
#============= local library imports  ==========================

def build_version(ver):
    #insert pychron src dir into sys.path
    build_sys_path(ver)

    #can now use src. 
    #build the global path structure
    from src.paths import paths
    paths.build(ver)

    #build globals
    build_globals()

def build_sys_path(ver):
    merc = os.path.join(os.path.expanduser('~'),
                        'Programming',
                        'mercurial')
    src = os.path.join(merc, 'pychron{}'.format(ver))
    sys.path.insert(0, src)

def build_globals():
    from src.helpers.parsers.initialization_parser import InitializationParser
    ip = InitializationParser()

    from globals import globalv
#    use_ipc = ip.get_global('use_ipc')
    boolfunc = lambda x:True if x in ['True', 'true', 'T', 't'] else False
    for attr, func in [('use_ipc', boolfunc),
                        #('mode', str)
                        ]:
        a = ip.get_global(attr)
        if a:
            setattr(globalv, attr, func(a))

#    if use_ipc:
#        globalv.use_ipc =
#
#    use_ipc = ip.get_global('use_ipc')
#    if use_ipc:
#        globalv.use_ipc = True if use_ipc in ['True', 'true', 'T', 't'] else False
#============= EOF =============================================

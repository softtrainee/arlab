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
import sys
import os


def include_path(p, level=1):
    '''
    level includes how many levels we are in the root
    src/launchers/path  level=2
    src/path level=1
    '''
    for _ in range(level):
        p = os.path.dirname(p)
    ps = sys.path
    if not p in ps:
        ps.insert(0, p)

    return p

#======== EOF ================================

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

def convert_to_bool(v):
    return True if v.lower().strip() in ['t', 'true'] else False

class Flag(object):
    _set = False
    def __init__(self, name):
        self.name = name

    def get(self):
        return self._set

    def set(self, value):
        if isinstance(value, str):
            value = convert_to_bool(value)
        else:
            value = bool(value)
        self._set = value

    def clear(self):
        self._set = False
#======== EOF ================================

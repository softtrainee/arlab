#===============================================================================
# Copyright 2011 Jake Ross
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



#=============enthought library imports=======================
#============= standard library imports ========================
#============= local library imports  ==========================

def code_generator(grp, start=0, step=1):
    i = start
    while 1:
        yield '{}{:02n}'.format(grp, i)
        i += step


def get_code_decorator(code_gen):
    def decorator(cls):
        if cls.code is None:
            cls.code = code_gen.next()
        return cls
    return decorator

class ErrorCode(object):
    msg = ''
    code = None
    description = ''
    def __init__(self, logger=None, *args, **kw):
        if logger is not None:
            logger.debug(self.msg)

    def __str__(self):
        return self.get_str()

    def get_str(self):

        return 'ERROR {} : {}'.format(self.code, self.msg)


#============= EOF =====================================

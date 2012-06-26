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
#============= local library imports  ==========================

def rpc_query(func, **kw):
    def _query(obj, *args, **kaw):
        handle = obj._communicator.handle
        try:
            return getattr(handle, func.__name__)(**kw)
        except Exception, e:
            print 'remote query', e

    return _query

#class RemoteDevice(CoreDevice):
#
#    def _query_(self, k):
#        handle = self._communicator.handle
#        try:
#            func = getattr(handle, k)
#            return func()
#        except Exception, e:
#            print 'remote device', e
#============= EOF =============================================

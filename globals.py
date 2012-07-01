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


class Globals(object):
    #use_shared_memory = False

    use_debug_logger = False
    #use_debug_logger = True

    open_logger_on_launch = True

    #force display flags
    show_warnings = True
    show_infos = True

    #using ipc_dgram is currently not working
    ipc_dgram = False

    #fusions logic board flags
    initialize_beam = True
    initialize_zoom = True

    ignore_initialization_warnings = True
    ignore_connection_warnings = True
    ignore_chiller_unavailable = True

    #use_ipc = False == embed the remote hardware servers into pychron
    #= True == an instance of RemoteHardwareServer must be launched
    use_ipc = False

#    mode = None #set mode to 'test' when running tests
    mode = 'test'
    def build(self):
        pass

globalv = Globals()

#class Globals():
#    _use_ipc = True
#    def get_use_ipc(self):
#        return self._use_ipc
#
#    def set_use_ipc(self, v):
#        self._use_ipc = v
#
#    use_ipc = property(fget=get_use_ipc,
#                     fset=set_use_ipc
#                     )
#
#
#
#global_obj = Globals()
#use_ipc = global_obj.use_ipc


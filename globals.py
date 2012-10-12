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
    show_warnings = False
    show_infos = False

    #using ipc_dgram is currently not working
    ipc_dgram = False

    ignore_initialization_warnings = False
    ignore_connection_warnings = True
    ignore_chiller_unavailable = True

    video_test = True
    video_test_path = '/Users/ross/Sandbox/pos_err/diodefailsnapshot.jpg'
    video_test_path = '/Users/ross/Sandbox/snapshot002-6.662--8.572.jpg'
    video_test_path = '/Users/ross/Sandbox/watershed_test.jpg'
    video_test_path = '/Users/ross/Sandbox/watershed_test2.jpg'
    video_test_path = '/Users/ross/Sandbox/snapshot002.jpg'
    show_autocenter_debug_image = True
    test_experiment_set = '/Users/ross/Pychrondata_experiment/experiments/bar.txt'
    #use_ipc = False == embed the remote hardware servers into pychron
    #= True == an instance of RemoteHardwareServer must be launched

    use_ipc = False

    _test = False #set test to 'true' when running tests

#    experiment_debug = False
    experiment_debug = False
    experiment_savedb = True
    automated_run_debug = False
    def build(self, ip):

        boolfunc = lambda x:True if x in ['True', 'true', 'T', 't'] else False
        for attr, func in [('use_ipc', boolfunc),
                           ('ignore_initialization_warnings', boolfunc),
                           ('ignore_connection_warnings', boolfunc),
                           ('ignore_chiller_unavailable', boolfunc),
                           ('show_infos', boolfunc),
                           ('show_warnings', boolfunc),
                           ('video_test', boolfunc),
                            ]:
            a = ip.get_global(attr)
            if a:
                setattr(globalv, attr, func(a))

    def _get_test(self):
        return self._test

    #mode is readonly. set once in the launchers/pychron.py module
    test = property(fget=_get_test)

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


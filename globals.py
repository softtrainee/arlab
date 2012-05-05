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


import os


beta = False if os.path.basename(os.path.dirname(__file__)) == 'pychron' else True
use_shared_memory = False

use_debug_logger = False
#use_debug_logger = True

open_logger_on_launch = False

show_warnings = False

#using ipc_dgram is currently not working
ipc_dgram = False

#fusions logic board flags
initialize_beam = True
initialize_zoom = True

ignore_initialization_warnings = True

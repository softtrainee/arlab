#!/usr/bin/python
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

import os
import sys
# add src to the path
version = ''
SRC_DIR = os.path.join(os.path.expanduser('~'), 'Programming',
                     'mercurial',
                     'pychron{}'.format(version))
sys.path.insert(0, SRC_DIR)

from src.bakeout.bakeout_manager import launch_bakeout
from src.helpers.logger_setup import logging_setup

if __name__ == '__main__':

    logging_setup('bakeout', level='DEBUG')
    launch_bakeout()
    os._exit(0)

# ============= EOF ====================================

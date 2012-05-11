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



'''
Pychron_beta Package contains

G{packagetree }

'''

import sys
from src.emulation.emulation_server import LinkServer, Server
from src.emulation.emulator import LinkHandler, BaseHandler
def start_emulation():
    args = sys.argv[1:]

    portn = 1059
    if len(args) == 1:
        portn = int(args[0])

    s = Server()
    s.start_server('localhost', portn, BaseHandler)

#    ls = LinkServer()
#    ls.start_server('localhost', 1070, LinkHandler())

if __name__ == '__main__':
    start_emulation()

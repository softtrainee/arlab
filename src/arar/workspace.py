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
from traits.api import Str, List
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from src.arar.nodes import ExperimentNode
import os


class Workspace(Loggable):
    name = Str('Workspace')
    experiments = List(ExperimentNode)
    root = Str
    def traits_view(self):
        v = View(
                 Item('name', show_label=False, style='readonly'),
                 )
        return v

    def init(self):
        self.info('initializing workspace {}'.format(self.root))
        if os.path.isdir(self.root):
            pass
#            if self.confirmation_dialog('Overwrite Directory {}'.format(self.root)):
#                pass
        else:
            os.mkdir(self.root)

    def new_experiment(self, name):
        exp = ExperimentNode(name=name)
        self.experiments.append(exp)
        return exp


#============= EOF =============================================

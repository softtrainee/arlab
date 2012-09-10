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
from traits.api import Str
#============= standard library imports ========================
import os
from src.loggable import Loggable
import shutil
#============= local library imports  ==========================

class Repository(Loggable):
    root = Str
    def __init__(self, root, *args, **kw):
        self.root = root
        super(Repository, self).__init__(*args, **kw)

    def addFile(self, src):
        dst = os.path.join(self.root, os.path.basename(src))
        shutil.copyfile(src, dst)


#============= EOF =============================================

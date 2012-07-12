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
from unittest import TestCase
#============= local library imports  ==========================


class ExtractionLineTests(TestCase):
    def setUp(self):
        from src.envisage.run import app
        self.app = app
        ep = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
        self._elm = app.get_service(ep)

#===============================================================================
# A Group
#===============================================================================
    def testAA_GetExtractionLineManager(self):
        self.assertNotEqual(self._elm, None)



#============= EOF =============================================

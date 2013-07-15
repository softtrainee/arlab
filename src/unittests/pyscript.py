#===============================================================================
# Copyright 2013 Jake Ross
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
import unittest
#============= standard library imports ========================
#============= local library imports  ==========================
class PyscriptTest(unittest.TestCase):
    def setUp(self):
        from src.pyscripts.parameter_editor import MeasurementParameterEditor
        self.editor = MeasurementParameterEditor()
    @classmethod
    def setUpClass(cls):
        p = './data/measurement_script.py'
        cls.txt = open(p).read()

    def testExtractFits(self):
        editor = self.editor
        editor.parse(self.txt)

        afit = editor.fit_blocks[0]

        self.assertEqual(afit, (None, ('linear', 'linear')))

#         self.assertEqual(afit, ((0, 5), ('linear', 'linear')))
#         afit = editor.fit_blocks[1]
#         self.assertEqual(afit, ((5, None), ('linear', 'parabolic')))

#============= EOF =============================================

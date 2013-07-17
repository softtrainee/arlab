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
from src.processing.entry.labnumber_entry import LabnumberEntry
from src.unittests.database import get_test_database
#============= standard library imports ========================
#============= local library imports  ==========================

class LabEntryTest(unittest.TestCase):
    def setUp(self):
        db = get_test_database().db
        self.le = LabnumberEntry(db=db)
        self.le.irradiation = 'NM-251'
        self.le.level = 'H'

    def testNPositions(self):
        n = len(self.le.irradiated_positions)
        self.assertEqual(n, 12)

    def testWrite(self):
        le = self.le

        le.make_table()

#============= EOF =============================================

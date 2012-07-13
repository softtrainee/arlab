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
#from traits.api import HasTraits
#from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from unittest import TestCase
#============= local library imports  ==========================


class BaseDatabaseTests(TestCase):
    _db = None
    _db_factory = None

    @classmethod
    def setUpClass(cls):
        if cls._db_factory:
            cls._db = cls._db_factory()
            cls._db.connect()

    @classmethod
    def tearDownClass(cls):
        if cls._db is not None:
            cls._db.close()

    def testA_Connected(self):
        self.assertTrue(self._db.connected)

    def _delete(self, deleter, arg, getter):
        db = self._db

        getattr(db, deleter)(arg)
        d = getattr(db, getter)()

        self.assertEqual(len(d), 0)

#============= EOF =============================================

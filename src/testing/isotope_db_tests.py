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
from os import path
#============= local library imports  ==========================
from database_tests import BaseDatabaseTests
from src.paths import paths
from src.database.adapters.isotope_adapter import IsotopeAdapter


class IsotopeDBTests(BaseDatabaseTests):


    @classmethod
    def _db_factory(self):
        db = IsotopeAdapter(kind='sqlite',
                             dbname=path.join(paths.test_dir, 'isotope_test.sqlite')
                             )
        return db

#===============================================================================
# tests
#===============================================================================

    def testBA_AddUser(self):
        d = self._add_user()
        from src.database.orms.isotope_orm import UserTable
        self.assertIsInstance(d, UserTable)

    def testBB_AddUniqueUser(self):
        d = self._add_user()
        self.assertIsNone(d)

    def testBC_AddProject(self):
        s = self._add_project()
        from src.database.orms.isotope_orm import ProjectTable
        self.assertIsInstance(s, ProjectTable)

    def testBC_AddUniqueProject(self):
        s = self._add_project()
        self.assertIsNone(s)

    def testBD_AddMaterial(self):
        db = self._db
        m = db.add_material('mineralite', commit=True)
        from src.database.orms.isotope_orm import MaterialTable
        self.assertIsInstance(m, MaterialTable)

    def testBE_AddSample(self):
        m = self._add_sample()
        from src.database.orms.isotope_orm import SampleTable
        self.assertIsInstance(m, SampleTable)

    def testBF_AddUniqueSample(self):
        m = self._add_sample()
        self.assertIsNone(m)

    def testBG_AddLabNumber(self):
        m = self._add_labnumber()
        from src.database.orms.isotope_orm import LabTable
        self.assertIsInstance(m, LabTable)

    def testBH_AddUniqueLabNumber(self):
        m = self._add_labnumber()
        self.assertIsNone(m)

    def testDA_DeleteUser(self):
        self._delete('delete_user', 'ROOT', 'get_users')

    def testDB_DeleteProject(self):
        self._delete('delete_project', 'TestProject', 'get_projects')

    def testDC_DeleteMaterial(self):
        self._delete('delete_material', 'mineralite', 'get_materials')

    def testDD_DeleteSample(self):
        self._delete('delete_sample', 'JR-1', 'get_samples')

    def testDE_DeleteLabnumber(self):
        self._delete('delete_labnumber', 10001, 'get_labnumbers')

    def _add_user(self):
        db = self._db
        d = db.add_user('ROOT', commit=True)
        return d

    def _add_project(self):
        db = self._db
        s = db.add_project('TestProject', commit=True)
        return s

    def _add_sample(self):
        db = self._db
        m = db.add_sample('JR-1', commit=True)
        return m

    def _add_labnumber(self):
        db = self._db
        m = db.add_labnumber(10001, sample='JR-1', commit=True)
        print 'asdfasd', m
        return m

#============= EOF =============================================

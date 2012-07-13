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
from src.database.adapters.database_adapter import DatabaseAdapter
from src.paths import paths
from src.database.orms.isotope_orm import ProjectTable, UserTable, SampleTable, \
    MaterialTable, AnalysisTable, AnalysisPathTable, LabTable
import sqlalchemy
from sqlalchemy.sql.expression import or_, and_
from src.database.adapters.functions import add, sql_retrieve, get_one, \
    delete_one
#from src.database.adapters.adapter_decorators import add, get_one, commit
#from sqlalchemy.sql.expression import or_
#============= standard library imports ========================
#============= local library imports  ==========================




class IsotopeAdapter(DatabaseAdapter):
    '''
        new style adapter 
        be careful with super methods you use they may deprecate
        
        using decorators is the new model
    '''
    #===========================================================================
    # adders
    #===========================================================================
    @add
    def add_project(self, name, **kw):
        proj = ProjectTable(name=name, **kw)
        return self._add_unique(proj, 'project', name)

    @add
    def add_material(self, name, **kw):
        mat = MaterialTable(name=name, **kw)
        return self._add_unique(mat, 'material', name)

    @add
    def add_user(self, name, project=None, **kw):
        user = UserTable(name=name, **kw)
        if isinstance(project, str):
            project = self.get_project(project)

        q = self._build_query_and(UserTable, name, ProjectTable, project)

        addflag = True
        u = sql_retrieve(q.one)
        if u is not None:
            addflag = not (u.project == project)

        if addflag:
            self.info('adding user {}'.format(name))
            if project is not None:
                project.users.append(user)

            return user

        self.info('user={} project={} already exists'.format(name, project.name if project else 'None'))

    @add
    def add_sample(self, name, project=None, material=None, **kw):
        sample = SampleTable(name=name, **kw)
        if isinstance(project, str):
            project = self.get_project(project)

        if isinstance(material, str):
            material = self.get_material(material)

        q = self._build_query_and(SampleTable, name, MaterialTable, material)
        q = self._build_query_and(SampleTable, name, ProjectTable, project, q=q)

        addflag = True

        sam = sql_retrieve(q.one)
        if sam is not None:
            addflag = not (sam.project == project or sam.material == material)

        if addflag:
            self.info('adding sample {}'.format(name))
            if project is not None:
                project.samples.append(sample)
                material.samples.append(sample)

            return sample


        self.info('sample={} material={} project={} already exists'.format(name,
                                                                           material.name if material else 'None',
                                                                           project.name if project else 'None'
                                                                           ))
    @add
    def add_labnumber(self, labnumber, sample=None, **kw):
        ln = LabTable(labnumber=labnumber, **kw)

        if isinstance(sample, str):
            sample = self.get_sample(sample)

        ln = self._add_unique(ln, 'labnumber', labnumber)
        if sample is not None and ln is not None:
            sample.labnumbers.append(ln)

        return ln

    @add
    def add_analysis(self, labnumber, **kw):
        if isinstance(labnumber, (str, int)):
            labnumber = self.get_labnumber(labnumber)

        kw = self._get_datetime_keywords(kw)
        anal = AnalysisTable(**kw)
        if labnumber is not None:
            labnumber.analyses.append(anal)

        return anal

    @add
    def add_analysis_path(self, path, analysis=None, **kw):
        kw = self._get_path_keywords(path, kw)
        anal_path = AnalysisPathTable(**kw)
        if isinstance(analysis, (str, int, long)):
            analysis = self.get_analysis(analysis)
#
        if analysis is not None:
            analysis.path = anal_path
            return anal_path

#    @add
#    def add_irradiation_chronology(self, irradiations, **kw):
#        '''
#            blob the chronology
#            
#            
#            irradiations = [(start, stop),...]
#             
#        '''
#    def add_irradiation_production(self, name, **kw):
#        item = None
#        self._add_unique(item, 'irradiation_production', name)

#===========================================================================
# getters single
#===========================================================================
    @get_one
    def get_analysis(self, rid):
        return AnalysisTable, 'lab_id'

    @get_one
    def get_project(self, name):
        return ProjectTable

    @get_one
    def get_material(self, name):
        return MaterialTable

    @get_one
    def get_sample(self, name):
        return SampleTable

    @get_one
    def get_labnumber(self, name):
        return LabTable, 'labnumber'

#===============================================================================
# ##getters multiple
#===============================================================================
    def get_users(self, **kw):
        return self._get_items(UserTable, globals(), **kw)

    def get_projects(self, **kw):
        return self._get_items(ProjectTable, globals(), **kw)

    def get_materials(self, **kw):
        return self._get_items(MaterialTable, globals(), **kw)

    def get_samples(self, **kw):
        return self._get_items(SampleTable, globals(), **kw)

    def get_labnumbers(self, **kw):
        return self._get_items(LabTable, globals(), **kw)
#===============================================================================
# deleters
#===============================================================================
    @delete_one
    def delete_user(self, name):
        return UserTable

    @delete_one
    def delete_project(self, name):
        return ProjectTable

    @delete_one
    def delete_material(self, name):
        return MaterialTable

    @delete_one
    def delete_sample(self, name):
        return SampleTable

    @delete_one
    def delete_labnumber(self, name):
        return LabTable, 'labnumber'


    def _build_query_and(self, table, name, jtable, attr, q=None):
        '''
            joins table and jtable 
            filters using an andclause
            
            e.g.
            q=sess.query(Table).join(JTable).filter(and_(Table.name==name, JTable.name==attr.name))
             
        '''

        sess = self.get_session()
        andclause = tuple()
        if q is None:
            q = sess.query(table)
            andclause = (table.name == name,)

        if attr:
            q = q.join(jtable)
            andclause += (jtable.name == attr.name,)

        if len(andclause) > 1:
            q = q.filter(and_(*andclause))

        elif len(andclause) == 1:
            q = q.filter(andclause[0])

        return q




if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('ia')
    ia = IsotopeAdapter(dbname=paths.isotope_db,
                        kind='sqlite')
    ia.connect()

    #===========================================================================
    # test adding
    #===========================================================================
    p = ia.add_project(
                   'Bar',
                   commit=True
                   )

    m = ia.add_material(name='quartz', commit=True)

    ia.add_sample(name='FC-b',
              material='quartz',
              project='Bar',
              commit=True)

    ia.add_user('Fuser', project='Foo', commit=True)

#    ia.add_user(project=p, name='mosuer', commit=True)
#    p = ia.get_project('Foo3')
#    m = ia.get_material('sanidine')
#    ia.add_sample(name='FC-7sdh2n', project=p, material=m, commit=True)
    #===========================================================================
    # test getting
    #===========================================================================
#    print ia.get_user('mosuer').id
#============= EOF =============================================

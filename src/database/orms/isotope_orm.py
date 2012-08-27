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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, \
     ForeignKey, BLOB, Float
from sqlalchemy.orm import relationship
#============= local library imports  ==========================

from src.database.core.base_orm import BaseMixin, NameMixin
from src.database.core.base_orm import PathMixin, ResultsMixin

Base = declarative_base()

def foreignkey(name):
    return Column(Integer, ForeignKey('{}.id'.format(name)))

def stringcolumn(size=40):
    return Column(String(size))

class ProjectTable(Base, NameMixin):
    users = relationship('UserTable', backref='project')
    samples = relationship('SampleTable', backref='project')
    analyses = relationship('AnalysisTable', backref='project')


class UserTable(Base, NameMixin):
    project_id = foreignkey('ProjectTable')


class SampleTable(Base, NameMixin):
    project_id = foreignkey('ProjectTable')
    material_id = foreignkey('MaterialTable')
    labnumbers = relationship('LabTable', backref='sample')

class MaterialTable(Base, NameMixin):
    samples = relationship('SampleTable', backref='material')


class AnalysisTable(Base, ResultsMixin):
    project_id = foreignkey('ProjectTable')
    lab_id = foreignkey('LabTable')
    extraction_id = foreignkey('ExtractionTable')
    measurement_id = foreignkey('MeasurementTable')
    experiment_id = foreignkey('ExperimentTable')


class AnalysisPathTable(Base, PathMixin):
    analysis_id = foreignkey('AnalysisTable')


class LabTable(Base, BaseMixin):
    labnumber = Column(Integer)
    aliquot = Column(Integer)
    sample_id = foreignkey('SampleTable')
    analyses = relationship('AnalysisTable', backref='labnumber')
    irradiation_id = foreignkey('IrradiationPositionTable')


class ScriptTable(BaseMixin):
    script_name = stringcolumn(80)
    script_blob = Column(BLOB)


class MeasurementTable(Base, ScriptTable):
    analysis = relationship('AnalysisTable', backref='measurement',
                          uselist=False
                          )


class ExtractionTable(Base, ScriptTable):
    position = Column(Integer)
    value = Column(Float)
    heat_duration = Column(Float)
    clean_up_duration = Column(Float)

    analysis = relationship('AnalysisTable', backref='extraction',
                          uselist=False
                          )

class IrradiationPositionTable(Base, BaseMixin):
    labnumber = relationship('LabTable', backref='irradiation_position',
                             uselist=False
                             )
    irradiation_id = foreignkey('IrradiationTable')

class IrradiationTable(Base, NameMixin):
    positions = relationship('IrradiationPositionTable', backref='irradiation')
    level = stringcolumn()

class ExperimentTable(Base, NameMixin):
    analyses = relationship('AnalysisTable', backref='experiment')
#============= EOF =============================================

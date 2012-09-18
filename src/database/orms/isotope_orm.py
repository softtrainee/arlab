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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, \
     ForeignKey, BLOB, Float, Time, Boolean, DateTime
from sqlalchemy.orm import relationship
#============= local library imports  ==========================

from src.database.core.base_orm import BaseMixin, NameMixin
from src.database.core.base_orm import PathMixin, ResultsMixin
from sqlalchemy.sql.expression import func

Base = declarative_base()

def foreignkey(name):
    return Column(Integer, ForeignKey('{}.id'.format(name)))

def stringcolumn(size=40):
    return Column(String(size))

class proc_BlanksSetTable(Base, BaseMixin):
    blank_id = foreignkey('proc_BlanksTable')
    blank_analysis_id = foreignkey('AnalysisTable')

class proc_BlanksHistoryTable(Base, BaseMixin):
    analysis_id = foreignkey('AnalysisTable')
    create_date = Column(DateTime, default=func.now())
    blanks = relationship('proc_BlanksTable', backref='history')

class proc_BlanksTable(Base, BaseMixin):
    history_id = foreignkey('proc_BlanksHistoryTable')
    user_value = Column(Float)
    user_error = Column(Float)
    use_set = Column(Boolean)
    isotope = stringcolumn()
    fit = Column(String(40))
    sets = relationship('proc_BlanksSetTable', backref='blanks')

class MassSpectrometerTable(Base, NameMixin):
#    experiments = relationship('ExperimentTable', backref='mass_spectrometer')
    measurements = relationship('MeasurementTable', backref='mass_spectrometer')

class ProjectTable(Base, NameMixin):
    users = relationship('UserTable', backref='project')
    samples = relationship('SampleTable', backref='project')


class UserTable(Base, NameMixin):
    project_id = foreignkey('ProjectTable')


class SampleTable(Base, NameMixin):
    material_id = foreignkey('MaterialTable')
    project_id = foreignkey('ProjectTable')
    labnumbers = relationship('LabTable', backref='sample')

class MaterialTable(Base, NameMixin):
    samples = relationship('SampleTable', backref='material')

class AnalysisTypeTable(Base, NameMixin):
    measurements = relationship('MeasurementTable', backref='analysis_type')

class AnalysisTable(Base, ResultsMixin):
    lab_id = foreignkey('LabTable')
    extraction_id = foreignkey('ExtractionTable')
    measurement_id = foreignkey('MeasurementTable')
    experiment_id = foreignkey('ExperimentTable')
    endtime = Column(Time)

    #proc relationships
    blanks_histories = relationship('proc_BlanksHistoryTable', backref='analysis')
    blanks_sets = relationship('proc_BlanksSetTable', backref='analysis')

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
    mass_spectrometer_id = foreignkey('MassSpectrometerTable')
    analysis_type_id = foreignkey('AnalysisTypeTable')

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

#    mass_spectrometer_id=foreignkey('MassSpectrometerTable')
#============= EOF =============================================

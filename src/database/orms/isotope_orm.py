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
from sqlalchemy.ext.declarative import declarative_base, declared_attr
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


class ScriptTable(BaseMixin):
    script_name = stringcolumn(80)
    script_blob = Column(BLOB)

#===============================================================================
# proc
#===============================================================================
class HistoryMixin(BaseMixin):
    @declared_attr
    def analysis_id(self):
        return foreignkey('AnalysisTable')

    create_date = Column(DateTime, default=func.now())
    user = stringcolumn()

class proc_BlanksSetTable(Base, BaseMixin):
    blanks_id = foreignkey('proc_BlanksTable')
    blank_analysis_id = foreignkey('AnalysisTable')


class proc_BlanksHistoryTable(Base, HistoryMixin):
    blanks = relationship('proc_BlanksTable', backref='history')
    selected = relationship('proc_SelectedHistoriesTable',
                            backref='selected_blanks',
                            uselist=False
                            )


class proc_BlanksTable(Base, BaseMixin):
    history_id = foreignkey('proc_BlanksHistoryTable')
    user_value = Column(Float)
    user_error = Column(Float)
    use_set = Column(Boolean)
    isotope = stringcolumn()
    fit = Column(String(40))
    sets = relationship('proc_BlanksSetTable', backref='blanks')


class proc_BackgroundsSetTable(Base, BaseMixin):
    backgrounds_id = foreignkey('proc_BackgroundsTable')
    background_analysis_id = foreignkey('AnalysisTable')


class proc_BackgroundsHistoryTable(Base, HistoryMixin):
    backgrounds = relationship('proc_BackgroundsTable', backref='history')
    selected = relationship('proc_SelectedHistoriesTable',
                            backref='selected_backgrounds',
                            uselist=False
                            )


class proc_BackgroundsTable(Base, BaseMixin):
    history_id = foreignkey('proc_BackgroundsHistoryTable')
    user_value = Column(Float)
    user_error = Column(Float)
    use_set = Column(Boolean)
    isotope = stringcolumn()
    fit = Column(String(40))
    sets = relationship('proc_BackgroundsSetTable', backref='backgrounds')


class proc_DetectorIntercalibrationSetTable(Base, BaseMixin):
    detector_intercalibration_id = foreignkey('proc_DetectorIntercalibrationTable')
    detector_intercalibration_analysis_id = foreignkey('AnalysisTable')



class proc_DetectorIntercalibrationHistoryTable(Base, HistoryMixin):
    detector_intercalibration = relationship('proc_DetectorIntercalibrationTable',
                                              backref='history',
                                              uselist=False)

    selected = relationship('proc_SelectedHistoriesTable',
                            backref='selected_detector_intercalibration',
                            uselist=False
                            )


class proc_DetectorIntercalibrationTable(Base, BaseMixin):
    history_id = foreignkey('proc_DetectorIntercalibrationHistoryTable')
    user_value = Column(Float)
    user_error = Column(Float)
#    use_set = Column(Boolean)
    fit = Column(String(40))
    sets = relationship('proc_DetectorIntercalibrationSetTable',
                        backref='detector_intercalibration',
                        )

class proc_SelectedHistoriesTable(Base, BaseMixin):
    analysis_id = foreignkey('AnalysisTable')
    selected_blanks_id = foreignkey('proc_BlanksHistoryTable')
    selected_backgrounds_id = foreignkey('proc_BackgroundsHistoryTable')
    selected_detector_intercalibration_id = foreignkey('proc_DetectorIntercalibrationHistoryTable')


#class proc_WorkspaceHistoryTable(Base, HistoryMixin):
#    workspace_id = foreignkey('WorkspaceTable')
#
#
#class proc_WorkspaceTable(Base, BaseMixin):
#    histories = relationship('WorkspaceHistoryTable', backref='workspace')
#    analyses = relationship('WorkspaceAnalysisSet', backref='workspace')

#class proc_WorkspaceAnalysisSet(Base, BaseMixin):
#    analysis_id = foreignkey('AnalysisTable')


class proc_WorkspaceSettings(Base, BaseMixin):
    '''
        settings is a yaml blob
    '''
    settings = BLOB()
#===============================================================================
# 
#===============================================================================
#===============================================================================
# measurement
#===============================================================================
class AnalysisPathTable(Base, PathMixin):
    analysis_id = foreignkey('AnalysisTable')


class AnalysisTable(Base, ResultsMixin):
    lab_id = foreignkey('LabTable')
    extraction_id = foreignkey('ExtractionTable')
    measurement_id = foreignkey('MeasurementTable')
    experiment_id = foreignkey('ExperimentTable')
    endtime = Column(Time)
    status = Column(Integer, default=1)
    isotopes = relationship('IsotopeTable', backref='analysis')

    #proc relationships
    blanks_histories = relationship('proc_BlanksHistoryTable', backref='analysis')
    blanks_sets = relationship('proc_BlanksSetTable', backref='analysis')

    backgrounds_histories = relationship('proc_BackgroundsHistoryTable', backref='analysis')
    backgrounds_sets = relationship('proc_BackgroundsSetTable', backref='analysis')

    detector_intercalibration_histories = relationship('proc_DetectorIntercalibrationHistoryTable',
                                                       backref='analysis')
    detector_intercalibration_sets = relationship('proc_DetectorIntercalibrationSetTable',
                                                   backref='analysis')

    selected_histories = relationship('proc_SelectedHistoriesTable',
                                      backref='analysis', uselist=False)

class AnalysisTypeTable(Base, NameMixin):
    measurements = relationship('MeasurementTable', backref='analysis_type')


class DetectorTable(Base, NameMixin):
    kind = stringcolumn()
    isotopes = relationship('IsotopeTable', backref='detector')


class ExperimentTable(Base, NameMixin):
    analyses = relationship('AnalysisTable', backref='experiment')


class ExtractionTable(Base, ScriptTable):
    position = Column(Integer)
    value = Column(Float)
    heat_duration = Column(Float)
    clean_up_duration = Column(Float)

    analysis = relationship('AnalysisTable', backref='extraction',
                          uselist=False
                          )


class irrad_HolderTable(Base, NameMixin):
    levels = relationship('irrad_LevelTable', backref='holder')
    geometry = Column(BLOB)

class irrad_LevelTable(Base, NameMixin):
    holder_id = foreignkey('irrad_HolderTable')
    irradiation_id = foreignkey('irrad_IrradiationTable')
    positions = relationship('irrad_PositionTable', backref='level')

class irrad_PositionTable(Base, BaseMixin):
    labnumber = relationship('LabTable', backref='irradiation_position',
                             uselist=False
                             )
    level_id = foreignkey('irrad_LevelTable')

class irrad_ProductionTable(Base, NameMixin):
    K4039 = Column(Float)
    K4039_err = Column(Float)
    K3839 = Column(Float)
    K3839_err = Column(Float)
    K3739 = Column(Float)
    K3739_err = Column(Float)

    Ca3937 = Column(Float)
    Ca3937_err = Column(Float)
    Ca3837 = Column(Float)
    Ca3837_err = Column(Float)
    Ca3637 = Column(Float)
    Ca3637_err = Column(Float)

    Cl3638 = Column(Float)
    Cl3638_err = Column(Float)


class irrad_IrradiationTable(Base, NameMixin):
    levels = relationship('irrad_LevelTable', backref='irradiation')


class IsotopeTable(Base, BaseMixin):
    molecular_weight_id = foreignkey('MolecularWeightTable')
    analysis_id = foreignkey('AnalysisTable')
    detector_id = foreignkey('DetectorTable')
    kind = stringcolumn()


class LabTable(Base, BaseMixin):
    labnumber = Column(Integer)
    aliquot = Column(Integer)
    sample_id = foreignkey('SampleTable')
    analyses = relationship('AnalysisTable', backref='labnumber')
    irradiation_id = foreignkey('irrad_PositionTable')


class MassSpectrometerTable(Base, NameMixin):
#    experiments = relationship('ExperimentTable', backref='mass_spectrometer')
    measurements = relationship('MeasurementTable', backref='mass_spectrometer')


class MaterialTable(Base, NameMixin):
    samples = relationship('SampleTable', backref='material')


class MeasurementTable(Base, ScriptTable):
    analysis = relationship('AnalysisTable', backref='measurement',
                          uselist=False
                          )
    mass_spectrometer_id = foreignkey('MassSpectrometerTable')
    analysis_type_id = foreignkey('AnalysisTypeTable')


class MolecularWeightTable(Base, NameMixin):
    isotopes = relationship('IsotopeTable', backref='molecular_weight')
    mass = Column(Float)


class ProjectTable(Base, NameMixin):
    users = relationship('UserTable', backref='project')
    samples = relationship('SampleTable', backref='project')


class SampleTable(Base, NameMixin):
    material_id = foreignkey('MaterialTable')
    project_id = foreignkey('ProjectTable')
    labnumbers = relationship('LabTable', backref='sample')


class UserTable(Base, NameMixin):
    project_id = foreignkey('ProjectTable')







#============= EOF =============================================

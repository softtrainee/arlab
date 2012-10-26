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
from src.database.core.base_orm import PathMixin, ResultsMixin, ScriptTable
from sqlalchemy.sql.expression import func

Base = declarative_base()

def foreignkey(name):
    return Column(Integer, ForeignKey('{}.id'.format(name)))

def stringcolumn(size=40):
    return Column(String(size))


#===============================================================================
# flux
#===============================================================================
class flux_FluxTable(Base, BaseMixin):
    j = Column(Float)
    j_err = Column(Float)
    history_id = foreignkey('flux_HistoryTable')

class flux_MonitorTable(Base, NameMixin):
    decay_constant = Column(Float)
    decay_constant_err = Column(Float)
    age = Column(Float)
    age_err = Column(Float)
    sample_id = foreignkey('SampleTable')

class flux_HistoryTable(Base, BaseMixin):
    irradiation_position_id = foreignkey('irrad_PositionTable')
    selected = relationship('LabTable',
                            backref='selected_flux_history',
                            uselist=False
                            )
    flux = relationship('flux_FluxTable',
                      backref='history',
                      uselist=False)
#===============================================================================
# proc
#===============================================================================
class HistoryMixin(BaseMixin):
    @declared_attr
    def analysis_id(self):
        return foreignkey('meas_AnalysisTable')

    create_date = Column(DateTime, default=func.now())
    user = stringcolumn()

class proc_BlanksSetTable(Base, BaseMixin):
    blanks_id = foreignkey('proc_BlanksTable')
    blank_analysis_id = foreignkey('meas_AnalysisTable')


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
    background_analysis_id = foreignkey('meas_AnalysisTable')


class proc_BackgroundsHistoryTable(Base, HistoryMixin):
    backgrounds = relationship('proc_BackgroundsTable',
                               backref='history')
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
    detector_intercalibration_analysis_id = foreignkey('meas_AnalysisTable')



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
    analysis_id = foreignkey('meas_AnalysisTable')
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
class meas_AnalysisPathTable(Base, PathMixin):
    analysis_id = foreignkey('meas_AnalysisTable')


class meas_AnalysisTable(Base, ResultsMixin):
    lab_id = foreignkey('LabTable')
    extraction_id = foreignkey('meas_ExtractionTable')
    measurement_id = foreignkey('meas_MeasurementTable')
    experiment_id = foreignkey('meas_ExperimentTable')
    endtime = Column(Time)
    status = Column(Integer, default=1)
    aliquot = Column(Integer)
    isotopes = relationship('meas_IsotopeTable', backref='analysis')

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


class meas_ExperimentTable(Base, NameMixin):
    analyses = relationship('meas_AnalysisTable', backref='experiment')


class meas_ExtractionTable(Base, ScriptTable):
    position = Column(Integer)
    extract_value = Column(Float)
    extract_duration = Column(Float)
    cleanup_duration = Column(Float)
    experiment_blob = Column(BLOB)
    extract_device_id = foreignkey('ExtractionDeviceTable')
    analysis = relationship('meas_AnalysisTable', backref='extraction',
                          uselist=False
                          )


class meas_SpectrometerParametersTable(Base, BaseMixin):
    measurement_id = foreignkey('meas_MeasurementTable')
    extraction_len = Column('extraction_lens', Float)
    ysymmetry = Column(Float)
    zsymmetry = Column(Float)
    zfocus = Column(Float)


class meas_SpectrometerDeflectionsTable(Base, BaseMixin):
    detector_id = foreignkey('DetectorTable')
    measurement_id = foreignkey('meas_MeasurementTable')
    deflection = Column(Float)

class meas_IsotopeTable(Base, BaseMixin):
    molecular_weight_id = foreignkey('MolecularWeightTable')
    analysis_id = foreignkey('meas_AnalysisTable')
    detector_id = foreignkey('DetectorTable')
    kind = stringcolumn()

class meas_MeasurementTable(Base, ScriptTable):
    analysis = relationship('meas_AnalysisTable', backref='measurement',
                          uselist=False
                          )
    mass_spectrometer_id = foreignkey('MassSpectrometerTable')
    analysis_type_id = foreignkey('AnalysisTypeTable')

    spectrometer_parameters = relationship('meas_SpectrometerParametersTable',
                                         backref='measurement',
                                         uselist=False
                                         )
    deflections = relationship('meas_SpectrometerDeflectionsTable', backref='measurement')

class meas_SignalsTable(Base, BaseMixin):
    analysis_id = foreignkey('meas_AnalysisTable')
    datablob = Column(BLOB)


#===============================================================================
# irradiation
#===============================================================================
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
    flux_histories = relationship('flux_HistoryTable', backref='position')

    level_id = foreignkey('irrad_LevelTable')
    position = Column(Integer)

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

    irradiations = relationship('irrad_IrradiationTable', backref='production')

class irrad_IrradiationTable(Base, NameMixin):
    levels = relationship('irrad_LevelTable', backref='irradiation')
    irradiation_production_id = foreignkey('irrad_ProductionTable')
    irradiation_chronology_id = foreignkey('irrad_ChronologyTable')

class irrad_ChronologyTable(Base, BaseMixin):
    chronology = Column(BLOB)
    irradiation = relationship('irrad_IrradiationTable', backref='chronology')

#===============================================================================
# 
#===============================================================================

#===============================================================================
# general
#===============================================================================


class AnalysisTypeTable(Base, NameMixin):
    measurements = relationship('meas_MeasurementTable', backref='analysis_type')


class DetectorTable(Base, NameMixin):
    kind = stringcolumn()
    isotopes = relationship('meas_IsotopeTable', backref='detector')
    deflections = relationship('meas_SpectrometerDeflectionsTable', backref='detector')


class ExtractionDeviceTable(Base, NameMixin):
    extractions = relationship('meas_ExtractionTable', backref='extraction_device')
    kind = stringcolumn()
    make = stringcolumn()
    model = stringcolumn()

class LabTable(Base, BaseMixin):
    labnumber = Column(Integer)
#    aliquot = Column(Integer)
    sample_id = foreignkey('SampleTable')
    analyses = relationship('meas_AnalysisTable', backref='labnumber')
    irradiation_id = foreignkey('irrad_PositionTable')
    selected_flux_id = foreignkey('flux_HistoryTable')


class MassSpectrometerTable(Base, NameMixin):
#    experiments = relationship('ExperimentTable', backref='mass_spectrometer')
    measurements = relationship('meas_MeasurementTable', backref='mass_spectrometer')


class MaterialTable(Base, NameMixin):
    samples = relationship('SampleTable', backref='material')


class MolecularWeightTable(Base, NameMixin):
    isotopes = relationship('meas_IsotopeTable', backref='molecular_weight')
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


#===============================================================================
# 
#===============================================================================
#============= EOF =============================================

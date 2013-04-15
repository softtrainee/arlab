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
# from src.database.core.base_orm import PathMixin, ResultsMixin, ScriptTable
from sqlalchemy.sql.expression import func
from datetime import datetime
from sqlalchemy.schema import Table
# from sqlalchemy.types import FLOAT

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
    sample_id = foreignkey('gen_SampleTable')

class flux_HistoryTable(Base, BaseMixin):
    irradiation_position_id = foreignkey('irrad_PositionTable')
    selected = relationship('gen_LabTable',
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

class proc_ArArHistoryTable(Base, HistoryMixin):
    arar_results = relationship('proc_ArArTable', backref='history')
    selected = relationship('proc_SelectedHistoriesTable',
                            backref='selected_arar',
                            uselist=False
                            )

class proc_ArArTable(Base, BaseMixin):
    history_id = foreignkey('proc_ArArHistoryTable')
    age = Column(Float)
    age_err = Column(Float)

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
    fit = stringcolumn()
    sets = relationship('proc_BackgroundsSetTable', backref='backgrounds')


class proc_DetectorIntercalibrationSetTable(Base, BaseMixin):
    intercalibration_id = foreignkey('proc_DetectorIntercalibrationTable')
    ic_analysis_id = foreignkey('meas_AnalysisTable')



class proc_DetectorIntercalibrationHistoryTable(Base, HistoryMixin):
    detector_intercalibration = relationship('proc_DetectorIntercalibrationTable',
                                              backref='history',
#                                              uselist=False
                                              )

    selected = relationship('proc_SelectedHistoriesTable',
                            backref='selected_detector_intercalibration',
                            uselist=False
                            )


class proc_DetectorIntercalibrationTable(Base, BaseMixin):
    history_id = foreignkey('proc_DetectorIntercalibrationHistoryTable')
    detector_id = foreignkey('gen_DetectorTable')
    user_value = Column(Float)
    user_error = Column(Float)
    fit = stringcolumn()
    sets = relationship('proc_DetectorIntercalibrationSetTable',
                        backref='detector_intercalibration',
                        )


class proc_FigureTable(Base, NameMixin):
    create_date = Column(DateTime, default=func.now())
    user = stringcolumn()
    project_id = foreignkey('gen_ProjectTable')

    analyses = relationship('proc_FigureAnalysisTable', backref='figure')

class proc_FigureAnalysisTable(Base, BaseMixin):
    figure_id = foreignkey('proc_FigureTable')
    analysis_id = foreignkey('meas_AnalysisTable')
    status = Column(Integer)
    graph = Column(Integer)
    group = Column(Integer)

class proc_FitHistoryTable(Base, HistoryMixin):
    fits = relationship('proc_FitTable', backref='history',
#                        uselist=False
                        )
    results = relationship('proc_IsotopeResultsTable', backref='history')
    selected = relationship('proc_SelectedHistoriesTable',
                            backref='selected_fits',
                            uselist=False
                            )

class proc_FitTable(Base, BaseMixin):
    history_id = foreignkey('proc_FitHistoryTable')
    isotope_id = foreignkey('meas_IsotopeTable')

    fit = stringcolumn()
    filter_outliers = Column(Boolean)
    filter_outlier_iterations = Column(Integer, default=1)
    filter_outlier_std_devs = Column(Integer, default=1)

class proc_SelectedHistoriesTable(Base, BaseMixin):
    analysis_id = foreignkey('meas_AnalysisTable')
    selected_blanks_id = foreignkey('proc_BlanksHistoryTable')
    selected_backgrounds_id = foreignkey('proc_BackgroundsHistoryTable')
    selected_det_intercal_id = foreignkey('proc_DetectorIntercalibrationHistoryTable')
    selected_fits_id = foreignkey('proc_FitHistoryTable')
    selected_arar_id = foreignkey('proc_ArArHistoryTable')

class proc_IsotopeResultsTable(Base, BaseMixin):
    signal_ = Column(Float(32))
    signal_err = Column(Float(32))
    isotope_id = foreignkey('meas_IsotopeTable')
    history_id = foreignkey('proc_FitHistoryTable')

class proc_NotesTable(Base, HistoryMixin):
    note = Column(BLOB)

# class proc_WorkspaceHistoryTable(Base, HistoryMixin):
#    workspace_id = foreignkey('WorkspaceTable')
#
#
# class proc_WorkspaceTable(Base, BaseMixin):
#    histories = relationship('WorkspaceHistoryTable', backref='workspace')
#    analyses = relationship('WorkspaceAnalysisSet', backref='workspace')

# class proc_WorkspaceAnalysisSet(Base, BaseMixin):
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
# class meas_AnalysisPathTable(Base, PathMixin):
#    analysis_id = foreignkey('meas_AnalysisTable')

class meas_SignalTable(Base, BaseMixin):
    data = Column(BLOB)
    isotope_id = foreignkey('meas_IsotopeTable')
#    detector_id = foreignkey('gen_DetectorTable')


class meas_AnalysisTable(Base, BaseMixin):
    lab_id = foreignkey('gen_LabTable')
    extraction_id = foreignkey('meas_ExtractionTable')
    measurement_id = foreignkey('meas_MeasurementTable')
    experiment_id = foreignkey('meas_ExperimentTable')
    import_id = foreignkey('gen_ImportTable')
    user_id=foreignkey('gen_UserTable')
    
    uuid = stringcolumn(40)
    analysis_timestamp = Column(DateTime, default=func.now())
    endtime = Column(Time)
    status = Column(Integer, default=0)
    aliquot = Column(Integer)
    step = stringcolumn(10)
    comment = Column(BLOB)

    # meas relationships
    isotopes = relationship('meas_IsotopeTable', backref='analysis')
    peak_center = relationship('meas_PeakCenterTable', backref='analysis', uselist=False)

    # proc relationships
    blanks_histories = relationship('proc_BlanksHistoryTable', backref='analysis')
    blanks_sets = relationship('proc_BlanksSetTable', backref='analysis')

    backgrounds_histories = relationship('proc_BackgroundsHistoryTable', backref='analysis')
    backgrounds_sets = relationship('proc_BackgroundsSetTable', backref='analysis')

    detector_intercalibration_histories = relationship('proc_DetectorIntercalibrationHistoryTable',
                                                       backref='analysis')
    detector_intercalibration_sets = relationship('proc_DetectorIntercalibrationSetTable',
                                                   backref='analysis')

    fit_histories = relationship('proc_FitHistoryTable', backref='analysis')

    selected_histories = relationship('proc_SelectedHistoriesTable',
                                      backref='analysis', uselist=False)
    arar_histories = relationship('proc_ArArHistoryTable', backref='analysis')
    figure_analyses = relationship('proc_FigureAnalysisTable', backref='analysis')
    notes = relationship('proc_NotesTable', backref='analysis')
    monitors = relationship('meas_MonitorTable', backref='analysis')
    

class meas_ExperimentTable(Base, NameMixin):
    analyses = relationship('meas_AnalysisTable', backref='experiment')


class meas_ExtractionTable(Base, BaseMixin):
#    position = Column(Integer)
    extract_value = Column(Float)
    extract_duration = Column(Float)
    cleanup_duration = Column(Float)
#    experiment_blob = Column(BLOB)
    weight = Column(Float)
    sensitivity_multiplier = Column(Float)

    sensitivity_id = foreignkey('gen_SensitivityTable')
    extract_device_id = foreignkey('gen_ExtractionDeviceTable')
    script_id = foreignkey('meas_ScriptTable')
    experiment_blob_id = foreignkey('meas_ScriptTable')
    image_id = foreignkey('med_ImageTable')

    analyses = relationship('meas_AnalysisTable', backref='extraction')
    positions = relationship('meas_PositionTable', backref='extraction')
    snapshots = relationship('med_SnapshotTable', backref='extraction')


class meas_PositionTable(Base, BaseMixin):
    position = Column(Integer)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)

    extraction_id = foreignkey('meas_ExtractionTable')


class meas_SpectrometerParametersTable(Base, BaseMixin):
#    measurement_id = foreignkey('meas_MeasurementTable')
    extraction_lens = Column('extraction_lens', Float)
    ysymmetry = Column(Float)
    zsymmetry = Column(Float)
    zfocus = Column(Float)
    hash = Column(String(32))
    measurements = relationship('meas_MeasurementTable', backref='spectrometer_parameters')

class meas_SpectrometerDeflectionsTable(Base, BaseMixin):
    detector_id = foreignkey('gen_DetectorTable')
    measurement_id = foreignkey('meas_MeasurementTable')
    deflection = Column(Float)

class meas_IsotopeTable(Base, BaseMixin):
    molecular_weight_id = foreignkey('gen_MolecularWeightTable')
    analysis_id = foreignkey('meas_AnalysisTable')
    detector_id = foreignkey('gen_DetectorTable')
    kind = stringcolumn()

    signals = relationship('meas_SignalTable', backref='isotope')
    fits = relationship('proc_FitTable', backref='isotope')
    results = relationship('proc_IsotopeResultsTable', backref='isotope')

class meas_MeasurementTable(Base, BaseMixin):
    mass_spectrometer_id = foreignkey('gen_MassSpectrometerTable')
    analysis_type_id = foreignkey('gen_AnalysisTypeTable')
    spectrometer_parameters_id = foreignkey('meas_SpectrometerParametersTable')
    script_id = foreignkey('meas_ScriptTable')
#    spectrometer_parameters = relationship('meas_SpectrometerParametersTable',
#                                         backref='measurement',
#                                         uselist=False
#                                         )
    analyses = relationship('meas_AnalysisTable', backref='measurement')
    deflections = relationship('meas_SpectrometerDeflectionsTable', backref='measurement')


class meas_PeakCenterTable(Base, BaseMixin):
    center = Column(Float(32))
    points = Column(BLOB)
    analysis_id = foreignkey('meas_AnalysisTable')

class meas_ScriptTable(Base, NameMixin):
    hash = Column(String(32))
    blob = Column(BLOB)
    measurements = relationship('meas_MeasurementTable', backref='script')
    extractions = relationship('meas_ExtractionTable',
                               primaryjoin='meas_ExtractionTable.experiment_blob_id==meas_ScriptTable.id',
                               backref='script')
    experiments = relationship('meas_ExtractionTable',
                               primaryjoin='meas_ExtractionTable.script_id==meas_ScriptTable.id',
                               backref='experiment')

class meas_MonitorTable(Base, NameMixin):
    data = Column(BLOB)

    parameter = stringcolumn()
    criterion = stringcolumn()
    comparator = stringcolumn()
    action = stringcolumn()
    tripped = Column(Boolean)

    analysis_id = foreignkey('meas_AnalysisTable')

#===============================================================================
# irradiation
#===============================================================================
class irrad_HolderTable(Base, NameMixin):
    levels = relationship('irrad_LevelTable', backref='holder')
    geometry = Column(BLOB)

class irrad_LevelTable(Base, NameMixin):
    z = Column(Float)
    holder_id = foreignkey('irrad_HolderTable')
    irradiation_id = foreignkey('irrad_IrradiationTable')
    positions = relationship('irrad_PositionTable', backref='level')

class irrad_PositionTable(Base, BaseMixin):
    labnumber = relationship('gen_LabTable', backref='irradiation_position',
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

    Ca_K = Column(Float)
    Ca_K_err = Column(Float)

    Cl_K = Column(Float)
    Cl_K_err = Column(Float)

    irradiations = relationship('irrad_IrradiationTable', backref='production')

class irrad_IrradiationTable(Base, NameMixin):
    levels = relationship('irrad_LevelTable', backref='irradiation')
    irradiation_production_id = foreignkey('irrad_ProductionTable')
    irradiation_chronology_id = foreignkey('irrad_ChronologyTable')

class irrad_ChronologyTable(Base, BaseMixin):
    chronology = Column(BLOB)
    irradiation = relationship('irrad_IrradiationTable', backref='chronology')

    def get_doses(self):
        def convert(x):
            return datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

        doses = self.chronology.split('$')
        doses = [di.strip().split('%') for di in doses]
        doses = [map(convert, d) for d in doses if d]
        return doses
#===============================================================================
#
#===============================================================================
#===============================================================================
# media
#===============================================================================
class med_ImageTable(Base, NameMixin):
    create_date = Column(DateTime, default=func.now())
    image = Column(BLOB)
    extractions = relationship('meas_ExtractionTable', backref='image')

class med_SnapshotTable(Base, BaseMixin):
    path = stringcolumn(200)
    create_date = Column(DateTime, default=func.now())
    image = Column(BLOB)
    extraction_id = foreignkey('meas_ExtractionTable')

#===============================================================================
# general
#===============================================================================


class gen_AnalysisTypeTable(Base, NameMixin):
    measurements = relationship('meas_MeasurementTable', backref='analysis_type')


class gen_DetectorTable(Base, NameMixin):
    kind = stringcolumn()
    isotopes = relationship('meas_IsotopeTable', backref='detector')
    deflections = relationship('meas_SpectrometerDeflectionsTable', backref='detector')
    intercalibrations = relationship('proc_DetectorIntercalibrationTable', backref='detector')

class gen_ExtractionDeviceTable(Base, NameMixin):
    extractions = relationship('meas_ExtractionTable', backref='extraction_device')
    kind = stringcolumn()
    make = stringcolumn()
    model = stringcolumn()

class gen_ImportTable(Base, BaseMixin):
    date = Column(DateTime, default=func.now())
    user = stringcolumn()
    source = stringcolumn()
    source_host = stringcolumn()
    analyses = relationship('meas_AnalysisTable')

class gen_LabTable(Base, BaseMixin):
    labnumber = Column(Integer)
#    aliquot = Column(Integer)
    sample_id = foreignkey('gen_SampleTable')
    analyses = relationship('meas_AnalysisTable', backref='labnumber')
    irradiation_id = foreignkey('irrad_PositionTable')
    selected_flux_id = foreignkey('flux_HistoryTable')
    note = stringcolumn(140)

class gen_MassSpectrometerTable(Base, NameMixin):
#    experiments = relationship('ExperimentTable', backref='mass_spectrometer')
    measurements = relationship('meas_MeasurementTable', backref='mass_spectrometer')
    sensitivities = relationship('gen_SensitivityTable', backref='mass_spectrometer')

class gen_MaterialTable(Base, NameMixin):
    samples = relationship('gen_SampleTable', backref='material')


class gen_MolecularWeightTable(Base, NameMixin):
    isotopes = relationship('meas_IsotopeTable', backref='molecular_weight')
    mass = Column(Float)


association_table = Table('association', Base.metadata,
                        Column('project_id', Integer, ForeignKey('gen_ProjectTable.id')),
                        Column('user_id', Integer, ForeignKey('gen_UserTable.id')),
                        )

class gen_ProjectTable(Base, NameMixin):
    samples = relationship('gen_SampleTable', backref='project')
    figures = relationship('proc_FigureTable', backref='project')
    users = relationship('gen_UserTable', secondary=association_table)

class gen_SampleTable(Base, NameMixin):
    material_id = foreignkey('gen_MaterialTable')
    project_id = foreignkey('gen_ProjectTable')
    labnumbers = relationship('gen_LabTable', backref='sample')


class gen_SensitivityTable(Base, BaseMixin):
    mass_spectrometer_id = foreignkey('gen_MassSpectrometerTable')
    sensitivity = Column(Float(32))
    create_date = Column(DateTime, default=func.now())
    user = stringcolumn()
    note = Column(BLOB)

    extractions = relationship('meas_ExtractionTable', backref='sensitivity')



class gen_UserTable(Base, NameMixin):
    
    analyses=relationship('meas_AnalysisTable', backref='user')
#    project_id = foreignkey('gen_ProjectTable')
    projects = relationship('gen_ProjectTable', secondary=association_table)
    
    
    password = stringcolumn(80)
    salt = stringcolumn(80)

    #===========================================================================
    # permissions
    #===========================================================================
    max_allowable_runs = Column(Integer, default=25)
    can_edit_scripts = Column(Boolean, default=False)
#===============================================================================
#
#===============================================================================
#============= EOF =============================================

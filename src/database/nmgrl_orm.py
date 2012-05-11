#===============================================================================
# Copyright 2011 Jake Ross
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



#=============enthought library imports=======================

#=============standard library imports ========================
from sqlalchemy import Column, Integer, Float, String, \
     ForeignKey, DateTime, Date, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, relationship

#=============local library imports  ==========================
Base = declarative_base()

class DataReductionSessionTable(Base):
    '''
    '''
    __tablename__ = 'datareductionsessiontable'
    DataReductionSessionID = Column(Integer, primary_key=True)
    SessionDate = Column(DateTime)

class DetectorTable(Base):
    '''
    '''
    __tablename__ = 'DetectorTable'
    DetectorID = Column(Integer, primary_key=True)
    DetectorTypeID = Column(Integer, default=0)
    EMV = Column(Float, default=0)
    Gain = Column(Float, default=0)
    Disc = Column(Float, default=1)
    DiscEr = Column(Float, default=0)
    ICFactor = Column(Float, default=1)
    ICFactorEr = Column(Float, default=0)
    IonCounterDeadtimeSec = Column(Float, default=0)
    Label = Column(String(40))

    isotopes = relation('IsotopeTable')


class IsotopeResultsTable(Base):
    '''
    iso = intercept - bkgrd
    '''
    __tablename__ = 'IsotopeResultsTable'
    Counter = Column(Integer, primary_key=True)
    LastSaved = Column(DateTime)
    IsotopeID = Column(Integer, ForeignKey('IsotopeTable.IsotopeID'))
    DataReductionSessionID = Column(Integer)
    InterceptEr = Column(Float)
    Intercept = Column(Float)
    Iso = Column(Float)
    IsoEr = Column(Float)
    CalibMolesPerSignalAtUnitGain = Column(Float)
    CalibMolesPerSignalAtUnitGainEr = Column(Float)
    SensCalibMoles = Column(Float)
    SensCalibMolesEr = Column(Float)
    VolumeCalibFactor = Column(Float)
    VolumeCalibFactorEr = Column(Float)
    VolumeCalibratedValue = Column(Float)
    VolumeCalibratedValueEr = Column(Float)
    Bkgd = Column(Float)
    BkgdEr = Column(Float)
    BkgdDetTypeID = Column(Integer)
    PkHtChangePct = Column(Float)
    Fit = Column(Integer)
    GOF = Column(Float)
    PeakScaleFactor = Column(Float)


class AnalysesChangeableItemsTable(Base):
    __tablename__ = 'AnalysesChangeableItemsTable'
    ChangeableItemsID = Column(Integer, primary_key=True)
    AnalysisID = Column(Integer, ForeignKey('AnalysesTable.AnalysisID'))
    Disc = Column(Float, default=1)
    DiscEr = Column(Float, default=0)
    History = Column(String, default='')
    StatusReason = Column(Integer, default=1)
    StatusLevel = Column(Integer, default=1)
    SignalNormalizationFactor = Column(Float, default=1)


class AnalysesTable(Base):
    '''
    '''
    __tablename__ = 'AnalysesTable'
    AnalysisID = Column(Integer, primary_key=True)
    RID = Column(String(40))

    IrradPosition = Column(Integer, ForeignKey('IrradiationPositionTable.IrradPosition'))
    SpecParametersID = Column(Integer, default=0)
    PwrAchievedSD = Column(Float, default=0)
    PwrAchieved_Max = Column(Float, default=0)
    DetInterCalibID = Column(Integer, default=0)
    AssociatedProjectID = Column(Integer, default=0)
    TrapCurrent = Column(Float, default=0)
    ManifoldOpt = Column(Integer, default=0)
    OriginalImportID = Column(String(1), default=0)
    RedundantSampleID = Column(Integer, ForeignKey('SampleTable.SampleID'))
    RunDateTime = Column(DateTime)
    LoginSessionID = Column(Integer)
    SpecRunType = Column(Integer)

    isotopes = relation('IsotopeTable', backref='AnalysesTable')
    araranalyses = relation('ArArAnalysisTable')
#    araranalyses = relation('ArArAnalysisTable', backref='AnalysesTable')
    changeable = relation('AnalysesChangeableItemsTable', uselist=False)


class ArArAnalysisTable(Base):
    '''
    WARNING
    the totals are not raw values and have been blank, discrimination and decay corrected already
    '''
    __tablename__ = 'ArArAnalysisTable'
#    AnalysisID = Column(Integer, primary_key=True)
    AnalysisID = Column(Integer, ForeignKey('AnalysesTable.AnalysisID'))
    DataReductionSessionID = Column(Integer)
    JVal = Column(Float, default=0)
    JEr = Column(Float, default=0)
    Tot40 = Column(Float, default=0)
    Tot39 = Column(Float, default=0)
    Tot38 = Column(Float, default=0)
    Tot37 = Column(Float, default=0)
    Tot36 = Column(Float, default=0)

    Tot40Er = Column(Float, default=0)
    Tot39Er = Column(Float, default=0)
    Tot38Er = Column(Float, default=0)
    Tot37Er = Column(Float, default=0)
    Tot36Er = Column(Float, default=0)

    Age = Column(Float, default=0, primary_key=True)
    ErrAge = Column(Float, default=0)


class BaselinesTable(Base):
    '''
    '''
    __tablename__ = 'baselinestable'
    BslnID = Column(Integer, primary_key=True)
    Label = Column(String(40))
    NumCnts = Column(Integer)
    PeakTimeBlob = Column(BLOB, nullable=True)


class MaterialTable(Base):
    '''
    '''
    __tablename__ = 'MaterialTable'
    ID = Column(Integer, primary_key=True)
    Material = Column(String(40))

    irradpositions = relation('IrradiationPositionTable')


class IrradiationPositionTable(Base):
    '''
    '''
    __tablename__ = 'IrradiationPositionTable'

    IrradPosition = Column(Integer, primary_key=True)
    IrradiationLevel = Column(String(40))
    HoleNumber = Column(Integer)
    Material = Column(String(40), ForeignKey('MaterialTable.Material'))
    SampleID = Column(Integer, ForeignKey('SampleTable.SampleID'))

    StandardID = Column(Integer, default=0)
    Size = Column(String(40), default='NULL')
    Weight = Column(Float, default=0)
    Note = Column(String(40), nullable=True)
    LabActivation = Column(Date, default='NULL')
    J = Column(Float, nullable=True)
    JEr = Column(Float, nullable=True)

    analyses = relation('AnalysesTable')


class IsotopeTable(Base):
    '''
    '''

    __tablename__ = 'IsotopeTable'
    IsotopeID = Column(Integer, primary_key=True)
    AnalysisID = Column(Integer, ForeignKey('AnalysesTable.AnalysisID'))
    DetectorID = Column(Integer, ForeignKey('DetectorTable.DetectorID'))
    BkgdDetectorID = Column(Integer, nullable=True)
    Label = Column(String(40))
    NumCnts = Column(Integer)
    NCyc = Column(Integer, nullable=True)
    #CycleStartIndexList
    #CycleStartIndexblob
    BslnID = Column(Integer, ForeignKey('baselinestable.BslnID'))
    RatNumerator = Column(Integer, nullable=True)
    RatDenominator = Column(Integer, nullable=True)
    HallProbeAtStartOfRun = Column(Float, nullable=True)
    HallProbeAtEndOfRun = Column(Float, nullable=True)

    peak_time_series = relation('PeakTimeTable')

    results = relation('IsotopeResultsTable')


class SampleTable(Base):
    '''
    '''
    __tablename__ = 'SampleTable'
    SampleID = Column(Integer, primary_key=True)
    Sample = Column(String(40))

    Project = Column(String(40))#, ForeignKey('projecttable.Project'))
#    Project = relation('ProjectTable', backref = 'SampleTable')
    ProjectID = Column(Integer, ForeignKey('projecttable.ProjectID'))

    Note = Column(String(40) , default='NULL')
    AlternateUserID = Column(String(40), default='NULL')
    CollectionDateTime = Column(DateTime, default='')
    Coordinates = Column(BLOB, default='NULL')
    Latitude = Column(String(40), default='NULL')
    Longitude = Column(String(40), default='NULL')
    Salinity = Column(Float, default=0)
    Temperature = Column(Float, default=0)

    irradpositions = relation('IrradiationPositionTable')
    analyses = relation('AnalysesTable')


class PeakTimeTable(Base):
    '''
    '''
    __tablename__ = 'PeakTimeTable'
    Counter = Column(Integer, primary_key=True)
    PeakTimeBlob = Column(BLOB)
    IsotopeID = Column(Integer, ForeignKey('IsotopeTable.IsotopeID'))

class ProjectTable(Base):
    '''
        G{classtree}
    '''
    __tablename__ = 'projecttable'
    ProjectID = Column(Integer, primary_key=True)
    Project = Column(String(40))
    samples = relation('SampleTable', backref='projecttable')

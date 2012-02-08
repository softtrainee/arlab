'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================

#=============standard library imports ========================
from sqlalchemy import Column, Integer, Float, String, \
     ForeignKey, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

#=============local library imports  ==========================
Base = declarative_base()

class Detectors(Base):
    __tablename__ = 'Detectors'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    gain = Column(Float)
    kind = Column(String(40))
    spectrometer_id = Column(Integer, ForeignKey('Spectrometers.id'))

class Spectrometers(Base):
    __tablename__ = 'Spectrometers'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    kind = Column(String(40))
    detectors = relationship('Detectors', order_by='Detectors.id')

class Analyses(Base):
    __tablename__ = 'Analyses'
    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('Samples.id'))
    status = Column(Integer, default=0)
    signals = relationship('Signals', backref='analysis')

class Samples(Base):
    __tablename__ = 'Samples'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    irradiation_id = Column(Integer, ForeignKey('Irradiations.id'))
    tray_id = Column(String(10), ForeignKey('IrradiationTrays.id'))
    holenum = Column(Integer)
    identifier = Column(Integer)
    analyses = relationship('Analyses', backref='sample')

class Signals(Base):
    __tablename__ = 'Signals'
    id = Column(Integer, primary_key=True)
    times = Column(BLOB)
    intensities = Column(BLOB)
    analysis_id = Column(Integer, ForeignKey('Analyses.id'))
    detector_id = Column(Integer, ForeignKey('Detectors.id'))
    detector = relationship('Detectors', backref='signals')

class Irradiations(Base):
    __tablename__ = 'Irradiations'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    reactor_id = Column(Integer, ForeignKey('Reactors.id'))

    samples = relationship('Samples', backref='irradiation')
    trays = relationship('IrradiationTrays', backref='irradiation')

class IrradiationTrays(Base):
    __tablename__ = 'IrradiationTrays'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    nholes = Column(Integer)
    irradiation_id = Column(Integer, ForeignKey('Irradiations.id'))
    samples = relationship('Samples', backref='irradiation_tray')


class Reactors(Base):
    __tablename__ = 'Reactors'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    irradiations = relationship('Irradiations', backref='reactor')
#class ArArAnalyses(Base):
#    __tablename__ = 'ArArAnalyses'
#    id = Column(Integer, primary_key = True)
#    analysis_id = Column(Integer, ForeignKey('Analyses.id'))
#    age = Column(Float)
#    error = Column(Float)
#class Projects(Base):
#    __tablename__ = 'Projects'
#    id = Column(Integer, primary_key = True)
#    name = Column(String(40))
#
#    samples = relation('Samples')
#
#
#class IrradiationHoles(Base):
#    __tablename__ = 'IrradiationHoles'
#    id = Column(Integer, primary_key = True)
#    irradiation_id = Column(Integer, ForeignKey('Irradiations.id'))
#    j = Column(Float)
#    jer = Column(Float)
#    hole = Column(Integer)
#    sample = relation('Samples', uselist = False, backref = backref('hole'))
#
#class IrradiationChronologies(Base):
#    __tablename__ = 'IrradiationChronologies'
#    id = Column(Integer, primary_key = True)
#    irradiation_id = Column(Integer, ForeignKey('Irradiations.id'))
#    start_time = Column(DateTime)
#    end_time = Column(DateTime)
#
#class IrradiationProductionRatios(Base):
#    __tablename__ = 'IrradiationProductionRatios'
#    id = Column(Integer, primary_key = True)
#    irradiation_id = Column(Integer, ForeignKey('Irradiations.id'))
#    ca3637 = Column(Float)
#    ca3837 = Column(Float)
#    ca3937 = Column(Float)
#    k3739 = Column(Float)
#    k3839 = Column(Float)
#    k4039 = Column(Float)
#    cl3638 = Column(Float)
#    cak = Column(Float)
#    clk = Column(Float)
#
#    ca3637er = Column(Float)
#    ca3837er = Column(Float)
#    ca3937er = Column(Float)
#    k3739er = Column(Float)
#    k3839er = Column(Float)
#    k4039er = Column(Float)
#    cl3638er = Column(Float)
#    caker = Column(Float)
#    clker = Column(Float)
#
#class Samples(Base):
#    '''
#        
#    '''
#    __tablename__ = 'Samples'
#    id = Column(Integer, primary_key = True)
#    name = Column(String(40))
#    project_id = Column(Integer, ForeignKey('Projects.id'))
#    irradiation_hole_id = Column(Integer, ForeignKey('IrradiationHoles.id'))
#
#    analyses = relation('Analyses', backref = 'sample')

#
#    corrected_signal = relation('CorrectedSignals', uselist = False)
#
#class Users(Base):
#    __tablename__ = 'Users'
#    id = Column(Integer, primary_key = True)
#    name = Column(String(40))

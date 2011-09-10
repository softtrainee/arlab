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
#@PydevCodeAnalysisIgnore

from sqlalchemy import *
from migrate import *
meta = MetaData()
projects = Table('Projects', meta,
	Column('id', Integer, primary_key=True),
	Column('name', String(40)),
)

users = Table('Users', meta,
	Column('id', Integer, primary_key=True),
	Column('name', String(40)),
	Column('phone', String(40)),
    Column('email', String(40)),
    Column('website', String(40)),
    Column('access_level', Integer),
)

samples = Table('Samples', meta,
    Column('id', Integer, primary_key=True),
)

analyses = Table('Analyses', meta,
    Column('id', Integer, primary_key=True),
    Column('identifier', Integer),
    Column('status', Integer)
)

spec = Table('Spectrometers', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(40)),
    Column('kind', String(40)),
)

extractionlines = Table('ExtractionLines', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(40)),
)

runconfig = Table('RunConfigurations', meta,
    Column('id', Integer, primary_key=True),
)

exconfig = Table('ExtractionConfigurations', meta,
    Column('id', Integer, primary_key=True),
)

scripts = Table('Scripts', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(40)),
    Column('kind', String(40)),
    Column('contents', BLOB)
)

signals = Table('Signals', meta,
    Column('id', Integer, primary_key=True),
    Column('times', BLOB),
    Column('intensities', BLOB),
    Column('mass', Float)
)

fitsignals = Table('FitSignals', meta,
    Column('id', Integer, primary_key=True),
    Column('i0', Float),
    Column('i0_err', Float),
    Column('fit', String(40)),
)

detectors = Table('Detectors', meta,
    Column('id', Integer, primary_key=True),
    Column('gain', Float),
    Column('kind', String(40)),
    Column('name', String(40)),
    Column('spectrometer_id', Integer, ForeignKey('Spectrometers.id'))
)

tables = [
        users, projects,
        samples, analyses, spec,
        extractionlines, exconfig,
        runconfig, scripts,
        signals, fitsignals, detectors
        ]

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    meta.bind = migrate_engine
    for t in tables:
        try:
            t.create()
        except:
            pass

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    for t in tables:
        t.drop()


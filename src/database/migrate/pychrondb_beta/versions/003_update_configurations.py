#@PydevCodeAnalysisIgnore

from sqlalchemy import *
from migrate import *
meta = MetaData()
et = Table('ExtractionConfigurations', meta)
rt = Table('RunConfigurations', meta)

rcol = Column('name', String(40))
ecol = Column('name', String(40))

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    meta.bind = migrate_engine
    ecol.create(et)
    rcol.create(rt)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    ecol.drop(et)
    rcol.drop(rt)
#@PydevCodeAnalysisIgnore

from sqlalchemy import *
from migrate import *
meta = MetaData()
table = Table('Samples', meta)
ocol = Column('tray', String(10))
ncol = Column('tray_id', Integer)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    meta.bind = migrate_engine
    ocol.drop(table)
    ncol.create(table)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    ocol.create(table)
    ncol.drop(table)
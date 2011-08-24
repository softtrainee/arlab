#@PydevCodeAnalysisIgnore

from sqlalchemy import *
from migrate import *
meta = MetaData()
table = Table('Samples', meta)
cols = [
    Column('irradiation_id', Integer),
    Column('holenum', Integer),
    Column('tray', String(10)),
    ]

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    meta.bind = migrate_engine
    for col in cols:
        col.create(table)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    for col in cols:
        col.drop(table)
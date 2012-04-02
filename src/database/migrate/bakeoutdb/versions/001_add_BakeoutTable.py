from sqlalchemy import *
from migrate import *
meta=MetaData()
t=Table('BakeoutTable',meta,
              Column('id', Integer, primary_key=True),
              Column('rundate',Date),
              Column('runtime',Time),
              )

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind=migrate_engine
    t.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind=migrate_engine
    t.drop()
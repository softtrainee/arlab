from sqlalchemy import *
from migrate import *
meta=MetaData()
t1 = Table('ScanTable', meta,
			Column('id', Integer, primary_key=True),
              Column('rundate', Date),
              Column('runtime', Time),
              Column('device_id',Integer)
)
t2=Table('DeviceTable',meta,
	Column('id', Integer, primary_key=True),
	Column('name', String(80)),
	Column('klass',String(80))
)
t3=Table('PathTable', meta,
	Column('id', Integer, primary_key=True),
	Column('root',String(200)),
	Column('filename',String(80)),
	Column('scan_id', Integer)
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind=migrate_engine
    t1.create()
    t2.create()
    t3.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind=migrate_engine
    t1.drop()
    t2.drop()
    t3.drop()

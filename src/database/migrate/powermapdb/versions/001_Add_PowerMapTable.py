from sqlalchemy import *
from migrate import *
meta=MetaData()
table=Table('PowerMapTable',meta,
			Column('id', Integer, primary_key=True),
              Column('rundate',Date),
              Column('runtime',Time),
)
def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
	meta.bind=migrate_engine
	table.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
	meta.bind=migrate_engine
	table.drop()
from sqlalchemy import MetaData, Column, Integer, Table, String, MetaData
meta=MetaData()
path=Table('paths',meta,
           Column('id', Integer, primary_key=True),
           Column('name', String(40)),
           Column('path',String(128))
           )

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind=migrate_engine
    path.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind=migrate_engine
    path.drop()
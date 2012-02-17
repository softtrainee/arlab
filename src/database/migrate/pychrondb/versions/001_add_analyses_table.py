from sqlalchemy import Integer, Column, MetaData, Table, DateTime

meta=MetaData()

analyses=Table(
               'analyses',meta,
               Column('id',Integer,primary_key=True),
               Column('runtime', DateTime),
               Column('spectrometer_id', Integer),
               Column('type_id', Integer)
               )

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind=migrate_engine
    analyses.create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind=migrate_engine
    analyses.drop()

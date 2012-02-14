from sqlalchemy import MetaData, Table, Column, Integer, Float

meta=MetaData()
intercepts=Table('intercepts', meta,
                 Column('id', Integer, primary_key=True),
                 Column('analysis_id', Integer),
                 Column('m40', Float),
                 Column('m39', Float),
                 Column('m38', Float),
                 Column('m37', Float),
                 Column('m36', Float),
                 Column('m40er', Float),
                 Column('m39er', Float),
                 Column('m38er', Float),
                 Column('m37er', Float),
                 Column('m36er', Float),
                 )


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind=migrate_engine
    intercepts.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind=migrate_engine
    intercepts.drop()
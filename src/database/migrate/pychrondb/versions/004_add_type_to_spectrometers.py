from sqlalchemy import MetaData, Table, Column, String


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta=MetaData(bind=migrate_engine)
    spec=Table('spectrometers',meta, autoload=True)
    
    type1=Column('type',String(40))
    type1.create(spec)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta=MetaData(bind=migrate_engine)
    spec=Table('spectrometers',meta, autoload=True)
    spec.c.type.drop()

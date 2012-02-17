from sqlalchemy import MetaData, Time, Table, Date, Column


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta=MetaData(bind=migrate_engine)
    a=Table('analyses',meta,autoload=True)
    
    a.c.runtime.alter(type=Time)
    
    col=Column('rundate',Date)
    col.create(a)
    
def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta=MetaData(bind=migrate_engine)
    a=Table('analyses',meta,autoload=True)
    a.c.rundate.drop()

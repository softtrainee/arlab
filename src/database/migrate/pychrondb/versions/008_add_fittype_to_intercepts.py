from sqlalchemy import Table, Column, Integer, MetaData


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta=MetaData(bind=migrate_engine)
    inter=Table('intercepts',meta,autoload=True)
    fit40=Column('fit40',Integer)
    fit39=Column('fit39',Integer)
    fit38=Column('fit38',Integer)
    fit37=Column('fit37',Integer)
    fit36=Column('fit36',Integer)
    
    fit40.create(inter)
    fit39.create(inter)
    fit38.create(inter)
    fit37.create(inter)
    fit36.create(inter)
    
def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta=MetaData(bind=migrate_engine)
    inter=Table('intercepts',meta,autoload=True)
    
    inter.c.fit40.drop()
    inter.c.fit39.drop()
    inter.c.fit38.drop()
    inter.c.fit37.drop()
    inter.c.fit36.drop()
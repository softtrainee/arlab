from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta=MetaData(bind=migrate_engine)
    t=Table('ControllerTable',meta, autoload=True)
    s=Column('script',String(40))
    sp=Column('setpoint',Float)
    d=Column('duration',Float)
    
    s.create(t)
    sp.create(t)
    d.create(t)
    
def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta=MetaData(bind=migrate_engine)
    t=Table('ControllerTable',meta, autoload=True)
    t.c.duration.drop()
    t.c.script.drop()
    t.c.setpoint.drop()
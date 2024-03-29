#===============================================================================
# Copyright 2011 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

from sqlalchemy import *
from migrate import *

meta = MetaData()

t1 = Table('VideoTable', meta,
            Column('id', Integer, primary_key=True),
              Column('rundate', Date),
              Column('runtime', Time),

)
t2 = Table('VideoPathTable', meta,
              Column('id', Integer, primary_key=True),
              Column('root', String(200)),
              Column('filename', String(80)),
              Column('video_id', Integer)
              )

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    t1.create()
    t2.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    t1.drop()
    t2.drop()

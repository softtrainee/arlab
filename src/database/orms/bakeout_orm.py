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

#=============enthought library imports=======================

#=============standard library imports ========================
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, \
     ForeignKey
from sqlalchemy.orm import relationship

#=============local library imports  ==========================
from src.database.core.base_orm import ResultsMixin, BaseMixin, PathMixin

Base = declarative_base()


class BakeoutTable(Base, ResultsMixin):
    controllers = relationship('ControllerTable')

class ControllerTable(Base, BaseMixin):
    bakeout_id = Column(Integer, ForeignKey('BakeoutTable.id'))

    name = Column(String(40))
    setpoint = Column(Float)
    duration = Column(Float)
    script = Column(String(40))

class BakeoutPathTable(Base, PathMixin):
    bakeout_id = Column(Integer, ForeignKey('BakeoutTable.id'))


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
from sqlalchemy import Column, Integer, Float, String, \
     ForeignKey, BLOB, DateTime, Time, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

#=============local library imports  ==========================
from base_orm import ResultsMixin, PathMixin
Base = declarative_base()


class PowerTable(Base, ResultsMixin):
    rid = Column(String(80))
#    __tablename__ = 'PowerTable'
#    id = Column(Integer, primary_key=True)
#    runtime = Column(Time)
#    rundate = Column(Date)

#    path = relationship('PowerPathTable', uselist=False)

class PowerPathTable(Base, PathMixin):
#    __tablename__ = 'PowerPathTable'
#    id = Column(Integer, primary_key=True)
    power_id = Column(Integer, ForeignKey('PowerTable.id'))

#    root = Column(String(200))
#    filename = Column(String(80))



#===============================================================================
# brightness
#===============================================================================
class BrightnessTable(Base, ResultsMixin):
    pass
#    __tablename__ = 'BrightnessTable'
#    id = Column(Integer, primary_key=True)
#    runtime = Column(Time)
#    rundate = Column(Date)

#    path = relationship('BrightnessPathTable', uselist=False)


class BrightnessPathTable(Base, PathMixin):
#    __tablename__ = 'BrightnessPathTable'
#    id = Column(Integer, primary_key=True)
    brightness_id = Column(Integer, ForeignKey('BrightnessTable.id'))

#    root = Column(String(200))
#    filename = Column(String(80))

#============= EOF =============================================


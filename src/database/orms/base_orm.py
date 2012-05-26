#===============================================================================
# Copyright 2012 Jake Ross
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

#============= enthought library imports =======================

#============= standard library imports ========================
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Time, Date
#============= local library imports  ==========================

class BaseMixin(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__

    id = Column(Integer, primary_key=True)

class ResultsMixin(BaseMixin):
    runtime = Column(Time)
    rundate = Column(Date)

    @declared_attr
    def path(self):
        name = self.__name__.replace('Table', 'PathTable')
        return relationship(name, uselist=False)


class RIDMixin(ResultsMixin):
    rid = Column(String(80))


class PathMixin(BaseMixin):
    root = Column(String(200))
    filename = Column(String(80))

#============= EOF =============================================

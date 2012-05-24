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

class VideoTable(Base, ResultsMixin):
    rid = Column(String(40))

class VideoPathTable(Base, PathMixin):
    video_id = Column(Integer, ForeignKey('VideoTable.id'))


#============= EOF =============================================



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



'''
RossLabs 2009
Ross  Jake Ross   jirhiker@gmail.com

Nov 11, 2009
'''

#=============enthought library imports=======================

#=============standard library imports ========================
import pickle
import os
#=============local library imports  ==========================
class KMLWriterConfigurationStream:
    pass
class KMLWriterConfiguration:
    source_paths = []

    style_dict = {}
    schema_dict = {}
    placemarker_dict = {}

    output_path = ''
    source_dir = ''
    image_dir = ''

    use_default = False
    display_figure = False
    age_in_name = False
    age_only = False

    image_tag = 'L#'


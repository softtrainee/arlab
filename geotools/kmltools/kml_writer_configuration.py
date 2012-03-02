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
    age_only=False
    
    image_tag = 'L#'


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

Nov 14, 2009
'''

#=============enthought library imports=======================

#=============standard library imports ========================
import csv
#=============local library imports  ==========================

def find_col(names, sh):
    index = None
    for i in names:
        try:
            index = sh.index(i)
        except:
            pass
        if index is not None:
            break
    return index
def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result
def import_csv(src_path):
    reader = csv.reader(open(src_path, 'U'))
    header = reader.next()
    data = [row for row in reader]
    return header, data
#
#def get_col_index(name, header):
#
#    if name == 'latitude':
#        names = flatten([(i.capitalize(), i.upper(), i) for i in [name[:3], name]])
#    elif name == 'sample' or name == 'name':
#        names = ['Sample Name', name, 'name', 'Name', 'sample_name', 'Sample_Name']
#    elif name == 'age':
#        names = [name.capitalize(), name.upper(), name]
#    elif name == 'longitude':
#        names = flatten([(i.capitalize(), i.upper(), i) for i in [name[:3], name[:4], name]])
#    elif name == 'elevation':
#        names = flatten([(i.capitalize(), i.upper(), i) for i in [name[:4], name]])
#    return find_col(names, header)

'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup
from src.helpers.hwc_parser import HWCParser

#============= standard library imports ========================
#import sys
import os
import re
#============= local library imports  ==========================

class HardwareCreator():
    hardware_name = None
    input_path = None
    out_path = None
    def __init__(self, name, in_path, out_path):
        self.hardware_name = name
        self.input_path = in_path
        self.out_path = out_path
        self.parser = HWCParser(self.input_path)

    def create(self):
        self.write_to_file(self.out_path)

    def write_to_file(self, p):
        with open(p, 'w') as f:
            f.write(self.render())

    def render(self):
        render_dict = dict(imports = 'from src.hardware.core.core_device import CoreDevice',
                           hw_name = self.hardware_name)
        self.text = '''
{imports}
class {hw_name}(CoreDevice):
'''.format(**render_dict)
        self._add_class_attributes()
        self._add_icore_interface()
        self._add_class_interface()
        self._add_private_interface()

        return self.text

    def _add_icore_interface(self):
        self._add_comment_block('icore device interface')

        self.text += '''
    def set(self, v):
        {set_func}

    def get(self):
        v = CoreDevice.get(self)
        if v is None:
            v = self.{get_func}()

        return v
        
'''.format(
           set_func = 'pass',
           get_func = 'foo',
           )

    def _add_class_attributes(self):
        for k, v in self.parser.get_class_attributes():
            self.text += "    {} = '{}'\n".format(k, v)

    def _add_class_interface(self):
        self._add_comment_block('{} interface'.format(self.hardware_name))
        for func in self.parser.get_functions():
            self.text += '''
    def {name}(self, {args}{kwargs}):
        {body}
'''.format(**func)

    def _add_configloadable_interface(self):
        self.text += '''
'''.format()

    def _add_private_interface(self):
        self._add_comment_block('private interface')
        self.text += '''
    def _build_command(self, cmd, *args, **kw):
        return cmd
        
    def _parse_response(self, resp, *args, **kw):
        return resp
'''
    def _add_comment_block(self, comment):
        self.text += '''    #===============================================================================
    # {}
    #===============================================================================
    '''.format(comment)

    def _add_eof(self):
        self.text += '\n#============= EOF ============================================='

def space_out_camel_case(stringAsCamelCase):
    """Adds spaces to a camel case string.  Failure to space out string returns the original string.
    >>> space_out_camel_case('DMLSServicesOtherBSTextLLC')
    'DMLS Services Other BS Text LLC'
    """

    pattern = re.compile('([A-Z][A-Z][a-z])|([a-z][A-Z])')
    if stringAsCamelCase is None:
        return None

    return pattern.sub(lambda m: m.group()[:1] + '_' + m.group()[1:], stringAsCamelCase)

def hardware_file_name(name):
    return '_'.join([a.lower() for a in space_out_camel_case(name).split('_')])

if __name__ == '__main__':
#    d = HardwareCreator()

    import argparse

    parser = argparse.ArgumentParser(description = 'Create a new hardware device')

    parser.add_argument('class_name', metavar = 'class_name', type = str, nargs = '?',
                       help = 'camel case class name')

    parser.add_argument('-o', metavar = 'file_name', type = str, nargs = '?',
                       help = 'Python file name for the hardware',
                       default = None)
    parser.add_argument('-i', metavar = 'input file_name', type = str, nargs = '?',
                       help = 'XML input file ',
                       default = None)

#    parser.add_argument('--sum', dest = 'accumulate', action = 'store_const',
#                       const = sum, default = max,
#                       help = 'sum the integers (default: find the max)')

    args = parser.parse_args()

    name = args.class_name
    oname = args.o
    if oname is None:
        oname = hardware_file_name(args.class_name)

    h = HardwareCreator(name, args.i, os.path.join(os.getcwd(), oname + '.py'))
    h.create()

    #print args.accumulate(args.integers)


#    print sys.argv[1:]
#
#    p = os.path.join(os.getcwd(),)

    #p = '/Users/Ross/Desktop/hwtest.py'
    #d.write_to_file(p)
#============= EOF =============================================

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
#============= standard library imports ========================
import argparse
#============= local library imports  ==========================
from installer import Installer

def cli_install():

    parser = argparse.ArgumentParser(description='Create a new Launchable Application')
    parser.add_argument('prefix',
                        #metavar = 'prefix', 
                        type=str, nargs='?',
                        help='Prefix name. used to identify the icon file and the launch script eg. pychron'
                        )
    parser.add_argument('name',
                        #metavar = 'name', 
                        type=str, nargs='?',
                        help='Name of the application bundle eg. Pychron')

    parser.add_argument('--icon', type=str, nargs='?',
                        help='icon file name')
    args = parser.parse_args()

    i = Installer(args.prefix, args.name, args.icon)
    i.install()

if __name__ == '__main__':

    cli_install()
#============= EOF =====================================  

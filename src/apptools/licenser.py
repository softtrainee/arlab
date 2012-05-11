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


this module is used to add licensing. 

specify a directory and the licenser will recursively visit all .py files, 
check to see it there is current licensing info and if not will add it.

specify a single file to add license only to that file

use keyword --remove to strip out the license information from a directory or file

TODO
since the license text is not pure boilerplate and files could have variable copyright years and authors
probably need to use a regex to check and remove license info instead of "in" and "replace" 
'''



#============= standard library imports ========================
import os
import datetime
import argparse

#============= local library imports  ==========================
from terminal import render

APACHE = '''
#===============================================================================
# Copyright {} {}
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

def render_red(msg):
    print render('%(RED)s{}%(NORMAL)s'.format(msg))
def render_blue(msg):
    print render('%(BLUE)s{}%(NORMAL)s'.format(msg))

def get_license(year, author):
    return "'''{}'''\n".format(APACHE.format(year, author))

def run(p, year, author, remove=False):

    if not os.path.exists(p) or (not os.path.isfile(p) and not os.path.isdir(p)):
        render_red('Invalid path {}'.format(p))
        return

    license = get_license(year, author)

    if os.path.isdir(p):
        for root, dirnames, files in os.walk(p):
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            for f in files:
                if f.startswith('.') or not f.endswith('.py'):
                    continue

                p = os.path.join(root, f)
                if remove:
                    func = remove_license
                else:
                    func = add_license

                func(p, license)

    elif os.path.isfile(p):
            add_license(p, license)

def remove_license(p, license):
    with open(p, 'r') as f:
        lines = ''.join([l for l in f])

    if license in lines:
        print 'remove license from {}'.format(p)
        lines = lines.replace(license, '')

    with open(p, 'w') as f:
        f.write(lines)

def add_license(p, license):
    with open(p, 'r') as f:
        lines = [l for l in f]

    with open(p, 'w') as f:

        #if the first 2 chars of the first line are a shebang
        #setting an interperter directive
        #skip
        if lines:
            if lines[0][:2] == '#!':
                f.write(lines[0])
                lines = lines[1:]

        #if already has this license clause dont add to file
        txt = ''.join(lines)
        render_red('checking {}'.format(p))
        if not license in txt:
            ci = [c for c in  ['Copyright', 'COPYRIGHT', 'copywrite'] if c in txt]
            if ci:
                render_blue('{} in {}'.format(ci, p))
            else:
                print 'adding license to {}'.format(p)
                f.write(license)

        f.write(txt)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='add license to file or directory tree')
    parser.add_argument('path', nargs=1, help='file or top of directory tree')
    parser.add_argument('-a', '--author', default='Jake Ross', help='copyright holder')
    parser.add_argument('-y', '--year', default=datetime.datetime.now().year, help='copyright year')
    parser.add_argument('-r', '--remove', action='store_true', help='remove license from file or directory tree')

    args = parser.parse_args()



    run(args.path, args.year, args.author, remove=args.remove)
#============= EOF =====================================

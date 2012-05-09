'''
Copyright 2012 Jake Ross

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
#from traits.api import HasTraits
#from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import os
import shutil
import zipfile
import argparse
#============= local library imports  ==========================
def make_pyc_archive(top, dst, clean=True):
    if clean:
        #remove the dst directory
        shutil.rmtree(dst)

    copy_pyc_files(top, dst)
    make_archive(dst)

def copy_pyc_files(top, dst):
    for r, _, f in os.walk(top):
        for fi in f:
            if fi.endswith('.pyc'):
                rr = r.split('pychron_beta')[1]
                if rr:
                    np = dst + rr
    #                np = os.path.join(dst, rr)
                else:
                    np = dst

                if not os.path.isdir(np):
                    print 'creating directory ', np
                    os.mkdir(np)

                si = os.path.join(r, fi)
                di = os.path.join(np, fi)
                print 'copying', si, 'to ', di
                shutil.copy(si, di)

def make_archive(dst):
    p = os.path.join(os.path.dirname(dst), 'pychron_source.zip')
    zi = zipfile.ZipFile(p, 'w')
    for r , _, f in os.walk(dst):
        for fi in f:
            if fi.startswith('.'):
                continue

            p = os.path.join(r, fi)
            print 'writing', p, 'to archive'
            zi.write(p)


if __name__ == '__main__':
    top = '/Users/ross/Programming/mercurial/pychron_beta'
    dst = '/Users/ross/Programming/mercurial/pyc'

    parser = argparse.ArgumentParser(description='Install Pychron')


    parser.add_argument(
        'src',
        metavar='src',
        type=str,
        nargs=1,
#        default='pychron',
        help='path to the source directory',
        )

    parser.add_argument(
        'dst',
        metavar='dst',
        type=str,
        nargs=1,
#        default='pychron',
        help='path to the destination directory',
        )

    args = parser.parse_args()

    top = args.top[0]
    dst = args.dst[0]
    if top != dst:
#    if top == '.':
#        top = os.getcwd()

        make_pyc_archive(top, dst)


#============= EOF =============================================

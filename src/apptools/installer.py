#!/usr/bin/python
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

import os
import sys
import shutil
import plistlib
def rec_make(pi):
    if pi and not os.path.exists(pi):
        try:
            os.mkdir(pi)
        except OSError:
            rec_make(os.path.split(pi)[0])
            os.mkdir(pi)

class Installer(object):

    prefix = None
    name = None
    icon_name = None
    version = ''
    include_pkgs = None
    include_mods = None
    def __init__(
        self,
        prefix,
        name,
        bundle_name=None,
        icon_name=None,
        include_pkgs=None,
        include_mods=None
        ):
        self.prefix = prefix
        self.name = name
        self.bundle_name = bundle_name if bundle_name else name
        self.icon_name = icon_name
        if include_pkgs is None:
            include_pkgs = []
        self.include_pkgs = include_pkgs

        if include_mods is None:
            include_mods = []
        self.include_mods = include_mods

    def change_version(self, op):
        np = op + '~'

        os.rename(op, np)
        dst = open(op, 'w')
        src = open(np, 'r')

        _version = "'{}'\n".format(self.version)
        print 'setting to version {}'.format(_version)
        for line in src:
            if line.startswith('version'):
                line = 'version = {}'.format(_version)

            dst.write(line)

        # close temp file
        src.close()
        dst.close()
        os.unlink(src.name)

    def install(self, root, version_name=None):
        if sys.platform == 'darwin':
            from BuildApplet import buildapplet
            print
            print 'Building {}.py as {}.app'.format(self.name, self.bundle_name)

            launchers_root = os.path.join(root, 'launchers')

            # ===================================================================
            # run build applet
            # ===================================================================
            op = os.path.join(launchers_root,
                            '{}.py'.format(self.name))
            sys.argv[1:] = [op]

            # set the version in the script
            # of = open(op, 'r')
#            self.change_version(op)
#            self.change_version(os.path.join(root, 'src', 'helpers', 'paths.py'))

            buildapplet()

            dist_root = os.path.join(launchers_root,
                    '{}.app/Contents'.format(self.prefix)
                    )

            if self.icon_name is not None:
                icon_file = '{}.icns'.format(self.icon_name)
            else:

                icon_file = '{}_icon.icns'.format(self.prefix)

            # ===================================================================
            # copy files
            # ===================================================================

            icon = os.path.join(root, 'resources', 'apps', icon_file)
            print icon
            if os.path.isfile(icon):
                shutil.copyfile(icon, os.path.join(dist_root,
                                'Resources', icon_file))
            else:
                print '----- No Icon File for {} -----'.format(self.prefix)

            resource_path = lambda x: os.path.join(dist_root, 'Resources', x)
            src_path = lambda x:resource_path(os.path.join('src', x))
            # copy the helpers module
            helpers_path = os.path.join(launchers_root, 'helpers.py')
            if os.path.isfile(helpers_path):
                shutil.copyfile(helpers_path,
                                resource_path('helpers.py')
                                )

            #===================================================================
            # copy all source file
            # will make this bundle self contained
            #===================================================================
            if not self.include_pkgs:
                print 'Copying entire src tree'
                # copy entire src directory
                shutil.copytree(os.path.join(root, 'src'),
                            resource_path('src'))
            else:
                print 'Copying include_pkgs...'
                self.include_pkgs.sort()
                for di in self.include_pkgs:
                    print 'pkg - ', di
                    shutil.copytree(os.path.join(root, 'src', di),
                                src_path(di))

            print 'Copying include_mods...'
            self.include_mods.sort()
            for mi in self.include_mods:
                print 'mod - ', mi
                mi = '{}.py'.format(mi)

                try:
                    shutil.copyfile(os.path.join(root, 'src', mi),
                                src_path(mi)
                                )
                except IOError:
                    di = os.path.dirname(src_path(mi))
                    rec_make(di)
                    shutil.copyfile(os.path.join(root, 'src', os.path.dirname(mi), '__init__.py'),
                                    os.path.join(di, '__init__.py')
                                    )
                    shutil.copyfile(os.path.join(root, 'src', mi),
                                src_path(mi)
                                )


            # walk the resource dir and add __init__ if missing
            for rt, _, files in os.walk(resource_path('src')):
                if not '__init__.py' in files:
                    p = os.path.join(rt, '__init__.py')
                    with open(p, 'w') as f:
                        pass


            shutil.copyfile(os.path.join(root, 'globals.py'),
                            resource_path('globals.py')
                            )

#            # copy pngs
#            for name in map('{}.png'.format, ['red_ball',
#                                              'gray_ball', 'green_ball',
#                                              'orange_ball', 'yellow_ball']):
#                shutil.copyfile(os.path.join(root, 'resources', name),
#                            resource_path(name)
#                            )

            # move splash and about into place
            if version_name:
                for ni, nd in (('splash', 'splashes'), ('about', 'abouts'),
                               ):
                    sname = '{}_{}.png'.format(ni, version_name)
                    shutil.copyfile(os.path.join(root, 'resources', nd, sname),
                                    resource_path(sname)
                                )

            for bi in ('blue', 'red', 'green', 'yellow', 'orange', 'gray'):
                name = '{}_ball.png'.format(bi)
#                print os.path.join(root, 'resources','balls',name)
                shutil.copyfile(os.path.join(root, 'resources', 'balls', name),
                                resource_path(name)
                                )




            # ===================================================================
            # #edit the plist
            # ===================================================================

            info_plist = os.path.join(dist_root, 'Info.plist')
            tree = plistlib.readPlist(info_plist)

            tree['CFBundleIconFile'] = icon_file
            tree['CFBundleName'] = self.bundle_name

            plistlib.writePlist(tree, info_plist)
            print 'Created {}'.format(os.path.join(launchers_root,
                    '{}.py'.format(self.name)))

            if self.bundle_name != self.prefix:
                print 'renaming {} to {}'.format(self.prefix, self.bundle_name)
                old = os.path.join(launchers_root, '{}.app'.format(self.prefix))
                new = os.path.join(launchers_root, '{}.app'.format(self.bundle_name))
                i = 0
                while 1:
                    try:
                        os.rename(old, new)
                        break
                    except OSError:
                        name = new[:-4]
                        bk = '{}_{:03d}bk.app'.format(name, i)
                        print '{} already exists. backing it up as {}'.format(new, bk)
                        try:
                            os.rename(new, bk)
                        except OSError:
                            i += 1

# ============= EOF =====================================

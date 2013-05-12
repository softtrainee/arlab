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
            name = self.name
            if version_name:
                name = '{}_{}'.format(name, version_name)

            print self.prefix
            print 'Building {}.py as {}.app'.format(name, self.bundle_name)

            launchers_root = os.path.join(root, 'launchers')

            # ===================================================================
            # run build applet
            # ===================================================================
            op = os.path.join(launchers_root,
                            '{}.py'.format(name))
#            sys.argv[1:] = [op]

            # set the version in the script
            # of = open(op, 'r')
#            self.change_version(op)
#            self.change_version(os.path.join(root, 'src', 'helpers', 'paths.py'))

            buildapplet(op)

            resource_path = lambda x: os.path.join(dist_root, 'Resources', x)
            dist_root = os.path.join(launchers_root, '{}.app/Contents'.format(name))

            if self.icon_name is not None:
                icon_file = '{}.icns'.format(self.icon_name)
            else:
                icon_file = 'py{}_icon.icns'.format(version_name)

            # make an egg
            version = '2.0.0'
            self._make_egg(root,
                           version,
                           resource_path
                           )

            self._copy_resources(version_name, root,
                                 launchers_root,
                                 resource_path,
                                 icon_file,
                                 version)

#            # make old bundle
#            self._make_bundle(root, launchers_root, dist_root, resource_path, version_name)

            # ===================================================================
            # #edit the plist
            # ===================================================================

            info_plist = os.path.join(dist_root, 'Info.plist')
            tree = plistlib.readPlist(info_plist)

            print icon_file
            tree['CFBundleIconFile'] = icon_file
            tree['CFBundleName'] = self.bundle_name

            # rewrite __argvemulator
            argv = '''
import os
execfile(os.path.join(os.path.split(__file__)[0], "{}.py"))
'''.format(name)

            p = resource_path('__argvemulator_{}.py'.format(name))
            with open(p, 'w') as fp:
                fp.write(argv)

            plistlib.writePlist(tree, info_plist)
            print 'Created {}'.format(os.path.join(launchers_root,
                    '{}.py'.format(name)))

            if self.bundle_name != self.prefix:
                print 'renaming {} to {}'.format(self.prefix, self.bundle_name)
                old = os.path.join(launchers_root, '{}.app'.format(name))
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

    def _make_egg(self, root, version, resource_path):

        from setuptools import setup, find_packages

        pkgs = find_packages(root,
                            exclude=('launchers', 'tests', 'app_utils')
                            )
        setup(name='pychron',
 #
 #              script_name='my_setup.py',
              script_args=('bdist_egg',),
              version=version,
              packages=pkgs
              )

        # make the .pth file
        with open(resource_path('pychron.pth')) as fp:
            fp.write('{}\n'.format('pychron-{}-py2.7.egg'))

    def _copy_resources(self, version_name, root,
                        launchers_root,
                        resource_path, icon_file,
                        egg_version
                        ):
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

        icon = os.path.join(root, 'resources', 'apps', icon_file)
        if os.path.isfile(icon):
            shutil.copyfile(icon,
                            resource_path(icon_file)
#                            os.path.join(dist_root,
#                            'Resources', icon_file)
                            )
        else:
            print '----- No Icon File for {} -----'.format(self.prefix)

        # copy the helpers module
        helpers_path = os.path.join(launchers_root, 'helpers.py')
        if os.path.isfile(helpers_path):
            shutil.copyfile(helpers_path,
                            resource_path('helpers.py')
                            )

        egg_name = 'pychron-{}-py2.7.egg'.format(egg_version)
        # copy the egg
        egg_path = os.path.join(root, 'dist',
                                egg_name)
        if os.path.isfile(egg_path):
            shutil.copyfile(
                            egg_path,
                            resource_path(egg_name)
                            )


#        pthname = 'pychron.pth'
#        pth_path = os.path.join(launchers_root, pthname)
        if os.path.isfile(pth_path):
            # copy the .pth
            shutil.copyfile(
                            pth_path,
                            resource_path(pthname)
                            )


    def _make_bundle(self, root, launchers_root,
                     dist_root, icon_file,
                     resource_path,
                     version_name
                     ):

        # ===================================================================
        # copy files
        # ===================================================================

#        icon = os.path.join(root, 'resources', 'apps', icon_file)
#        print icon
#        if os.path.isfile(icon):
#            shutil.copyfile(icon, os.path.join(dist_root,
#                            'Resources', icon_file))
#        else:
#            print '----- No Icon File for {} -----'.format(self.prefix)

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

#        # move splash and about into place
#        if version_name:
#            for ni, nd in (('splash', 'splashes'), ('about', 'abouts'),
#                           ):
#                sname = '{}_{}.png'.format(ni, version_name)
#                shutil.copyfile(os.path.join(root, 'resources', nd, sname),
#                                resource_path(sname)
#                            )
#
#        for bi in ('blue', 'red', 'green', 'yellow', 'orange', 'gray'):
#            name = '{}_ball.png'.format(bi)
# #                print os.path.join(root, 'resources','balls',name)
#            shutil.copyfile(os.path.join(root, 'resources', 'balls', name),
#                            resource_path(name)
#                            )

# ============= EOF =====================================

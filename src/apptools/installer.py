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
import os
import sys
import shutil
import plistlib
#============= local library imports  ==========================
class Installer(object):
    prefix = None
    name = None
    icon_name = None
    def __init__(self, prefix, name, icon_name=None):
        self.prefix = prefix
        self.name = name
        self.icon_name = icon_name

    def install(self, root):
        if sys.platform == 'darwin':
            from BuildApplet import buildapplet
            print 'Building {}.py'.format(self.name)

            sys.argv[1:] = [os.path.join(root, '{}.py'.format(self.name))]
            buildapplet()

            #===================================================================
            # run build applet
            #===================================================================
            dist_root = os.path.join(root, '{}.app/Contents'.format(self.prefix))


            if self.icon_name is not None:
                icon_file = '{}.icns'.format(self.icon_name)

            else:
                icon_file = '{}_icon.icns'.format(self.prefix)


            #===================================================================
            # copy files
            #===================================================================

            icon = os.path.join(root, 'resources', icon_file)
            if os.path.isfile(icon):
                shutil.copyfile(icon,
                            os.path.join(dist_root, 'Resources', icon_file))
            else:
                print '----- No Icon File for {} -----'.format(self.prefix)

            #===================================================================
            # #edit the plist
            #===================================================================

            info_plist = os.path.join(dist_root, 'Info.plist')
            tree = plistlib.readPlist(info_plist)


            tree['CFBundleIconFile'] = icon_file
            tree['CFBundleName'] = self.name

            plistlib.writePlist(tree, info_plist)
            print 'Created {}'.format(os.path.join(root, '{}.py'.format(self.name)))
#============= EOF =====================================

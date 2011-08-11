import os
import shutil
import sys
import plistlib

root = os.getcwd()

class Installer(object):
    prefix = None
    name = None
    icon_name = None
    def __init__(self, prefix, name, icon_name = None):
        self.prefix = prefix
        self.name = name
        self.icon_name = icon_name

    def install(self):
        if sys.platform == 'darwin':
            from BuildApplet import buildapplet

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

            #===================================================================
            # change app prefix
            #===================================================================
#            p1 = os.path.join(root, '{}.app'.format(self.prefix))
#            p2 = os.path.join(root, '{}.app'.format(self.name))
#
#            if os.path.exists(p2):
#                shutil.rmtree(p2)
#            os.rename(p1, p2)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description = 'Create a new Launchable Application')
    parser.add_argument('prefix',
                        #metavar = 'prefix', 
                        type = str, nargs = '?',
                        help = 'Prefix name. used to identify the icon file and the launch script eg. pychron'
                        )
    parser.add_argument('name',
                        #metavar = 'name', 
                        type = str, nargs = '?',
                        help = 'Name of the application bundle eg. Pychron')

    parser.add_argument('--icon', type = str, nargs = '?',
                        help = 'icon file name')
    args = parser.parse_args()

    i = Installer(args.prefix, args.name, args.icon)
    i.install()

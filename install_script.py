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
#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
#make this file exectutable

#============= standard library imports ========================
import os
import shutil
import sys
import plistlib
import argparse
import subprocess
#============= local library imports  ==========================



class Installer(object):
    prefix = None
    name = None
    icon_name = None
    def __init__(self, prefix, name, icon_name = None):
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
            #===================================================================
            # change app prefix
            #===================================================================
#            p1 = os.path.join(root, '{}.app'.format(self.prefix))
#            p2 = os.path.join(root, '{}.app'.format(self.name))
#
#            if os.path.exists(p2):
#                shutil.rmtree(p2)
#            os.rename(p1, p2)


def install_pychron_suite():
    

    parser = argparse.ArgumentParser(description = 'Install Pychron')
    
    parser.add_argument('-d', '--data', action='store_true',
                        help = 'overwrite the current pychron_data directory')
    parser.add_argument('-f', '--force-data', action='store_true',
                        help = 'dont ask to overwrite the data dir, just do it')
    parser.add_argument('-a', '--apps-only', action='store_true',
                        help = 'only create the app bundles')
    
    parser.add_argument('-s', '--source', action='store_true',
                        help = 'download source')
    
    parser.add_argument('-r', '--root', type=str,nargs='?',
                        help = 'set the root directory')
    
    parser.add_argument('-n', '--name',type=str, nargs='?',
                        default='pychron',
                        help = 'name of the cloned source directory')

    
    args = parser.parse_args()

    if args.root[0]:
        root=args.root[0]
    else:
        root = os.getcwd()

    
    print 'Using {} as working dir'.format(root)
    
    if args.source:
        
        #ask user for user name
        user=raw_input('username: ')
        if user is None:
            user='jirhiker'
            
        repo='code.google.com/p/arlab'
        print 'cloning source for user {} from repo {}'.format(user, repo)
        repo='https://{}@{}'.format(user,repo)
    
        name=args.name        
        base=name
        i=0
        while os.path.exists(os.path.join(root,name)):
            name='{}_{:03n}'.format(base,i)
            i+=1
            
            
        #should check to make sure mercurial is installed
        #if not issue warning, install instructions and quit
        
            cmd='hg clone {} {}'.format(repo, name)
            try:
                subprocess.check_call([cmd.split(' ')], stdout=subprocess.PIPE)
            except subprocess.CalledProcessError,e:
                print e
                print 'Mercurial version control is not installed'
                print 'See http://mercurial.selenic.com/'
                return 
        
    
    i=Installer('pychron_beta', 'pychron_beta')
    i.install(os.path.join(root,name))
    
    i.prefix='remote_hardware_server'
    i.name='remote_hardware_server'
    i.install(os.path.join(root,name))
    

    #move data into place
    if args.apps_only:
        return 
    
    data=os.path.join(os.getcwd(),'data')
    home=os.path.expanduser('~')
    dst=os.path.join(home, 'pychron_data_beta')

    try:
        shutil.copytree(data, dst)
        print 'copying {} -> {}'.format(data,dst)
    except OSError:
        if args.data:
            rin='y'
            if not args.force_data:
                rin=raw_input('overwrite exisiting data y/n [y] >> ').strip().lower()
                
            if len(rin)==0 or rin in ['y','yes']:
                print 'copying {} -> {}'.format(data,dst)   
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(data, dst)
        

def cli_install():
    
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
    
if __name__ == '__main__':
    
#    cli_install()
    
    install_pychron_suite()
#============= EOF =====================================

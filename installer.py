#===============================================================================
# Copyright 2012 Jake Ross
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

#============= enthought library imports =======================
#============= standard library imports ========================
import os
import subprocess
import shutil
#============= local library imports  ==========================

'''
    this script executes pychron installation 
    
    1. install EPD
    2. install XCode
    3. install MySQL
    
    4. relink gcc
    
    5. install pandas 0.8
    6. install statsmodels 0.5
    7. install mysql-python
    
    8. move support files into place
'''

def main():
    if install_epd():
        return

    print
    if install_xcode():
        return

    print
    if install_mysql():
        return

    if change_gcc_version('4.0'):
        return

    root = os.getcwd()

    print
    if install_python_package(root, 'pandas', '0.8.1'):
        return

    print
    if install_python_package(root, 'statsmodels', '0.4.3'):
        return

    print
    if install_python_package(root, 'MySQL-python', '1.2.4b4'):
        return

    if move_support_files(root):
        return

def move_support_files(root, version='processing'):
    home = os.path.expanduser('~')

    name = 'Pychrondata_{}'.format(version)
    dst = os.path.join(home, name)
    src = os.path.join(root, name)
    shutil.copytree(src, dst)

def install_python_package(root, name, version):
    os.chdir(os.path.join(root, '{}-{}'.format(name, version)))
    subprocess.call(['python', 'hello.py', 'install'])
#    subprocess.call(['python', 'setup.py', 'install'])


def change_gcc_version(version):
    '''
        change gcc version to 4.0
    '''
    gcc = '/usr/bin/gcc'
    print 'changing {} symlink to use gcc version {}'.format(gcc, version)

    os.remove(gcc)
    gcc_v = '/usr/bin/gcc-{}'.format(version)
    os.symlink(gcc_v, gcc)

def install_epd():
    print 'open epd installer'

    if user_cancel():
        return True

def user_cancel():
    '''
        returns True if user doesnt enter y
    '''
    _input = raw_input('hit "enter" to continue. "n" to cancel>> ')

    if _input.strip() == 'n':
        return True

def install_xcode():
    print 'open xcode installer'
    if user_cancel():
        return True

def install_mysql():
    print 'open mysql installer'
    if user_cancel():
        return True



if __name__ == '__main__':
    main()

#============= EOF =============================================

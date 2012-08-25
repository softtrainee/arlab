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
import shutil
import argparse
import subprocess

from installer import Installer


def install_pychron_suite():

    parser = argparse.ArgumentParser(description='Install Pychron')

    parser.add_argument('-d', '--data', action='store_true',
                        help='overwrite the current pychron_data directory'
                        )
    parser.add_argument('-f', '--force-data', action='store_true',
                        help='dont ask to overwrite the data dir, just do it'
                        )
    parser.add_argument('-a', '--apps-only', action='store_true',
                        help='only create the app bundles')

    parser.add_argument('-s', '--source', action='store_true',
                        help='download source')

    parser.add_argument('-v', '--version',
                        nargs=1,
                        type=str,
                        default=[''],
                        help='set the version number e.g 1.0')

    parser.add_argument(
        '-r',
        '--root',
        type=str,
        nargs=1,
        default='.',
        help='set the root directory',
        )

    parser.add_argument(
        'name',
        metavar='N',
        type=str,
        nargs=1,
        default='pychron',
        help='name of the cloned source directory',
        )

    args = parser.parse_args()

    # if args.root[0]:

    root = args.root[0]
    name = args.name[0]

    version = args.version[0]

    src_dir = os.path.join(root, name)

    print 'Using {} as working dir'.format(root)
    if args.source:

        # ask user for user name

        user = raw_input('username [jirhiker]: ')
        if not user:
            user = 'jirhiker'

        repo = 'code.google.com/p/arlab'
        print 'cloning source for user {} from repo {}'.format(user,
                repo)
        repo = 'https://{}@{}'.format(user, repo)

        base = name
        i = 0
        while os.path.exists(os.path.join(root, name)):
            name = '{}_{:03n}'.format(base, i)
            i += 1

        # should check to make sure mercurial is installed
        # if not issue warning, install instructions and quit

        src_dir = os.path.join(root, name)
        cmd = 'hg clone {} {}'.format(repo, src_dir)
        try:
            subprocess.check_call(cmd.split(' '),
                                  stdout=subprocess.PIPE)
        except OSError, e:
            print 'Mercurial version control is not installed'
            print 'See http://mercurial.selenic.com/'
            return
        except subprocess.CalledProcessError, e:

            print e
            print 'Problem with mercurial'
            print 'See http://mercurial.selenic.com/'
            return

    #build pychron
    i = Installer('pychron', 'pychron')
    i.version = version
#    i.install(src_dir)

    #build remote hardware server
    i.prefix = 'remote_hardware_server'
    i.name = 'remote_hardware_server'
    default_pkgs = ['rpc', 'helpers', 'led']
    i.include_pkgs = ['remote_hardware', 'messaging'] + default_pkgs

    default_mods = ['paths', 'loggable', 'config_loadable',
                    'viewable', 'managers/displays/rich_text_display',
                    'managers/manager',
                    ]
    i.include_mods = [
                      'managers/remote_hardware_server_manager',
                      ] + default_mods
#    i.install(src_dir)

#    build bakeout
    i.prefix = 'bakeout'
    i.name = 'bakeout'
    i.include_mods = ['hardware/bakeout_controller',
                      'hardware/watlow_ezzone',
                      'database/orms/bakeout_orm',
                      'database/adapters/bakeout_adapter',
                      'database/selectors/bakeout_selector',
                      'database/data_warehouse',
                      'managers/script_manager',
                      'has_communicator'
                      ] + default_mods
    i.include_pkgs = ['bakeout',
                      'hardware/core',
                      'hardware/gauges',
                      'scripts',
                      'managers/data_managers',
                      'graph',
                      'data_processing/time_series',
                      'database/core'
                      ] + default_pkgs

    i.install(src_dir)

    # move data into place

    if not args.data:
        return

    data = os.path.join(src_dir, 'data')
    home = os.path.expanduser('~')
    dst = os.path.join(home, 'pychron_data_beta')

    try:
        shutil.copytree(data, dst)
        print 'copying {} -> {}'.format(data, dst)
    except OSError:
        rin = 'y'
        if not args.force_data:
            rin = \
                raw_input('overwrite exisiting data at {} y/n [y] >> '.format(dst)).strip().lower()

        if len(rin) == 0 or rin in ['y', 'yes']:
            print 'copying {} -> {}'.format(data, dst)
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(data, dst)


if __name__ == '__main__':

    install_pychron_suite()

# ============= EOF =====================================

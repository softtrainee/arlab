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
from src.helpers.logger_setup import setup
'''
    1. find all files older than Y
        - move to archive
    2. remove archive directories older than X
'''
from traits.api import Int
import os
import shutil
from datetime import datetime, timedelta

from src.loggable import Loggable

MONTH_NAMES = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', \
               'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


class VideoDirectoryMaintainceScript(Loggable):
    archive_days = Int(3)

    def clean(self, root):
        archive_date = datetime.today() - timedelta(days=self.archive_days)
        self.info('Videos older than {} will be archived'.format(archive_date))
        for p in self._get_files(root):
            rp = os.path.join(root, p)
            result = os.stat(rp)
            mt = result.st_mtime
            creation_date = datetime.fromtimestamp(mt)
            if creation_date < archive_date:
                self._archive(root, p)

        self.info('Archives older than 3 months will be deleted')
        self._clean_archive(root)

    def _get_files(self, root):
        return [p for p in os.listdir(root) if not p.startswith('.')]

    def _clean_archive(self, root):
        arch = os.path.join(root, 'archive')
        rdate = datetime.today() - timedelta(days=3 * 30)

        if os.path.isdir(arch):
            for year_dir in self._get_files(arch):
                yarch = os.path.join(arch, year_dir)
                for month_dir in self._get_files(yarch):
                    adate = datetime(year=int(year_dir),
                                    month=MONTH_NAMES.index(month_dir) + 1,
                                     day=1
                                     )
                    if rdate > adate:
                        self.info('Deleting archive {}/{}'.format(year_dir,
                                                                month_dir))
                        shutil.rmtree(os.path.join(arch, year_dir, month_dir))

                #remove empty year archives
                if not os.listdir(yarch):
                    self.info('Deleting empty year archive {}'.format(year_dir))
                    os.rmdir(yarch)

    def _archive(self, root, p):
        #create an archive directory
        today = datetime.today()
        month = MONTH_NAMES[today.month - 1]
        year = today.year
        arch = os.path.join(root, 'archive')
        if not os.path.isdir(arch):
            os.mkdir(arch)

        yarch = os.path.join(arch, str(year))
        if not os.path.isdir(yarch):
            os.mkdir(yarch)

        march = os.path.join(yarch, month)
        if not os.path.isdir(march):
            os.mkdir(march)

        src = os.path.join(root, p)
        dst = os.path.join(march, p)
        self.info('Archiving {:30s} to ./archive/{}/{}'.format(p, year, month))
        shutil.move(src, dst)

if __name__ == '__main__':
    setup('video_main')
    c = VideoDirectoryMaintainceScript(trim_days=30)
    root = '/Users/ross/Desktop/test'
    c.clean(root)



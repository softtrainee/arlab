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
from multiprocessing.process import Process
'''
    1. find all files older than Y
        - move to archive
    2. remove archive directories older than X
'''
from traits.api import Range, Int, Bool, Str
import os
import shutil
from datetime import datetime, timedelta


from src.loggable import Loggable

MONTH_NAMES = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', \
               'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


class Archiver(Loggable):
    archive_days = Range(1, 31)
    archive_months = Range(1, 12, 3)
    clean_archives = Bool(True)
    root = Str

    def clean(self, spawn_process=True):
        if spawn_process:
            p = Process(target=self._clean)
            p.start()
        else:
            self._clean()

    def _clean(self):
        root = self.root
        if not root:
            return

        archive_date = datetime.today() - timedelta(days=self.archive_days)
        self.info('Files older than {} will be archived'.format(archive_date))
        for p in self._get_files(root):
#            print p
            rp = os.path.join(root, p)
            result = os.stat(rp)
            mt = result.st_mtime
            creation_date = datetime.fromtimestamp(mt)
            if creation_date < archive_date:
                self._archive(root, p)

        if self.clean_archives:
            self._clean_archive(root)

    def _get_files(self, root):
        return [p for p in os.listdir(root)
                if not p.startswith('.') and os.path.isfile(os.path.join(root, p))]

    def _clean_archive(self, root):
        self.info('Archives older than {} months will be deleted'.format(self.archive_months))
        arch = os.path.join(root, 'archive')
        rdate = datetime.today() - timedelta(days=self.archive_months * 30)

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
        try:
            shutil.move(src, dst)
        except Exception, e:
            self.warning('Archiving failed')
            self.warning(e)

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('video_main')
    c = Archiver(trim_days=30)
    root = '/Users/ross/Desktop/test'
    c.clean(root)



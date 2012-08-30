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
from traits.api import HasTraits, Button, Instance, Str, Any, Property, List
from traitsui.api import View, Item, TabularEditor
#============= standard library imports ========================
import sqlite3
import os
from src.managers.manager import Manager
from traitsui.tabular_adapter import TabularAdapter
import time
import datetime
#============= local library imports  ==========================
os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = '/usr/local/git/bin/git'
from git import Repo

class DBSync(object):
    @classmethod
    def dump(cls, dbname, out):
        con = sqlite3.connect(dbname)
        with open(out, 'w') as f:
            for line in con.iterdump():
                f.write('{}\n'.format(line))

    @classmethod
    def load(cls, dbname, in_):
        with open(in_, 'r') as f:
            if os.path.isfile(dbname):
                os.remove(dbname)
            cls.execute_sqlscript(dbname, f.read())
#            conn = sqlite3.connect(dbname)
#
#            with conn:
#                cur = conn.cursor()
#                cur.executescript(f.read())

    @classmethod
    def loadstream(cls, dbname, in_):
        conn = sqlite3.connect(dbname)
        with conn:
            cur = conn.cursor()
            cur.executescript(in_.getvalue())

    @classmethod
    def execute_sqlscript(cls, dbname, sql):
        conn = sqlite3.connect(dbname)
        with conn:
            cur = conn.cursor()
            cur.executescript(sql)

    @classmethod
    def execute_sql(cls, dbname, sql):
        conn = sqlite3.connect(dbname)
        with conn:
            cur = conn.cursor()
            try:
                cur.execute(sql)
            except sqlite3.OperationalError, e:
                print e




class DBSyncManager(Manager):
    remote = Repository
    local = Instance(Repository)
    new_repository_button = Button('New Repo')
    def _new_repository_button_fired(self):
        path = self.save_file_dialog()
        if path:
            self.new_repository(path)

    def new_repository(self, name):

        root = '/Users/ross/Sandbox/datasync'
        name = os.path.join(root, name)
        repo = Repository(name)
        if not repo.git_repo:
            master_path = '/Users/ross/Sandbox/datasync/master.git'
            repo.clone(master_path)

            self.info('cloned {} to {}'.format(master_path, repo.root))
        else:
            self.info('repository already exists {}'.format(name))
        self.local = repo

    def traits_view(self):
        v = View(
                 Item('local', style='custom', show_label=False),
                 Item('new_repository_button', show_label=False),
                 resizable=True,
                 width=500,
                 )
        return v


def version_control_file(repo, fname, msg, pull=True):
    if pull:
        repo.remotes.origin.pull()
    repo.index.add([fname])
    repo.index.commit(msg)
    repo.remotes.origin.push('master')


def make_file(root, name, txt):
    with open(os.path.join(root, name), 'w') as f:
        f.write(txt)


def main():
    from src.helpers.logger_setup import logging_setup
    logging_setup('sync')
    setup = False
    #do setup for testing
    if setup:
        rootpath = '/Users/ross/Sandbox/datasync'

        #create shared repository
        name = 'master.git'
        p = os.path.join(rootpath, name)
        master = Repo.init(p, bare=True)

        #create the default machine repo
        machine = master.clone(os.path.join(rootpath, 'machine'))
        fname = 'analysis.txt'
        make_file(machine.working_dir, fname, '1,2,3,4')
        version_control_file(machine, fname, 'added {}'.format(fname), pull=False)

        #push changes to shared
        machine.remotes.origin.push('master')

    dbsync = DBSyncManager()
    dbsync.new_repository('working_a')
    dbsync.configure_traits()

def time_dump():
#    os.remove('/Users/ross/Sandbox/datasync/timetest.db')

    DBSync.dump('/Users/ross/Sandbox/datasync/timetest.db',
                '/Users/ross/Sandbox/datasync/timetest.dump'
                )
def time_load(dbname='/Users/ross/Sandbox/datasync/timetestnew.db',
              in_='/Users/ross/Sandbox/datasync/timetest.dump'
              ):
    DBSync.load(dbname,
                in_
                )

def baseline():
    os.remove('/Users/ross/Sandbox/datasync/timetest.db')


def main3():


if __name__ == '__main__':
#    main()
#    main2()
    main3()
#    fname = 'analysis001.txt'
#    make_file(machine.working_dir, fname, '5,4,3,2')
#    version_control_file(machine, fname, 'added {}'.format(fname))
#
#    #push changes to shared
#    machine.remotes.origin.push('master')
#
#
#    #scenario 1. 
#    # synced.
#    dbsync.pull_changes()
#    #. local makes changes
#    local = dbsync.local
#    fname = 'analysis_local.txt'
#    make_file(local.root, fname, '1adsf,2,3,4')
#
#    # machine makes changes while local was making changes
#    # therefore local is out of date
#    fname = 'analysis_machine.txt'
#    make_file(machine.working_dir, fname, '1adsf,2,3,4')
#    version_control_file(machine, fname, 'added {}'.format(fname))
#
#    #trying to commit local changes should fail
#    fname = 'analysis_local.txt'
#    repo = local.git_repo
##    msg = 'added {}'.format(fname)
##    repo.index.add([fname])
##    repo.index.commit(msg)
##    repo.remotes.origin.push('master')
#    version_control_file(repo, fname, 'added {}'.format(fname))
#
#    machine.remotes.origin.pull()

#    dbsync.configure_traits()


#
#def main2():
#    from timeit import Timer
#
#
#
#    dbname = '/Users/ross/Sandbox/datasync/timetest.db'
##    try:
##    bt = Timer('baseline()', 'from __main__ import baseline')
##    bs = bt.timeit(1)
#    bs = 0
#
#    t = Timer('time_dump()', 'from __main__ import time_dump')
#    tl = Timer('time_load()', 'from __main__ import time_load')
#    ts = []
#    tls = []
#    xs = []
#    sqltable = '''
#CREATE TABLE "ProjectTable" (
#    id INTEGER NOT NULL, 
#    name VARCHAR(40), 
#    PRIMARY KEY (id)
#);
#
#'''
##    DBSync.execute_sqlscript(dbname, sql)
##    execute_sqlscript(dbname, sql)
#    pc = 0
#
#    st = time.time()
#    from jinja2 import Template
#
#    for n in range(12):
#
#        st_strtime = time.time()
#        x = 2 ** n
#
#
#        sqltemp = '{% for i in x %} INSERT INTO "ProjectTable" VALUES({{pc+i}},"Test");\n {% endfor %}'
#        sql = Template(sqltemp).render(x=xrange(x), pc=pc)
#        pc += x
##        print 'sqlbuild time ', time.time() - st_strtime
#
#        stex = time.time()
#        if os.path.isfile(dbname):
#            os.remove(dbname)
#        DBSync.execute_sqlscript(dbname, sqltable + sql)
#
##        in_ = '/Users/ross/Sandbox/datasync/temp.txt'
##        with open(in_, 'w') as f:
##            f.write(sqltable + sql)
#
##        time_load(dbname, in_)
#        tt = t.timeit(1)
#        print 'sqlex time', time.time() - stex, tt
###        print sql
#        ts.append(tt - bs)
#        xs.append(pc)
#
#        ttt = tl.timeit(1)
#        tls.append(ttt - bs)
#        print 'time {} {}'.format(x, time.time() - st_strtime), ttt
#
#    print 'analysis time for {} rows= {}'.format(pc, time.time() - st)
#    from pylab import plot, show
#    plot(xs, ts, color='black')
#    plot(xs, tls, color='red')
##
#    show()
##================
#'''
#non jinj2 results
#time 1 0.00475192070007
#time 2 0.00857901573181
#time 4 0.0148499011993
#time 8 0.0276160240173
#time 16 0.0498888492584
#time 32 0.0920119285583
#time 64 0.705885887146
#time 128 1.99481487274
#time 256 4.59080195427
#time 512 8.94680094719
#time 1024 21.1523230076
#time 2048 43.4470188618
#analysis time for 4095 rows=
#'''
#============= EOF =============================================

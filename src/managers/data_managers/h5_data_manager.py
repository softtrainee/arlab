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
#============= enthought library imports =======================

#============= standard library imports ========================
from tables import openFile, NodeError
from numpy import array
#============= local library imports  ==========================
from data_manager import DataManager
from table_descriptions import table_description_factory


class H5DataManager(DataManager):
    '''
    '''
    _extension = 'h5'

    def set_group_attribute(self, group, key, value):
        f = self._frame

        if isinstance(group, str):
            group = getattr(f, group)

        setattr(group._v_attrs, key, value)
#        print group._v_attrs[]
#        group.flush()
#    def set_table_attribute(self, key, value, table):
#        '''
#            
#        '''
#        _df, table = self._get_parent(table)
#        setattr(table.attrs, key, value)
#        table.flush()

    def record(self, values, table):
        '''

        '''
        _df, ptable = self._get_parent(table)
        nr = ptable.row
        for key in values:
            nr.__setitem__(key, values[key])

        nr.append()
        ptable.flush()

    def new_frame(self, *args, **kw):
        '''
            
        '''
        p = self._new_frame_path(*args, **kw)
        self._frame = openFile(p, mode='w')
        return self._frame

    def new_group(self, group_name, parent='root', description=''):
        if parent == 'root':
            parent = self._frame
            parent_group = self._frame.root

        grp = parent.createGroup(parent_group, group_name, description)
        return grp

    def new_table(self, group, table_name, table_style='TimeSeries'):
        table = self._frame.createTable(group, table_name,
                                        table_description_factory(table_style))
        return table

    def get_table(self, name, group):
        f = self._frame
        try:
            grp = getattr(f.root, group)
            return getattr(grp, name)
        except AttributeError:
            pass

    def get_groups(self):
        return [g for g in self._frame.walkGroups() if g != self._frame.root]

    def get_tables(self):
        f = self._frame

        for n in f.walkNodes('/', 'Table'):
            print n

        return

    def open_data(self, path):
        try:
            self._frame = openFile(path, 'r')
            return True
        except ValueError:
            return False

    def close(self):
        try:
            self.info('saving data to file')
            self._frame.close()
        except Exception, e:
            print e

    def kill(self):
        self.close()
#        for table in f.walkNodes('/', 'Table'):

#    def add_table(self, table, table_style='Timestamp', parent='root'):
#        '''
#        '''
#        df, pgrp = self._get_parent(parent)
#
#        alpha = [chr(i) for i in range(65, 91)]
#        s = array([[''.join((b, a)) for a in alpha] for b in alpha]).ravel()
#
#        add = True
#        cnt = 0
#        base_table = table
#        while add:
#            try:
#                df.createTable(pgrp, table, table_description_factory(table_style))
#            except NodeError:
#
#                table = '%s%s' % (base_table, s[cnt])
#                cnt += 1
#                add = True
#            finally:
#                add = False
#        return table
#
#    def add_group(self, group, parent='root'):
#        '''
#
#
#        '''
#
#        df, pgrp = self._get_parent(parent)
#        df.createGroup(pgrp, group)
#
#        self._frame = df
#
#    def _get_parent(self, parent, df=None):
#        '''
#
#
#        '''
#        if not df:
#            df = self._frame
#
#        p = parent.split('.')
#        pgrp = None
#        prev_obj = None
#        for i, pi in enumerate(p):
#            if i == 0:
#                obj = df
#            else:
#                obj = prev_obj
#
#            pgrp = getattr(obj, pi)
#            prev_obj = pgrp
#
#        return df, pgrp
#
#    def _get_tables(self, df=None, path=None):
#        '''
#        '''
#        names = []
#        tabs = {}
#        #tabs=[]
#        if path is not None:
#            df = openFile(path, mode='r')
#
#        for group in df.walkGroups('/'):
#
##            grpname = self._get_group_name(group)
#            for table in df.listNodes(group, classname='Table'):
#                #name = '%s.%s' % (grpname, table.name)
#                #tabs.append((grpname, table.name))
#                tabs[table.name] = table
#                names.append(table.name)
#
#        return names, tabs
#
#    def _get_groups(self, df):
#        '''
#
#        '''
#        grps = df.root._v_groups.keys()
#        self.selected_group = grps[0]
#        return grps
#
#    def _get_group_name(self, group):
#        '''
#        '''
#        s = group.__str__()
#        p, _c, _d = s.split(' ')
#        return p.split('/')[-1:][0]
if __name__ == '__main__':
    d = H5DataManager()
    print d
#============= EOF ====================================
#    def add_note(self, note = None):
#        df = self.data_frames[len(self.data_frames) - 1]
#        self._available_tables = self._get_tables(df)
#        info = self.edit_traits(view = 'note_view')
#        if info.result:
#            table = self._get_tables(df)[self.selected_table]
#            setattr(table.attrs, 'note', self.note)

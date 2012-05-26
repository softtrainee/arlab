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

#============= enthought library imports =======================
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.adapters.database_adapter import DatabaseAdapter
from src.database.orms.video_orm import VideoTable, VideoPathTable
from src.database.selectors.video_selector import VideoSelector
from src.helpers.paths import co2laser_db


class VideoAdapter(DatabaseAdapter):
    test_func = None
    selector_klass = VideoSelector

#==============================================================================
#    getters
#==============================================================================

    def get_video_records(self, join_table=None, filter_str=None):
        try:
            if isinstance(join_table, str):
                join_table = globals()[join_table]

            q = self._get_query(VideoTable, join_table=join_table,
                                 filter_str=filter_str)
            return q.all()
        except Exception, e:
            print e

#=============================================================================
#   adder
#=============================================================================
    def add_video_record(self, commit=False, **kw):
        b = self._add_timestamped_item(VideoTable, commit, **kw)
        return b

    def add_video_path(self, video, path, commit=False, **kw):
        kw = self._get_path_keywords(path, kw)
        p = VideoPathTable(**kw)
        video.path = p
        if commit:
            self.commit()
        return p


if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('vid')
    db = VideoAdapter(dbname=co2laser_db, kind='sqlite')
    db.connect()

    dbs = VideoSelector(_db=db)

#    dbs.criteria = 'vm_recordingii'
#    dbs.parameter = 'VideoTable.rid'
#    dbs.comparator = 'like'
#    dbs._execute_query()
    dbs.load_recent()
#    si = dbs.results[0]
#    from pyface.timer.do_later import do_later
#    from pyface.timer.do_later import do_after
#    do_after(10, si.edit_traits)
    dbs.configure_traits()
#    print db.get_bakeouts(join_table='ControllerTable',
#                    filter_str='ControllerTable.script="---"'
#                    )
#============= EOF =============================================


#============= enthought library imports =======================
from src.managers.data_managers.db_data_manager import DBDataManager
from src.database.pychron_database_adapter import PychronDatabaseAdapter
from src.helpers.filetools import parse_file

#============= standard library imports ========================

#============= local library imports  ==========================
class PychronDBDataManager(DBDataManager):
    def _database_default(self):
        return PychronDatabaseAdapter()

    def _import_(self):
        '''
            import files first 2 lines should be the table name and a header row
        '''
        p = '/Users/Ross/Desktop/detector_table.txt'
        self.info('import file {}'.format(p))

        contents = parse_file(p)
        _table = contents.pop(0)
        _header = contents.pop(0).split(',')

        self.database.connect()

#        func = getattr(self, '_{}_importer'.format(table.lower()))
#        func(header, contents)
#
#        self.database.flush()
        db = self.database
#        sam = db.get_sample(dict(name = 'bar'))
#        db.add_analysis(sample = sam)
#
#        db.add_analysis(sample = 'cs-40')

#        spec = db.get_spectrometer('obama')
#
#        db.add_signal(analysis = dict(identifier = 1000003),
#                      detector = spec.detectors[2]
#
#                      )


        s = db.get_signal(dict(analysis_id = 1,
                               detector_id = 25
                               ))
        import struct
        width = 8
        blob = s.times

        ts = [struct.unpack('>d', blob[i:i + width])[0] for i in range(0, len(blob), width)]
        blob = s.intensities
        vs = [struct.unpack('>d', blob[i:i + width])[0] for i in range(0, len(blob), width)]

        for t, v in zip(ts, vs):
            print t, v
    def _detector_importer(self, header, detectors):
        db = self.database

        for d in detectors:
            kw = dict()
            attrs = d.split(',')
            for i, col in enumerate(header):
                kw[col] = attrs[i]

            db.add_detector(**kw)

    def commit(self):
        sess = self.database.get_session()
        sess.commit()

    def __getattr__(self, attr):

        try:
            return getattr(self.database, attr)
        except AttributeError:
            pass
if __name__ == '__main__':
    d = PychronDBDataManager()
    d.configure_traits()
#============= EOF ====================================

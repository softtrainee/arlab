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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
from src.loggable import Loggable
from src.experiment.mass_spec_database_importer import MassSpecDatabaseImporter
import os
import struct
import base64
#============= standard library imports ========================
#============= local library imports  ==========================

class MassSpecExporter(Loggable):
    def export(self, spec, destination=None):
        '''
            spec: ExportSpec 
            destination: either path or dict. 
                if path export to xml/csv 
                if dict, required keys are (username, password, host, name)
        '''
        if isinstance(destination, dict):
            self.export_import(spec, destination)
        else:
            self.export_xml(spec, destination)

    def export_import(self, spec, destination):
        '''
            import spec into dest 
            use massspecdatabase_importer for import
        '''
        importer = MassSpecDatabaseImporter()
        db = importer.db
        for k in ('username', 'password', 'host', 'name'):
            setattr(db, k, destination[k])

        db.connect()
        # add analysis
        importer.add_analysis(spec)

    def _make_timeblob(self, t, v):
        blob = ''
        for ti, vi in zip(t, v):
            blob += struct.pack('>ff', float(vi), float(ti))
        return blob

    def export_xml(self, spec, path):
        '''
            
        '''
        from src.helpers.parsers.xml_parser import XMLParser
        xmlp = XMLParser()
        an = xmlp.add('analysis', '', None)
        meta = xmlp.add('metadata', '', an)
        xmlp.add('RID', spec.rid, meta)
        xmlp.add('Aliquot', spec.aliquot, meta)
        xmlp.add('Step', spec.step, meta)

        data = xmlp.add('data', '', None)
        sig = xmlp.add('signals', '', data)
        base = xmlp.add('baselines', '', data)
        blank = xmlp.add('blanks', '', data)

        for ((det, isok), si, bi, ublank, signal, baseline, sfit, bfit) in spec.iter():
            iso = xmlp.add(isok, '', sig)

            xmlp.add('detector', det, iso)
            xmlp.add('fit', sfit, iso)
            xmlp.add('value', signal.nominal_value, iso)
            xmlp.add('error', signal.std_dev(), iso)

            t, v = zip(*si)
            xmlp.add('blob',
                     base64.b64encode(self._make_timeblob(t, v)), iso,
                     dt="binary.base64"
                     )

            iso = xmlp.add(isok, '', base)
            xmlp.add('detector', det, iso)
            xmlp.add('fit', bfit, iso)
            xmlp.add('value', baseline.nominal_value, iso)
            xmlp.add('error', baseline.std_dev(), iso)

            t, v = zip(*bi)
            xmlp.add('blob',
                     base64.b64encode(self._make_timeblob(t, v)), iso,
                     dt="binary.base64"
                     )

            iso = xmlp.add(isok, '', blank)
            xmlp.add('detector', det, iso)
            xmlp.add('value', ublank.nominal_value, iso)
            xmlp.add('error', ublank.std_dev(), iso)

        if os.path.isdir(os.path.dirname(path)):
            xmlp.save(path)


class Exporter(Loggable):
    def export(self, kind='MassSpec'):
        if kind == 'MassSpec':
            klass = MassSpecExporter
        exp = klass()
        exp.export()
#============= EOF =============================================

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
#============= standard library imports ========================
import cPickle as pickle
#============= local library imports  ==========================

def try_key_error(func):
    def decorator(*args, **kw):
        try:
            func(*args, **kw)
        except KeyError, e:
            print e, 'keyerre'

    return decorator
class FigureStore(object):
    path = None

    _f_analyses = None
    _f_statuses = None
    figure = None

    def __init__(self, path, figure):
        self.path = path
        self.figure = figure

    def dump(self):
        self._build()
        with open(self.path, 'wb') as fp:

            ksvs = [(attr, getattr(self, attr))
                                for attr in dir(self) if attr.startswith('_f_')]
            params = dict(ksvs)
            pickle.dump(params, fp)

    def load(self):
        with open(self.path, 'rb') as fp:
            try:
                params = pickle.load(fp)
                self._set_series(params)
                self._set_graph_selector(params)
                self._set_analyses(params)
                self._set_ideogram_selected(params)
            except pickle.PickleError:
                pass

    def _build(self):
        f = self.figure
        if f.analyses:
            self._f_analyses, self._f_groupids = zip(*[(ai.uuid, ai.group_id)
                                                   for ai in f.analyses])

            self._f_graph_x_limits = [0, 1]
            self._f_graph_y_limits = [0, 1]
            self._f_graph_selector = f.graph_selector
            self._f_series_configs = f.series_configs
            if f.ideogram:
                sel = f.ideogram.graph.plots[1].plots['plot0'][0].index.metadata.get('selections')
                self._f_ideogram_selected = sel

    @try_key_error
    def _set_series(self, params):
        ser = params['_f_series_configs']
        self.figure.series_configs = ser

    @try_key_error
    def _set_analyses(self, params):
        names = params['_f_analyses']
        groupids = params['_f_groupids']
        self.figure.load_analyses(names, groupids=groupids)

    @try_key_error
    def _set_graph_selector(self, params):
        self.figure.graph_selector = params['_f_graph_selector']

    @try_key_error
    def _set_ideogram_selected(self, params):
        ideo = self.figure.ideogram
        if ideo:
            index = ideo.graph.plots[1].plots['plot0'][0].index
            index.metadata['selections'] = params['_f_ideogram_selected']

if __name__ == '__main__':
    class b:
        @property
        def uuid(self):
            return 45
    class a:
        analyses = [b(), b(), b()]

    fs = FigureStore('/Users/ross/Sandbox/test.yaml', a())
    fs.dump()
    fs.load()
#============= EOF =============================================

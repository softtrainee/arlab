#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, List, Instance, on_trait_change, Any
from traitsui.api import View, Item
from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.graph.graph import Graph
from src.processing.plotter_options_manager import IdeogramOptionsManager
from src.database.records.isotope_record import IsotopeRecord
from src.processing.analysis import Analysis, Marker
from src.processing.search.selector_manager import SelectorManager
#============= standard library imports ========================
#============= local library imports  ==========================
class Processor(IsotopeDatabaseManager):
    count = 0
    options_manager = Instance(IdeogramOptionsManager, ())
    selector_manager = Instance(SelectorManager)
    active_editor = Any
    analyses = List
    @on_trait_change('''options_manager:plotter_options:[+, aux_plots:+]
''')
    def _options_update(self, name, new):
        if self.active_editor:
            comp = self.new_ideogram(ans=self.analyses)
            if comp:

                self.active_editor.component = comp

    def _gather_data(self):
        d = self.selector_manager
        if self.db.connect():
            info = d.edit_traits(kind='livemodal')
            if info.result:

                db = self.db
                def factory(pi):
                    rec = IsotopeRecord(_dbrecord=db.get_analysis_uuid(pi.uuid),
                                        graph_id=pi.graph_id,
                                        group_id=pi.group_id)
                    a = Analysis(isotope_record=rec)
                    a.load_isotopes()
                    return a


        #        self.db.selector.load_last(n=10)
                ans = [factory(ri) for ri in d.selected_records
                                    if not isinstance(ri, Marker)]
                return ans

    def new_ideogram(self, ans=None):
        '''
            return a plotcontainer
        '''
        from src.processing.plotters.ideogram import Ideogram

#        g = self._window_factory()

        probability_curve_kind = 'cumulative'
        mean_calculation_kind = 'weighted_mean'
        data_label_font = None
        metadata_label_font = None
#        highlight_omitted = True
        display_mean_indicator = True
        display_mean_text = True
        title = 'Foo {}'.format(self.count)
        self.count += 1
        p = Ideogram(db=self.db,
#                     processing_manager=self,
                     probability_curve_kind=probability_curve_kind,
                     mean_calculation_kind=mean_calculation_kind
                     )

        plotter_options = self.options_manager.plotter_options
#        ps = self._build_aux_plots(plotter_options.get_aux_plots())
        options = dict(
#                       aux_plots=ps,
#                       use_centered_range=plotter_options.use_centered_range,
#                       centered_range=plotter_options.centered_range,
#                       xmin=plotter_options.xmin,
#                       xmax=plotter_options.xmax,
#                       xtitle_font=xtitle_font,
#                       xtick_font=xtick_font,
#                       ytitle_font=ytitle_font,
#                       ytick_font=ytick_font,
                       data_label_font=data_label_font,
                       metadata_label_font=metadata_label_font,
                       title=title,
                       display_mean_text=display_mean_text,
                       display_mean_indicator=display_mean_indicator,
                       )
        if ans is None:
            ans = self._gather_data()

        if ans:
            self.analyses = ans
            gideo = p.build(ans, options=options,
                            plotter_options=plotter_options)
            if gideo:
                gideo, _plots = gideo

            return gideo

#===============================================================================
# defaults
#===============================================================================
    def _selector_manager_default(self):
        db = self.db
        d = SelectorManager(db=db)
        return d

#============= EOF =============================================

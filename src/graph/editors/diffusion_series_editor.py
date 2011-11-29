#=============enthought library imports=======================
from traits.api import Str, Bool

#============= standard library imports ========================

#============= local library imports  ==========================
from src.graph.editors.series_editor import SeriesEditor
class DiffusionSeriesEditor(SeriesEditor):
    runid=Str
    show_sample=Bool(True)
    show_model=Bool(True)
    isspectrum=Bool(False)
    def _show_sample_changed(self):
        if self.isspectrum:
            #toggles visibility of the error envelope
            self.graph.set_series_visiblity(self.show_sample, plotid=self.plotid,
                                            series=self.id-1)
        
        
        self.graph.set_series_visiblity(self.show_sample, plotid=self.plotid,
                                        series=self.id)
    
    def _show_model_changed(self):
        self.graph.set_series_visiblity(self.show_model, plotid=self.plotid,
                                        series=self.id+1)
    
#============= EOF =====================================

#=============enthought library imports=======================
from traits.api import HasTraits, List
from traitsui.api import View, Item, ListEditor
from traitsui.table_column import ObjectColumn

#============= standard library imports ========================

#============= local library imports  ==========================
from src.graph.editors.plot_editor import PlotEditor
from src.graph.editors.diffusion_series_editor import DiffusionSeriesEditor
from traitsui.extras.checkbox_column import CheckboxColumn
from chaco.polygon_plot import PolygonPlot
class DiffusionPlotEditor(PlotEditor):
    _series_editors=List
    def _build_series_editors(self):
        self.series_editors=[]        
            
        plots=self._get_plots()
        if plots:
            for i,rid in enumerate(self.graph.runids):
                
                #hack because polygon plot needs special editor
                isspectrum=False
                plot=plots['plot{}'.format(i)][0]
                if isinstance(plot, PolygonPlot):
                    isspectrum=True
                    i+=1
                    plot=plots['plot{}'.format(i)][0]
                    
                kwargs=self._get_series_editor_kwargs(plot, i)
                kwargs['runid']=rid    
                kwargs['isspectrum']=isspectrum
                
                
                e=DiffusionSeriesEditor(**kwargs)
                self.series_editors.append(e)

                
            self._sync_limits(plots['plot0'][0])
        
        
        super(DiffusionPlotEditor,self)._build_series_editors(editors=self._series_editors)
        
    def _get_selected_group(self):
        grp=Item('_series_editors',editor=ListEditor(use_notebook=True,
                            dock_style='tab',
                            page_name='.name'),
                 style='custom',
                 show_label=False)
        return grp
    def _get_table_columns(self):
        return [ObjectColumn(name='runid', editable=False),
                CheckboxColumn(name='show_sample', label='Sample'),
                CheckboxColumn(name='show_model', label='Model'),
                ]
        
#============= EOF =====================================

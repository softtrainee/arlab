#=============enthought library imports=======================
from traits.api import HasTraits, List
from traitsui.api import View, Item, ListEditor, TableEditor
from traitsui.table_column import ObjectColumn

#============= standard library imports ========================

#============= local library imports  ==========================
from src.graph.editors.plot_editor import PlotEditor
from src.graph.editors.diffusion_series_editor import DiffusionSeriesEditor, \
    PolyDiffusionSeriesEditor, ContourPolyDiffusionSeriesEditor
from traitsui.extras.checkbox_column import CheckboxColumn
from chaco.polygon_plot import PolygonPlot
from chaco.contour_poly_plot import ContourPolyPlot
from chaco.cmap_image_plot import CMapImagePlot
class DiffusionPlotEditor(PlotEditor):
    _series_editors = List
    def _build_series_editors(self):
        self.series_editors = []        
            
        plots = self._get_plots()
        
        #if plots really long means its an unconstrained thermal hist
        # and we dont want to display series editors
        if plots and len(plots) < 100:
            super(DiffusionPlotEditor, self)._build_series_editors(self._series_editors)
            for i, rid in enumerate(self.graph.runids):
                
                #hack because polygon plot needs special editor
                isspectrum = False
                self.iscoolinghistory = False
                plot = plots['plot{}'.format(i)][0]
                print plots
                if isinstance(plot, PolygonPlot):
                    if isinstance(plots['plot{}'.format(i + 1)][0], PolygonPlot):
                        self.iscoolinghistory = True
                    else:
                        isspectrum = True
                        i += 1
                    
                    plot = plots['plot{}'.format(i)][0]
                    
                elif isinstance(plot, CMapImagePlot):
#                elif isinstance(plot, ContourPolyPlot):
                    self.isunconstrained_thermal_history = True
#                    i+=1
#                    plot=plots['plot{}'.format(i)][0]

                kwargs = self._get_series_editor_kwargs(plot, i)
                kwargs['runid'] = rid    
                kwargs['isspectrum'] = isspectrum
                kwargs['iscoolinghistory'] = self.iscoolinghistory
                
                if self.iscoolinghistory:
                    editor = PolyDiffusionSeriesEditor
                elif self.isunconstrained_thermal_history:
                    editor = ContourPolyDiffusionSeriesEditor
#                    i+=1
#                    plot=plots['plot{}'.format(i)][0]
#                    kwargs['series2']=plot
                else:
                    editor = DiffusionSeriesEditor

                self.series_editors.append(editor(**kwargs))

                
        self._sync_limits(plots['plot0'][0])
            
    def _get_additional_groups(self):
        cols = [ObjectColumn(name='name', editable=False),
                CheckboxColumn(name='show')]
        table_editor = TableEditor(columns=cols,
                                   selected='_selected',
                                   selection_mode='row')
        grp = Item('_series_editors',
                 editor=table_editor,
                 style='custom',
                 show_label=False
                 
                 )
        return grp
#            super(DiffusionPlotEditor,self)._build_series_editors(editors=self._series_editors)
#    
#    def _get_plots(self):
#        p=super(DiffusionPlotEditor,self)._get_plots()
#        ps=dict()
#        for i in range(3):
#            k='plot{}'.format(i)
#            ps[k]=p[k]
#        return ps

#    def _get_selected_group(self):
#        grp=Item('_series_editors',
#                 editor=ListEditor(use_notebook=True,
#                            dock_style='tab',
#                            page_name='.name'),
#                 style='custom',
#                 show_label=False)
#        return grp
    def _get_table_columns(self):
        if self.iscoolinghistory:
            return [ObjectColumn(name='runid', editable=False),
                    CheckboxColumn(name='show_model', label='Inner'),
                    CheckboxColumn(name='show_sample', label='Outer'),
                    ]
        else:
            return [ObjectColumn(name='runid', editable=False),
                CheckboxColumn(name='show_sample', label='Sample'),
                CheckboxColumn(name='show_model', label='Model'),
                ]
        
#============= EOF =====================================

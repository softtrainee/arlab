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
from traits.api import Bool
#from traitsui.api import View, Item, Group, HGroup, VGroup, HSplit, VSplit
#============= standard library imports ========================
#from tables import openFile
from numpy import transpose, array, shape, max, linspace, rot90
#============= local library imports  ==========================
from src.graph.contour_graph import ContourGraph
#from src.managers.data_managers.h5_data_manager import H5DataManager

class PowerMapProcessor:
    '''
    '''
    correct_baseline = Bool(False)
    color_map = 'hot'
    levels = 10

#    def load_graph(self, table, window_title = ''):
    def load_graph(self, reader, window_title = ''):
        '''
        '''

        cg = ContourGraph(window_width = 725,
                          window_height = 635)
    #    cg.plotcontainer = cg._container_factory(type = 'h')

        z, metadata = self._extract_power_map_data(reader)
        x, y, z = self._prep_2D_data(z)

        bounds = (-float(metadata[1][1]), float(metadata[1][1]))
        cplot = cg.new_plot(add = False,
                            padding_top = 15,
                            padding_left = 20,
                            padding_right = 5,
                            resizable = '',
                            bounds = [400, 400],
                          )
        cplot.index_axis.title = 'mm'
        cplot.value_axis.title = 'mm'

        cg.new_series(x = x, y = y, z = z, style = 'contour',
                      xbounds = bounds,
                      ybounds = bounds,
                      cmap = self.color_map,
                      colorbar = True,
                      levels = self.levels)

        cpolyplot = cplot.plots['plot0'][0]
        options = dict(style = 'cmap_scatter',
                     type = 'cmap_scatter',
                     marker = 'circle',
                     color_mapper = cpolyplot.color_mapper
                     )

        p_xaxis = cg.new_plot(add = False,
                            padding_bottom = 0,
                            padding_left = 20,
                            padding_right = 5,
                            padding_top = 30,
                            resizable = '',
                            bounds = [400, 100],
                            title = 'Power Map'
                            )

        p_xaxis.index_axis.visible = False
        p_xaxis.value_axis.title = 'Power (%)'
        cg.new_series(plotid = 1, render_style = 'connectedpoints')
        cg.new_series(plotid = 1, **options)

        p_yaxis = cg.new_plot(add = False,
                              orientation = 'v',
                              padding_left = 0,
                              padding_bottom = 60,
                              resizable = '',
                              bounds = [120, 400]
                             )

        p_yaxis.index_axis.visible = False
        p_yaxis.value_axis.title = 'Power (%)'

        cg.new_series(plotid = 2, render_style = 'connectedpoints')
        cg.new_series(plotid = 2, **options)

        ma = max([max(z[i, :]) for i in range(len(x))])
        mi = min([min(z[i, :]) for i in range(len(x))])

        cg.set_y_limits(min = mi, max = ma, plotid = 1)
        cg.set_y_limits(min = mi, max = ma, plotid = 2)

        cg.show_crosshairs()

        cpolyplot.index.on_trait_change(cg.metadata_changed,
                                           'metadata_changed')

        container = cg._container_factory(type = 'v',
                                          bounds = [400, 600],
                                          resizable = ''
                                          )
        container.add(cplot)
        container.add(p_xaxis)

        cg.plotcontainer.add(container)
        cg.plotcontainer.add(p_yaxis)

        return cg

    def _extract_power_map_data(self, reader):
        '''
        '''

        cells = []
        metadata = []
        reader_meta = False
        for _index, row in enumerate(reader):

            if reader_meta:
                metadata.append(row)
                continue
            if '<metadata>' in row[0]:
                reader_meta = True
                continue
            if '</metadata>' in row[0]:
                reader_meta = False
                continue



            x = int(row[0])

            try:
                nr = cells[x]
            except:
                cells.append([])
                nr = cells[x]

            #baseline = self._calc_baseline(table, index) if self.correct_baseline else 0.0
            baseline = 0
            try:
                pwr = row['power']
            except:
                pwr = float(row[2])
            nr.append(max(pwr - baseline, 0))



        #rotate the array
        return rot90(array(cells), k = 2), metadata



    def _calc_baseline(self, table, index):
        '''
        '''

        try:
            b1 = table.attrs.baseline1
            b2 = table.attrs.baseline2
        except:
            b1 = b2 = 0
#        print b1,b2
#    ps=[row['power'] for row in table]
#    b1=ps[0]
#    b2=ps[-1:][0]
        size = table.attrs.NROWS - 1

        bi = (b2 - b1) / size * index + b1

        return bi

    def _prep_2D_data(self, z):
        '''
     
        '''
        z = transpose(z)
        mx = float(max(z))

        z = array([100 * x / mx for x in [y for y in z]])

        r, c = shape(z)
        x = linspace(0, 1, r)
        y = linspace(0, 1, c)
        return x, y, z

#if __name__ == '__main__':
#    p=PowerMapViewer()
#    
#    pa=sys.argv[1]
#    if pa[-2:]!='.h5':
#        pa+='.h5'
#        
#    
#    pa=os.path.join(paths.data_dir,'powermap',pa)
#    if os.path.isfile(pa):
#        p.open_power_map(pa)
#============= EOF ====================================
#            try:
#                x = int(row['col'])
#            except:
#                try:
#                    x = int(row['x'])
#                except:
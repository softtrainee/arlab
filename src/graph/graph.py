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
#=============enthought library imports=======================
from traits.api import HasTraits, Instance, Any, Bool, \
        List, Str, Property, Dict
from traitsui.api import View, Item, Handler

from enable.component_editor import ComponentEditor
from chaco.api import PlotGraphicsContext, OverlayPlotContainer, \
    VPlotContainer, HPlotContainer, GridPlotContainer, \
    BasePlotContainer, Plot, ArrayPlotData, PlotLabel, \
    add_default_axes, create_line_plot
from chaco.tools.api import ZoomTool, LineInspector
from chaco.axis import PlotAxis

from traitsui.menu import Menu, Action
from pyface.api import FileDialog, OK

from pyface.timer.api import do_after as do_after_timer, do_later
#=============standard library imports ========================
import numpy as np
from numpy.core.numeric import Inf
import csv
import math
#=============local library imports  ==========================
from src.helpers.color_generators import colorname_generator as color_generator
from src.graph.minor_tick_overlay import MinorTicksOverlay
from editors.plot_editor import PlotEditor
from guide_overlay import GuideOverlay

from tools.contextual_menu_tool import ContextualMenuTool
from tools.pan_tool import MyPanTool as PanTool
from chaco.data_label import DataLabel
from src.loggable import Loggable


def name_generator(base):
    '''
    '''
    i = 0
    while 1:
        n = base + str(i)
        yield n
        i += 1

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.gif']
DEFAULT_IMAGE_EXT = IMAGE_EXTENSIONS[0]
VALID_FONTS = ['Helvetica', 'Arial',
               'Lucida Grande', 'Times New Roman',
               'Geneva']


def fmt(data):
    return ['%0.8f' % d for d in data]


class GraphHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui


class Graph(Loggable):
    '''
        A Graph represents a collection of Plots
        A Plot represents a collection of series
        A series can be a line plot, scatter plot etc
        
        to graph data the generic protocol is 
        
        g=Graph()
        #add a plot to the Graph
        #this plot will have plotid =0
        g.new_plot()
        
        #plot attributes can be set with keywords
        #keywords are passed to Plot class
        #g.new_plot(title='time v. Temp')
        
        #add line plot
        #xdata,ydata two data arrays of same dimension
        g.new_series(x=xdata,y=ydata)
        
        #series attributes can be set with keywords
        #keywords are passed to the rendering class
        #g.new_series(x=x,y=y,color='green')
        
        #add a scatter plot
        g.new_series(x=xdata,y=ydata,type='scatter')
        
        #add a new plot
        #plotid=1
        g.new_plot()
        
        #add a series to second plot ie plotid=1 
        g.new_series(x=xdata,y=ydata,plotid=1)
       
       If you would like to create a standard template
       subclass Graph and implement the new_graph method
       
        
    '''
    name = Str
    plotcontainer = Instance(BasePlotContainer)
    container_dict = Dict
    plots = List(Plot)

    selected_plotid = Property
    selected_plot = Plot
    window_title = ''
    window_width = 600
    window_height = 500
    window_x = 500
    window_y = 250

    width = 300
    height = 300
    resizable = True
    crosshairs_enabled = False
    editor_enabled = True

    line_inspectors_write_metadata = False

    plot_editor = Any

    plot_editor_klass = PlotEditor

    graph_editor = Any
    autoupdate = Bool(False)

    _title = Str
    _title_font = None
    _title_size = None
    _control = None

    status_text = Str
    groups = None

    current_pos = None


    view_identifier = None
    def __init__(self, *args, **kw):
        '''
        '''
        super(Graph, self).__init__(*args, **kw)
        self.clear()

#    def close_ui(self):
#        if self.ui is not None:
#            #disposes 50 ms from now
#            do_later(self.ui.dispose)

    def update_group_attribute(self, plot, attr, value, dataid=0):
        pass

    def action_factory(self, name, func, **kw):
        '''
        '''
        return Action(name=name, on_perform=getattr(self, func),
                       **kw)

    def get_contextual_menu_save_actions(self):
        '''
        '''
        return [
                ('Clipboard', '_render_to_clipboard', {}),
                ('PDF', 'save_pdf', {}),
               ('PNG', 'save_png', {})]

    def contextual_menu_contents(self):
        '''
        '''
        save_actions = []
        for n, f, kw in self.get_contextual_menu_save_actions():
            save_actions.append(self.action_factory(n, f, **kw))

        save_menu = Menu(
                       name='Save Figure',
                       *save_actions)

        if not self.crosshairs_enabled:
            crosshairs_action = self.action_factory('Show Crosshairs',
                           'show_crosshairs'
                           )
        else:
            crosshairs_action = self.action_factory('Hide Crosshairs',
                           'destroy_crosshairs')

        export_actions = [
                          self.action_factory('Window', 'export_data'),
                          self.action_factory('All', 'export_raw_data'),

                          ]

        export_menu = Menu(name='Export',
                         *export_actions)
        contents = [save_menu, crosshairs_action, export_menu]
        if self.editor_enabled:
            contents += [self.action_factory('Show Plot Editor', 'show_plot_editor')]
            contents += [self.action_factory('Show Graph Editor', 'show_graph_editor')]

        return contents

    def get_contextual_menu(self):
        '''
        '''
        menu = Menu(*self.contextual_menu_contents()
                         )
        return menu

    def get_num_plots(self):
        '''
        '''
        return len(self.plots)

    def get_num_series(self, plotid):
        '''
        '''
        return len(self.series[plotid])

    def get_data(self, plotid=0, series=0, axis=0):
        '''

        '''
        s = self.series[plotid][series]
        p = self.plots[plotid]
        return p.data.get_data(s[axis])

    def save_png(self, path=None):
        '''
        '''
        self._save_(type='pic', path=path)

    def save_pdf(self, path=None):
        '''
        '''
        self._save_(type='pdf', path=path)

    def save(self, path=None):
        '''
        '''
        self._save_(path=path)

    def export_raw_data(self, path=None, header=None, plotid=0):
        if path is None:
            path = self._path_factory()
        if path is not None:
            self._export_raw_data(path, header, plotid)

    def export_data(self, path=None):
        if path is None:
            path = self._path_factory()
        if path is not None:
            self._export_data(path)

    def _path_factory(self):

        dlg = FileDialog(action='save as')
        if dlg.open() == OK:
            return dlg.path

    def _name_generator_factory(self, name):
        return name_generator(name)

    def read_xy(self, p, header=False, series=0, plotid=0):
        x = []
        y = []
        with open(p, 'r') as f:
            reader = csv.reader(f)
            if header:
                reader.next()
            for line in reader:
                if line[0].startswith('#'):
                    continue
                if len(line) == 2:
                    x.append(float(line[0]))
                    y.append(float(line[1]))

        self.set_data(x, plotid, series)
        self.set_data(y, plotid, series, axis=1)

    def close(self):
        if self.ui is not None:
            do_later(self.ui.dispose)
        self.ui = None

    def clear(self):
        '''
        '''
        self.plots = []

        self.xdataname_generators = [self._name_generator_factory('x')]
        self.ydataname_generators = [self._name_generator_factory('y')]
        self.yerdataname_generators = [self._name_generator_factory('yer')]

        self.color_generators = [color_generator()]

        self.series = []
        self.data_len = []

        self.raw_x = []
        self.raw_y = []
        self.raw_yer = []

        self.data_limits = []
        self.plotcontainer = self.container_factory()

    def set_axis_label_color(self, *args, **kw):
        '''
        '''

        kw['attr'] = 'title'
        self._set_axis_color(*args, **kw)

    def set_axis_tick_color(self, *args, **kw):
        '''
        '''
        attrs = ['tick_label', 'tick']
        if 'attrs' in kw:
            attrs = kw['attrs']

        for a in attrs:
            kw['attr'] = a
            self._set_axis_color(*args, **kw)

    def _set_axis_color(self, name, color, **kw):
        '''
        '''
        attr = kw['attr']
        p = self.plots[kw['plotid']]
        if 'axis' in kw:
            ax = kw['axis']
        else:
            ax = getattr(p, '{}_axis'.format(name))
        if isinstance(attr, str):
            attr = [attr]
        for a in attr:
            setattr(ax, '{}_color'.format(a), color)

    def set_data(self, d, plotid=0, series=0, axis=0):
        '''
        '''
        n = self.series[plotid][series]
        self.plots[plotid].data.set_data(n[axis], d)

    def set_axis_traits(self, plotid=0, axis='x', **kw):
        '''
        '''
        plot = self.plots[plotid]

        attr = getattr(plot, '{}_axis'.format(axis))
        attr.trait_set(**kw)

    def set_grid_traits(self, plotid=0, grid='x', **kw):
        '''
        '''
        plot = self.plots[plotid]

        attr = getattr(plot, '{}_grid'.format(grid))
        attr.trait_set(**kw)

    def set_series_traits(self, d, plotid=0, series=0):
        '''
        '''

        plot = self.plots[plotid].plots['plot%i' % series][0]
        plot.trait_set(**d)
        self.plotcontainer.request_redraw()

#    def set_series_type(self, t, plotid = 0, series = 0):
#        '''

#        '''
#        p = self.plots[plotid]
#        s = 'plot%i' % series
#
#        ss = p.plots[s][0]
#        x = ss.index.get_data()
#        y = ss.value.get_data()
#
#        p.delplot(s)
#
#        series,plot=self.new_series(x = x, y = y, color = ss.color, plotid = plotid, type = t, add = True)
#        self.plotcontainer.invalidate_and_redraw()
#        return series
#        #self.refresh_editor()
    def get_series_label(self, plotid=0, series=0):
        r = ''
        legend = self.plots[plotid].legend
        if isinstance(series, str):
            if series in legend.labels:
                return series
            return

        try:
            r = legend.labels[series]
        except IndexError:
            pass

        return r

    def set_series_label(self, label, plotid=0, series=0):
        '''
        
            A chaco update requires that the legends labels match the keys in the plot dict
            
            save the plots from the dict
            resave them with label as the key
            
        '''

        legend = self.plots[plotid].legend

        try:
            legend.labels[series] = label
        except Exception, e:
            legend.labels.append(label)

        if isinstance(series, int):
            series = 'plot{}'.format(series)

        plots = self.plots[plotid].plots[series]
        self.plots[plotid].plots[label] = plots
        self.plots[plotid].plots.pop(series)

#        print legend.plots['plot0'][0].visible
#        print legend.labels
#        legend.hide_invisible_plots = False
#        legend._cached_label_names = legend.labels

    def clear_legend(self, keys, plotid=0):
        legend = self.plots[plotid].legend
        for key in keys:
            legend.plots.pop(key)

    def set_series_visiblity(self, v, plotid=0, series=0):
        '''
        '''
        p = self.plots[plotid]

        if isinstance(series, int):
            series = 'plot%i' % series
        p.showplot(series) if v else p.hideplot(series)

        self.plotcontainer.invalidate_and_redraw()

    def get_x_limits(self, plotid=0):
        '''
        '''
        return self._get_limits('index', plotid=plotid)

    def get_y_limits(self, plotid=0):
        '''
        '''
        return self._get_limits('value', plotid=plotid)

    def set_y_limits(self, min=None, max=None, pad=0, plotid=0, **kw):
        '''
        '''
        self._set_limits(min, max, 'value', plotid, pad, **kw)

    def set_x_limits(self, min=None, max=None, pad=0, plotid=0, **kw):
        '''
        '''
        self._set_limits(min, max, 'index', plotid, pad, **kw)

    def set_x_tracking(self, track, plotid=0):
        plot = self.plots[plotid]
        if track:
            plot.index_range.tracking_amount = track
            plot.index_range.high_setting = 'track'
            plot.index_range.low_setting = 'auto'
        else:
            plot.index_range.high_setting = 'auto'
            plot.index_range.low_setting = 'auto'

    def set_title(self, t, font='Helvetica', size=None):
        '''
        '''
        self._title = t

        pc = self.plotcontainer
        if pc.overlays:
            pc.overlays.pop()
        if not font in VALID_FONTS:
            font = 'Helvetica'

        if size is None:
            size = 12
        self._title_font = font
        self._title_size = size
        font = '%s %s' % (font, size)
        pc.overlays.append(PlotLabel(t,
                                     component=pc,
                                 font=font,
                                 vjustify='bottom',
                                 overlay_position='top'
                                 ))
#        pc.invalidate_and_redraw()
        pc.request_redraw()

    def get_x_title(self, plotid=0):
        '''
        '''
        return self._get_title('y_axis', plotid)

    def get_y_title(self, plotid=0):
        '''
        '''
        return self._get_title('x_axis', plotid)

    def set_x_title(self, title, plotid=0):
        '''
        '''
        self._set_title('x_axis', title, plotid)

    def set_y_title(self, title, plotid=0):
        '''
        '''
        self._set_title('y_axis', title, plotid)

    def add_plot_label(self, txt, x, y, plotid=0):
        '''
        '''
#         
        self.plots[plotid].overlays.append(PlotLabel(txt, x=x, y=y))

    def add_data_label(self, x, y, plotid=0):
        #print self.plots, plotid
        plot = self.plots[plotid]
        label = DataLabel(component=plot, data_point=(x, y),
                          label_position="top left", padding=40,
                          bgcolor="lightgray",
                          border_visible=False)
        plot.overlays.append(label)
    def add_guide(self, value, orientation='h', plotid=0, color=(0, 0, 0)):
        '''
        '''

        plot = self.plots[plotid]

        guide_overlay = GuideOverlay(component=plot,
                                   value=value,
                                   color=color)
        plot.overlays.append(guide_overlay)

    def new_plot(self, add=True, **kw):
        '''
        '''
        p = self._plot_factory(**kw)

        self.plots.append(p)
        self.color_generators.append(color_generator())
        self.xdataname_generators.append(name_generator('x'))
        self.ydataname_generators.append(name_generator('y'))
        self.yerdataname_generators.append(name_generator('yer'))

        self.series.append([])
        self.raw_x.append([])
        self.raw_y.append([])
        self.raw_yer.append([])

        pc = self.plotcontainer
        if add:
            pc.add(p)

        zoom = kw['zoom'] if 'zoom' in kw  else False
        pan = kw['pan'] if 'pan' in kw else False

        contextmenu = kw['contextmenu'] if 'contextmenu' in kw.keys() else True

        if zoom:
            nkw = dict(tool_mode='box',
                    always_on=False
                    )
            if 'zoom_dict' in kw:
                zoomargs = kw['zoom_dict']
                for k in zoomargs:
                    nkw[k] = zoomargs[k]
            zt = ZoomTool(component=p, **nkw)
            p.overlays.append(zt)

        if pan:
            kwargs = dict(always_on=False)
            if isinstance(pan, str):
                kwargs['constrain'] = True
                kwargs['constrain_direction'] = pan
                kwargs['constrain_key'] = None

            p.tools.append(PanTool(p, **kwargs))

        for tool in pc.tools:
            if isinstance(tool, ContextualMenuTool):
                contextmenu = False

        plotid = len(self.plots) - 1
        if contextmenu:
            menu = ContextualMenuTool(parent=self,
                                      component=pc,
                                    plotid=plotid)

            pc.tools.append(menu)

        for t in ['x', 'y']:
            title = '{}title'.format(t)
            if title in kw:
                self._set_title('{}_axis'.format(t), kw[title], plotid)

        return p

    def new_graph(self, *args, **kw):
        '''
        '''
        raise NotImplementedError

    def new_series(self, x=None, y=None, yer=None, plotid=None, aux_plot=False, **kw):
        '''
        '''
        if plotid is None:
            plotid = len(self.plots) - 1
        kw['plotid'] = plotid
        plotobj, names, rd = self._series_factory(x, y, yer=None, **kw)
        #print 'downsample', plotobj.use_downsample

        plotobj.use_downsample = True
        if aux_plot:
            if x is None:
                x = np.array([])
            if y is None:
                y = np.array([])
            renderer = create_line_plot((x, y))
#            l, b = add_default_axes(renderer)
#
#            l.orientation = 'right'
#            b.orientation = 'top'

            plotobj.add(renderer)
#            print 'plotobj%s' % names[0][-1:][0]
            n = 'aux{:03n}'.format(int(names[0][-1:][0]))
            plotobj.plots[n] = [renderer]

            return renderer, plotobj

        else:
            if 'type' in rd:
                if rd['type'] == 'line_scatter':

                    renderer = plotobj.plot(names, type='scatter', marker_size=2,
                                       marker='circle', color=rd['color'],
                                        outline_color=rd['color'])
                    rd['type'] = 'line'

                elif rd['type'] == 'scatter':
                    rd['outline_color'] = rd['color']

            renderer = plotobj.plot(names, **rd)
            return renderer[0], plotobj

    def show_graph_editor(self):
        '''
        '''
        from editors.graph_editor import GraphEditor

        g = self.graph_editor
        if g is None:
            g = GraphEditor(graph=self)
            self.graph_editor = g

        g.edit_traits(parent=self._control)

    def show_plot_editor(self):
        '''
        '''
        self._show_plot_editor()

    def _show_plot_editor(self, **kw):
        '''
        '''
        p = self.plot_editor
        if p is None or not p.plot == self.selected_plot:
            p = self.plot_editor_klass(plot=self.selected_plot,
                           graph=self,
                           **kw
                     )
            self.plot_editor = p

            p.edit_traits(parent=self._control)

    def auto_update(self, *args, **kw):
        '''
        '''
        pass
    def add_aux_axis(self, po, p):
        from chaco.axis import PlotAxis
        axis = PlotAxis(p, orientation='right',
                        axis_line_visible=False,
                        tick_color='red',
                        tick_label_color='red')
        p.underlays.append(axis)
        po.add(p)
        po.plots['aux'] = [p]

    def add_datum_to_aux_plot(self, datum, plotid=0, series=1):
        '''
        '''
        plot = self.plots[plotid]

        series = plot.plots['aux{:03n}'.format(series)][0]

        oi = series.index.get_data()
        ov = series.value.get_data()

        series.index.set_data(np.hstack((oi, [datum[0]])))
        series.value.set_data(np.hstack((ov, [datum[1]])))

    def add_data(self, data, plotlist=None, **kw):
        if plotlist is None:
            plotlist = xrange(len(data))
        for pi, d in zip(plotlist, data):
            self.add_datum(d,
                           plotid=pi,
                           ** kw)

    def add_datum(self, datum, plotid=0, series=0, update_y_limits=False, ypadding=10, do_after=None):
        '''
        '''
        def add():
            names = self.series[plotid][series]
            plot = self.plots[plotid]
            for i, name in enumerate(names):
                d = plot.data.get_data(name)
                nd = np.hstack((d, float(datum[i])))
                plot.data.set_data(name, nd)

                if i == 1:
                    #y values
                    mi = min(nd)
                    ma = max(nd)

            if update_y_limits:
                self.set_y_limits(min=mi - ypadding,
                                  max=ma + ypadding,
                                  plotid=plotid)

        if do_after:
            do_after_timer(do_after, add)
        else:
            add()

    def show_crosshairs(self):
        '''
        '''
        self.crosshairs_enabled = True
        self._crosshairs_factory()
        self.plotcontainer.request_redraw()

    def destroy_crosshairs(self):
        '''
        '''
        self.crosshairs_enabled = False
        plot = self.plots[0].plots['plot0'][0]
        plot.overlays = [o for o in plot.overlays if not isinstance(o, LineInspector)]
        self.plotcontainer.request_redraw()

    def add_vertical_rule(self, v, plotid=0, **kw):
        plot = self.plots[plotid]
        l = GuideOverlay(plot, value=v, orientation='v', **kw)

        plot.overlays.append(l)

    def add_horizontal_rule(self, v, plotid=0, **kw):
        plot = self.plots[0]

        l = GuideOverlay(plot, value=v, **kw)

        plot.overlays.append(l)

    def add_opposite_ticks(self, plotid=0, key=None):
        p = self.plots[plotid]
        if key is None:
            for key in ['x', 'y']:
                ax = self._plot_axis_factory(p, key, False)
                p.underlays.append(ax)

        else:
            ax = self._plot_axis_factory(p, key, False)
            p.underlays.append(ax)

    def _plot_axis_factory(self, p, key, normal, **kw):
        if key == 'x':
            m = p.index_mapper
            if normal:
                o = 'bottom'
            else:
                o = 'top'
                kw['tick_label_formatter'] = lambda x: ''
        else:
            if normal:
                o = 'left'
            else:
                o = 'right'
                kw['tick_label_formatter'] = lambda x: ''
            m = p.value_mapper

        ax = PlotAxis(component=p,
                      mapper=m,
                      orientation=o,
                      axis_line_visible=False,
                      **kw
                      )
        return ax

    def add_minor_xticks(self, plotid=0, **kw):
        p = self.plots[plotid]
        m = MinorTicksOverlay(component=p, orientation='v', **kw)
        p.underlays.append(m)

    def add_minor_yticks(self, plotid=0, **kw):
        p = self.plots[plotid]

        m = MinorTicksOverlay(component=p, orientation='h', **kw)
        p.underlays.append(m)

    def redraw(self, force=True):
        if force:
            self.plotcontainer._layout_needed = True
            self.plotcontainer.invalidate_and_redraw()
        else:
            self.plotcontainer.request_redraw()

    def container_factory(self):
        '''
        '''
        return self._container_factory(**self.container_dict)

    def _add_line_inspector(self, plot, axis='x', color='red'):
        '''
        '''
        plot.overlays.append(LineInspector(component=plot,
                                           axis='index_%s' % axis,
                                           write_metadata=self.line_inspectors_write_metadata,
                                           inspect_mode='indexed',
                                           is_listener=False,
                                           color=color
                                           ))

    def _container_factory(self, **kw):
        '''
        '''
        if 'type' in kw:
            type = kw['type']
        else:
            type = 'v'

        types = ['v', 'h', 'g', 'o']
        containers = [VPlotContainer, HPlotContainer, GridPlotContainer, OverlayPlotContainer]

        c = containers[types.index(type)]

        options = dict(
                       bgcolor='white',
                     #spacing = spacing,
                     #padding=25,
                     padding=[40, 10, 60, 10],
                     fill_padding=True,
                     use_backbuffer=True
                     )

        for k in options:
            if k not in kw.keys():
                kw[k] = options[k]

        container = c(**kw)

        #add some tools
#        cm=ContextualMenuTool(parent=container,
#                              component=container
#                              )
#        container.tools.append(cm)
#        
        #gt = TraitsTool(component = container)
        #container.tools.append(gt)
        return container

    def _crosshairs_factory(self, plot=None):
        '''
        '''
        if plot is None:
            plot = self.plots[0].plots['plot0'][0]
        self._add_line_inspector(plot, axis='x', color='black')
        self._add_line_inspector(plot, axis='y', color='black')

    def _plot_factory(self, **kw):
        '''
        '''
        p = Plot(data=ArrayPlotData(),
               use_backbuffer=True,
               **kw
               )

        vis = kw['show_legend'] if 'show_legend' in kw else False

        if not isinstance(vis, bool):
            align = vis
            vis = True
        else:
            align = 'lr'

        p.legend.visible = vis
        p.legend.align = align
        return p

    def _export_raw_data(self, path, header, plotid):
        def name_generator(base):
            i = 0
            while 1:
                yield '%s%s%8s' % (base, i, '')
                i += 1

        xname_gen = name_generator('x')
        yname_gen = name_generator('y')

        writer = csv.writer(open(path, 'w'))
        if plotid is None:
            plotid = self.selected_plotid

        xs = self.raw_x[plotid]
        ys = self.raw_y[plotid]

        cols = []
        nnames = []
        for xd, yd in zip(xs, ys):
            cols.append(fmt(xd))
            cols.append(fmt(yd))
            nnames.append(xname_gen.next())
            nnames.append(yname_gen.next())

        if header is None:
            header = nnames
        writer.writerow(header)
        rows = zip(*cols)
        writer.writerows(rows)

    def _export_data(self, path):
        writer = csv.writer(open(path, 'w'))
        plot = self.selected_plot
        data = plot.data
        names = data.list_data()
        xs = names[len(names) / 2:]
        xs.sort()
        ys = names[:len(names) / 2]
        ys.sort()
        cols = []
        nnames = []
        for xn, yn in zip(xs, ys):
            yd = data.get_data(yn)
            xd = data.get_data(xn)

            cols.append(fmt(xd))
            cols.append(fmt(yd))
            nnames.append(xn)
            nnames.append(yn)

        writer.writerow(nnames)
        rows = zip(*cols)
        writer.writerows(rows)

    def _series_factory(self, x, y, yer=None, plotid=0, add=True, **kw):
        '''
        '''
        if x is None:
            x = np.array([])
        if y is None:
            y = np.array([])

        plot = self.plots[plotid]
        if add:
            if 'xname' in kw:
                xname = kw['xname']
            else:

                xname = self.xdataname_generators[plotid].next()
            if 'yname' in kw:
                yname = kw['yname']
            else:
                yname = self.ydataname_generators[plotid].next()

            names = (xname, yname)
            self.raw_x[plotid].append(x)
            self.raw_y[plotid].append(y)
            if yer is not None:
                self.raw_yer[plotid].append(yer)
                yername = self.yerdataname_generators[plotid].next()
                names += (yername,)
            self.series[plotid].append(names)
        else:
            try:
                xname = self.series[plotid][0][0]
                yname = self.series[plotid][0][1]
                if yer is not None:
                    yername = self.series[plotid][0][2]
            except IndexError:
                pass

        plot.data.set_data(xname, x)
        plot.data.set_data(yname, y)
        if yer is not None:
            plot.data.set_data(yername, yer)

        colorkey = 'color'
        if not 'color' in kw.keys():
            color_gen = self.color_generators[plotid]
            c = color_gen.next()
        else:
            c = kw['color']

        if 'type' in kw:

            if kw['type'] == 'bar':
                colorkey = 'fill_color'
            elif kw['type'] == 'polygon':
                colorkey = 'face_color'
                kw['edge_color'] = c
            elif kw['type'] == 'scatter':
                kw['outline_color'] = c

        for k, v in [('render_style', 'connectedpoints'),
                     (colorkey, c)
                     ]:
            if k not in kw.keys():
                kw[k] = v

        return plot, (xname, yname), kw

    def _save_(self, type='pic', path=None):
        '''
        '''
        if path is None:
            dlg = FileDialog(action='save as')
            if dlg.open() == OK:
                path = dlg.path
                self.status_text = 'Image Saved: %s' % path

        if path is not None:
            if type == 'pdf':
                self._render_to_pdf(filename=path)
            else:
                #auto add an extension to the filename if not present
                #extension is necessary for PIL compression
                #set default save type DEFAULT_IMAGE_EXT='.png'

                #see http://infohost.nmt.edu/tcc/help/pubs/pil/formats.html
                saved = False
                for ei in IMAGE_EXTENSIONS:
                    if path.endswith(ei):
                        self._render_to_pic(path)
                        saved = True
                        break

                if not saved:
                    self._render_to_pic(path + DEFAULT_IMAGE_EXT)

#                base, ext = os.path.splitext(path)
#                
#                if not ext in IMAGE_EXTENSIONS:
#                    path = ''.join((base, DEFAULT_IMAGE_EXT))

    def _render_to_pdf(self, filename=None, dest_box=None, canvas=None):
        '''
        '''
        from chaco.pdf_graphics_context import PdfPlotGraphicsContext

        if not filename.endswith('.pdf'):
            filename += '.pdf'

        gc = PdfPlotGraphicsContext(filename=filename,
                                  pdf_canvas=canvas,
                                  pagesize='letter',
                                  dest_box=dest_box,
                                  dest_box_units='inch')
        gc.render_component(self.plotcontainer)
        gc.save()

    def _render_to_pic(self, filename):
        '''
        '''
        p = self.plotcontainer
        gc = PlotGraphicsContext((int(p.outer_width), int(p.outer_height)))
        p.use_backbuffer = False
        gc.render_component(p)
        p.user_backbuffer = True
        gc.save(filename)

    def _render_to_clipboard(self):
        '''
            on mac osx the bitmap gets copied to the clipboard
            
            the contents of clipboard are available to Preview and NeoOffice 
            but not Excel
            
            More success may be had on windows 
            
            Copying to clipboard is used to get a Graph into another program
            such as Excel or Illustrator
            
            Save the image as png then Insert Image is probably equivalent but not
            as convenient
            
        '''
        import wx
        p = self.plotcontainer
        #gc = PlotGraphicsContext((int(p.outer_width), int(p.outer_height)))
        width, height = p.outer_bounds
        gc = PlotGraphicsContext((width, height), dpi=72)
        p.use_backbuffer = False
        gc.render_component(p)
        p.use_backbuffer = True

        # Create a bitmap the same size as the plot
        # and copy the plot data to it

        bitmap = wx.BitmapFromBufferRGBA(width + 1, height + 1,
                                     gc.bmp_array.flatten())
        data = wx.BitmapDataObject()
        data.SetBitmap(bitmap)

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()

    def _get_title(self, axis, plotid):
        '''
        '''
        axis = getattr(self.plots[plotid], axis)
        return axis.title

    def _set_title(self, axis, title, plotid):
        '''
        '''
        axis = getattr(self.plots[plotid], axis)
        axis.trait_set(title=title)
        self.plotcontainer.request_redraw()

    def _get_limits(self, axis, plotid):
        '''
        '''
        plot = self.plots[plotid]
        try:
            ra = getattr(plot, '%s_range' % axis)
            return ra.low, ra.high
        except AttributeError, e:
            print e

#    def _set_limits(self, mi, ma, axis, plotid, auto, track, pad):
    def _set_limits(self, mi, ma, axis, plotid, pad, force=True):
        '''
        '''
        plot = self.plots[plotid]
        ra = getattr(plot, '%s_range' % axis)

        scale = getattr(plot, '%s_scale' % axis)
        if scale == 'log':
            try:
                if mi <= 0:

                    mi = Inf
                    for di in plot.data.list_data():
                        if 'y' in di:
                            ya = np.copy(plot.data.get_data(di))
                            ya.sort()
                            i = 0
                            try:
                                while ya[i] <= 0:
                                    i += 1
                                if ya[i] < mi:
                                    mi = ya[i]

                            except IndexError:
                                mi = 0.01

                mi = 10 ** math.floor(math.log(mi, 10))

                ma = 10 ** math.ceil(math.log(ma, 10))
            except ValueError:
                return
        else:
            if isinstance(pad, str):
                #interpet pad as a percentage of the range
                #ie '0.1' => 0.1*(ma-mi)
                if ma is not None and mi is not None:
                    pad = float(pad) * (ma - mi)
                    if abs(pad - 0) < 1e-10:
                        pad = 1
            if ma is not None:
                ma += pad

            if mi is not None:
                mi -= pad

        if mi is not None:
            if mi < ra.high_setting:
                ra.low_setting = mi
        if ma is not None:
            if ma > ra.low_setting:
                ra.high_setting = ma

        self.redraw(force=force)
    def _get_selected_plotid(self):
        '''
        '''
        r = 0
        if self.selected_plot is not None:
            try:
                r = self.plots.index(self.selected_plot)
            except ValueError:
                pass
        return r

    def traits_view(self):
        '''
        '''

        plot = Item('plotcontainer',
                    style='custom',
                    show_label=False,
                    editor=ComponentEditor(
                                             size=(self.width,
                                                     self.height)
                                             ),
                    )

        v = View(plot,
                 resizable=self.resizable,
                 title=self.window_title,
                 width=self.window_width,
                 height=self.window_height,
                 x=self.window_x,
                 y=self.window_y,
                 handler=GraphHandler,
#                 statusbar = 'status_text',
                 )

        if self.view_identifier:
            v.id = self.view_identifier
        return v
#============= EOF ====================================

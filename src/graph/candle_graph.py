#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from graph import Graph
class CandleGraph(Graph):
    '''
        G{classtree}
    '''
    def new_series(self, plotid = 0, *args, **kw):

        plot, names, rd = self._series_factory(plotid = 0, *args, **kw)
        plot.x_axis.tick_interval = 1
        series = plot.candle_plot(names, **rd)
        return series[0], plot

    def clear(self):
        #super(CandleGraph, self).clear()
        Graph.clear(self)
        self.minname_generators = [self._name_generator_factory('min')]
        self.maxname_generators = [self._name_generator_factory('max')]
        self.barminname_generators = [self._name_generator_factory('barmin')]
        self.barmaxname_generators = [self._name_generator_factory('barmax')]

    def _series_factory(self, plotid = 0, *args, **kw):

        minname = self.minname_generators[plotid].next()
        maxname = self.maxname_generators[plotid].next()
        barminname = self.barminname_generators[plotid].next()
        barmaxname = self.barmaxname_generators[plotid].next()

        plot = self.plots[plotid]
        rnames = []
        for name in ['min', 'barmin', 'barmax', 'max']:
            data = kw['y{}'.format(name)]
            nn = locals()['{}name'.format(name)]
            plot.data.set_data(nn, data)
            rnames.append(nn)

        plot, names, rd = super(CandleGraph, self)._series_factory(*args, **kw)
        rname = [names[0]] + rnames[:2] + [names[1]] + rnames[2:]
        return  plot, tuple(rname), rd

if __name__ == '__main__':
    c = CandleGraph()
    c.new_plot()
    x = [1, 2, 3, 4, 5]
    ymin = [5, 5, 5, 5, 5]
    ybarmin = [6, 6, 6, 6, 6]
    y = [10, 9, 8, 9, 11]
    ybarmax = [20, 20, 20, 20, 20]
    ymax = [25, 25, 25, 25, 25]

    c.new_series(x = x, y = y, ymin = ymin, ymax = ymax, ybarmin = ybarmin, ybarmax = ybarmax)
    c.configure_traits()
#============= EOF ====================================

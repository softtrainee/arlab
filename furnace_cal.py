#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================

import os
from src.helpers import paths
from src.graph.time_series_graph import TimeSeriesGraph


def extract_data(p):
    '''
    '''
    import csv
    reader = csv.reader(open(p, 'U'), delimiter = '\t')
    x = []
    y = []

    max = 40000
    for i, row in enumerate(reader):
        if i == 0:
            continue

        if i == 1:
            t_zero = float(row[0])
            t = 0
        else:
            t = float(row[0]) - t_zero

        if i == max:
            break
        x.append(t)
        y.append(float(row[2]))

    return x, y
def plot_data(x, y, x1, y1):
    '''
        @type y: C{str}
        @param y:

        @type x1: C{str}
        @param x1:

        @type y1: C{str}
        @param y1:
    '''
    g = TimeSeriesGraph()

    g.new_plot(show_legend = True, zoom = True, pan = True)
    g.new_series(x = x, y = y)
    g.new_series(x = x1, y = y1)

    g.set_series_label('Inside')

    g.set_series_label('Outside', series = 1)

    g.configure_traits()
if __name__ == '__main__':
    p1 = os.path.join(paths.data_dir, 'furnace_calibration', 'DPi32TemperatureMonitor002.txt')
    p2 = os.path.join(paths.data_dir, 'furnace_calibration', 'Eurotherm002.txt')

    x, y = extract_data(p1)
    x1, y1 = extract_data(p2)

    plot_data(x, y, x1, y1)

#============= EOF ====================================

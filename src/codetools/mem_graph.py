from pylab import *

import os
def plot_file(p, normalize=False, stacked=False):

    x = []
    y = []
    ts = []
    cnt = 0
    n=0
    mi=Inf
    ma=-Inf
    with open(p, 'r') as fp:
        xi = 0
        ticked = False
        for line in fp:
            # print line
            msg, mem = map(str.strip, line.split(':'))
            try:
                yi = float(mem)
                y.append(yi)
                x.append(xi)
                mi=min(mi, yi)
                ma=max(ma, yi)
                xi += 1
                ts.append(msg)
            except ValueError:
                continue

            if msg.endswith('teardown'):
                n+=1
                if not ticked and stacked:
                    xticks(x, ts, rotation=-90)
                    ticked = True

                y = array(y)
                if normalize:
                    y -= y[0]
                
                plot(x, y, label=os.path.basename(p) + str(cnt))
                if stacked:
                    xi = 0
                x = []
                y = []
                ts = []
                cnt += 1
        if x:
            n+=1
            y = array(y)
            if normalize:
                y -= y[0]
            if not ticked and stacked:
                xticks(x, ts, rotation=-90)
            plot(x, y, label=os.path.basename(p) + str(cnt))

        print 'Min: {}  Max: {} avg: {} n: {}'.format(mi,ma, (ma-mi)/float(n), n)
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n,--normalize', dest='normalize', 
                        action='store_const',
                        const=bool,
                        default=False)
    parser.add_argument('-s,--stacked', dest='stacked', 
                        action='store_const',
                        const=bool,
                        default=False)
    parser.add_argument('paths', metavar='p', nargs='+')
    args = parser.parse_args()
    print args

    root = os.path.expanduser('~')
    d=os.path.join(root, 'Desktop', 'memtest')
    if args:
        paths = args.paths
        normalize = args.normalize
        stacked=args.stacked
        if paths[0]=='last':
            i=1
            while 1:
                pa=os.path.join(d, 'mem{:03n}.txt'.format(i))
                if os.path.isfile(pa):
                    i+=1
                else:
                    pa=os.path.join(d, 'mem{:03n}.txt'.format(i-1))
                    break
            
            plot_file(pa, normalize=normalize, stacked=stacked)
            tight_layout()
            show()
        else:
            for ai in paths:
                n = 'mem{:03n}.txt'.format(int(ai))
                p = os.path.join(d, n)
                plot_file(p, normalize=normalize, stacked=stacked)
                legend(loc='upper left')
                tight_layout()
                show()

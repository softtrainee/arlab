from pylab import *

import os
def plot_file(p, normalize=False):
    
    x=[]
    y=[]
    ts=[]
    cnt=0
    with open(p,'r') as fp:
        xi=0
        ticked=False
        for line in fp:
            #print line
            msg,mem=map(str.strip, line.split(':'))
            try:
                yi=float(mem)       
                y.append(yi)
                x.append(xi)
                xi+=1
                ts.append(msg)
            except ValueError:
                continue
                
            if msg.endswith('teardown'):
                if not ticked:
                    xticks(x, ts, rotation=-90)     
                    ticked=True
                    
                y=array(y)
                if normalize:
                    y-=y[0]
                plot(x,y, label=os.path.basename(p)+str(cnt))
                xi=0
                x=[]
                y=[]
                ts=[]
                cnt+=1
        if x:
            y=array(y)
            if normalize:
                 y-=y[0]
            if not ticked:
                xticks(x, ts, rotation=-90)
            plot(x,y, label=os.path.basename(p)+str(cnt))
                
                
if __name__ == '__main__':  
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('-n,--normalize',dest='normalize', default=False)
    parser.add_argument('paths',metavar='p', nargs='+')
    args=parser.parse_args()
    print args
    
    if args: 
        paths=args.paths
        normalize=args.normalize
        for ai in paths:
            
            p='/Users/argus1ms/Desktop/memtest/mem{:03n}.txt'.format(int(ai))
            plot_file(p, normalize=normalize)
            legend(loc='upper left')
            tight_layout()
            show()
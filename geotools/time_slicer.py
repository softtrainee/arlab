#=============enthought library imports=======================

#=============standard library imports ========================
import os
from pylab import *
#=============local library imports  ==========================
from filetools.import_file_tools import import_csv, find_col

def _slice_(ages,data):
    n=int(ceil(max(ages)))
    
    ind=digitize(ages,bins=range(n))
  #  data_ind=ind.argsort()
    #print ind
    #print ages
    bin=[[] for i in range(n)]
    for k,i in enumerate(ind):
        bin[i-1].append(data[k])
    return bin
   # for k in range(n,0,-1):
    #    timeslice[i-1].append(data[k])
    
def time_slice_file(path):
    header,data=import_csv(path)
    print header
    age_index=find_col(['age','Age'],header)
    ages=array([float(s[age_index].split('+')[0]) for s in data])
    slices=_slice_(ages,data)
    write_to_file(slices,os.path.dirname(p),header)
    
def write_to_file(slices,base,header):
    
    for i,s in enumerate(slices):    
        if len(s)!=0:
            slicename='slice%i_%i.txt'%(i,i+1)
            p=os.path.join(base,slicename)
            
            file=open(p,'w')
            file.write('%s\n'%join_array(header))
            for si in s:
                line=join_array(si)
                file.write('%s\n'%line)
def join_array(data):
    return ''.join(['%s,'%d for d in data])[:-1]        
if __name__ == '__main__':
    p=os.path.join(os.getcwd(),'data','datedsamples06.txt')
    time_slice_file(p)
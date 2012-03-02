#=============enthought library imports=======================

#=============standard library imports ========================
import csv
#=============local library imports  ==========================
from import_file_tools import find_col, import_csv


def prep_list(data,writer, header=False):
    for args in data:
        #args=line.split(',')
        if header:
            nstr='utm'
        else:
            nstr='%s %s'%(args[eindex],args[nindex])
        args[eindex]=nstr
        args.pop(nindex)
        
        writer.writerow(args)
if __name__ == '__main__':
    p1='/Users/Ross/Programming/Geotools/data/trachyte_samples'
    header,data=import_csv(p1+'.original.csv')
    
    
    outf=open(p1+'.csv','w')
    eindex=find_col('E',header)
    nindex=find_col('N',header)
    
    writer=csv.writer(outf)
    
    prep_list([header],writer, header=True)
    prep_list(data,writer)


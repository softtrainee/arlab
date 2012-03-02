'''
RossLabs 2009
Ross  Jake Ross   jirhiker@gmail.com

Nov 14, 2009
'''

#=============enthought library imports=======================

#=============standard library imports ========================
import os
from pylab import *
from mpl_toolkits.mplot3d import axes3d
#=============local library imports  ==========================
from kmlwriter.filetools.import_file_tools import import_csv, get_col_index
def _time_slice(ages, data):
    n = int(max(ages))
    indes = digitize(ages, bins = range(n))
    bins = range(n)


   #print indes
    data_indes = indes.argsort()

    timeslice = [[]for x in range(n)]
    k = 0

    for i in indes:
        #print k,i
        timeslice[i - 1].append(data[k])
        k += 1
    i = 0
    return timeslice
def create_elevation_plot(p):

    header, data = import_csv(p)
    cols = ['age', 'elevation', 'sample', 'latitude', 'longitude']
    index_dict = {}
    for c in cols:
        index_dict[c] = get_col_index(c, header)


    age_index = index_dict['age']
    lat_index = index_dict['latitude']
    long_index = index_dict['longitude']

    #n_a_e=[(s[name_index],float(s[age_index].split(' ')[0]),float(s[elev_index])) for s in data]
    ages = [float(s[age_index].split(' ')[0]) for s in data]
    lats = [float(s[lat_index]) for s in data]
    longs = [float(s[long_index]) for s in data]
    xmin = min(longs)
    xmax = max(longs)
    ymin = min(lats)
    ymax = max(lats)

    #build_polygon(lat_long_elev)
    ages = asarray(ages)
    timeslices = _time_slice(ages, data)
  #  build_polygon(timeslices[7],index_dict)


   # for t in timeslices:

    #t=timeslices[7]
    fig = figure()

    tag = ['121', '122', ]
    tag = ['331', '332', '333', '334',
         '335', '336', '337', '338', '339']
    tag.reverse()
    sh = False
    k = 0
    j = 0
    two_d = False
    #timeslices=[timeslices[6]]
    a = None
    for t in timeslices:
       # t=timeslices[i]
       # print t        
        x, y, z, xx, yy, zz = _plot(t, index_dict)
        if len(x) >= 1:
            if two_d or len(x) > 2:
                a = subplot(tag[k], wspace = 0)
#            for i in range(len(x)):
#                a.text(x[i],y[i],'df')
            #print k
#            a=subplot(tag[k],axisbg='red')


            #print r
#            ax=axes3d.Axes3D(fig,rect=r)
#            
#            ax.scatter(x, y, z,cmap=cm.jet)
#            
#            ax.plot(x,y,z)
#            ax.contourf3D(xx,yy,zz,20)
#            ax.contour3D(xx,yy,zz,20)
#            #print ax.get_xaxis().set_visible(False)
#            ax.set_xlim3d((min(x)-0.5,max(x)+0.5))
#            ax.set_ylim3d((min(y)-0.05,max(y)+0.05))

            if two_d:
                a.scatter(x, y)
                a.contour(xx, yy, zz)
                a.set_xlim(xmin, xmax)
                a.set_ylim(ymin, ymax)
            elif a is not None:
                r = a.get_position()
                a.get_xaxis().set_visible(False)
                a.get_yaxis().set_visible(False)
                ax = axes3d.Axes3D(fig, rect = r)
                ax.contourf3D(xx, yy, zz, 20)
                ax.scatter(x, y)
                ax.scatter(x, y, z)
                ax.set_xlim3d(xmin, xmax)
                ax.set_ylim3d(ymin, ymax)

#            a.set_xlim((min(x)-0.5,max(x)+0.5))
#            a.set_ylim((min(y)-0.05,max(y)+0.05))
          #  ax.plot_surface(xx,yy,zz,rstride=1, cstride=1,cmap=cm.jet)


            title('%s-%s Ma' % (j + 1, j))
            sh = True
            #break
            k += 1
        j += 1
    if sh:
        show()
def _plot(t, index_dict):
    t = sort(t, 0)
    long_index = index_dict['longitude']
    lat_index = index_dict['latitude']
    elev_index = index_dict['elevation']
    x = [float(s[long_index]) for s in t]
    y = [float(s[lat_index]) for s in t]
    z = [float(s[elev_index]) for s in t]
    n = 10.
#    cx=asarray(x).copy()
#    cy=asarray(y).copy()
#    cz=asarray(z).copy()
#    for i in range(1,len(x)-1):
#        lx=cx[i-1]
#        rx=cx[i]
#        ly=cy[i-1]
#        ry=cy[i]
#        lz=cz[i-1]
#        rz=cz[i]
#        for k in range(n):
#            x.insert(i-1,lx+(lx-rx)/n*k)
#            y.insert(i-1,ly+(ly-ry)/n*k)
#            z.insert(i-1,0)
#            

   # xy=[(float(s[long_index]),float(s[lat_index])) for s in t]
    xx, yy = meshgrid(x, y)
   # z=[[i]*len(x) for i in z]
    zz = diag(z)


#    r,c=zz.shape
#    zs=[]
#    xs=[]
#    ys=[]
#    zs.append(zz[0][0])
#    xs.append(xx[0][0])
#    ys.append(yy[0][0])
#    


#    for i in range(1,r-1):
#        for j in range(1,c-1):
#            
#           if i==j:
#               zz[i][j-1]=z1=zz[i][j]-150
#               zz[i][j+1]=z2=zz[i][j]-150
#               zs.append(z1)
#               zs.append(z2)
#               xs.append(xx[i][j-1])
#               xs.append(xx[i][j+1])
#               ys.append(yy[i][j-1])
#               ys.append(yy[i][j+1])
#    zs.append(zz[r-1][c-1])
#    xs.append(xx[r-1][c-1])
#    ys.append(yy[r-1][c-1]) 
    x, y, z = asarray(x), asarray(y), asarray(z)
    xx, yy, zz = asarray(xx), asarray(yy), asarray(zz)


    return x, y, z, xx, yy, zz
def main():
    p = os.getcwd()
    p = os.path.join(p, 'data', 'datedsamples07.csv')
    create_elevation_plot(p)
if __name__ == '__main__':
    main()
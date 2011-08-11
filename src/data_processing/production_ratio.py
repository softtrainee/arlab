#'''
#RossLabs 2009
#Ross  Jake Ross   jirhiker@gmail.com
#
#Oct 23, 2009
#'''
#
##=============enthought library imports=======================
#
##=============standard library imports ========================
##import uncertainties as un
#from uncertainties import ufloat
#
##=============local library imports  ==========================
#class ProductionRatio(object):
#    '''
#        G{classtree}
#    '''
#    ca3637 = ufloat((0.0, 0.0))
#    ca3837 = ufloat((0.0, 0.0))
#    ca3937 = ufloat((0.0, 0.0))
#    k3739 = ufloat((0.0, 0.0))
#    k3839 = ufloat((0.0, 0.0))
#    k4039 = ufloat((0.0, 0.0))
#    cl3638 = ufloat((0.0, 0.0))
#    cak = ufloat((0.0, 0.0))
#    clk = ufloat((0.0, 0.0))
#
#    def __init__(self, dbpr):
#        for item in dir(self):
#            if not item.startswith('_'):
#                nom = getattr(dbpr, item)
#                std = getattr(dbpr, '%ser' % item)
#                setattr(self, item, ufloat((nom, std)))

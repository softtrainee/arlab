'''
RossLabs 2009
Ross  Jake Ross   jirhiker@gmail.com

Nov 11, 2009
'''

#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
def folder(sn):
    return '''<Folder>
<name>%s</name>

    ''' % sn
def endfolder():
    return '</Folder>'
import kmldom
import os
def create_placemark(options):
    factory=kmldom.KmlFactory_GetFactory()
    pm=factory.CreatePlacemark()
    
    if options.has_key('name'):
        pm.set_name(options['name'])
    
    if options.has_key('lat') and options.has_key('lng'):
        coordinates=factory.CreateCoordinates()
        lat=options['lat']
        lng=options['lng']
        coordinates.add_latlng(lat,lng)
        
        point=factory.CreatePoint()
        point.set_coordinates(coordinates)
        
        pm.set_geometry(point)
       
        
       
    return pm

def main():
    factory=kmldom.KmlFactory_GetFactory()
    document =factory.CreateDocument()
    
    options=dict(name='helooplacemark',
                 lat=1,
                 lng=1)
    pm=create_placemark(options)
    document.add_feature(pm)
    
    icon = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
    style=factory.CreateStyle()
    
    kml= factory.CreateKml()
    kml.set_feature(document)
    
    base='/Users/Ross/Programming/Geotools/data/geotools_output_%03i.kml'
    i=1
    
    while os.path.isfile(base%i):
        i+=1
        
    outpath=base%i
    outfile=open(outpath,'w')
    
    kmltext=kmldom.SerializePretty(kml)
    for line in kmltext.split('\n'):
        outfile.write(line+'\n')
        
    outfile.close()
if __name__ == '__main__':
    
    main()
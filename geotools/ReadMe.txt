READ ME

Welcome to KML Writer
Jake Ross 2009
jirhiker@gmail.com
NMGRL

A simple script to create customizable kml files for Google Earth from a text (csv) file 

Source Files:
    source files must be comma separated value (csv) files
    the first line in the file should be a header ie column name
    
    sources files need at least the 3 following columns
    Name,Latitude,Longitude

    !PLUS-MINUS NOTE!
    use +/- or +- instead of ±

    !COMMA NOTE!
    keep commas out off columns
    
TIP:
    if you do not know a value to enter simple hit return
    
    return after >> will yield the default value
    
    !WILL NOT WORK FOR SOURCE FILES!
    currently source files must be located in the source directory
    and are the only files the you need to specify during configuration
    
see Jake for help

Install:
	get the source code from Jake
	
	unzip kmlwriter.zip to a directory  (/kmlrwiter)
	kmlwriter.zip contains
		     kmlwriter.py - the main scripy
		     src - directory containing helper coder
	
Run:
	add your source files to a source directory 
	should be the directoy where kmlwriter.py is installed (/kmlwriter)
	
	in the Terminal cd to the install directory 
	>> cd /kmlwriter

	run the script
	>> python kmlwriter.py  

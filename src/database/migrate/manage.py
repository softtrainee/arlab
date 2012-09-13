#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':

#    main(url='sqlite:////usr/local/pychron/isotope.sqlite', debug='False', repository='isotopedb/')


#    p = '/Users/ross/Pychrondata_experiment/data/isotopedb.sqlite'
    #p = '/usr/local/pychron/isotope.sqlite
#    p = '/Users/ross/Sandbox/pychron_test_data/data/isotopedb.sqlite'
#    main(url='sqlite:///{}'.format(p) , debug='False', repository='isotopedb/')

    url = 'mysql://root:Argon@localhost/isotopedb?connect_timeout=3'
    main(url=url , debug='False', repository='isotopedb/')

#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='sqlite:////usr/local/pychron/isotope.sqlite', debug='False', repository='isotopedb/')

#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='mysql://root:Argon@localhost/co2laserdb', debug='False', repository='co2laserdb/')

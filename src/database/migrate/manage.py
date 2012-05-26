#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
#    main(url='sqlite:////usr/local/pychron/device_scans.db', debug='False', repository='device_scans')
#    main(url='sqlite:////Users/ross/Sandbox/device_scans.sqlite', debug='False', repository='device_scans')
#    main(url='sqlite:////usr/local/pychron/device_scans/scans.sqlite', debug='False', repository='device_scans')
#	main(url='sqlite:////usr/local/pychron/bakeoutdb/bakeouts.sqlite', debug='False', repository='bakeoutdb')
	main(url='sqlite:////usr/local/pychron/co2.sqlite', debug='False', repository='co2laserdb')
#	main(url='sqlite:////Users/ross/Sandbox/co2.sqlite', debug='False', repository='co2laserdb')

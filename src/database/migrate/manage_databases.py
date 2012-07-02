#!/usr/bin/env python
from migrate.versioning.api import test, version_control, upgrade, version
from migrate.exceptions import DatabaseAlreadyControlledError, KnownError
import os



if __name__ == '__main__':

	root = '/usr/local/pychron'
	dbs = [
#		('{}/co2.sqlite', 'co2laserdb'),
#		('{}/bakeoutdb/bakeouts.sqlite', 'bakeoutdb'),
		('{}/device_scans/device_scans.sqlite', 'device_scans'),
		('{}/diode.sqlite','diodelaserdb')
		]

#	root = '/Users/ross/Sandbox/sqlite'
#	dbs = [
#		('{}/co2.sqlite', 'co2laserdb'),
#		('{}/bakeouts.sqlite', 'bakeoutdb'),
#		('{}/device_scans.sqlite', 'device_scans'),
#
#		]

	for url, repo in dbs:
		url = url.format(root)

		b = os.path.split(url)[0]
		if not os.path.isdir(b):
			os.mkdir(b)
		url = 'sqlite:///{}'.format(url)

		print url
		try:
			version_control(url, repo)
		except DatabaseAlreadyControlledError:
			pass

#		print version(repo)
		n = version(repo)
		for i in range(n + 1):
			try:
				upgrade(url, repo, version=i)
				print 'upgrading {} to {}'.format(repo, i)
			except KnownError:
				pass
		#test(url, repo)
		#upgrade(url, repo)


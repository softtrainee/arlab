#!/usr/bin/env python
from migrate.versioning.shell import main
main(url = 'mysql://root:Argon@localhost/pychrondb_beta', debug = 'False', repository = './pychrondb_beta/')

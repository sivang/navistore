#!/usr/bin/env python
import common
import unittest
import time
import os
import testNavistoreBackend
from navistore.backend.nsqlite import SqliteStorageBackend

"""
This module is used to contain all the backend tests.

To implement a new backend, just subclass StorageBackendTest,
add your setup and teardown logic and iterate through
implementation and testing until the test completes with SUCCESS.

If your backend requires special considerations for things like
in memory processing and syncing, override the test method from
the base StorageBackendTestCase , add your special care, and
then execute the parent's method for the actual logic test.

"""

SQLITE_STORE = common.TESTS_OUTPUT_PATH + common.SQLITE_DB_FILE

class SqliteStorageBackendTestCase(testNavistoreBackend.StorageBackendTestCase):
	"""
	Just provide the neccessary setup and teardown required to have
	the store ready for compliance test by the generic backend test.

	We override the test_loadstore since we need to explicitly
	sync a connection before destorying or recreating it, in order
	to persist still in memory data to disk.

	And this is exactly what we do in setUp, reassigning
	a new backend object to the self.store reference which
	wipes out the previous object with all its state data.

	"""
	store = None
	def setUp(self):
		"""
		create a backend object that allows us
		to interact with the key value storage
		"""
		self.store = SqliteStorageBackend(SQLITE_STORE)
	def tearDown(self):
		os.unlink(SQLITE_STORE)
	def test_loadstore(self):
		# this also tests the SqliteStorageBackend.sync 
		# propery is working properly, and also shows
		# one of the possible uses for force commit.
		self.store.sync = True
		super(SqliteStorageBackendTestCase, self).test_loadstore()
		self.store.sync = False


if __name__ == '__main__':
	unittest.main()

	

class StorageBackend(object):
	"""
	This an abstract class that defines the the 
	interface that different storage backends
	need to implement to be used in Navistore.
	
	Navistore HTTP layer uses the methods defined here
	to cater for the actual saving of values by keys.
	E.g. Navistore does not know and should know nothing about
	either disk, database backends or anything of the sort. 
	It delegates the task of the actual physical saving
	of data to the underlying backend.
	"""
	def __init__(self):
		"""
		Any required initialization shold go
		here.

		If the backend failed to initialize its
		environment like files, dirs, services
		this method should throw an expection
		with appropriate error.
		"""
	def listkeys(self):
		"""
		Logic to list all the keys
		that are currently in the store.

		Should return a Python list populated
		with the keys.
		"""
	def haskey(self, key):
		"""
		Return True if key is in store,
		False otherwise.
		"""
	def save(self, key, value):
		"""
		Logic to store the value held by
		'value' into the store, to be accessible
		through the 'key' key.

		Just returnes on success, should raise
		a storage backend exception otherwise.
		"""
	def get(self, key):
		"""
		Returns the value referenced by
		the key 'key'
		"""
	def delete(self, key, getvalue=False):
		"""
		Delete a value from the store by the
		key 'key'.

		If getvalue is True, return the deleted
		value prior to deleting it.

		Returns True if succeded, False otherwise.
		"""
	def close(self):
		"""
		If your backend needs to do something to persist
		data when its process ends, add it here.

		For example, finishing transactions, writing in memory
		data to disk etc.

		Should not return anything but rather raise an exception
		if the action failed.
		"""

	

import iface
import sqlite3
import os

class SqliteStorageBackend(iface.StorageBackend):
	"""
	This class implements the Navistore backend interface and provides 
	support for storing data via sqlite3.

	sqlite and its corrosponding python bindings
	need to be installed on the system.

	Please note that in order to increase performance
	the default operation mode is to rely on sqlite3's
	default commit model, as explained here:
	- http://docs.python.org/library/sqlite3.html#sqlite3-controlling-transactions

	For more reliable, but slower operation (this is always a trade off)
	set sync = True on the backend object after instantiation.

	This will cause a commit to be made for every save() and delete()
	call and will ensure data consistency even across power failures,
	unless ofcourse the failure happens while the file is being written.
	"""
	storepath = None
	conn = None
	cursor = None
	sync = False
	def __init__(self, storepath=None):
		if not storepath:
			self.storepath = "./navistore.db"
		else:
			self.storepath = storepath
		self.conn = sqlite3.connect(self.storepath)
		self.cursor = self.conn.cursor()
		r = self.cursor.execute("select type from SQLITE_MASTER where name='navistore'")
		if r.fetchone():
			pass
		else:
			# create the table only if it does not exist already
			self.cursor.execute('''create table navistore(key text, value text)''')
		self.sync and self.conn.commit()
	def listkeys(self, max=None):
		l = []
		c = self.cursor.execute("select key from navistore")
		for i in c.fetchall():
			l.append(str(i[0]))
		return l
	def haskey(self, key):
		c = self.cursor.execute("select key from navistore")
		return ((key,) in c)
	def save(self, key, value):
		try:
			self.get(key)
		except KeyError:
			self.cursor.execute('insert into navistore values (?,?)', (key, value))
		else:
			self.cursor.execute("update navistore set value=? where key=?", (value, key))
		self.sync and self.conn.commit()
	def get(self, key):
		c = self.cursor.execute("select value from navistore where key=?", (key,))
		value = c.fetchone()
		if not value:
			raise KeyError, "No such key in the store."
		return value[0]
	def delete(self, key, getvalue=False):
		c = self.cursor.execute("select value from navistore where key=?", (key,))
		value = c.fetchone()
		if not value:
			raise KeyError, "No such key in the store."
		self.cursor.execute("delete from navistore where key=?", (key,))
		self.sync and self.conn.commit()
		return value[0]
	def reset(self):
		c = self.cursor.execute("delete from navistore")
		self.conn.commit()
	def close(self):
		"""
		Documentation of sqlite tells us we must explicitly call commit
		to commit last transaction before closing the connection, or
		otherwise changes will be lost
		"""
		self.conn.commit()
		self.conn.close()

		


	

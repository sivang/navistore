#!/usr/bin/env python

import os, sys, time, signal


def demonize(pidfile, server_start_func, *args):
	"""
	Try to demonize the current process.
	If there was a failure writing the pid file,
	exit and stop execution to prevent demonizing
	without knowing the pid of the daemon.

	If extra argument need to be passed to the 
	server_start_func, pass them through the 
	*args variable length argument array.
	"""
	pid = os.fork()
	if not pid:
		otherpid = os.fork()
		if not otherpid:
			ppid = os.getppid()
			try:
				server_start_func(*args)
			except Exception, e:
				print "Failed to start: ", str(e.args)
				os._exit(1)
			while ppid != 1:
				time.sleep(0.5)
				ppid = os.getppid()
			return
		else:
			status = None
			time.sleep(1)
			status = os.waitpid(otherpid, os.WIFEXITED(1) | os.WNOHANG)
			if status[1]:
				print "daemon exited with error 1"
				os._exit(1)
			else:
				try:
					# create a pid file for user with start-stop-daemon.
					f = file(pidfile, 'w')
					f.write(str(otherpid))
					f.close()
				except Exception, e:
					print "Cannot create pidfile: ", str(e.args)
					os.kill(otherpid, signal.SIGTERM)
					os._exit(1)
				os._exit(0)
	else:
		status = os.wait()
		if status[1]:
			sys.exit(1)
		else:
			sys.exit(0)


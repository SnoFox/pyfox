# Copyright (C) David B. Dixon II 2012
import sparks

import signal
import os
import sys

from confparser import confparser

def on_sigint(signum, frame):
	sys.exit(os.EX_OK)

def main():
	# Grab configurations
	config = confparser('servers.conf')

	# Basic Setup
	signal.signal(signal.SIGINT, on_sigint)
	
	for s in config.sections_list():
		server = config.get_section(s)

		server['name'] = s
		server['admins'] = [] if 'admins' not in server else server['admins'].split(',')

		if not server['triggers']:
			print('Network triggers have not been setup for %s. Stopping!' % server['name'])
			exit()

		server['triggers'] = server['triggers'].split(',', 1)

		if len(server['triggers']) != 2:
			print('Triggers have not been setup correctly for %s. Stopping!' % server['name'])
			exit()

		sparks.newClient(server)

	# Fork Background Stolen from Skyakdar! Thank you dKingston
	# PROTIP: This might not work.... 
	if '-bg' in sys.argv:
		try:
			pid = os.fork()
		except OSError as e:
			print e.errno, e.strerror
	
		# This is the child process.
		if pid == 0:
			os.setsid()
	
			# Now the child fork()'s a child in order to prevent
			# acquisition of a controlling terminal.
			try:
				pid = os.fork()
			except OSError as e:
				print e.errno, e.strerror
	
			# This is the second child process.
			if pid == 0:
				os.chdir(os.getcwd())
				os.umask(0)

			# This is the first child.
			else:
				print 'Running dbbot in background mode [%s] (%s)' % (pid, os.getcwd())
				os._exit(0)
		else:
			os._exit(0)
	
		# Try to write the pid file.
		try:
			pid_file = open('dbbot.pid', 'w')
			pid_file.write(str(os.getpid()))
			pid_file.close()
		except IOError as e:
			print >> sys.stderr, 'Unable to write PID to %s: %s.' % (os.getpid(), os.strerror(e.args[0]))
	
		# Try to close all open file descriptors.
		# If we can't find the max number, just close
		# the first 256.
		try:	    
			maxfd = os.sysconf('SC_OPEN_MAX')
		except (AttributeError, ValueError):
			maxfd = 256
		
		for fd in range(0, maxfd):
			try:		
				os.close(fd)    
			except OSError:
				pass
		    
		# Redirect the standard file descriptors to /dev/null.
		os.open('/dev/null', os.O_RDONLY)		     
		os.open('/dev/null', os.O_RDWR)  
		os.open('/dev/null', os.O_RDWR)

	sparks.loop()

if __name__ == '__main__':
	main()

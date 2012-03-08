# Copyright (C) David B. Dixon II 2012
import sparks
import modules

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

	sparks.loop()

if __name__ == '__main__':
	main()

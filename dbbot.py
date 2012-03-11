# Copyright (C) David B. Dixon II 2012
import sparks

import signal
import os
import sys
import yaml

def on_sigint(signum, frame):
	sys.exit(os.EX_OK)

def main():
	# Grab configurations
	config = yaml.load(open('servers.conf'))

	# Basic Setup
	signal.signal(signal.SIGINT, on_sigint)

	if len(sys.argv) == 2: # Connect to a specific network
		for name, conf in config.items():
			if name == sys.argv[1]:

				conf['name'] = name
				conf['admins'] = [] if 'admins' not in conf else conf['admins'].split(',')

				if not conf['triggers']:
					print('Network triggers have not been setup for %s. Stopping!' % conf['name'])
					exit()

				conf['triggers'] = conf['triggers'].split(',', 1)

				if len(conf['triggers']) != 2:
					print('Triggers have not been setup correctly for %s. Stopping!' % conf['name'])
					exit()

				sparks.newClient(conf)

	else:
		for name, conf in config.items():

			conf['name'] = name
			conf['admins'] = [] if 'admins' not in conf else conf['admins'].split(',')

			if not conf['triggers']:
				print('Network triggers have not been setup for %s. Stopping!' % conf['name'])
				exit()

			conf['triggers'] = conf['triggers'].split(',', 1)

			if len(conf['triggers']) != 2:
				print('Triggers have not been setup correctly for %s. Stopping!' % conf['name'])
				exit()

			sparks.newClient(conf)

	sparks.loop()

if __name__ == '__main__':
	main()

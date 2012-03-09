# Copyright (C) David B. Dixon II 2012
# IRC module

import modules
import asyncore
import socket
import re

from modules import dbmods as mods
from time import sleep, time
from thread import start_new_thread as threader

class newClient(asyncore.dispatcher):
	# Let's make everything overly complicated! Not...
	# Yes, no twisted. Suck it #python.

	def __init__(self, config):
		asyncore.dispatcher.__init__(self)

		self.config = config
		self.received = None
		self.buffer = []
		self.hang = 0

		self.cl = {}

		# In a nutshell, Get a list of IPs for that domain and connect to it.
		socket_data = socket.getaddrinfo(self.config['server'], int(self.config['port']), 0, 1)[0]
		self.create_socket(socket_data[0], socket_data[1])
		self.connect(socket_data[4])

		# Does the network need a password in order to connect?
		if 'serverpass' in self.config:
			self.push('PASS %s' % self.config['serverpass'])

	def handle_connect(self):
		self.push('NICK %s' % self.config['nick'])
		self.push('USER %s 0 0 :dbbot written by dbdii407' % self.config['nick'])

		# Start the pinging process!
		threader(self.handle_check, ())

	def handle_close(self):
		pass

	def handle_write(self):
		for line in self.buffer:
			try:
				sent = self.send(line)

			except socket.error as e:
				self.close()
				break

			if sent < len(line):
				print('Sent number lower than intended (%s/%s)' % (sent, len(line)))

		self.buffer = []

	def handle_read(self):
		try:
			data = self.recv(4096)

		except socket.error:
			data = None

		if not data:
			return

		if self.received:
			data = self.received + data
			self.received = None

		if not data.endswith('\r\n'):
			self.received = data

		else:
			for line in data.split('\r\n'):
				if line != '':
					print line

					line = [q for q in line.split(' ') if q != '']

					if line[0] == 'PING':
						self.push('PONG %s' % line[1])

					if line[1] == 'PONG':
						self.hang -= 1

					if line[1] == 'PRIVMSG': # What we need! Finally.
						client = re.split(':(.*)!(.*)@(.*)', line[0])

						if client:
							if line[2].startswith('#'): # Channel
								command = line[3].strip(':')
								params = line[4:]

								if len(command) > 1:
									trigger = command[0]

									if trigger in self.config['triggers']:
										if trigger == self.config['triggers'][0] and client[3] in self.config['admins']: # Admin trigger
											for mod in modules.dbmods:
												if hasattr(mod, 'ca_%s' % command[1:]):
													cmd = getattr(mod, 'ca_%s' % command[1:])
													cmd(self, client, line[2], params)

										elif trigger == self.config['triggers'][1]: # Public trigger
											for mod in modules.dbmods:
												if hasattr(mod, 'cp_%s' % command[1:]):
													cmd = getattr(mod, 'cp_%s' % command[1:])
													cmd(self, client, line[2], params)

							else: # Private Message
								pass

						else: # Server
							pass

					for mod in modules.dbmods:
						if hasattr(mod, 'sr_%s' % line[1].lower()):
							cmd = getattr(mod, 'sr_%s' % line[1].lower())
							cmd(self, line[2:])

	def handle_check(self):
		while True:
			if self.hang == None:
				# Something quit the process. Stop the cycle.
				break

			elif self.hang == 11:
				# We're no longer here....
				self.handle_close()
				break

			else:
				self.push('PING %s' % int(time()))
				self.hang += 1
				sleep(25)

	def handle_error(self):
		raise


	def writable(self):
		return len(self.buffer) > 0

	# Extra stuff!

	def push(self, line):
		self.buffer.append("%s\r\n" % line)

	def privmsg(self, location, line):
		self.push('PRIVMSG %s :%s' % (location, line))

	def notice(self, location, line):
		self.push('NOTICE %s :%s' % (location, line))

	def join(self, channel):
		self.push('JOIN %s' % channel)

	def part(self, channel):
		self.push('PART %s' % channel)

def loop():
	while True:
		if len(asyncore.socket_map) == 0:
			sleep(1)
		else:
			asyncore.poll(1)

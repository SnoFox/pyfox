# Copyright (C) David B. Dixon II 2012

import modules
import asyncore
import socket

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
		self.push('USER %s 0 0 :%s' % (self.config['nick'],self.config['realname']) )

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

					if not line[0].startswith( ':' ):
						# Direct stuff (ping/pong/my quit/error)
						if line[0] == 'PING':
							self.push('PONG %s' % line[1])
							continue

						if line[1] == 'PONG':
							self.hang -= 1
					else:	
						# "relayed" (actual IRC stuff)
						source = line[0][1:]
						command = line[1]
						target = line[2]
						params = line[3:]
						
						if len( params ) > 0:
							# Check for param-less cmds >.<
							if params[0].startswith( ':' ):
								# Strip the leading colon here instead of in a thousand
								# other places in the code...
								params[0] = params[0][1:]

						# Server or user-sourced? Also, give it an ident@address
						client = source.split( '!', 2 )
						if len( client ) < 2:
							# server sourced; set a fake address, I guess?
							client.append( '<server>' )
						else:
							# user-sourced; add their address to the client[] list
							address = client[1].split( '@', 2 )
							client[1] = address[0]
							client.append( address[1] )
							# totally saving about .2ms here
							del address

						if command == 'PRIVMSG': # What we need! Finally.
							#:SnoFox!~SnoFox@is.in-addr.arpa PRIVMSG #ext3 :Kiba ftw! :'D

							try:
								if target[0] in self.isupport['CHANTYPES']:
									chanmsg = True
								else:
									chanmsg = False
							except NameError:
								print "ERROR: Got a PRIVMSG before proper registration. Go slap the server dev. :("
								print "       We need the RPL_ISUPPORT numeric (005) with the CHANTYPES value to"
								print "       properly handle channel messages."
								chanmsg = False

							if chanmsg:
								botCmd = params[0]
								params = params[1:]


								if len(botCmd) > 1:
									trigger = botCmd[0]


									if trigger in self.config['triggers']:
										print "Searching cmds..."
										if trigger == self.config['triggers'][0] and client[2] in self.config['admins']: # Admin trigger
											for mod in modules.dbmods:
												if hasattr(mod, 'tca_%s' % botCmd[1:]):
													cmd = getattr(mod, 'tca_%s' % botCmd[1:])
													threader(cmd, (self, client, target, params))
												elif hasattr(mod, 'ca_%s' % botCmd[1:]):
													cmd = getattr(mod, 'ca_%s' % botCmd[1:])
													cmd(self, client, target, params)

										elif trigger == self.config['triggers'][1]: # Public trigger
											for mod in modules.dbmods:
												if hasattr(mod, 'tcp_%s' % botCmd[1:]):
													cmd = getattr(mod, 'tcp_%s' % botCmd[1:])
													threader(cmd, (self, client, target, params))
												elif hasattr(mod, 'cp_%s' % botCmd[1:]):
													cmd = getattr(mod, 'cp_%s' % botCmd[1:])
													cmd(self, client, target, params)

							else: # Private Message
								botCmd = params[1]
								params = params[2:]

								if botCmd.startswith(self.config['triggers'][0]):
									if client[2] in self.config['admins']: # Admin trigger

										for mod in modules.dbmods:
											if hasattr(mod, 'tpa_%s' % botCmd[1:]):
												cmd = getattr(mod, 'tpa_%s' % botCmd[1:])
												threader(cmd, (self, client, params))
											elif hasattr(mod, 'pa_%s' % botCmd[1:]):
												cmd = getattr(mod, 'pa_%s' % botCmd[1:])
												cmd(self, client, params)

								else: # Public Private Commands don't require a trigger.
									for mod in modules.dbmods:
										if hasattr(mod, 'tpp_%s' % botCmd):
											cmd = getattr(mod, 'tpp_%s' % botCmd)
											threader(cmd, (self, client, params))
										elif hasattr(mod, 'pp_%s' % botCmd):
											cmd = getattr(mod, 'pp_%s' % botCmd)
											cmd(self, client, params)

						for mod in modules.dbmods:

							if hasattr(mod, 'tsr_%s' % command.lower() ):
								cmd = getattr(mod, 'tsr_%s' % command.lower())
								threader(cmd, (self, client, line[2:]))
							elif hasattr(mod, 'sr_%s' % command.lower()):
								cmd = getattr(mod, 'sr_%s' % command.lower())
								cmd(self, client, line[2:])

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

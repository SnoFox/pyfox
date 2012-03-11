# This file is basic for dbbot
from re import search
from time import sleep

def tsr_001(irc, params):
	# Nick Authentication
	auth = irc.config['modules']['auth']

	if 'nick' in auth: # Authenticate using a nick
		if type(auth['nick']) == bool:
			irc.privmsg(auth['service'], "%s %s %s" % (auth['command'], self.config['nick'], auth['password']))
		else:
			irc.privmsg(auth['service'], "%s %s %s" % (auth['command'], auth['nick'], auth['password']))

	else:
		irc.privmsg(auth['service'], "%s %s" % (auth['command'], auth['password']))

	# Join channels
	channels = irc.config['modules']['join']

	sleep(1)

	irc.join(channels)

def sr_005(irc, params):
	# Find all the modes!

	line = ' '.join(params) if 'PREFIX' in ' '.join(params) else None

	if line:

		rprefix = search('PREFIX=\(([^)]+)\)([^ ]+)', line).groups()
		irc.statusmodes = dict(zip(rprefix[1], rprefix[0]))

def sr_353(irc, params):
	# Create a nicklist for each channel
	if not hasattr(irc, 'chanlists'):
		irc.chanlists = {}

	# Coded by _habnabit #python Freenode. Greatly appreciated!
	ret = {}
	ret2 = {}

	for nick in params[3:]:
		nick = nick.lstrip(':')
		nick_modes = []

		for e, char in enumerate(nick):
			if char not in irc.statusmodes:
				ret[nick[e:]] = nick_modes
				break

			nick_modes.append(irc.statusmodes[char])

	for r in ret:
		ret2[r] = ''.join(ret[r])

	irc.chanlists[params[2]] = ret2

def sr_part(irc, params):
	if params[0].startswith(':'):
		params[0] = params[0][1:]

	irc.push("NAMES %s" % params[0])

def sr_join(irc, params):
	if params[0].startswith(':'):
		params[0] = params[0][1:]

	irc.push("NAMES %s" % params[0])

def sr_mode(irc, params):
	if params[0].startswith(':'):
		params[0] = params[0][1:]

	irc.push("NAMES %s" % params[0])

def ca_chanlist(irc, client, channel, params):
	irc.privmsg(channel, irc.chanlists[channel])

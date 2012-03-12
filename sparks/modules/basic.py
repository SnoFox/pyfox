# This file is basic for dbbot
from re import search # needs regex for dbdii's prefix "sorter"
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
    # 005 parser by SnoFox <SnoFox@SnoFox.net>
	if not hasattr( irc, 'statusmodes' ):
		# Set some default so dbbot dosen't crash
		irc.statusmodes = dict( zip('@+', 'ov') )

	if not hasattr( irc, 'isupport' ):
		# Create the initial dict so we can update it later
		irc.isupport = dict()
	
	params.pop(0) # remove the nickname from params

	x = 0;
	while x < 5:
		# literally "hack" off ":are supported by this server"
		# Will break on broken, non-RFC-following servers
		params.pop()
		x += 1

	# Iterate through the list
	for isupport in params:
		feature = isupport.split( '=', 2 )
		if len(feature) < 2:
			value = None
		else:
			value = feature[1]
		irc.isupport.update( { feature[0]: value } )

		# ok; now utilize some awesome ones for the core
		if feature[0] == "PREFIX":
			# Dave's original code, modified to work here
			rprefix = search('\(([^)]+)\)([^ ]+)', value).groups()
			irc.statusmodes = dict(zip(rprefix[1], rprefix[0]))

		if feature[0] == "CHANMODES":
			# CHANMODES=eIbq,k,flj,CEFGJKLMOPQSTcdgimnprstz
			# refer to Atheme's technical document "MODES" for more info
			# on how modes are classified here
			# http://git.atheme.org/atheme/tree/doc/technical/MODES?id=atheme-services-7.0.0-alpha14
			# A: listmodes
			# B: parameter when set/unset
			# C: parameter only when set
			# D: no param
			# E: prefix mode (not dealt with here)

			# indecies of the list:
			# 0 = A, 1 = B, 2 = C, 3 = D
			tmpList = [] # temporary list for the loop below
			tmpList.insert( 0, [] ) # give it a blank list to modify
			onType = 0 # the index of tmpList we're modifying atm

			for char in value:
				if char == ",":
					# Comma is the type delimiter; next!
					onType += 1
					tmpList.insert( onType, [] ) # Create a new blank list in there to modify
				else:
					# Add the letter to the current list type
					tmpList[onType].append( char )
			# } for char in value

			# take all the data out of the temporary list and put it in global areas
			irc.listmodes = tmpList[0]
			irc.typebmodes = tmpList[1]
			irc.typecmodes = tmpList[2]
			irc.flagmodes = tmpList[3]
	# } for isupport in params
# } def sr_005


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

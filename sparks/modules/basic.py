# This file is basic for dbbot
from re import search # needs regex for dbdii's prefix "sorter"
from time import sleep
from sparks.modules import dbmods # required to emit events from the mode parser

def tsr_001(irc, client, params):
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

def sr_005(irc, client, params):
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
		print "pop %d" % x
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
			# PREFIX=(aohv)!@%+
			# Dave's original code, modified to work here
			rprefix = search('\(([^)]+)\)([^ ]+)', value).groups()
			irc.statusmodes = dict(zip(rprefix[1], rprefix[0]))
			irc.typeemodes = rprefix[0] # stick the letters in a list 
										# because I can't figure out how
										# to iterate through a dict's values
										# efficiently - SnoFox

		if feature[0] == "CHANMODES":
			# CHANMODES=eIbq,k,flj,CEFGJKLMOPQSTcdgimnprstz
			# refer to Atheme's technical document "MODES" for more info
			# on how modes are classified here
			# http://git.atheme.org/atheme/tree/doc/technical/MODES?id=atheme-services-7.0.0-alpha14
			# A: listmodes
			# B: parameter when set/unset
			# C: parameter only when set
			# D: no param (flagmodes)
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


def sr_353(irc, client, params):
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

def sr_part(irc, client, params):
	irc.push("NAMES %s" % params[0])

def sr_join(irc, client, params):
	irc.push("NAMES %s" % params[0])

def sr_mode(irc, client, params):
	irc.push("NAMES %s" % params[0])

	target = params[0]
	# Mode parser
	# Sends out mode events for other modules to use
	# - SnoFox

	#print "sr_mode(): params = %s" % params
	#sr_mode(): params = ['#foxtest', '-kCT', '*']
	
	# First of all, channel mode or user mode?

	if target[0] in irc.isupport['CHANTYPES']:
		chmode = True 
	else:
		chmode = False
	
	adding = True # true = adding a mode; false = removing
	paramNum = 2  # count of which param we're using 
				  # This starts at 2 due to Sparks' garbage in the params list :\

	# XXX: This will crash the bot if the IRCd lied to us in the 005 version string
	# then later sends us a mode line that doesn't agree with our knowledge of modes
	# That ... Should probably be fixed.
	for char in params[1]:
		# Are we adding or subtracting the mode?
		if char == '+':
			adding = True
		elif char == '-':
			adding = False
		else:
			param = None
			if chmode:
				# Check to see what kind of mode this is
				if char in irc.typeemodes or char in irc.listmodes or char in irc.typebmodes or (char in irc.typecmodes and adding):
					# These types of modes have params
					# Launch events! Woo!
					for n, mod in enumerate(dbmods):
						# Dunno what the tsr_ events are for; let's not emit them to save another .2ms
						# (for now)
						#if hasattr(mod, 'tsr_%s' % command.lower() ):
						#	cmd = getattr(mod, 'tsr_%s' % command.lower())
						#	threader(cmd, (self, client, params))
						if hasattr( mod, 'sr_chmode_%s' % char ):
							cmd = getattr( mod, 'sr_chmode_%s' % char )
							cmd( irc, client, target, adding, params[paramNum] )
					paramNum += 1
					continue
				else:
					# This is a letter, hopefully, or at least a mode.
					# Fire off an event for it
					for n, mod in enumerate(dbmods):
						if hasattr( mod, 'sr_chmode_%s' % char ):
							cmd = getattr( mod, 'sr_chmode_%s' % char )
							cmd( irc, client, target, adding, None )
			else:
				# Usermode get
				print "Got user mode %s. Not a fuck was given that modeline." % char





def ca_chanlist(irc, client, channel, params):
	irc.privmsg(channel, irc.chanlists[channel])

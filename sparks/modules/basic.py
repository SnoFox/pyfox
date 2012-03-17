# This file is basic for dbbot
from re import search # needs regex for dbdii's prefix "sorter"
from time import sleep
from sparks.modules import dbmods # required to emit events from the mode parser

# Helper functions
def ircStrCmp( irc, str1, str2 ):
	casemap = 'rfc1459'
	if hasattr( irc, 'isupport' ):
		if 'CASEMAPPING' in irc.isupport:
			casemap = irc.isupport[ 'CASEMAPPING' ]

	''' # To add more supported casemaps:
		if casemap == 'blah':
			doStuff
		elif casemap == 'blah2':
			doOtherStuff
		else
			print "Error: Unknown casemap %s used on network %s; defaulting to rfc1459" % ( irc.isupport['CASEMAPPING'], irc.name )
			casemap = rfc1459
	'''
	if casemap == 'rfc1459':
		'''
			"Because of IRC's scandanavian origin, the characters {}| are considered to be the lower case equivalents
			 of the characters []\, respectively. This is a critical issue when determining the equivalence of two nicknames."
				 -- rfc1459
		'''
		str1 = str1.replace( '[', '{' )
		str1 = str1.replace( ']', '}' )
		str1 = str1.replace( '\\', '|' )
		str2 = str2.replace( '[', '{' )
		str2 = str2.replace( ']', '}' )
		str2 = str2.replace( '\\', '|' )

		str1 = str1.lower()
		str2 = str2.lower()

	if str1 == str2:
		return True

	return False

def ircStrLower( irc, string ):
	casemap = 'rfc1459'
	if hasattr( irc, 'isupport' ):
		if 'CASEMAPPING' in irc.isupport:
			casemap = irc.isupport[ 'CASEMAPPING' ]

	if casemap == 'rfc1459':
		string = string.replace( '[', '{' )
		string = string.replace( ']', '}' )
		string = string.replace( '\\', '|' )
		str1 = str1.lower()
		str2 = str2.lower()

	return string


# directly related to IRC
def tsr_001(irc, client, target, params):
	# Nick Authentication
	auth = irc.modconf['auth']

	if 'nick' in auth: # Authenticate using a nick
		if type(auth['nick']) == bool:
			irc.privmsg(auth['service'], "%s %s %s" % (auth['command'], self.config['nick'], auth['password']))
		else:
			irc.privmsg(auth['service'], "%s %s %s" % (auth['command'], auth['nick'], auth['password']))

	else:
		irc.privmsg(auth['service'], "%s %s" % (auth['command'], auth['password']))

	# Join channels
	channels = irc.modconf['join']

	sleep(1)

	irc.join(channels)

def sr_005(irc, client, target, params):
    # 005 parser by SnoFox <SnoFox@SnoFox.net>
	if not hasattr( irc, 'statusmodes' ):
		# Set some default so dbbot dosen't crash
		irc.statusmodes = dict( zip('@+', 'ov') )

	if not hasattr( irc, 'isupport' ):
		# Create the initial dict so we can update it later
		irc.isupport = dict()
	
	# params.pop(0) # remove the nickname from params

	# Remove ":Are supported by this server
	params = ' '.join(params).rpartition( ':' )
	params = params[0].split( ' ' )

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


def sr_353(irc, client, target, params):
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

def sr_part(irc, client, target, params):
	irc.push("NAMES %s" % target)

def sr_join(irc, client, target, params):
	irc.push("NAMES %s" % target)

def sr_mode(irc, client, target, params):
	# Mode parser
	# Sends out mode events for other modules to use
	# - SnoFox

	if target[0] in irc.isupport['CHANTYPES']:
		irc.push("NAMES %s" % target)
		chmode = True 
	else:
		chmode = False
	
	adding = True # true = adding a mode; false = removing
	paramNum = 1  # count of which param we're using 

	# XXX: This will crash the bot if the IRCd lied to us in the 005 version string
	# then later sends us a mode line that doesn't agree with our knowledge of modes
	# That ... Should probably be fixed.
	for char in params[0]:
		if char == '+':
			adding = True
		elif char == '-':
			adding = False
		else:
			param = None

			if chmode:
				if char in irc.typeemodes or char in irc.listmodes or char in irc.typebmodes or (char in irc.typecmodes and adding):
					for n, mod in enumerate(dbmods):
						if hasattr( mod, 'sr_chmode_%s' % char ):
							cmd = getattr( mod, 'sr_chmode_%s' % char )
							cmd( irc, client, target, adding, params[paramNum] )

					paramNum += 1
					continue
				else:
					for n, mod in enumerate(dbmods):
						if hasattr( mod, 'sr_chmode_%s' % char ):
							cmd = getattr( mod, 'sr_chmode_%s' % char )
							cmd( irc, client, target, adding, None )
			else:
				# Usermode get
				# IRCds don't provide us with a way to get params like RPL_ISUPPORT CHANMODES
				# so we won't support usermodes with params. I don't know of any umodes with
				# params anyway --SnoFox
				for n, mod in enumerate(dbmods):
					if hasattr( mod, 'sr_umode_%s' % char ):
						cmd = getattr( mod, 'sr_umode_%s' % char )
						cmd( irc, client, target, adding, None )
				




def ca_chanlist(irc, client, channel, params):
	irc.privmsg(channel, irc.chanlists[channel])

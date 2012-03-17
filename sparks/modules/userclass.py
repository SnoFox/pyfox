########################
# Sparks IRC framework
# User state module
# Provides a class to create user objects
# And keep their channel states 
# Author: Josh "SnoFox" Johnson
#		   <snofox@snofox.net>
########################

from time import time
from sparks.modules.basic import ircStrCmp, ircStrLower

class User:

	# irc = an IRC object that this user is in
	def __init__( self, irc, nick ):
	
		self.__nick = nick
		self.__ident = None # string of everything before the @ in hostname
		self.__address = None # string of everything after the @ in hostname
		self.__gecos = None # The user's gecos/realname field
		self.__channels = dict() # dicts where chan is the key and the modes they have in it (+ohv ... ) is the value
		self.__time = int(time()) # time we found this user (useful for users that PM'd us)
								  # currently unused

		irc.userList.append( self )

	def changeNick( self, newNick ):
		self.__nick = newNick

	def setAddress( self, address ):
		self.__address = address

	def setIdent( self, ident ):
		self.__ident = ident
	
	def setGecos( self, name ):
		self.__gecos = name

	def addChan( self, chan, prefixes = "" ):
		if not chan in self.__channels:
			self.__channels.update( { chan: prefixes } )
		else:
			print "Error: Got duplicate join for %s in %s" % ( self.__nick, chan )

	def setPrefix( self, chan, prefixes ):
		try:
			self.__channels[chan] = prefixes
		except NameError:
			print "Error: Got info for user %s in channel %s, but we don't know about that channel" % ( self.__nick, chan )

	def delChan( self, chan ):
		try:
			del self.__channels[chan]
		except NameError:
			print "Error: Got a part/kick for user %s in chan %s, but they weren't there in the first place" % ( self.__nick, chan )

	def getNick( self ):
		return self.__nick

	def getIdent( self ):
		return self.__ident

	def getAddress( self ):
		return self.__address

	def getGecos( self ):
		return self.__gecos

	def getPrefix( self, chan ):
		try:
			return self.__channels[chan]
		except NameError:
			return None

	def getChans( self ):
		return self.__channels

def modinit( irc ):
	irc.userList = []

def sr_join( irc, client, chan, null ):
	chan = chan.strip( ":" )

	if client[0] == irc.nick:
		irc.push( 'WHO %s' % chan )
	else:
		user = None
		for thisUser in irc.userList:
			if ircStrCmp( irc, thisUser.getNick(), client[0] ):
				user = thisUser
				break

		if not user:
			user = User( irc, client[0] )
			user.setIdent( client[1] )
			user.setAddress( client[2] )
			user.addChan( ircStrLower( irc, chan ) )

def sr_part( irc, client, chan, reason ):
	chan = chan.strip( ":" )
	if client[0] == irc.nick: # I left the channel
		tempList = list( irc.userList )
		for user in tempList:
			if chan in user.getChans():
				user.delChan( chan )
				if len( user.getChans() ) == 0:
					irc.userList.remove( user )
	else:
		user = None
		for thisUser in irc.userList:
			if ircStrCmp( irc, thisUser.getNick(), client[0] ):
				user = thisUser
				break
		if not user:
			print "Error: got a part for user we don't know about: %s!%s@%s on %s" % ( client[0], client[1], client[2], chan )
		else:
			user.delChan( ircStrLower( irc, chan ) )

def sr_quit( irc, client, reason, null ):
	user = None
	for thisUser in irc.userList:
		if ircStrCmp( irc, thisUser.getNick(), client[0] ):
			user = thisUser
			break
	if not user:
		print "Error: got a quit for user we don't know about: %s!%s@%s" % ( client[0], client[1], client[2] )
	else:
		irc.userList.remove( user )


def sr_kick( irc, client, chan, params ):
	chan = ircStrLower( irc, chan.strip( ":" ) )
	victim = params[0]

	if victim == irc.nick: # I left the channel
		tempList = list( irc.userList )
		for user in tempList:
			if chan in user.getChans():
				user.delChan( chan )
				if len( user.getChans() ) == 0:
					irc.userList.remove( user )
	else:	
		user = None
		for thisUser in irc.userList:
			if ircStrCmp( irc, thisUser.getNick(), victim ):
				user = thisUser
				break
		if not user:
			print "Error: got a kick for user we don't know about: %s kicking %s in %s" % ( client[0], victim, chan)
		else:
			user.delChan( ircStrLower( irc, chan ) )

def sr_nick( irc, client, newNick, null ):
	user = None
	for thisUser in irc.userList:
		if ircStrCmp( irc, thisUser.getNick(), client[0] ):
			user = thisUser
			break
	if user:
		user.changeNick( newNick.strip( ":" ) )
	else:
		print "Error: got nick change for %s -> %s, but we don't know them" % ( client[0], newNick )


def sr_352( irc, client, target, params ):
# >> :dualcore.ext3.net 352 PyFox #foxtest ~SnoFox is.in-addr.arpa void.ext3.net SnoFox H*! :2 Fox of Sno
	chan = ircStrLower( irc, params[0] )
	ident = params[1]
	address = params[2]
	nick = params[4]
	prefix = params[5] # need to be cleaned
	gecos = ' '.join( params[7:] )

	realPrefix = ""
	for char in prefix:
		if char in irc.statusmodes:
			realPrefix += char
	# Now translate !@%+ to aohv
	prefix = ""
	for thisPrefix in realPrefix:
		prefix += irc.statusmodes[ thisPrefix ]

	user = None
	for thisUser in irc.userList:
		if ircStrCmp( irc, thisUser.getNick(), nick ):
			user = thisUser
			break
	if not user:
		user = User( irc, nick )
		user.setIdent( ident )
		user.setAddress( address )
		user.setGecos( gecos )

	user.addChan( chan, prefix )



def sr_mode(irc, client, target, params):
	# XXX: Icky, code duplication. Could add a prefix-change event to prevent this
	# Mode parser
	# Sends out mode events for other modules to use
	# - SnoFox

	if target[0] in irc.isupport['CHANTYPES']:
		chmode = True 
		target = ircStrLower( irc, target )
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
				if char in irc.listmodes or char in irc.typebmodes or (char in irc.typecmodes and adding):
					paramNum += 1
					continue

				if char in irc.typeemodes:
					# We only care about prefix modes here
					user = None
					for thisUser in irc.userList:
						if ircStrCmp( irc, thisUser.getNick(), params[ paramNum ] ):
							user = thisUser

					if user:
						if adding:
							prefixes = user.getPrefix( target )
							if not char in prefixes:
								prefixes += char
								user.setPrefix( target, prefixes )
						else:
							prefixes = user.getPrefix( target )
							newPrefixes = ""
							for thisPrefix in prefixes:
								if not thisPrefix == char:
									newPrefixes += char
							user.setPrefix( target, newPrefixes )

					else: 
						print "Error: nick %s in %s got a prefix, but I don't know who he is" % ( params[ paramNum ], target )

					paramNum += 1
					continue
				else:
					# flag type mode; we don't care here
					pass
			else:
				# Usermode get
				# not a fuck was given that mode
				pass


def ca_ulist( irc, client, chan, params ):
	irc.privmsg( chan, "I know about the following users: " )
	for thisUser in irc.userList:
		irc.privmsg( chan, 'Nick: %s u@h: %s@%s Real: %s' % ( thisUser.getNick(), thisUser.getIdent(), thisUser.getAddress(), thisUser.getGecos() ) )
		irc.privmsg( chan, 'Chan info: %s' % thisUser.getChans() )
	irc.privmsg( chan, "== End of userlist ==" )

'''
Behavior notes:
	- Learning a user from join will not fill in their GECOS - could change in future
	- Nicks are compared via basic checks
		- this means Sno|Fox and Sno\Fox; and Sno[Fox] and Sno{Fox} are "different" nicks,
			which is incorrect behavior for IRC.
'''

#######
# EOF #
#######

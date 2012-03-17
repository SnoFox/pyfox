########################
# Sparks IRC framework
# User state module
# Provides a class to create user objects
# And keep their channel states 
# Author: Josh "SnoFox" Johnson
#		   <snofox@snofox.net>
########################

from time import time

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
		# Iterate through our list of objects to look for duplicates
		# If no dupes, just set self.nick to newNick, remove the old entry, add a new one self.__nick = newNick 
		pass
	def setAddress( self, address ):
		self.__address = address

	def setIdent( self, ident ):
		self.__ident = ident
	
	def setGecos( self, name ):
		self.__gecos = name

	def addChan( self, chan, prefixes ):
		self.__channels.update( { chan: prefixes } )

	def updateChan( self, chan, prefixes ):
		try:
			self.__channels[chan] = prefixes
		except NameError:
			print "Got info for user %s in channel %s, but we don't know about that channel" % (self.nick, chan)

	def delChan( self, chan ):
		try:
			del self.__channels[chan]
		except NameError:
			print "Got a part for user %s in chan %s, but they weren't there in the first place" % (self.nick, chan)

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
	if client[0] == irc.nick:
		irc.push( 'WHO %s' % chan )
	else:
		user = None
		for thisUser in irc.userList:
			if thisUser.getNick().lower() == client[0].lower():
				# XXX: temporary until I do proper case checks
				user = thisUser
				break

		if not user:
			user = User( irc, client[0] )
			user.setIdent( client[1] )
			user.setAddress( client[2] )
			user.addChan( chan.lower(), None )

def sr_part( irc, client, chan, reason ):
	if client[0] == irc.nick:
		# clean up the userlist by iterating through the userlist and deleting
		# all users who were just in that channel with the bot
		pass
	else:
		user = None
		for thisUser in irc.userList:
			if thisUser.getNick().lower() == client[0].lower():
				# XXX: temporary until I do proper case checks
				user = thisUser
				break
		if not user:
			print "Error: got a part for user we don't know about: %s!%s@%s on %s" % (client[0],client[1],client[2],chan)
		else:
			try:
				user.delChan( chan.lower() )
			except KeyError:
				print "Error: got a part for user %s on %s, but they weren't there" % ( user.getNick(), chan )

def sr_quit( irc, client, reason, null ):
	user = None
	for thisUser in irc.userList:
		if thisUser.getNick().lower() == client[0].lower():
			# XXX: temporary until I do proper case checks
			user = thisUser
			break
	if not user:
		print "Error: got a quit for user we don't know about: %s!%s@%s" % (client[0],client[1],client[2])
	else:
		irc.userList.remove( user )


def sr_kick( irc, client, chan, params ):
	victim = params[0]
	
	user = None
	for thisUser in irc.userList:
		if thisUser.getNick().lower() == victim.lower():
			# XXX: temporary until I do proper case checks
			user = thisUser
			break
	if not user:
		print "Error: got a kick for user we don't know about: %s kicking %s in %s" % (client[0],victim,chan)
	else:
		try:
			user.delChan( chan.lower() )
		except KeyError:
			print "Error: user %s was kicked from %s, but they weren't there" % ( user.getNick(), chan )

def sr_352( irc, client, target, params ):
# >> :dualcore.ext3.net 352 PyFox #foxtest ~SnoFox is.in-addr.arpa void.ext3.net SnoFox H*! :2 Fox of Sno
	chan = params[0]
	ident = params[1]
	address = params[2]
	nick = params[4]
	prefix = params[5] # need to be cleaned
	gecos = ' '.join( params[7:] )

	# XXX: sort out prefixes and add them

	user = None
	for thisUser in irc.userList:
		if thisUser.getNick().lower() == nick.lower():
			user = thisUser
			break
	if not user:
		user = User( irc, nick )
		user.setIdent( ident )
		user.setAddress( address )
		user.setGecos( gecos )

	user.addChan( chan, None )
	


def ca_ulist( irc, client, chan, params ):
	irc.privmsg( chan, "I know about the following users: " )
	for thisUser in irc.userList:
		irc.privmsg( chan, 'Nick: %s u@h: %s@%s' % (thisUser.getNick(),thisUser.getIdent(),thisUser.getAddress()) )
		irc.privmsg( chan, 'Chan info: %s' % thisUser.getChans() )
	irc.privmsg( chan, "== End of userlist ==" )



'''
Behavior notes:
	- Learning a user from join will not fill in their GECOS
	- Nicks are compared via basic checks; changing them to lowercase and matching
		- this means Sno|Fox and Sno\Fox; and Sno[Fox] and Sno{Fox} are "different" nicks,
			which is incorrect behavior for IRC.

TODO:
	- Nick changes are currently not supported
	- Mode changes do not work
	- Prefixes don't work
	- Fix addition of duplicates
'''


#######
# EOF #
#######

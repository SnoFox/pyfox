########################
# Sparks IRC framework
# User state module
# Provides a class to create user objects
# And keep their channel states 
# Author: Josh "SnoFox" Johnson
#		   <snofox@snofox.net>
########################

class User:

	# irc = an IRC object that this user is in
	def __init__( self, irc, nick ):
	
		self.__nick = nick
		self.__ident = None # string of everything before the @ in hostname
		self.__address = None # string of everything after the @ in hostname
		self.__gecos = None # The user's gecos/realname field
		self.__channels = dict() # dicts where chan is the key and the modes they have in it (+ohv ... ) is the value

		if not hasattr( irc, "userList" ):
			irc.userList = []

		irc.userList.append( self )

	def changeNick( self, newNick ):
		# Iterate through our list of objects to look for duplicates
		# If no dupes, just set self.nick to newNick, remove the old entry, add a new one
		self.__nick = newNick

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


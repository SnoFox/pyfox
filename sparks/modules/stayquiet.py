#############################################################
# This is a module written for the "Sparks" IRC framework   #
# The goal of this module is to keep users with +q devoiced #
# Author: Josh "SnoFox" <SnoFox@SnoFox.net>                 #
# Created: Mar 12, 2012                                     #
# Last edited: Mar 12, 2012                                 #
#############################################################

from sparks.modules.basic import ircStrLower, ircStrCmp

quietlist = dict()

def sr_join( irc, client, chan, null ):
	if client[0] == irc.nick:
		#print '> Buggie: I just joined %s' % chan
		global quietlist
		chan = ircStrLower( irc, chan )
		quietlist.update( { chan: [] } ) # Create a new list for this new channel
		irc.push( 'MODE %s +q' % chan )


def sr_chmode_q( irc, client, chan, adding, param ):
	global quietlist
	chan = ircStrLower( irc, chan )
	if adding:
		#print '> Buggie: new quiet get for %s: %s' % ( chan, param )
		quietlist[chan].append( param )
		for user in irc.userList:
			if ircStrLower( irc, chan ) in user.getChans():
				sr_chmode_v( irc, client, chan, adding, user.getNick() )
	else:
		#print '> Buggie: unquiet on %s: %s' % ( chan, param )
		try:
			quietlist[chan].remove( param )
		except NameError:
			print '> Buggie: Uh-oh; got a quiet we don\'t know about! :o'
			
	#print '> Buggie: Quiet list for %s now looks like: %s' % ( chan, quietlist )

def sr_728( irc, client, target, param ):
	chan = ircStrLower( irc, param[0] )
	quiet = param[2]
	# :void.ext3.net 728 SnoFox #ext3 q Ocelot!*@* SnoFox!~SnoFox@is.in-addr.arpa 1331143363
	# :void.ext3.net 728 SnoFox #ext3 q Panther!*@* SnoFox!~SnoFox@is.in-addr.arpa 1331143363
	#print '> Buggie: got old quiet for %s: %s' % ( chan, quiet )
	quietlist[chan].append( quiet )

	#print '> Buggie: Quiet list for %s now looks like: %s' % ( chan, quietlist[chan] )

def sr_729( irc, client, target, param ):
	# :void.ext3.net 729 SnoFox #ext3 q :End of Channel Quiet List
	# ['#ext3', 'q', ':End', 'of'...
	#print '> Buggie: got end of quiet list for %s' % param[1]
	pass


def sr_chmode_v( irc, client, chan, adding, param ):
	if not client[0] == irc.nick and adding:
		# Ignore my own changes
		global quietlist
		chan = ircStrLower( irc, chan )
		
		didMode = False
		
		myUser = None
		for user in irc.userList:
			if ircStrCmp( irc, param, user.getNick() ):
				myUser = user
				break

		if myUser == None:
			return
		for quiet in quietlist[ chan ]:
			address = '%s!%s@%s' % ( user.getNick(), user.getIdent(), user.getAddress() )
			if globmatch( quiet, address ):
				if not didMode:	
					irc.push( 'MODE %s -v %s' % ( chan, param ) )
					reply = '%s was denied voice due to the following quietbans: ' % param
					didMode = True
				reply += '%s ' % quiet
		if didMode:
			irc.push( 'NOTICE %s :%s' % ( client[0], reply ) )
			

def globmatch(pattern, text):
	"""simple glob matcher by bellbind @ GitHub"""
	if len(text) == 0: return len(pattern) == 0
	if len(pattern) == 0: return False
	if pattern[0] == "[":
		end = pattern.find("]")
		if end < 1: return False
		if text[0] in pattern[1:end]:
			return globmatch(pattern[(end+1):], text[1:])
		return False
	if pattern[0] == "*":
		return (globmatch(pattern, text[1:]) or
				globmatch(pattern[1:], text) or
				globmatch(pattern[1:], text[1:]))
	if pattern[0] == "?" or pattern[0] == text[0]:
		return globmatch(pattern[1:], text[1:])
	return False

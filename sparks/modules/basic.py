# This file is basic for dbbot

def sr_001(irc, params):
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

	irc.join(channels)

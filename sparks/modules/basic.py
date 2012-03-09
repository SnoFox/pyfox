# This file is basic for dbbot

def sr_001(irc, params):
	channels = irc.config['modules']['join']

	irc.join(channels)

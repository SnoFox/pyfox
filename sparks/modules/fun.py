# Jesse wants...
def cp_say(irc, client, channel, params):
	if len(params) > 0:
		irc.privmsg(channel, ' '.join(params))

# Jesse wants...
def cp_do(irc, client, channel, params):
	if len(params) > 0:
		irc.privmsg(channel, "ACTION %s" % ' '.join(params))

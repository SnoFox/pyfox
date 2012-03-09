# Public Channel Command
def cp_hello(irc, client, channel, params):
	irc.privmsg(channel, "Hello %s! :D" % client)

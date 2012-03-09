# Public Channel Command
def cp_hello(irc, client, channel, params):
	irc.privmsg(channel, "Hello %s! :D" % client[1])

def ca_hello(irc, client, channel, params):
	irc.privmsg(channel, "Why hello Admin %s! :)" % client[1])

def pp_hello(irc, client, params):
	irc.privmsg(client[1], "Hello! :D")

def pa_hello(irc, client, params):
	irc.privmsg(client[1], "Aloha admin %s! :)" % client[1])

# Public Channel Command
def cp_hello(irc, client, channel, params):
	irc.privmsg(channel, "Hello, %s! :D" % client[0])

def ca_hello(irc, client, channel, params):
	irc.privmsg(channel, "Hello admin %s! :)" % client[0])

def pp_hello(irc, client, params):
	irc.privmsg(client[0], "Hello! :D")

def pa_hello(irc, client, params):
	irc.privmsg(client[0], "Aloha admin %s! :)" % client[0])

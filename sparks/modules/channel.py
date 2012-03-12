from asyncore import socket_map as sockets

def ca_part(irc, client, channel, params):
	if len(params) == 1:
		irc.part(params[0])

def ca_join(irc, client, channel, params):
	if len(params) == 1:
		irc.join(params[0])

def ca_cycle(irc, client, channel, params):
	if len(params) == 1:
		irc.part(params[0])
		irc.join(params[0])

from asyncore import socket_map as sockets

def ca_raw(irc, client, channel, params):
	if len(params) > 0:
		irc.push(' '.join(params))

def ca_rawon(irc, client, channel, params):
	if len(params) > 1:
		for s in sockets:
			network = sockets[s]
			if network.name == params[0]:
				network.push(' '.join(params[1:]))

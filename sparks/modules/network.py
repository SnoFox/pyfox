import sparks
import yaml

def ca_reconnect(irc, client, channel, params):
	irc.push("QUIT :Reconnect command received from %s" % client[1])
	irc.close()

	sparks.newClient(irc.config)

def ca_connect(irc, client, channel, params):
	config = yaml.load(open('servers.conf'))

	if len(params) == 1:
		for name, conf in config.items():
			if name == params[0]:

				conf['name'] = name
				conf['admins'] = [] if 'admins' not in conf else conf['admins'].split(',')

				if not conf['triggers']:
					print('Network triggers have not been setup for %s. Stopping!' % conf['name'])
					exit()

				conf['triggers'] = conf['triggers'].split(',', 1)

				if len(conf['triggers']) != 2:
					print('Triggers have not been setup correctly for %s. Stopping!' % conf['name'])
					exit()

				irc.privmsg(channel, "Connecting to %s..." % name)
				sparks.newClient(conf)

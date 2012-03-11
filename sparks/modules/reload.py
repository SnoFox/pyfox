from sparks.modules import dbmods
import imp
import os

def ca_loaded(irc, client, channel, params):
	l = []

	irc.privmsg(channel, "Haha! Loaded... like you!")

	for n, mod in enumerate(dbmods):
		c = []

		for x in dir(mod):
			if len(x) > 3 and x[:3] in ('sr_', 'cp_', 'ca_', 'pp_', 'pa_'):
				c.append(x)
			elif len(x) > 4 and x[:4] in ('tsr_', 'tcp_', 'tca_', 'tpp_', 'tpa_'):
				c.append(x)

		irc.privmsg(channel, "%s: %s" % (mod.__file__, ' '.join(c)))

def ca_reload(irc, client, channel, params):
	if len(params) == 0:
		irc.privmsg(channel, "Sure! I can reload thin air! ....Not really.")
		return

	# This is cool. It allows us to edit dbmods!
	for n, mod in enumerate(dbmods):
		name = os.path.splitext(os.path.basename(mod.__file__))[0]

		if name == params[0]:
			irc.privmsg(channel, "Reloading %s (%s)..." % (name, mod.__file__))
			del dbmods[n]

			pypath = "sparks.modules.%s" % name
			filepath = "sparks/modules/%s.py" % name

			module = imp.load_source(pypath, filepath)

			if module:
				dbmods.append(module)
				irc.privmsg(channel, "Successfully reloaded %s!" % name)
				break

def ca_load(irc, client, channel, params):
	if len(params) == 0:
		irc.privmsg(channel, "Sure! I can reload thin air! ....Not really.")
		return

	# This is cool. It allows us to edit dbmods!
	for n, mod in enumerate(dbmods):
		name = os.path.splitext(os.path.basename(mod.__file__))[0]

		if name == params[0]:
			irc.privmsg(channel, "Module is already loaded. Use %sreload." % irc.config['triggers'][0])
			return

	pypath = "sparks.modules.%s" % params[0]
	filepath = "sparks/modules/%s.py" % params[0]

	if not os.path.exists(filepath):
		irc.privmsg(channel, "Sure! I can load thin air! ....Not really.")
		return

	module = imp.load_source(pypath, filepath)

	if module:
		dbmods.append(module)
		irc.privmsg(channel, "Successfully loaded %s!" % params[0])

def ca_unload(irc, client, channel, params):
	if len(params) == 0:
		irc.privmsg(channel, "Sure! I can unload thin air! ....Not really.")
		return

	# This is cool. It allows us to edit dbmods!
	for n, mod in enumerate(dbmods):
		name = os.path.splitext(os.path.basename(mod.__file__))[0]

		if name == params[0]:
			del dbmods[n]

			irc.privmsg(channel, "Successfully unloaded %s!" % params[0])
			break

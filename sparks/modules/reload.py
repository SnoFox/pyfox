from sparks.modules import dbmods
import imp
import os

def ca_loaded(irc, client, channel, params):
	l = []

	irc.privmsg(channel, "Haha! Loaded... like you!")

	for n, mod in enumerate(dbmods):
		l.append(mod.__file__)

	irc.privmsg(channel, "Loaded modules: %s" % ' '.join(l))

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
				irc.privmsg(channel, "Successfully reloading %s!" % name)
				return

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

from sparks.modules import dbmods
import imp
import os

def ca_reload(irc, client, channel, params):
	if len(params) == 0:
		irc.privmsg(channel, "Sure! I can reload thin air! ....Not really.")
		return

	# This is cool. It allows us to edit dbmods!
	for n, mod in enumerate(dbmods):
		name = os.path.splitext(os.path.basename(mod.__file__))[0]

		if name == params[0]:
			irc.privmsg(channel, "Reloading %s..." % name)
			del dbmods[n]

			pypath = "sparks.modules.%s" % name
			filepath = "sparks/modules/%s.py" % name

			module = imp.load_source(pypath, filepath)

			if module:
				dbmods.append(module)
				irc.privmsg(channel, "Successfully reloading %s!" % name)

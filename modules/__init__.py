import os
import imp

# Modules with stuff...
dbmods = []

for filename in os.listdir(os.path.join(os.getcwd(), 'modules')):
	if filename.endswith('.py') and not filename.startswith('_'):
		name = os.path.basename(filename).strip('.py')

		# Import module...
		module = imp.load_source(name, "modules/%s" % filename)

		# Append module to list
		dbmods.append(module)

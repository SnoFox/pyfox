# Copyright (C) David B. Dixon II 2012
import ConfigParser
import os

# If you want the bot to work, I suggest you not to touch and/or delete this.

class confparser:
	def __init__(self, altfile):
		try:
			self.db = altfile
			self.conf = ConfigParser.RawConfigParser()
			self.conf.readfp(open(self.db))
		except Exception as e:
			raise Exception("Error getting %s. Reason: %s" % (self.db,e))

	def section_exists(self, section):
		if self.conf.has_section(section):
			return True
		else:
			return None

	def sections_list(self):
		return self.conf.sections()

	def option_exists(self, section, option):
		if self.section_exists(section):
			if self.conf.has_option(section, option):
				return True
			else:
				return None
		else:
			return None

	def get_option(self, section, option):
		return self.conf.get(section, option)

	def get_section(self, section):
		settings = self.conf.items(section)
		# Remove tuples. They're ugly
		_data = {}
		for q in settings:
			_option = list(q)[0]
			_value = list(q)[1]
			_data[_option] = _value
		return _data

	def del_option(self, section, option):
		self.conf.remove_option(section, option)

	def del_section(self, section):
		self.conf.remove_section(section)

	def add_section(self, section):
		self.conf.add_section(section)

	def set(self, section, option, value, encrypt=None):
		if encrypt:
			self.conf.set(section, option, self.gen_hex(value))
		else:
			self.conf.set(section, option, value)

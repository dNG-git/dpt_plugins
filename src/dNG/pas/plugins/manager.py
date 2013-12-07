# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.plugins.Manager
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;plugins

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasPluginsVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from os import path
import os

from dNG.pas.module.named_loader import NamedLoader

class Manager(NamedLoader):
#
	"""
"Manager" provides methods to handle plugins.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: plugins
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	plugins = { }
	"""
Dict of loaded plugins
	"""

	@staticmethod
	def load_plugin(plugin, prefix = None):
	#
		"""
Load and register all plugins for the given plugin name and prefix (defaults
to "dNG.pas.plugins").

:param plugin: Plugin name
:param prefix: Plugin name prefix

:return: (bool) True on success
:since:  v0.1.00
		"""

		_return = False

		if (prefix == None): prefix = "dNG.pas.plugins"
		package = "{0}.{1}".format(prefix, plugin)

		if (NamedLoader._load_package(package) != None):
		#
			package_path = path.normpath("{0}/{1}".format(Manager._get_loader().get_base_dir(), package.replace(".", path.sep)))
			if (not os.access(package_path, os.R_OK)): package_path = None
		#
		else: package_path = None

		if (package_path != None and path.isdir(package_path)):
		#
			for dir_entry in os.listdir(package_path):
			#
				if (dir_entry.endswith(".py") and dir_entry != "__init__.py"):
				#
					module_name = "{0}.{1}".format(package, dir_entry[:-3])
					module = NamedLoader._load_module(module_name)

					if (module != None and hasattr(module, "plugin_registration")):
					#
						try:
						#
							if (package not in Manager.plugins): Manager.plugins[package] = [ ]
							if (module_name not in Manager.plugins[package]): Manager.plugins[package].append(module_name)

							module.plugin_registration()
							_return = True
						#
						except Exception as handled_exception:
						#
							if (Manager.log_handler != None): Manager.log_handler.error(handled_exception)
						#
					#
				#
			#
		#

		return _return
	#

	@staticmethod
	def reload_plugins(prefix = None):
	#
		"""
Reload all plugins or the plugins matching the given prefix.

:param prefix: Plugin prefix

:return: (bool) True on success
:since:  v0.1.00
		"""

		_return = True

		for package in Manager.plugins:
		#
			if (prefix == None or package.startswith(prefix)):
			#
				modules = Manager.plugins[package]

				for module_name in modules:
				#
					module = NamedLoader._load_module(module_name)

					if (module != None and hasattr(module, "plugin_deregistration")):
					#
						try:
						#
							module.plugin_deregistration()
							module.plugin_registration()
						#
						except Exception as handled_exception:
						#
							if (Manager.log_handler != None): Manager.log_handler.error(handled_exception)
							_return = False
						#
					#
					else: _return = False
				#
			#
		#

		return _return
	#
#

##j## EOF
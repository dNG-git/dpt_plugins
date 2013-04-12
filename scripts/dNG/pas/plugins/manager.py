# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.plugins.manager
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
#echo(pasCoreVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from os import path
import os

from dNG.pas.module.named_loader import direct_named_loader

class direct_manager(direct_named_loader):
#
	"""
"direct_named_loader" provides singletons and objects based on a callable
common name.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   pas.core
:since:     v0.1.00
:license:   http://www.direct-netware.de/redirect.py?licenses;mpl2
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
Get the class name for the given common name.

:param common_name: Common name
:param classprefix: A classname prefix

:return: (bool) True on success
:since:  v0.1.00
		"""

		var_return = True

		if (prefix == None): prefix = "dNG.pas.plugins"
		package = "{0}.{1}".format(prefix, plugin)

		if (direct_named_loader.load_package(package) != None):
		#
			package_path = path.normpath("{0}/{1}".format(direct_manager.get_loader().get_base_dir(), package.replace(".", path.sep)))
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
					module = direct_named_loader.load_module(module_name)

					if (module != None and hasattr(module, "plugin_registration")):
					#
						try:
						#
							if (package not in direct_manager.plugins): direct_manager.plugins[package] = [ ]
							if (module_name not in direct_manager.plugins[package]): direct_manager.plugins[package] += module_name

							module.plugin_registration()
						#
						except Exception as handled_exception:
						#
							if (direct_named_loader.log_handler != None): direct_named_loader.log_handler.error(handled_exception)
						#
					#
				#
			#
		#

		return var_return
	#
#

##j## EOF
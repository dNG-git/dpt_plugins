# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;plugins

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasPluginsVersion)#
#echo(__FILEPATH__)#
"""

from copy import copy
from os import path
import os

_MODE_IMP = 1
"""
Use "imp" based methods for import
"""
_MODE_IMPORT_MODULE = 2
"""
Use "import_module" for import
"""

_mode = _MODE_IMP

try:

	from importlib import reload
	import importlib

	_mode = _MODE_IMPORT_MODULE

except ImportError: from imp import reload

from dNG.module.named_loader import NamedLoader
from dNG.runtime.exception_log_trap import ExceptionLogTrap

class Manager(NamedLoader):
#
	"""
"Manager" provides methods to handle plugins.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: plugins
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	_plugins = { }
	"""
Dict of loaded plugins
	"""

	@staticmethod
	def load_plugin(plugin, prefix = None):
	#
		"""
Load and register all plugins for the given plugin name and prefix (defaults
to "dNG.plugins").

:param plugin: Plugin name
:param prefix: Plugin name prefix

:return: (bool) True on success
:since:  v0.2.00
		"""

		_return = False

		if (prefix is None): prefix = "dNG.plugins"
		package = "{0}.{1}".format(prefix, plugin)

		if (NamedLoader._load_package(package) is not None):
		#
			package_path = path.join(Manager._get_loader().get_base_dir(), package.replace(".", path.sep))
			if (not os.access(package_path, os.R_OK)): package_path = None
		#
		else: package_path = None

		if (package_path is not None and path.isdir(package_path)):
		#
			for dir_entry in os.listdir(package_path):
			#
				if (dir_entry.endswith(".py") and dir_entry != "__init__.py"):
				#
					module_name = "{0}.{1}".format(package, dir_entry[:-3])
					module = NamedLoader._load_module(module_name)

					if (module is not None and hasattr(module, "register_plugin")):
					#
						with ExceptionLogTrap("pas_plugins"):
						#
							if (package not in Manager._plugins): Manager._plugins[package] = [ ]
							if (module_name not in Manager._plugins[package]): Manager._plugins[package].append(module_name)

							module.register_plugin()
							_return = True
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
:since:  v0.2.00
		"""

		# pylint: disable=broad-except

		_return = True

		for package in Manager._plugins:
		#
			if (prefix is None or package.startswith("{0}.".format(prefix))):
			#
				modules = (Manager._plugins[package].copy()
				           if (hasattr(Manager._plugins[package], "copy")) else
				           copy(Manager._plugins[package])
				          )

				if (_mode == _MODE_IMPORT_MODULE
				    and hasattr(importlib, "invalidate_caches")
				   ): importlib.invalidate_caches()

				for module_name in modules:
				#
					try:
					#
						module = NamedLoader._get_module(module_name)

						if (module is not None and hasattr(module, "unregister_plugin")): module.unregister_plugin()

						try: reload(module)
						except Exception: Manager._plugins[package].remove(module_name)

						if (module is not None and hasattr(module, "on_plugin_reloaded")): module.on_plugin_reloaded()
					#
					except Exception as handled_exception:
					#
						if (Manager._log_handler is not None): Manager._log_handler.error(handled_exception, context = "pas_plugins")
						_return = False
					#
				#

				package_prefix = (package[:package.rindex(".")] if (prefix is None) else prefix)
				package_plugin = package[1 + package.rindex("."):]

				Manager.load_plugin(package_plugin, package_prefix)
			#
		#

		return _return
	#
#

##j## EOF
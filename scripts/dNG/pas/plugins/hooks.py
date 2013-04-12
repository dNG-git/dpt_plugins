# -*- coding: utf-8 -*-
##j## BOF

"""
Our main abstraction layer for plugins.
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

from threading import RLock

from dNG.pas.pythonback import direct_str
from .manager import direct_manager

class direct_hooks(dict):
#
	"""
The direct_hooks class provides hook-based Python plugins.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   pas_plugins
:since:     v0.1.00
:license:   http://www.direct-netware.de/redirect.py?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	instance = None
	"""
Registered hook instance
	"""
	log_handler = None
	"""
The log_handler is called whenever debug messages should be logged or errors
happened.
	"""
	synchronized = RLock()
	"""
Lock used in multi thread environments.
	"""

	def return_instance(self):
	#
		"""
The last "return_instance()" call will activate the Python singleton
destructor.

:since: v0.1.00
		"""

		pass
	#

	@staticmethod
	def call(hook, **params):
	#
		"""
Call all functions registered for the hook with the specified parameters.

:param hook: Hook-ID
:param params: Keyword parameters

:return: (mixed) Hook results; None if not defined
:since:  v0.1.00
		"""

		hook = direct_str(hook)

		if (direct_hooks.log_handler != None): direct_hooks.log_handler.debug("#echo(__FILEPATH__)# -pluginHooks.call_hook_handler({0}, params)- (#echo(__LINE__)#)".format(hook))
		var_return = None

		hooks = direct_hooks.get_instance()

		if (hook in hooks and type(hooks[hook]) == list):
		#
			if ("hook" not in params): params['hook'] = hook

			for py_function in hooks[hook]:
			#
				try: var_return = py_function(params, last_return = var_return)
				except Exception as handled_exception:
				#
					if (direct_hooks.log_handler != None): direct_hooks.log_handler.error(handled_exception)
					var_return = handled_exception
				#
			#
		#

		return var_return
	#

	@staticmethod
	def get_instance(count = False):
	#
		"""
Get the hooks singleton.

:param count: Count "get()" request

:return: (direct_hooks) Object on success
:since:  v0.1.00
		"""

		direct_hooks.synchronized.acquire()
		if (direct_hooks.instance == None): direct_hooks.instance = direct_hooks()
		direct_hooks.synchronized.release()

		return direct_hooks.instance
	#

	@staticmethod
	def load(plugin):
	#
		"""
Scans a plugin and loads its hooks.

:param package:

:since: v0.1.00
		"""

		direct_manager.load_plugin(plugin)
	#

	@staticmethod
	def register(hook, py_function, prepend = False, exclusive = False):
	#
		"""
Register a python function for the hook.

:param hook: Hook-ID
:param py_function: Python function to be registered
:param prepend: Add function at the beginning of the stack if true.
:param exclusive: Add the given function exclusively.

:since: v0.1.00
		"""

		hook = direct_str(hook)

		if (direct_hooks.log_handler != None): direct_hooks.log_handler.debug("#echo(__FILEPATH__)# -pluginHooks.register({0}, py_function, prepend, exclusive)- (#echo(__LINE__)#)".format(hook))

		hooks = direct_hooks.get_instance()

		if (exclusive): hooks[hook] = [ py_function ]
		else:
		#
			if (hook not in hooks): hooks[hook] = [ ]

			if (prepend): hooks[hook].insert(0, py_function)
			else: hooks[hook].append(py_function)
		#
	#

	@staticmethod
	def set_log_handler(log_handler):
	#
		"""
Sets the log_handler.

:param log_handler: log_handler to use

:since: v0.1.00
		"""

		if (log_handler != None): log_handler.debug("#echo(__FILEPATH__)# -pluginHooks.set_log_handler(log_handler)- (#echo(__LINE__)#)")
		direct_hooks.log_handler = log_handler
	#

	@staticmethod
	def unregister(hook, py_function):
	#
		"""
Unregister a python function from the hook.

:param hook: Hook-ID
:param py_function: Python function to be unregistered

:since: v0.1.00
		"""

		hook = direct_str(hook)

		if (direct_hooks.log_handler != None): direct_hooks.log_handler.debug("#echo(__FILEPATH__)# -pluginHooks.unregister({0}, py_function)- (#echo(__LINE__)#)".format(hook))

		hooks = direct_hooks.get_instance()
		if (hook in hooks and py_function in hooks[hook]): del(hooks[hook][hooks[hook].index(py_function)])
	#
#

##j## EOF
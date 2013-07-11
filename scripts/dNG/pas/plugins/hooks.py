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
from weakref import proxy, WeakSet

from dNG.pas.data.binary import Binary
from .manager import Manager

class Hooks(dict):
#
	"""
The Hooks class provides hook-based Python plugins.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: plugins
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
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

		hook = Binary.str(hook)

		if (Hooks.log_handler != None): Hooks.log_handler.debug("#echo(__FILEPATH__)# -Hooks.call_hook_handler({0}, params)- (#echo(__LINE__)#)".format(hook))
		_return = None

		hooks = Hooks.get_instance()

		if (hook in hooks and type(hooks[hook]) == list):
		#
			if ("hook" not in params): params['hook'] = hook

			for callback in hooks[hook]:
			#
				try: _return = callback(params, last_return = _return)
				except Exception as handled_exception:
				#
					if (Hooks.log_handler != None): Hooks.log_handler.error(handled_exception)
					_return = handled_exception
				#
			#
		#

		return _return
	#

	@staticmethod
	def free():
	#
		"""
Free all plugin hooks to enable garbage collection.

:param package:

:since: v0.1.00
		"""

		with Hooks.synchronized:
		#
			hooks = Hooks.get_instance()

			for hook in hooks:
			#
				if (not isinstance(hooks[hook], WeakSet)): hooks[hook] = WeakSet(hooks[hook])
			#
		#
	#

	@staticmethod
	def get_instance():
	#
		"""
Get the hooks singleton.

:return: (Hooks) Object on success
:since:  v0.1.00
		"""

		with Hooks.synchronized:
		#
			if (Hooks.instance == None): Hooks.instance = Hooks()
		#

		return Hooks.instance
	#

	@staticmethod
	def load(plugin):
	#
		"""
Scans a plugin and loads its hooks.

:param package:

:since: v0.1.00
		"""

		Manager.load_plugin(plugin)
	#

	@staticmethod
	def register(hook, callback, prepend = False, exclusive = False):
	#
		"""
Register a python function for the hook.

:param hook: Hook-ID
:param callback: Python function to be registered
:param prepend: Add function at the beginning of the stack if true.
:param exclusive: Add the given function exclusively.

:since: v0.1.00
		"""

		hook = Binary.str(hook)

		if (Hooks.log_handler != None): Hooks.log_handler.debug("#echo(__FILEPATH__)# -Hooks.register({0}, callback, prepend, exclusive)- (#echo(__LINE__)#)".format(hook))

		hooks = Hooks.get_instance()

		if (exclusive): hooks[hook] = [ callback ]
		else:
		#
			if (hook not in hooks): hooks[hook] = [ ]

			if (prepend): hooks[hook].insert(0, callback)
			else: hooks[hook].append(callback)
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

		Hooks.log_handler = proxy(log_handler)
	#

	@staticmethod
	def unregister(hook, callback):
	#
		"""
Unregister a python function from the hook.

:param hook: Hook-ID
:param callback: Python function to be unregistered

:since: v0.1.00
		"""

		hook = Binary.str(hook)

		if (Hooks.log_handler != None): Hooks.log_handler.debug("#echo(__FILEPATH__)# -Hooks.unregister({0}, callback)- (#echo(__LINE__)#)".format(hook))

		hooks = Hooks.get_instance()
		if (hook in hooks and callback in hooks[hook]): del(hooks[hook][hooks[hook].index(callback)])
	#
#

##j## EOF
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
from weakref import ref

from dNG.data.binary import Binary
from dNG.runtime.instance_lock import InstanceLock
from dNG.runtime.value_exception import ValueException
from dNG.runtime.weakref_method import WeakrefMethod

from .manager import Manager

class Hook(dict):
#
	"""
The Hooks class provides hook-based Python plugins.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: plugins
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	_instance = None
	"""
Registered hook instance
	"""
	_instance_freed = False
	"""
True after "free()" has been called
	"""
	_instance_lock = InstanceLock()
	"""
Thread safety lock
	"""
	_log_handler = None
	"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
	"""

	@staticmethod
	def call(_hook, **kwargs):
	#
		"""
Call all functions registered for the hook with the specified parameters.

:param _hook: Hook-ID

:return: (mixed) Hook results; None if not defined
:since:  v0.2.00
		"""

		# pylint: disable=broad-except

		_hook = Binary.str(_hook)

		if (Hook._log_handler is not None): Hook._log_handler.debug("#echo(__FILEPATH__)# -Hook.call({0})- (#echo(__LINE__)#)", _hook, context = "pas_plugins")
		_return = None

		hook_registry = Hook.get_instance()
		params = kwargs

		if (_hook in hook_registry and (not Hook._instance_freed)):
		#
			if ("hook" not in params): params['hook'] = _hook
			hooks = (hook_registry[_hook].copy() if (hasattr(hook_registry[_hook], "copy")) else copy(hook_registry[_hook]))

			for _callback in hooks:
			#
				callback = (_callback()
				            if (isinstance(_callback, WeakrefMethod) or type(_callback) is ref) else
				            _callback
				           )

				if (callback is None): Hook.unregister(_hook, _callback)
				else:
				#
					try: _return = callback(params, last_return = _return)
					except Exception as handled_exception:
					#
						if (Hook._log_handler is not None): Hook._log_handler.error(handled_exception, context = "pas_plugins")
						_return = handled_exception
					#
				#
			#
		#

		return _return
	#

	@staticmethod
	def call_one(_hook, **kwargs):
	#
		"""
Calls one function registered for the hook with the specified parameters.
This has to be the only registered function and may throw exceptions.

:param _hook: Hook-ID

:return: (mixed) Hook result; None if not defined
:since:  v0.2.00
		"""

		_hook = Binary.str(_hook)

		if (Hook._log_handler is not None): Hook._log_handler.debug("#echo(__FILEPATH__)# -Hook.call_one({0})- (#echo(__LINE__)#)", _hook, context = "pas_plugins")
		_return = None

		hook_registry = Hook.get_instance()
		params = kwargs

		if (_hook in hook_registry and (not Hook._instance_freed)):
		#
			if ("hook" not in params): params['hook'] = _hook
			hooks = (hook_registry[_hook].copy() if (hasattr(hook_registry[_hook], "copy")) else copy(hook_registry[_hook]))

			callbacks_count = len(hooks)

			if (callbacks_count > 1): raise ValueException("More than one function registered for the called hook")
			elif (callbacks_count > 0):
			#
				callback = (hooks[0]()
				            if (isinstance(hooks[0], WeakrefMethod)) else
				            hooks[0]
				           )

				if (callback is None): Hook.unregister(_hook, hooks[0])
				else: _return = callback(params)
			#
		#

		return _return
	#

	@staticmethod
	def free():
	#
		"""
Free all plugin hooks to enable garbage collection.

:since: v0.2.00
		"""

		with Hook._instance_lock:
		#
			hook_registry = Hook.get_instance()
			hook_registry.clear()

			Hook._instance_freed = True
			Hook._log_handler = None
		#
	#

	@staticmethod
	def get_instance():
	#
		"""
Get the hooks singleton.

:return: (Hook) Object on success
:since:  v0.2.00
		"""

		if (Hook._instance is None):
		# Thread safety
			with Hook._instance_lock:
			#
				if (Hook._instance is None): Hook._instance = Hook()
			#
		#

		return Hook._instance
	#

	@staticmethod
	def load(plugin):
	#
		"""
Scans a plugin and loads its hooks.

:param plugin: Plugin name

:since: v0.2.00
		"""

		Manager.load_plugin(plugin)
	#

	@staticmethod
	def register(hook, callback, prepend = False, exclusive = False, _weakref_only = False):
	#
		"""
Register a python function for the hook.

:param hook: Hook-ID
:param callback: Python function to be registered
:param prepend: Add function at the beginning of the stack if true.
:param exclusive: Add the given function exclusively.
:param _weakref_only: True to use a weak reference

:since: v0.2.00
		"""

		hook = Binary.str(hook)

		if (Hook._log_handler is not None): Hook._log_handler.debug("#echo(__FILEPATH__)# -Hook.register({0}, {1!r})- (#echo(__LINE__)#)", hook, callback, context = "pas_plugins")

		hook_registry = Hook.get_instance()

		if (not Hook._instance_freed):
		#
			with Hook._instance_lock:
			# Thread safety
				if (not Hook._instance_freed):
				#
					if (_weakref_only):
					#
						callback = (WeakrefMethod(callback)
						            if (hasattr(callback, "__self__")) else
						            ref(callback)
						           )
					#

					if (exclusive): hook_registry[hook] = [ callback ]
					else:
					#
						if (hook not in hook_registry): hook_registry[hook] = [ ]

						if (callback not in hook_registry[hook]):
						#
							if (prepend): hook_registry[hook].insert(0, callback)
							else: hook_registry[hook].append(callback)
						#
					#
				#
			#
		#
	#

	@staticmethod
	def register_weakref(hook, callback, prepend = False, exclusive = False):
	#
		"""
Register a weakly referenced python function for the hook.

:param hook: Hook-ID
:param callback: Python function to be registered
:param prepend: Add function at the beginning of the stack if true.
:param exclusive: Add the given function exclusively.

:since: v0.2.00
		"""

		Hook.register(hook, callback, prepend, exclusive, True)
	#

	@staticmethod
	def set_log_handler(log_handler):
	#
		"""
Sets the LogHandler.

:param log_handler: LogHandler to use

:since: v0.2.00
		"""

		Hook._log_handler = log_handler
	#

	@staticmethod
	def unregister(hook, callback):
	#
		"""
Unregister a python function from the hook.

:param hook: Hook-ID
:param callback: Python function to be unregistered

:since: v0.2.00
		"""

		hook = Binary.str(hook)

		if (Hook._log_handler is not None): Hook._log_handler.debug("#echo(__FILEPATH__)# -Hook.unregister({0}, {1!r})- (#echo(__LINE__)#)", hook, callback, context = "pas_plugins")

		hook_registry = Hook.get_instance()

		if (hook in hook_registry and callback in hook_registry[hook]):
		#
			with Hook._instance_lock:
			# Thread safety
				if (hook in hook_registry and callback in hook_registry[hook]): hook_registry[hook].remove(callback)
			#
		#
	#
#

##j## EOF
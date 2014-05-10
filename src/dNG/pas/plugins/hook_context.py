# -*- coding: utf-8 -*-
##j## BOF

"""
Context manager to call "before", "after" and "exception" hooks
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

from .hook import Hook

class HookContext(object):
#
	"""
Provides an call context to provide "before", "after" and "exception" hooks.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: plugins
:since:      v0.1.01
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self, hook_prefix, **kwargs):
	#
		"""
Constructor __init__(HookContext)

:since: v0.1.01
		"""

		self.hook_prefix = hook_prefix
		"""
Prefix used for ".before", ".after" and ".exception" calls
		"""
		self.kwargs = kwargs
		"""
Keyword arguments used for hook calls
		"""
	#

	def __call__(self, f):
	#
		"""
python.org: Called when the instance is "called" as a function [..].

:since: v0.1.01
		"""

		def decorator(*args, **kwargs):
		#
			"""
Decorator for wrapping a function or method with a call context.
			"""

			with self: return f(*args, **kwargs)
		#

		return decorator
	#

	def __enter__(self):
	#
		"""
python.org: Enter the runtime context related to this object.

:since: v0.1.01
		"""

		# pylint: disable=star-args

		Hook.call("{0}.before".format(self.hook_prefix), **self.kwargs)
	#

	def __exit__(self, exc_type, exc_value, traceback):
	#
		"""
python.org: Exit the runtime context related to this object.

:since: v0.1.01
		"""

		# pylint: disable=star-args

		if (exc_type == None and exc_value == None): Hook.call("{0}.after".format(self.hook_prefix), **self.kwargs)
		else: Hook.call("{0}.exception".format(self.hook_prefix), **self.kwargs)
	#
#

##j## EOF
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

from weakref import ref

from dNG.pas.runtime.value_exception import ValueException

class WeakrefMethod(object):
#
	"""
This class provides a weak reference to an instance method.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: plugins
:since:      v0.1.03
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self, method):
	#
		"""
Constructor __init__(WeakrefMethod)

:param method: Instance method to be bound

:since: v0.1.03
		"""

		if (not hasattr(method, "__self__")): raise ValueException("Instance method given is invalid")

		self.instance = ref(method.__self__)
		"""
Weakly referenced instance
		"""
		self.method_name = method.__name__
		"""
Instance method name
		"""
	#

	def __call__(self):
	#
		"""
python.org: Called when the instance is "called" as a function [..].

:return: (object) Bound method; None if garbage collected
:since:  v0.1.03
		"""

		instance = self._get_instance()
		return (None if (instance is None) else getattr(instance, self.method_name))
	#

	def __eq__(self, other):
	#
		"""
python.org: The correspondence between operator symbols and method names is
as follows: x==y calls x.__eq__(y)

:param other: Object to be compaired with

:return: (bool) True if equal
:since:  v0.1.03
		"""

		# pylint: disable=protected-access

		instance = self._get_instance()

		return (instance is not None
		        and isinstance(other, WeakrefMethod)
		        and instance == other._get_instance()
		        and self.method_name == other._get_method_name()
		       )
	#

	def __ne__(self, other):
	#
		"""
python.org: The correspondence between operator symbols and method names is
as follows: x!=y and x<>y call x.__ne__(y)

:param other: Object to be compaired with

:return: (bool) True if not equal
:since:  v0.1.03
		"""

		return (not (self == other))
	#

	def _get_instance(self):
	#
		"""
Returns the bound instance.

:return: (object) Bound instance; None if garbage collected
:since:  v0.1.03
		"""

		return self.instance()
	#

	def _get_method_name(self):
	#
		"""
Returns the method name of this weak reference instance.

:return: (str) Method name
:since:  v0.1.03
		"""

		return self.instance()
	#
#

##j## EOF
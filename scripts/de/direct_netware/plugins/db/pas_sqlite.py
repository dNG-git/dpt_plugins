# -*- coding: utf-8 -*-
##j## BOF

"""
de.direct_netware.plugins.db.pas_sqlite
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.php?pas

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.php?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasBasicVersion)#
pas/#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from de.direct_netware.classes.dbraw.pas_sqlite import direct_sqlite
from de.direct_netware.classes.pas_pluginmanager import direct_plugin_hooks

def direct_basic_dbraw_sqlite_init (params = None,last_return = None):
#
	"""
Returns an instance to handle SQLite databases.

:param params: Parameter specified calling "direct_pluginmanager".
:param last_return: The return value from the last hook called.

:return: (direct_dbraw_sqlite) Instance on success
:since:  v0.1.00
	"""

	return direct_sqlite ()
#

def plugin_deregistration ():
#
	"""
Deregister plugin hooks.

:since: v0.1.00
	"""

	pass
#

def plugin_registration ():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	direct_plugin_hooks.register ("de.direct_netware.db.sqlite.get",direct_basic_dbraw_sqlite_init,exclusive = True)
#

##j## EOF
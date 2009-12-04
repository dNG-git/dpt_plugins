# -*- coding: utf-8 -*-
##j## BOF

"""/*n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.php?pas

This work is distributed under the W3C (R) Software License, but without any
warranty; without even the implied warranty of merchantability or fitness
for a particular purpose.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.php?licenses;w3c
----------------------------------------------------------------------------
#echo(pasBasicVersion)#
pas/#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n*/"""
"""
We need a unified interface for communication with SQL-compatible database
servers. This is the abstract interface.

@internal   We are using epydoc (JavaDoc style) to automate the
            documentation process for creating the Developer's Manual.
            Use the following line to ensure 76 character sizes:
----------------------------------------------------------------------------
@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    pas_basic
@subpackage db
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;w3c
            W3C (R) Software License
"""

from classes.pas_dbraw_sqlite import direct_dbraw_sqlite
from de.direct_netware.plugins.classes.pas_pluginmanager import direct_plugin_hooks

def direct_basic_dbraw_sqlite_init (f_params = None,f_last_return = None):
#
	"""
Returns an instance to handle SQLite databases.

@param  f_params Parameter specified calling "direct_pluginmanager".
@param  f_last_return The return value from the last hook called.
@return (direct_dbraw_sqlite) Instance on success
@since  v1.0.0
	"""

	return direct_dbraw_sqlite ()
#

def plugin_registration ():
#
	"""
Register direct_plugin_hooks

@since v1.0.0
	"""

	direct_plugin_hooks.register ("de.direct_netware.db.sqlite.get",direct_basic_dbraw_sqlite_init,f_exclusive = True)
#

##j## EOF
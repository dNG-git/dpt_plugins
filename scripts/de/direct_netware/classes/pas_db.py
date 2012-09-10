# -*- coding: utf-8 -*-
##j## BOF

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
@license    http://www.direct-netware.de/redirect.php?licenses;mpl2
            Mozilla Public License, v. 2.0
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

from threading import RLock
import random,re

from .pas_globals import direct_globals
from .pas_pluginmanager import direct_pluginmanager,direct_plugin_hooks
from .pas_pythonback import direct_str
from .pas_xml_bridge import direct_xml_bridge

_direct_basic_db = None
_direct_basic_db_counter = 0

class direct_db (object):
#
	"""
This is the abstract interface to communicate with SQL servers.

@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    pas_basic
@subpackage db
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	E_NOTICE = 1
	"""
Error notice: It is save to ignore it
	"""
	E_WARNING = 2
	"""
Warning type: Could create trouble if ignored
	"""
	E_ERROR = 4
	"""
Error type: An error occured and was handled
	"""

	db_driver = None
	"""
Database layer
	"""
	db_driver_name = ""
	"""
Database layer
	"""
	data = ""
	"""
Result data
	"""
	debug = None
	"""
Debug message container
	"""
	error_callback = None
	"""
Function to be called for logging exceptions and other errors
	"""
	query_attributes = [ "*" ]
	"""
SQL query attributes
	"""
	query_element = 0
	"""
Counter for the element tags
	"""
	query_grouping = [ ]
	"""
SQL query GROUP BY
	"""
	query_joins = [ ]
	"""
SQL query JOIN
	"""
	query_limit = 0
	"""
SQL query LIMIT
	"""
	query_offset = 0
	"""
SQL query OFFSET
	"""
	query_ordering = ""
	"""
SQL query ORDER BY
	"""
	query_row_conditions = ""
	"""
SQL query WHERE
	"""
	query_search_conditions = ""
	"""
SQL query search conditions
	"""
	query_set_attributes = [ ]
	"""
SQL query SET
	"""
	query_table = ""
	"""
SQL query FROM
	"""
	query_type = ""
	"""
SQL query type
	"""
	query_values = ""
	"""
SQL query VALUES
	"""
	query_values_keys = [ ]
	"""
SQL query KEYS
	"""
	synchronized = None
	"""
Lock used in multi thread environments.
	"""

	"""
----------------------------------------------------------------------------
Construct the class
----------------------------------------------------------------------------
	"""

	def __init__ (self,peristent = False,error_callback = None):
	#
		"""
Constructor __init__ (direct_db)

@since v0.1.00
		"""

		self.debug = direct_globals['debug']
		self.error_callback = error_callback
		self.synchronized = RLock ()

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.__init__ (direct_db)- (#echo(__LINE__)#)")
		random.seed ()

		if (direct_globals['basic_functions'].settings_get ("{0}/settings/pas_db.xml".format (direct_globals['settings']['path_data']))):
		#
			if ("db_driver" in direct_globals['settings']): self.db_driver_name = direct_globals['settings']['db_driver']
			else: self.db_driver_name = "sqlite"

			if ("db_dbprefix" not in direct_globals['settings']): direct_globals['settings']['db_dbprefix'] = "pas_"

			if (peristent): direct_globals['settings']['db_peristent'] = True
			elif ("db_peristent" not in direct_globals['settings']): direct_globals['settings']['db_peristent'] = peristent
			else: direct_globals['settings']['db_peristent'] = False

			direct_pluginmanager ("de.direct_netware.plugins.db")
			self.db_driver = direct_plugin_hooks.call ("de.direct_netware.db.{0}.get".format (self.db_driver_name))
			if (self.db_driver == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class.__init__ (direct_db)- (#echo(__LINE__)#) reporting: Fatal error while loading the raw SQL handler",self.E_ERROR)
		#
		else: self.trigger_error ("#echo(__FILEPATH__)# -db_class.__init__ (direct_db)- (#echo(__LINE__)#) reporting: Fatal error while loading database settings",self.E_ERROR)
	#

	def __del__ (self):
	#
		"""
Destructor __del__ (direct_dbraw_sqlite)

@since v0.1.00
		"""

		self.del_direct_db ()
	#

	def del_direct_db (self):
	#
		"""
Destructor del_direct_db (direct_db)

@since v0.1.00
		"""

		self.db_driver = None
	#

	def define_attributes (self,attribute_list):
	#
		"""
Defines SQL attributes. (Only supported for SQL SELECT)

@param  attribute_list Requested attributes (including AS definition) as
        array or a string for "*"
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_attributes (attribute_list)- (#echo(__LINE__)#)")

		if (self.query_type == "select"):
		#
			if (type (attribute_list) == list): self.query_attributes = attribute_list
			else: self.query_attributes = [ attribute_list ]

			return True
		#
		else: return False
	#

	def define_grouping (self,attribute_list):
	#
		"""
Defines the SQL GROUP BY clause. (Only supported for SQL SELECT)

@param  attribute_list Requested grouping (including AS definition) as
        array or a string (for a single attribute)
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_grouping (attribute_list)- (#echo(__LINE__)#)")

		if (self.query_type == "select"):
		#
			if (type (attribute_list) == list): self.query_grouping = attribute_list
			else: self.query_grouping = [ attribute_list ]

			return True
		#
		else: return False
	#

	def define_join (self,join_type,table,requirements):
	#
		"""
Defines the SQL JOIN clause. (Only supported for SQL SELECT)

@param  join_type Type of JOIN
@param  table Name of the table (" AS Name" is valid)
@param  requirements ON definitions given as an array
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		join_type = direct_str (join_type)
		table = direct_str (table)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_join ({0},{1},requirements)- (#echo(__LINE__)#)".format (join_type,table))

		f_return = False

		if (self.query_type == "select"):
		#
			if ((type (requirements) == str) or (type == "cross-join")):
			#
				self.query_joins.append = { "type": join_type,"table": table,"requirements": requirements }
				f_return = True
			#
		#

		return f_return
	#

	def define_limit (self,limit):
	#
		"""
Defines a row limit for queries.

@param  limit Limit for the query
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_limit ({0:d})- (#echo(__LINE__)#)".format (limit))

		if ((self.query_type == "delete") or (self.query_type == "select") or (self.query_type == "update")):
		#
			self.query_limit = limit
			return True
		#
		else: return False
	#

	def define_offset (self,offset):
	#
		"""
Defines an offset for queries.

@param  offset Offset for the query (0 for none)
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_offset ({0:d})- (#echo(__LINE__)#)".format (offset))

		if (self.query_type == "select"):
		#
			self.query_offset = offset
			return True
		#
		else: return False
	#

	def define_ordering (self,ordering_list):
	#
		"""
Defines the SQL ORDER BY items.

@param  ordering_list XML-encoded elements how to order the list
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_ordering (ordering_list)- (#echo(__LINE__)#)")
		f_return = False

		ordering_list = direct_str (ordering_list)

		if ((self.query_type == "select") and (type (ordering_list) == str)):
		#
			self.query_ordering = ordering_list
			f_return = True
		#

		return f_return
	#

	def define_row_conditions (self,requirements):
	#
		"""
Defines the SQL WHERE clause.

@param  requirements WHERE definitions given as an array
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_row_conditions (requirements)- (#echo(__LINE__)#)")
		f_return = False

		requirements = direct_str (requirements)

		if (((self.query_type == "delete") or (self.query_type == "select") or (self.query_type == "update")) and (type (requirements) == str)):
		#
			self.query_row_conditions = requirements
			f_return = True
		#

		return f_return
	#

	def define_row_conditions_encode (self,attribute,value,value_type,logical_operator = "==",condition_mode = "and"):
	#
		"""
Returns valid XML sqlbox code for WHERE. Useful to secure values of
attributes against SQL injection.

@param  attribute Attribute
@param  value Value of the attribute
@param  value_type Value type (attribute, number, string)
@param  logical_operator Logical operator
@param  condition_mode Condition of this element
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		attribute = direct_str (attribute)
		value = direct_str (value)
		value_type = direct_str (value_type)
		logical_operator = direct_str (logical_operator)
		condition_mode = direct_str (condition_mode)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_row_conditions_encode ({0},{1},{2},{3},{4})- (#echo(__LINE__)#)".format (attribute,value,value_type,logical_operator,condition_mode))
		f_return = False

		f_xml_object = direct_xml_bridge.py_get ()

		if (f_xml_object != None):
		#
			if (value_type == "attribute"): value = re.compile("\\W").sub ("",value)
			elif (value_type == "number"):
			#
				try: value = "{0:d}".format (int (value))
				except ValueError:
				#
					try: value = "{0:g}".format (float (value))
					except ValueError: value = None
				#
			#
			elif (value_type != "sublevel"):
			#
				value_type = "string"
				if (value != None): value = self.v_secure (value)
			#

			if (condition_mode != "or"): condition_mode = "and"
			if ((logical_operator != "!=") and (logical_operator != "<") and (logical_operator != "<=") and (logical_operator != ">") and (logical_operator != ">=")): logical_operator = "=="

			f_xml_node_array = {
"tag": ("elementpas{0}".format (self.query_element)),
"attributes": { "attribute": attribute,"condition": condition_mode,"operator": logical_operator,"type": value_type }
			}

			if (value == None):
			#
				f_xml_node_array['attributes']['null'] = 1
				f_xml_node_array['value'] = ""
			#
			else: f_xml_node_array['value'] = value

			self.query_element += 1
			f_return = f_xml_object.array2xml_item_encoder (f_xml_node_array,strict_standard = False)
		#

		return f_return
	#

	def define_search_conditions (self,conditions):
	#
		"""
Defines search conditions for the database.

@param  conditions Conditions to search for
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_search_conditions (conditions)- (#echo(__LINE__)#)")
		f_return = False

		conditions = direct_str (conditions)

		if ((self.query_type == "select") and (type (conditions) == str)):
		#
			self.query_search_conditions = conditions
			f_return = True
		#

		return f_return
	#

	def define_search_conditions_term (self,term):
	#
		"""
Creates the search term definition XML code for the given term.

@param  term Term to search for
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_search_conditions_term (term)- (#echo(__LINE__)#)")
		f_return = False

		f_xml_object = direct_xml_bridge.py_get ()

		if (f_xml_object != None):
		#
			f_xml_node_array = { "tag": "searchterm","value": term }
			f_return = f_xml_object.array2xml_item_encoder (f_xml_node_array,strict_standard = False)
		#

		return f_return
	#

	def define_set_attributes (self,attribute_list):
	#
		"""
Defines the SQL SET clause.

@param  attribute_list Attributes to set
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_set_attributes (attribute_list)- (#echo(__LINE__)#)")
		f_return = False

		attribute_list = direct_str (attribute_list)
		f_continue_check = True
		if ((self.query_type != "insert") and (self.query_type != "replace") and (self.query_type != "update")): f_continue_check = False
		if (len (self.query_values) > 0): f_continue_check = False

		if ((f_continue_check) and (type (attribute_list) == str)):
		#
			self.query_set_attributes = attribute_list
			f_return = True
		#

		return f_return
	#

	def define_set_attributes_encode (self,attribute,value,value_type):
	#
		"""
Returns valid XML sqlbox code for SET. Useful to secure values against SQL
injection.

@param  attribute Attribute
@param  value Value string
@param  value_type Value type (attribute, number, string)
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		attribute = direct_str (attribute)
		value = direct_str (value)
		value_type = direct_str (value_type)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_set_attributes_encode ({0},{1},{2})- (#echo(__LINE__)#)".format (attribute,value,value_type))
		f_return = False

		f_xml_object = direct_xml_bridge.py_get ()

		if (f_xml_object != None):
		#
			if (value_type == "attribute"): value = re.compile("\\W").sub ("",value)
			elif (value_type == "number"):
			#
				try: value = "{0:d}".format (int (value))
				except ValueError:
				#
					try: value = "{0:g}".format (float (value))
					except ValueError: value = None
				#
			#
			else:
			#
				value_type = "string"
				if (value != None): value = self.v_secure (value)
			#

			f_xml_node_array = { "tag": ("elementpas{0}".format (self.query_element)),"attributes": { "attribute": attribute,"type": value_type } }

			if (value == None):
			#
				f_xml_node_array['attributes']['null'] = 1
				f_xml_node_array['value'] = ""
			#
			else: f_xml_node_array['value'] = value

			self.query_element += 1
			f_return = f_xml_object.array2xml_item_encoder (f_xml_node_array,strict_standard = False)
		#

		return f_return
	#

	def define_values (self,values):
	#
		"""
Defines the SQL VALUES element.

@param  values WHERE definitions given as an array
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_values (values)- (#echo(__LINE__)#)")
		f_return = False

		f_continue_check = True
		if ((self.query_type != "insert") and (self.query_type != "replace")): f_continue_check = False
		if (len (self.query_set_attributes) > 0): f_continue_check = False
		values = direct_str (values)

		if ((f_continue_check) and (type (values) == str)):
		#
			self.query_values = values
			f_return = True
		#

		return f_return
	#

	def define_values_encode (self,value,value_type):
	#
		"""
Returns valid XML sqlbox code for VALUES. Useful to secure values against
SQL injection.

@param  value Value string
@param  value_type Value type (attribute, number, string)
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		value = direct_str (value)
		value_type = direct_str (value_type)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_values_encode ({0},{1})- (#echo(__LINE__)#)".format (value,value_type))
		f_return = False

		f_xml_object = direct_xml_bridge.py_get ()

		if (f_xml_object != None):
		#
			if (value_type == "attribute"): value = re.compile("\\W").sub ("",value)
			elif (value_type == "number"):
			#
				try: value = "{0:d}".format (int (value))
				except ValueError:
				#
					try: value = "{0:g}".format (float (value))
					except ValueError: value = None
				#
			#
			elif (value_type != "newrow"):
			#
				value_type = "string"
				if (value != None): value = self.v_secure (value)
			#

			f_xml_node_array = { "tag": ("elementpas{0}".format (self.query_element)),"attributes": { "type": value_type } }

			if (value == None):
			#
				f_xml_node_array['attributes']['null'] = 1
				f_xml_node_array['value'] = ""
			#
			else: f_xml_node_array['value'] = value

			self.query_element += 1
			f_return = f_xml_object.array2xml_item_encoder (f_xml_node_array,strict_standard = False)
		#

		return f_return
	#

	def define_values_keys (self,keys_list):
	#
		"""
Defines the SQL WHERE clause.

@param  keys_list WHERE definitions given as an array
@return (bool) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.define_values_keys (keys_list)- (#echo(__LINE__)#)")

		if (((self.query_type == "insert") or (self.query_type == "replace")) and (type (keys_list) == list)):
		#
			self.query_values_keys = keys_list
			return True
		#
		else: return False
	#

	def init_delete (self,table):
	#
		"""
Initiates a DELETE request.

@param  table Name of the table (" AS Name" is valid)
@return (bool) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		table = direct_str (table)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.init_delete ({0})- (#echo(__LINE__)#)".format (table))

		if ((self.db_driver != None) and (len (self.query_type) < 1)):
		#
			self.data = ""
			self.query_attributes = [ "*" ]
			self.query_grouping = ""
			self.query_joins = [ ]
			self.query_limit = 0
			self.query_offset = 0
			self.query_ordering = ""
			self.query_row_conditions = ""
			self.query_search_conditions = ""
			self.query_set_attributes = [ ]
			self.query_table = table
			self.query_type = "delete"
			self.query_values = ""
			self.query_values_keys = [ ]

			return True
		#
		else: return False
	#

	def init_insert (self,table):
	#
		"""
Initiates a INSERT request.

@param  table Name of the table (" AS Name" is valid)
@return (bool) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		table = direct_str (table)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.init_insert ({0})- (#echo(__LINE__)#)".format (table))

		if ((self.db_driver != None) and (len (self.query_type) < 1)):
		#
			self.data = ""
			self.query_attributes = [ "*" ]
			self.query_grouping = ""
			self.query_joins = [ ]
			self.query_limit = 0
			self.query_offset = 0
			self.query_ordering = ""
			self.query_row_conditions = ""
			self.query_search_conditions = ""
			self.query_set_attributes = [ ]
			self.query_table = table
			self.query_type = "insert"
			self.query_values = ""
			self.query_values_keys = [ ]

			return True
		#
		else: return False
	#

	def init_replace (self,table):
	#
		"""
Initiates a REPLACE request.

@param  table Name of the table (" AS Name" is valid)
@return (bool) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		table = direct_str (table)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.init_replace ({0})- (#echo(__LINE__)#)".format (table))

		if ((self.db_driver != None) and (len (self.query_type) < 1)):
		#
			self.data = ""
			self.query_attributes = [ "*" ]
			self.query_grouping = ""
			self.query_joins = [ ]
			self.query_limit = 0
			self.query_offset = 0
			self.query_ordering = ""
			self.query_row_conditions = ""
			self.query_search_conditions = ""
			self.query_set_attributes = [ ]
			self.query_table = table
			self.query_type = "replace"
			self.query_values = ""
			self.query_values_keys = [ ]

			return True
		#
		else: return False
	#

	def init_select (self,table):
	#
		"""
Initiates a SELECT request.

@param  table Name of the table (" AS Name" is valid)
@return (bool) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		table = direct_str (table)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.init_select ({0})- (#echo(__LINE__)#)".format (table))

		if ((self.db_driver != None) and (len (self.query_type) < 1)):
		#
			self.data = ""
			self.query_attributes = [ "*" ]
			self.query_grouping = ""
			self.query_joins = [ ]
			self.query_limit = 0
			self.query_offset = 0
			self.query_ordering = ""
			self.query_row_conditions = ""
			self.query_search_conditions = ""
			self.query_set_attributes = [ ]
			self.query_table = table
			self.query_type = "select"
			self.query_values = ""
			self.query_values_keys = [ ]

			return True
		#
		else: return False
	#

	def init_update (self,table):
	#
		"""
Initiates a UPDATE request.

@param  table Name of the table (" AS Name" is valid)
@return (bool) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		table = direct_str (table)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.init_update ({0})- (#echo(__LINE__)#)".format (table))

		if ((self.db_driver != None) and (len (self.query_type) < 1)):
		#
			self.data = ""
			self.query_attributes = [ "*" ]
			self.query_grouping = ""
			self.query_joins = [ ]
			self.query_limit = 0
			self.query_offset = 0
			self.query_ordering = ""
			self.query_row_conditions = ""
			self.query_search_conditions = ""
			self.query_set_attributes = [ ]
			self.query_table = table
			self.query_type = "update"
			self.query_values = ""
			self.query_values_keys = [ ]

			return True
		#
		else: return False
	#

	def lock_acquire (self):
	#
		"""
Acquires the lock.

@since v0.1.00
		"""

		self.synchronized.acquire ()
	#

	def lock_release (self):
	#
		"""
Releases the previously acquired lock.

@since v0.1.00
		"""

		self.synchronized.release ()
	#

	def optimize_random (self,table):
	#
		"""
Optimizes a given table randomly (1/3).

@param  table Name of the table
@return (bool) True on success
@since  v0.1.00
		"""

		table = direct_str (table)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.optimize_random ({0})- (#echo(__LINE__)#)".format (table))

		if (random.randint (0,30) > 20): return self.v_optimize (table)
		else: return True
	#

	def query_exec (self,answer = "sa"):
	#
		"""
Transmits defined data to the SQL builder and returns the result in a
developer specified format via answer.

@param  answer Defines the requested type that should be returned
        The following types are supported: "ar", "co", "ma", "ms", "nr",
        "sa" or "ss".
@return (mixed) Result returned by the server in the specified format
@since  v0.1.00
		"""

		answer = direct_str (answer)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_exec ({0})- (#echo(__LINE__)#)".format (answer))
		f_return = False

		if ((self.db_driver != None) and (len (self.query_type) > 0)):
		#
			f_data = { }
			f_data['answer'] = answer

			f_data['attributes'] = self.query_attributes
			self.query_attributes = [ "*" ]

			f_data['grouping'] = self.query_grouping
			self.query_grouping = [ ]

			f_data['joins'] = self.query_joins
			self.query_joins = [ ]

			f_data['limit'] = self.query_limit
			self.query_limit = 0

			f_data['offset'] = self.query_offset
			self.query_offset = 0

			f_data['ordering'] = self.query_ordering
			self.query_ordering = ""

			f_data['row_conditions'] = self.query_row_conditions
			self.query_row_conditions = ""

			f_data['search_conditions'] = self.query_search_conditions
			self.query_search_conditions = ""

			f_data['set_attributes'] = self.query_set_attributes
			self.query_set_attributes = [ ]

			f_data['table'] = self.query_table
			self.query_table = ""

			f_data['type'] = self.query_type
			self.query_type = ""

			f_data['values'] = self.query_values
			self.query_values = ""

			f_data['values_keys'] = self.query_values_keys
			self.query_values_keys = [ ]

			self.data = self.v_query_build (f_data)
			f_return = self.data
		#

		return f_return
	#

	def set_trigger (self,py_function = None):
	#
		"""
Set a given function to be called for each exception or error.

@param py_function Python function to be called
@since v0.1.00
		"""

		self.error_callback = py_function
		if (self.db_driver != None): self.db_driver.set_trigger (py_function)
	#

	def trigger_error (self,message,message_type = None):
	#
		"""
Calls a user-defined function for each exception or error.

@param message Error message
@param message_type Error type
@since v0.1.00
		"""

		if (message_type == None): message_type = self.E_NOTICE
		if (self.error_callback != None): self.error_callback (message,message_type)
	#

	def v_connect (self):
	#
		"""
Opens the connection to a database server and selects a database. This
method acquires the lock automatically to support multi thread environments.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.v_connect ()- (#echo(__LINE__)#)")

		if (self.db_driver == None): f_return = False
		else:
		#
			self.synchronized.acquire ()
			f_return = self.db_driver.connect ()
			self.synchronized.release ()
		#

		return f_return
	#

	def v_disconnect (self):
	#
		"""
Closes an active database connection to the server. This method acquires the
lock automatically to support multi thread environments.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.v_disconnect ()- (#echo(__LINE__)#)")

		if (self.db_driver == None): f_return = False
		else:
		#
			self.synchronized.acquire ()
			f_return = self.db_driver.disconnect ()
			self.synchronized.release ()
		#

		return f_return
	#

	def v_optimize (self,table):
	#
		"""
Optimizes a given table.

@param  table Name of the table
@return (bool) True on success
@since  v0.1.00
		"""

		table = direct_str (table)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.v_optimize ({0})- (#echo(__LINE__)#)".format (table))

		if (self.db_driver == None): return False
		else: return self.db_driver.optimize (table)
	#

	def v_query_build (self,query):
	#
		"""
Builds and runs the SQL statement using the connected database specific
layer.

@param  query Dictionary containing query specific information.
@return (mixed) Result returned by the server in the specified format
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.v_query_build (query)- (#echo(__LINE__)#)")

		if (self.db_driver == None): return False
		else: return self.db_driver.query_build (query)
	#

	def v_query_exec (self,answer,query):
	#
		"""
Transmits an SQL query and returns the result in a developer specified
format via answer.

@param  answer Defines the requested type that should be returned
        The following types are supported: "ar", "co", "ma", "ms", "nr",
        "sa" or "ss".
@param  query Valid SQL query
@return (mixed) Result returned by the server in the specified format
@since  v0.1.00
		"""

		answer = direct_str (answer)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.v_query_exec ({0},query)- (#echo(__LINE__)#)".format (answer))

		if (self.db_driver == None): return False
		else: return self.db_driver.query_exec (answer,query)
	#

	def v_secure (self,data):
	#
		"""
Secures a given string to protect against SQL injections.

@param  data Input array or string
@return (mixed) Modified input or None on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.v_secure (data)- (#echo(__LINE__)#)")

		if (self.db_driver == None): return None
		else: return self.db_driver.secure (data)
	#

	def v_transaction_begin (self):
	#
		"""
Starts a transaction.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.v_transaction_begin ()- (#echo(__LINE__)#)")

		if (self.db_driver == None): return False
		else: return self.db_driver.transaction_begin ()
	#

	def v_transaction_commit (self):
	#
		"""
Commits all transaction statements.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.v_transaction_commit ()- (#echo(__LINE__)#)")

		if (self.db_driver == None): return False
		else: return self.db_driver.transaction_commit ()
	#

	def v_transaction_rollback (self):
	#
		"""
Calls the ROLLBACK statement.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.v_transaction_rollback ()- (#echo(__LINE__)#)")

		if (self.db_driver == None): return False
		else: return self.db_driver.transaction_rollback ()
	#

	def py_del ():
	#
		"""
The last "py_del ()" call will activate the Python singleton destructor.

@since v0.1.00
		"""

		global _direct_basic_db,_direct_basic_db_counter

		_direct_basic_db_counter -= 1
		if (_direct_basic_db_counter == 0): _direct_basic_db = None
	#
	py_del = staticmethod (py_del)

	def py_get (count = True):
	#
		"""
Get the direct_db singleton.

@param  count Count "get ()" request
@return (direct_db) Object on success
@since  v0.1.00
		"""

		global _direct_basic_db,_direct_basic_db_counter

		if (_direct_basic_db == None): _direct_basic_db = direct_db ()
		if (count): _direct_basic_db_counter += 1

		return _direct_basic_db
	#
	py_get = staticmethod (py_get)
#

##j## EOF
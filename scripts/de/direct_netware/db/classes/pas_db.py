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

from de.direct_netware.classes.pas_basic_functions import direct_basic_functions
from de.direct_netware.classes.pas_debug import direct_debug
from de.direct_netware.classes.pas_settings import direct_settings
from de.direct_netware.classes.pas_xml_bridge import direct_xml_bridge
from de.direct_netware.plugins.classes.pas_pluginmanager import direct_plugin_hooks
from threading import Lock
import de.direct_netware.db,random,re

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
@license    http://www.direct-netware.de/redirect.php?licenses;w3c
            W3C (R) Software License
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

	def __init__ (self,f_peristent = False,f_error_callback = None):
	#
		"""
Constructor __init__ (direct_db)

@since v0.1.00
		"""

		f_settings = direct_settings.get ()

		self.debug = direct_debug.get ()
		self.error_callback = f_error_callback
		self.synchronized = Lock ()

		direct_settings.py_del ()
		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->__construct (direct_db)- (#echo(__LINE__)#)")
		random.seed ()

		if (direct_basic_functions.get().settings_get ("%s/settings/pas_db.xml" % f_settings['path_data'])):
		#
			if (f_settings.has_key ("db_driver")): self.db_driver_name = f_settings['db_driver']
			else: self.db_driver_name = "sqlite"

			if (not f_settings.has_key ("db_dbprefix")): f_settings['db_dbprefix'] = "pas_"

			if (f_peristent): f_settings['db_peristent'] = True
			elif (not f_settings.has_key ("db_peristent")): f_settings['db_peristent'] = f_peristent
			else: f_settings['db_peristent'] = False

			self.db_driver = direct_plugin_hooks.call ("de.direct_netware.db.%s.get" % self.db_driver_name)
			if (self.db_driver == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class->__construct (direct_db)- (#echo(__LINE__)#) reporting: Fatal error while loading the raw SQL handler",self.E_ERROR)
		#
		else: self.trigger_error ("#echo(__FILEPATH__)# -db_class->__construct (direct_db)- (#echo(__LINE__)#) reporting: Fatal error while loading database settings",self.E_ERROR)

		direct_basic_functions.py_del ()
	#

	def __del__ (self):
	#
		"""
Destructor __del__ (direct_dbraw_sqlite)

@since v0.1.00
		"""

		direct_debug.py_del ()
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

	def define_attributes (self,f_attribute_list):
	#
		"""
Defines SQL attributes. (Only supported for SQL SELECT)

@param  f_attribute_list Requested attributes (including AS definition) as
        array or a string for "*"
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_attributes (+f_attribute_list)- (#echo(__LINE__)#)")

		if (self.query_type == "select"):
		#
			if (type (f_attribute_list) == list): self.query_attributes = f_attribute_list
			else: self.query_attributes = [ "*" ]

			return True
		#
		else: return False
	#

	def define_grouping (self,f_attribute_list):
	#
		"""
Defines the SQL GROUP BY clause. (Only supported for SQL SELECT)

@param  f_attribute_list Requested grouping (including AS definition) as
        array or a string (for a single attribute)
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_grouping (+f_attribute_list)- (#echo(__LINE__)#)")

		if (self.query_type == "select"):
		#
			if (type (f_attribute_list) == list): self.query_grouping = f_attribute_list
			else: self.query_grouping = [ f_attribute_list ]

			return True
		#
		else: return False
	#

	def define_join (self,f_type,f_table,f_requirements):
	#
		"""
Defines the SQL JOIN clause. (Only supported for SQL SELECT)

@param  f_type Type of JOIN
@param  f_table Name of the table (" AS Name" is valid)
@param  f_requirements ON definitions given as an array
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_join (%s,%s,+f_requirements)- (#echo(__LINE__)#)" % ( f_type,f_table ))
		f_return = False

		if (self.query_type == "select"):
		#
			f_type_requirements = type (f_requirements)

			if ((f_type_requirements == str) or (f_type_requirements == unicode) or (f_type == "cross-join")):
			#
				self.query_joins.append = { "type": f_type,"table": f_table,"requirements": f_requirements }
				f_return = True
			#
		#

		return f_return
	#

	def define_limit (self,f_limit):
	#
		"""
Defines a row limit for queries.

@param  f_limit Limit for the query
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_limit (%i)- (#echo(__LINE__)#)" % f_limit)
		f_return = False

		if ((self.query_type == "delete") or (self.query_type == "select") or (self.query_type == "update")):
		#
			self.query_limit = f_limit
			return True
		#
		else: return False
	#

	def define_offset (self,f_offset):
	#
		"""
Defines an offset for queries.

@param  f_offset Offset for the query (0 for none)
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_offset (%i)- (#echo(__LINE__)#)" % f_offset)
		f_return = False

		if (self.query_type == "select"):
		#
			self.query_offset = f_offset
			return True
		#
		else: return False
	#

	def define_ordering (self,f_ordering_list):
	#
		"""
Defines the SQL ORDER BY items.

@param  f_ordering_list XML-encoded elements how to order the list
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_ordering (+f_ordering_list)- (#echo(__LINE__)#)")
		f_return = False

		if (self.query_type == "select"):
		#
			f_type = type (f_ordering_list)

			if ((f_type == str) or (f_type == unicode)):
			#
				self.query_ordering = f_ordering_list
				f_return = True
			#
		#

		return f_return
	#

	def define_row_conditions (self,f_requirements):
	#
		"""
Defines the SQL WHERE clause.

@param  f_requirements WHERE definitions given as an array
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_row_conditions (+f_requirements)- (#echo(__LINE__)#)")
		f_return = False

		if ((self.query_type == "delete") or (self.query_type == "select") or (self.query_type == "update")):
		#
			f_type = type (f_requirements)

			if ((f_type == str) or (f_type == unicode)):
			#
				self.query_row_conditions = f_requirements
				f_return = True
			#
		#

		return f_return
	#

	def define_row_conditions_encode (self,f_attribute,f_value,f_type,f_logical_operator = "==",f_condition_mode = "and"):
	#
		"""
Returns valid XML sqlbox code for WHERE. Useful to secure values of
attributes against SQL injection.

@param  f_attribute Attribute
@param  f_value Value of the attribute
@param  f_type Value type (attribute, number, string)
@param  f_logical_operator Logical operator
@param  f_condition_mode Condition of this element
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_row_conditions_encode (%s,%s,%s,%s,%s)- (#echo(__LINE__)#)" % ( f_attribute,f_value,f_type,f_logical_operator,f_condition_mode ))
		f_return = False

		f_xml_object = direct_xml_bridge.get_xml_bridge ()

		if (f_xml_object != None):
		#
			if (f_type == "attribute"): f_value = re.compile("\W").sub ("",f_value)
			elif (f_type == "number"):
			#
				try: f_value = int (f_value)
				except Exception,f_handled_exception:
				#
					try: f_value = float (f_value)
					except Exception,f_handled_inner_exception: f_value = None
				#
			#
			elif (f_type != "sublevel"):
			#
				f_type = "string"
				if (f_value != None): f_value = self.v_secure (f_value)
			#

			if (f_condition_mode != "or"): f_condition_mode = "and"
			if ((f_logical_operator != "!=") and (f_logical_operator != "<") and (f_logical_operator != "<=") and (f_logical_operator != ">") and (f_logical_operator != ">=")): f_logical_operator = "=="

			f_xml_node_array = {
"tag": "elementpas%s" % self.query_element,
"attributes": { "attribute": f_attribute,"condition": f_condition_mode,"operator": f_logical_operator,"type": f_type }
			}

			if (f_value == None):
			#
				f_xml_node_array['attributes']['null'] = 1
				f_xml_node_array['value'] = ""
			#
			else: f_xml_node_array['value'] = f_value

			self.query_element += 1
			f_return = f_xml_object.array2xml_item_encoder (f_xml_node_array,f_strict_standard = False)
		#

		return f_return
	#

	def define_search_conditions (self,f_conditions):
	#
		"""
Defines search conditions for the database.

@param  f_conditions Conditions to search for
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_search_conditions (+f_conditions)- (#echo(__LINE__)#)")
		f_return = False

		if (self.query_type == "select"):
		#
			f_type = type (f_conditions)

			if ((f_type == str) or (f_type == unicode)):
			#
				self.query_search_conditions = f_conditions
				f_return = True
			#
		#

		return f_return
	#

	def define_search_conditions_term (self,f_term):
	#
		"""
Creates the search term definition XML code for the given term.

@param  f_term Term to search for
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_search_conditions_term (+f_term)- (#echo(__LINE__)#)")
		f_return = False

		f_xml_object = direct_xml_bridge.get_xml_bridge ()

		if (f_xml_object != None):
		#
			f_xml_node_array = { "tag": "searchterm","value": f_term }
			f_return = f_xml_object.array2xml_item_encoder (f_xml_node_array,f_strict_standard = False)
		#

		return f_return
	#

	def define_set_attributes (self,f_attribute_list):
	#
		"""
Defines the SQL SET clause.

@param  string $f_attribute_list Attributes to set
@return boolean False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_set_attributes (+f_attribute_list)- (#echo(__LINE__)#)")
		f_return = False

		f_continue_check = True
		if ((self.query_type != "insert") and (self.query_type != "replace") and (self.query_type != "update")): f_continue_check = False
		if (len (self.query_values) > 0): f_continue_check = False

		if (f_continue_check):
		#
			f_type = type (f_attribute_list)

			if ((f_type == str) or (f_type == unicode)):
			#
				self.query_set_attributes = f_attribute_list
				f_return = True
			#
		#

		return f_return
	#

	def define_set_attributes_encode (self,f_attribute,f_value,f_type):
	#
		"""
Returns valid XML sqlbox code for SET. Useful to secure values against SQL
injection.

@param  f_attribute Attribute
@param  f_value Value string
@param  f_type Value type (attribute, number, string)
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_set_attributes_encode (%s,%s,%s)- (#echo(__LINE__)#)" % ( f_attribute,f_value,f_type ))
		f_return = False

		f_xml_object = direct_xml_bridge.get_xml_bridge ()

		if (f_xml_object != None):
		#
			if (f_type == "attribute"): f_value = re.compile("\W").sub ("",f_value)
			elif (f_type == "number"):
			#
				try: f_value = int (f_value)
				except Exception,f_handled_exception:
				#
					try: f_value = float (f_value)
					except Exception,f_handled_inner_exception: f_value = None
				#
			#
			else:
			#
				f_type = "string"
				if (f_value != None): f_value = self.v_secure (f_value)
			#

			f_xml_node_array = { "tag": "elementpas%s" % self.query_element,"attributes": { "attribute": f_attribute,"type": f_type } }

			if (f_value == None):
			#
				f_xml_node_array['attributes']['null'] = 1
				f_xml_node_array['value'] = ""
			#
			else: f_xml_node_array['value'] = f_value

			self.query_element += 1
			f_return = f_xml_object.array2xml_item_encoder (f_xml_node_array,f_strict_standard = False)
		#

		return f_return
	#

	def define_values (self,f_values):
	#
		"""
Defines the SQL VALUES element.

@param  f_values WHERE definitions given as an array
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_values (+f_values)- (#echo(__LINE__)#)")
		f_return = False

		f_continue_check = True
		if ((self.query_type != "insert") and (self.query_type != "replace")): f_continue_check = False
		if (len (self.query_set_attributes) > 0): f_continue_check = False

		if (f_continue_check):
		#
			f_type = type (f_values)

			if ((f_type == str) or (f_type == unicode)):
			#
				self.query_values = f_values
				f_return = True
			#
		#

		return f_return
	#

	def define_values_encode (self,f_value,f_type):
	#
		"""
Returns valid XML sqlbox code for VALUES. Useful to secure values against
SQL injection.

@param  f_value Value string
@param  f_type Value type (attribute, number, string)
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_values_encode (%s,%s)- (#echo(__LINE__)#)" % ( f_value,f_type ))
		f_return = False

		f_xml_object = direct_xml_bridge.get_xml_bridge ()

		if (f_xml_object != None):
		#
			if (f_type == "attribute"): f_value = re.compile("\W").sub ("",f_value)
			elif (f_type == "number"):
			#
				try: f_value = int (f_value)
				except Exception,f_handled_exception:
				#
					try: f_value = float (f_value)
					except Exception,f_handled_inner_exception: f_value = None
				#
			#
			elif (f_type != "newrow"):
			#
				f_type = "string"
				if (f_value != None): f_value = self.v_secure (f_value)
			#

			f_xml_node_array = { "tag": "elementpas%s" % self.query_element,"attributes": { "type": f_type } }

			if (f_value == None):
			#
				f_xml_node_array['attributes']['null'] = 1
				f_xml_node_array['value'] = ""
			#
			else: f_xml_node_array['value'] = f_value

			self.query_element += 1
			f_return = f_xml_object.array2xml_item_encoder (f_xml_node_array,f_strict_standard = False)
		#

		return f_return
	#

	def define_values_keys (self,f_keys_list):
	#
		"""
Defines the SQL WHERE clause.

@param  f_requirements WHERE definitions given as an array
@return (boolean) False if query is empty or on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->define_values_keys (+f_keys_list)- (#echo(__LINE__)#)")

		if (((self.query_type == "insert") or (self.query_type == "replace")) and (type (f_keys_list) == list)):
		#
			self.query_values_keys = f_keys_list
			return True
		#
		else: return False
	#

	def init_delete (self,f_table):
	#
		"""
Initiates a DELETE request.

@param  f_table Name of the table (" AS Name" is valid)
@return (boolean) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->init_delete (%s)- (#echo(__LINE__)#)" % f_table)

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
			self.query_table = f_table
			self.query_type = "delete"
			self.query_values = ""
			self.query_values_keys = [ ]

			return True
		#
		else: return False
	#

	def init_insert (self,f_table):
	#
		"""
Initiates a INSERT request.

@param  f_table Name of the table (" AS Name" is valid)
@return (boolean) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->init_insert (%s)- (#echo(__LINE__)#)" % f_table)

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
			self.query_table = f_table
			self.query_type = "insert"
			self.query_values = ""
			self.query_values_keys = [ ]

			return True
		#
		else: return False
	#

	def init_replace (self,f_table):
	#
		"""
Initiates a REPLACE request.

@param  f_table Name of the table (" AS Name" is valid)
@return (boolean) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->init_replace (%s)- (#echo(__LINE__)#)" % f_table)

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
			self.query_table = f_table
			self.query_type = "replace"
			self.query_values = ""
			self.query_values_keys = [ ]

			return True
		#
		else: return False
	#

	def init_select (self,f_table):
	#
		"""
Initiates a SELECT request.

@param  f_table Name of the table (" AS Name" is valid)
@return (boolean) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->init_select (%s)- (#echo(__LINE__)#)" % f_table)

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
			self.query_table = f_table
			self.query_type = "select"
			self.query_values = ""
			self.query_values_keys = [ ]

			return True
		#
		else: return False
	#

	def init_update (self,f_table):
	#
		"""
Initiates a UPDATE request.

@param  f_table Name of the table (" AS Name" is valid)
@return (boolean) False if query cache is not empty (Query not executed?)
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->init_update (%s)- (#echo(__LINE__)#)" % f_table)

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
			self.query_table = f_table
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

@since  v0.1.00
		"""

		self.synchronized.acquire ()
	#

	def lock_release (self):
	#
		"""
Releases the previously acquired lock.

@since  v0.1.00
		"""

		self.synchronized.release ()
	#

	def optimize_random (self,f_table):
	#
		"""
Optimizes a given table randomly (1/3).

@param  f_table Name of the table
@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->optimize_random (%s)- (#echo(__LINE__)#)" % f_table)

		if (random.randint (0,30) > 20): return self.v_optimize (f_table)
		else: return True
	#

	def query_exec (self,f_answer = "sa"):
	#
		"""
Transmits defined data to the SQL builder and returns the result in a
developer specified format via f_answer.

@param  f_answer Defines the requested type that should be returned
        The following types are supported: "ar", "co", "ma", "ms", "nr",
        "sa" or "ss".
@return (mixed) Result returned by the server in the specified format
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_exec (%s)- (#echo(__LINE__)#)" % f_answer)
		f_return = False

		if ((self.db_driver != None) and (len (self.query_type) > 0)):
		#
			f_data = { }
			f_data['answer'] = f_answer

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

	def set_trigger (self,f_function = None):
	#
		"""
Set a given function to be called for each exception or error.

@param f_function Python function to be called
@since v0.1.00
		"""

		self.error_callback = f_function
		if (self.db_driver != None): self.db_driver.set_trigger (f_function)
	#

	def trigger_error (self,f_message,f_type = None):
	#
		"""
Calls a user-defined function for each exception or error.

@param f_message Error message
@param f_type Error type
@since v0.1.00
		"""

		if (f_type == None): f_type = self.E_NOTICE
		if (self.error_callback != None): self.error_callback (f_message,f_type)
	#

	def v_connect (self):
	#
		"""
Opens the connection to a database server and selects a database. This
method acquires the lock automatically to support multi thread environments.

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->v_connect ()- (#echo(__LINE__)#)")

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

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->v_disconnect ()- (#echo(__LINE__)#)")

		if (self.db_driver == None): f_return = False
		else:
		#
			self.synchronized.acquire ()
			f_return = self.db_driver.disconnect ()
			self.synchronized.release ()
		#

		return f_return
	#

	def v_optimize (self,f_table):
	#
		"""
Optimizes a given table.

@param  f_table Name of the table
@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->v_optimize (%s)- (#echo(__LINE__)#)" % f_table)

		if (self.db_driver == None): return False
		else: return self.db_driver.optimize (f_table)
	#

	def v_query_build (self,f_query):
	#
		"""
Builds and runs the SQL statement using the connected database specific
layer.

@param  f_data Array containing query specific information.
@return (mixed) Result returned by the server in the specified format
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->v_query_build (+f_query)- (#echo(__LINE__)#)")

		if (self.db_driver == None): return False
		else: return self.db_driver.query_build (f_query)
	#

	def v_query_exec (self,f_answer,f_query):
	#
		"""
Transmits an SQL query and returns the result in a developer specified
format via f_answer.

@param  f_answer Defines the requested type that should be returned
        The following types are supported: "ar", "co", "ma", "ms", "nr",
        "sa" or "ss".
@param  f_query Valid SQL query
@return (mixed) Result returned by the server in the specified format
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->v_query_exec (%s,+f_query)- (#echo(__LINE__)#)" % f_answer)

		if (self.db_driver == None): return False
		else: return self.db_driver.query_exec (f_answer,f_query)
	#

	def v_secure (self,f_data):
	#
		"""
Secures a given string to protect against SQL injections.

@param  f_data Input array or string
@return (mixed) Modified input or None on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->v_secure (+f_data)- (#echo(__LINE__)#)")

		if (self.db_driver == None): return None
		else: return self.db_driver.secure (f_data)
	#

	def v_transaction_begin (self):
	#
		"""
Starts a transaction.

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->v_transaction_begin ()- (#echo(__LINE__)#)")

		if (self.db_driver == None): return False
		else: return self.db_driver.transaction_begin ()
	#

	def v_transaction_commit (self):
	#
		"""
Commits all transaction statements.

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->v_transaction_commit ()- (#echo(__LINE__)#)")

		if (self.db_driver == None): return False
		else: return self.db_driver.transaction_commit ()
	#

	def v_transaction_rollback (self):
	#
		"""
Calls the ROLLBACK statement.

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->v_transaction_rollback ()- (#echo(__LINE__)#)")

		if (self.db_driver == None): return False
		else: return self.db_driver.transaction_rollback ()
	#

	@staticmethod
	def get ():
	#
		"""
Get the direct_db singleton.

@return (direct_db) Object on success
@since  v1.0.0
		"""

		global _direct_basic_db,_direct_basic_db_counter

		if (_direct_basic_db == None): _direct_basic_db = direct_db ()
		_direct_basic_db_counter += 1

		return _direct_basic_db
	#

	@staticmethod
	def get_db ():
	#
		"""
Get the direct_db singleton.

@return (direct_db) Object on success
@since  v1.0.0
		"""

		return direct_db.get ()
	#

	@staticmethod
	def py_del ():
	#
		"""
The last "py_del ()" call will activate the Python singleton destructor.

@since  v1.0.0
		"""

		global _direct_basic_db,_direct_basic_db_counter

		_direct_basic_db_counter -= 1
		if (_direct_basic_db_counter == 0): _direct_basic_db = None
	#
#

##j## EOF
# -*- coding: utf-8 -*-
##j## BOF

"""
We need a unified interface for communication with SQL-compatible database
servers. This one is designed for SQLite.

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

from os import path
from threading import local
import re,sqlite3

from de.direct_netware.classes.pas_globals import direct_globals
from de.direct_netware.classes.pas_pythonback import direct_str
from de.direct_netware.classes.pas_xml_bridge import direct_xml_bridge

class direct_sqlite (object):
#
	"""
This class has been designed to be used with a SQLite database.

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

	activity = None
	"""
Activity cache
	"""
	debug = None
	"""
Debug message container
	"""
	error_callback = None
	"""
Function to be called for logging exceptions and other errors
	"""
	local = None
	"""
Local data handle
	"""

	"""
----------------------------------------------------------------------------
Construct the class
----------------------------------------------------------------------------
	"""

	def __init__ (self):
	#
		"""
Constructor __init__ (direct_sqlite)

@since v0.1.00
		"""

		self.debug = direct_globals['debug']
		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.__init__ (direct_sqlite)- (#echo(__LINE__)#)")
		self.local = local ()
	#

	def __del__ (self):
	#
		"""
Destructor __del__ (direct_sqlite)

@since v0.1.00
		"""

		self.del_direct_sqlite ()
	#

	def del_direct_sqlite (self):
	#
		"""
Destructor del_direct_sqlite (direct_sqlite)

@since v0.1.00
		"""

		self.disconnect ()
	#

	def connect (self):
	#
		"""
Opens the connection to a database server and selects a database.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.connect ()- (#echo(__LINE__)#)")

		f_return = True
		self.thread_local_check ()

		if ("db_dbfile" in direct_globals['settings']):
		#
			if (self.local.resource == None):
			#
				try:
				#
					self.local.resource = sqlite3.connect ((path.normpath ("{0}/{1}".format (direct_globals['settings']['path_base'],direct_globals['settings']['db_dbfile']))),isolation_level = None,detect_types = sqlite3.PARSE_DECLTYPES)
					self.local.resource.row_factory = sqlite3.Row
				#
				except Exception as f_handled_exception:
				#
					f_return = False
					self.trigger_error (("#echo(__FILEPATH__)# -db_class.connect ()- (#echo(__LINE__)#) reporting: {0!r}".format (f_handled_exception)),self.E_ERROR)
				#
			#
		#
		else: f_return = False

		return f_return
	#

	def disconnect (self):
	#
		"""
Closes an active database connection to the server.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.disconnect ()- (#echo(__LINE__)#)")

		self.thread_local_check ()

		if (self.local.resource != None):
		#
			self.local.resource.close ()
			return True
		#
		else: return False
	#

	def query_build (self,data):
	#
		"""
Builds a valid SQL query for SQLite and executes it.

@param  data Dictionary containing query specific information.
@return (mixed) Result returned by the server in the specified format
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_build (data)- (#echo(__LINE__)#)")
		f_return = False

		f_continue_check = True
		f_xml_object = direct_xml_bridge.py_get ()
		self.thread_local_check ()

		self.local.query_parameters = ( )

		if (data['type'] == "delete"):
		#
			if (len (data['table']) < 1): f_continue_check = False
			self.local.query_cache = "DELETE FROM "
		#
		elif (data['type'] == "insert"):
		#
			if ((len (data['set_attributes']) < 1) and (len (data['values']) < 1)): f_continue_check = False
			if (len (data['table']) < 1): f_continue_check = False

			self.local.query_cache = "INSERT INTO "
		#
		elif (data['type'] == "replace"):
		#
			if (len (data['table']) < 1): f_continue_check = False
			if (len (data['values']) < 1): f_continue_check = False

			self.local.query_cache = "REPLACE INTO "
		#
		elif (data['type'] == "select"):
		#
			if (data['answer'] == "nr"): data['attributes'] = [ "count-rows(*)" ]
			elif (len (data['attributes']) < 1): f_continue_check = False

			if (len (data['table']) < 1): f_continue_check = False

			self.local.query_cache = "SELECT "
		#
		elif (data['type'] == "update"):
		#
			if ((len (data['set_attributes']) < 1) and (len (data['values']) < 1)): f_continue_check = False
			if (len (data['table']) < 1): f_continue_check = False

			self.local.query_cache = "UPDATE "
		#
		else: f_continue_check = False

		if (f_continue_check):
		#
			if ((data['type'] == "select") and (len (data['attributes']) > 0)): self.local.query_cache += "{0} FROM ".format (self.query_build_attributes (data['attributes']))
			self.local.query_cache += data['table']

			if ((data['type'] == "select") and (len (data['joins']) > 0)):
			#
				for f_join_dict in data['joins']:
				#
					if (f_join_dict['type'] == "cross-join"): self.local.query_cache += " CROSS JOIN {0}".format (f_join_dict['table'])
					elif (f_join_dict['type'] == "inner-join"): self.local.query_cache += " INNER JOIN {0} ON ".format (f_join_dict['table'])
					elif (f_join_dict['type'] == "left-outer-join"): self.local.query_cache += " LEFT OUTER JOIN {0} ON ".format (f_join_dict['table'])
					elif (f_join_dict['type'] == "natural-join"): self.local.query_cache += " NATURAL JOIN {0}".format (f_join_dict['table'])
					elif (f_join_dict['type'] == "right-outer-join"): self.local.query_cache += " RIGHT OUTER JOIN {0} ON ".format (f_join_dict['table'])

					if (len (f_join_dict['requirements']) > 0):
					#
						f_xml_node_dict = f_xml_object.xml2array (f_join_dict['requirements'],strict_standard = False)
						if ("sqlconditions" in f_xml_node_dict): self.local.query_cache += self.query_build_row_conditions_walker (f_xml_node_dict['sqlconditions'])
					#
				#
			#

			if (((data['type'] == "insert") or (data['type'] == "replace") or (data['type'] == "update")) and (len (data['set_attributes']) > 0)):
			#
				f_xml_node_dict = f_xml_object.xml2array (data['set_attributes'],strict_standard = False)

				if ("sqlvalues" in f_xml_node_dict):
				#
					if (data['type'] == "update"): self.local.query_cache += " SET {0}".format (self.query_build_set_attributes (f_xml_node_dict['sqlvalues']))
					else: self.local.query_cache += " {0}".format (self.query_build_values_keys (f_xml_node_dict['sqlvalues']))
				#
			#

			if ((data['type'] == "delete") or (data['type'] == "select") or (data['type'] == "update")):
			#
				f_where_defined = False

				if (len (data['row_conditions']) > 0):
				#
					f_xml_node_dict = f_xml_object.xml2array (data['row_conditions'],strict_standard = False)

					if ("sqlconditions" in f_xml_node_dict):
					#
						f_where_defined = True
						self.local.query_cache += " WHERE {0}".format (self.query_build_row_conditions_walker (f_xml_node_dict['sqlconditions']))
					#
				#

				if (data['type'] == "select"):
				#
					if (len (data['search_conditions']) > 0):
					#
						f_xml_node_dict = f_xml_object.xml2array (data['search_conditions'],strict_standard = False)

						if ("sqlconditions" in f_xml_node_dict):
						#
							if (f_where_defined): self.local.query_cache += " AND ({0})".format (self.query_build_search_conditions (f_xml_node_dict['sqlconditions']))
							else: self.local.query_cache += " WHERE {0}".format (self.query_build_search_conditions (f_xml_node_dict['sqlconditions']))
						#
					#

					if (len (data['grouping']) > 0): self.local.query_cache += " GROUP BY {0}".format (",".join (data['grouping']))
				#
			#

			if ((data['type'] == "select") and (len (data['ordering']) > 0)):
			#
				f_xml_node_dict = f_xml_object.xml2array (data['ordering'],strict_standard = False)
				if ("sqlordering" in f_xml_node_dict): self.local.query_cache += " ORDER BY {0}".format (self.query_build_ordering (f_xml_node_dict['sqlordering']))
			#

			if ((data['type'] == "insert") or (data['type'] == "replace")):
			#
				if (data['values_keys']):
				#
					if (type (data['values_keys']) == list):
					#
						f_values_keys = ""

						for f_values_key in data['values_keys']:
						#
							if (len (f_values_keys) > 0): f_values_keys += ",?"
							else: f_values_keys += "?"

							self.local.query_parameters += ( f_values_key[(f_values_key.find (".") + 1):], )
						#

						self.local.query_cache += " ({0})".format (f_values_keys)
					#
				#

				if (len (data['values']) > 0):
				#
					f_xml_node_dict = f_xml_object.xml2array (data['values'],strict_standard = False)
					if ("sqlvalues" in f_xml_node_dict): self.local.query_cache += " VALUES {0}".format (self.query_build_values (f_xml_node_dict['sqlvalues']))
				#
			#

			if (data['type'] == "select"):
			#
				if (data['limit']):
				#
					self.local.query_cache += " LIMIT ?"
					self.local.query_parameters += ( data['limit'], )
				#

				if (data['offset']):
				#
					self.local.query_cache += " OFFSET ?"
					self.local.query_parameters += ( data['offset'], )
				#
			#

			if (data['answer'] == "sql"): f_return = self.local.query_cache
			else: f_return = self.query_exec (data['answer'],self.local.query_cache,self.local.query_parameters)
		#
		else: self.trigger_error ("#echo(__FILEPATH__)# -db_class.query_build ()- (#echo(__LINE__)#) reporting: Required definition elements are missing",self.E_WARNING)

		return f_return
	#

	def query_build_attributes (self,attributes_list):
	#
		"""
Builds the SQL attributes list of a query.

@param  attributes_list List of attributes
@return (str) Attributes list with translated function names
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_build_attributes (attributes_list)- (#echo(__LINE__)#)")
		f_return = ""

		if ((type (attributes_list) == list) and (len (attributes_list) > 0)):
		#
			f_re_attribute = re.compile ("^(.*?)\\((.*?)\\)(.*?)$")

			for f_attribute in attributes_list:
			#
				if (len (f_return) > 0): f_return += ", "
				f_result_object = f_re_attribute.match (f_attribute)

				if (f_result_object == None): f_return += f_attribute
				else:
				#
					if (f_result_object.group (1) == "count-rows"): f_return += "COUNT({0}){1}".format (f_result_object.group (2),(f_result_object.group (3)))
					elif (f_result_object.group (1) == "sum-rows"): f_return += "SUM({0}){1}".format (f_result_object.group (2),(f_result_object.group (3)))
					else: f_return += "{0}({1}){2}".format (f_result_object.group (1),(f_result_object.group (2)),(f_result_object.group (3)))
				#
			#
		#

		return f_return
	#

	def query_build_ordering (self,ordering_dict):
	#
		"""
Builds the SQL ORDER BY part of a query.

@param  ordering_dict ORDER BY list given as a XML dictionary tree
@return (str) Valid SQL ORDER BY definition
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_build_ordering (ordering_dict)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (ordering_dict) == dict):
		#
			if ("xml.item" in ordering_dict): del (ordering_dict['xml.item'])

			for f_ordering_key in ordering_dict:
			#
				f_ordering_dict = ordering_dict[f_ordering_key]
				if (len (f_return) > 0): f_return += ", "

				if (f_ordering_dict['attributes']['type'] == "desc"): f_return += "{0} DESC".format (f_ordering_dict['attributes']['attribute'])
				else: f_return += "{0} ASC".format (f_ordering_dict['attributes']['attribute'])
			#
		#

		return f_return
	#

	def query_build_row_conditions_walker (self,requirements_dict):
	#
		"""
Creates a WHERE string including sublevel conditions.

@param  requirements_dict WHERE definitions given as a XML dictionary tree
@return (str) Valid SQL WHERE definition
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_build_row_conditions_walker (requirements_dict)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (requirements_dict) == dict):
		#
			if ("xml.item" in requirements_dict): del (requirements_dict['xml.item'])

			for f_requirement_key in requirements_dict:
			#
				f_requirement_dict = requirements_dict[f_requirement_key]

				if (type (f_requirement_dict) == dict):
				#
					if ("xml.item" in f_requirement_dict):
					#
						if (len (f_return) > 0):
						#
							if (("condition" in f_requirement_dict['xml.item']['attributes']) and (f_requirement_dict['xml.item']['attributes']['condition'] == "or")): f_return += " OR "
							else: f_return += " AND "
						#

						if (len (f_requirement_dict) > 2): f_return += "({0})".format (self.query_build_row_conditions_walker (f_requirement_dict))
						else: f_return += self.query_build_row_conditions_walker (f_requirement_dict)
					#
					elif (f_requirement_dict['value'] != "*"):
					#
						if ("type" not in f_requirement_dict['attributes']): f_requirement_dict['attributes']['type'] = "string"

						if (len (f_return) > 0):
						#
							if (("condition" in f_requirement_dict['attributes']) and (f_requirement_dict['attributes']['condition'] == "or")): f_return += " OR "
							else: f_return += " AND "
						#

						if ("operator" not in f_requirement_dict['attributes']): f_requirement_dict['attributes']['operator'] = ""
						if ((f_requirement_dict['attributes']['operator'] != "!=") and (f_requirement_dict['attributes']['operator'] != "<") and (f_requirement_dict['attributes']['operator'] != "<=") and (f_requirement_dict['attributes']['operator'] != ">") and (f_requirement_dict['attributes']['operator'] != ">=")): f_requirement_dict['attributes']['operator'] = "=="
						f_return += "{0}".format (f_requirement_dict['attributes']['attribute'])

						if ("null" in f_requirement_dict['attributes']): f_return += " {0} NULL".format (f_requirement_dict['attributes']['operator'])
						elif (len (f_requirement_dict['value']) > 0):
						#
							f_return += " {0} ?".format (f_requirement_dict['attributes']['operator'])

							if ((f_requirement_dict['attributes']['type'] == "string") and (len (f_requirement_dict['value']) > 1) and (f_requirement_dict['value'][0:1] == "'")): self.local.query_parameters += ( f_requirement_dict['value'][1:-1], )
							else: self.local.query_parameters += ( f_requirement_dict['value'], )
						#
						elif (f_requirement_dict['attributes']['type'] == "string"): f_return += " {0} ''".format (f_requirement_dict['attributes']['operator'])
						else: f_return += " {0} NULL".format (f_requirement_dict['attributes']['operator'])
					#
				#
			#
		#

		return f_return
	#

	def query_build_search_conditions (self,conditions_dict):
	#
		"""
Creates search requests

@param  conditions_dict WHERE definitions given as a XML dictionary tree
@return (str) Valid SQL WHERE definition
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_build_search_conditions (conditions_dict)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (conditions_dict) == dict):
		#
			f_attributes_list = [ ]
			f_search_term = ""

			if ("xml.item" in conditions_dict): del (conditions_dict['xml.item'])

			for f_condition_name in conditions_dict:
			#
				f_condition_dict = conditions_dict[f_condition_name]

				if (type (f_condition_dict) == dict): f_dict = True
				else: f_dict = False

				if ((f_dict) and ("xml.mtree" in f_condition_dict)): f_mtree = True
				else: f_mtree = False

				if ((f_condition_name == "attribute") and (f_mtree)):
				#
					for f_condition_attribute_key in f_condition_dict:
					#
						f_condition_attribute_dict = f_condition_dict[f_condition_attribute_key]
						if ("value" in f_condition_attribute_dict): f_attributes_list.append (f_condition_attribute_dict['value'])
					#
				#
				elif ((f_condition_name == "searchterm") and (f_mtree)):
				#
					for f_condition_searchterm_key in f_condition_dict:
					#
						f_condition_searchterm_dict = f_condition_dict[f_condition_searchterm_key]
						if (("value" in f_condition_searchterm_dict) and (len (f_condition_searchterm_dict['value']) > 0)): f_search_term += f_condition_searchterm_dict['value']
					#
				#
				elif ((f_dict) and ("tag" in f_condition_dict)):
				#

					if (f_condition_dict['tag'] == "attribute"): f_attributes_list.append (f_condition_dict['value'])
					elif ((f_condition_dict['tag'] == "searchterm") and (len (f_condition_dict['value']) > 0)): f_search_term += f_condition_dict['value']
				#
			#

			if ((len (f_attributes_list) > 0) and (len (f_search_term) > 0)):
			#
				"""
----------------------------------------------------------------------------
We will split on spaces to get valid LIKE expressions for each word.
"Test Test1 AND Test2 AND Test3 Test4 Test5 Test6 AND Test7" should be
Result is: [0] => %Test% [1] => %Test1 Test2 Test3% [2] => %Test4%
           [3] => %Test5% [4] => %Test6 Test7%
----------------------------------------------------------------------------
				"""

				f_search_term = re.compile("^\\*",re.M).sub ("%",f_search_term)
				f_search_term = re.compile("(\\w)\\*").sub ("\\1%",f_search_term)
				f_search_term = f_search_term.replace (" OR "," ")
				f_search_term = f_search_term.replace (" NOT "," ")
				f_search_term = f_search_term.replace ("HIGH ","")
				f_search_term = f_search_term.replace ("LOW ","")

				f_words = f_search_term.split (" ")
				f_and_check = False
				f_search_term_list = [ ]
				f_single_check = False
				f_word_buffer = ""

				for f_word in f_words:
				#
					if (f_word == "AND"):
					#
						f_single_check = True
						f_and_check = True
						f_word_buffer += " "
					#
					elif (f_single_check):
					#
						f_single_check = False
						f_word_buffer += f_word
					#
					else:
					#
						if (f_and_check):
						#
							f_and_check = False
							f_word_buffer = "%{0}%".format (f_word_buffer.strip ())
							f_search_term_list.append (f_word_buffer.replace ("%%","%"))
							f_word_buffer = f_word
						#
						else:
						#
							if (len (f_word_buffer) > 0):
							#
								f_word_buffer = "%{0}%".format (f_word_buffer.strip ())
								f_search_term_list.append (f_word_buffer.replace ("%%","%"))
							#

							f_word_buffer = f_word
						#
					#
				#

				"""
----------------------------------------------------------------------------
Don't forget to check the buffer $f_word_buffer
----------------------------------------------------------------------------
				"""

				if (len (f_word_buffer) > 0):
				#
					f_word_buffer = "%{0}%".format (f_word_buffer.strip ())
					f_search_term_list.append (f_word_buffer.replace ("%%","%"))
				#

				for f_attribute in f_attributes_list:
				#
					for f_search_term in f_search_term_list:
					#
						if (len (f_return) > 0): f_return += " OR "
						f_return += "{0} LIKE ?".format (f_attribute)
						self.local.query_parameters += ( f_search_term, )
					#
				#
			#
		#

		return f_return
	#

	def query_build_set_attributes (self,attributes_dict):
	#
		"""
Builds the SQL attributes and values list for UPDATE.

@param  attributes_dict Attributes given as a XML dictionary tree
@return (str) Attributes list with translated function names
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_build_set_attributes (attributes_dict)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (attributes_dict) == dict):
		#
			if ("xml.item" in attributes_dict): del (attributes_dict['xml.item'])

			for f_attribute_key in attributes_dict:
			#
				f_attribute_dict = attributes_dict[f_attribute_key]

				if (len (f_return) > 0): f_return += ", {0}=".format (f_attribute_dict['attributes']['attribute'][(f_attribute_dict['attributes']['attribute'].find (".") + 1):])
				else: f_return += "{0}=".format (f_attribute_dict['attributes']['attribute'][(f_attribute_dict['attributes']['attribute'].find (".") + 1):])

				if ("null" in f_attribute_dict['attributes']): f_return += "NULL"
				elif (len (f_attribute_dict['value']) > 0):
				#
					f_return += "?"

					if ((f_attribute_dict['attributes']['type'] == "string") and (len (f_attribute_dict['value']) > 1) and (f_attribute_dict['value'][0:1] == "'")): self.local.query_parameters += ( f_attribute_dict['value'][1:-1], )
					else: self.local.query_parameters += ( f_attribute_dict['value'], )
				#
				elif (f_attribute_dict['attributes']['type'] == "string"): f_return += "''"
				else: f_return += "NULL"
			#
		#

		return f_return
	#

	def query_build_values (self,values_dict):
	#
		"""
Builds the SQL VALUES part of a query.

@param  values_dict WHERE definitions given as a XML dictionary tree
@return (str) Valid SQL VALUES definition
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_build_values (values_dict)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (values_dict) == dict):
		#
			if ("xml.item" in values_dict): del (values_dict['xml.item'])
			f_bracket_check = False

			for f_value_key in values_dict:
			#
				f_value_dict = values_dict[f_value_key]

				if ("xml.item" in f_value_dict):
				#
					if (len (f_return) > 0): f_return += ","
					f_return += self.query_build_values (f_value_dict)
				#
				else:
				#
					f_bracket_check = True

					if (len (f_return) > 0): f_return += ","
					else: f_return += "("

					if ("null" in f_value_dict['attributes']): f_return += "NULL"
					elif (len (f_value_dict['value']) > 0):
					#
						f_return += "?"

						if ((f_value_dict['attributes']['type'] == "string") and (len (f_value_dict['value']) > 1) and (f_value_dict['value'][0:1] == "'")): self.local.query_parameters += ( f_value_dict['value'][1:-1], )
						else: self.local.query_parameters += ( f_value_dict['value'], )
					#
					elif (f_value_dict['attributes']['type'] == "string"): f_return += "''"
					else: f_return += "NULL"
				#
			#

			if (f_bracket_check): f_return += ")"
		#

		return f_return
	#

	def query_build_values_keys (self,attributes_dict):
	#
		"""
Builds the SQL attributes and values list for INSERT.

@param  attributes_dict Attributes given as a XML dictionary tree
@return (str) Attributes list with translated function names
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_build_values_keys (attributes_dict)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (attributes_dict) == dict):
		#
			if ("xml.item" in attributes_dict): del (attributes_dict['xml.item'])
			f_keys = [ ]
			f_values = [ ]

			for f_attribute_key in attributes_dict:
			#
				f_attribute_dict = attributes_dict[f_attribute_key]
				f_keys.append (f_attribute_dict['attributes']['attribute'][(f_attribute_dict['attributes']['attribute'].find (".") + 1):])

				if ("null" in f_attribute_dict['attributes']): f_values.append ("NULL")
				elif (len (f_attribute_dict['value']) > 0):
				#
					f_values.append ("?")

					if ((f_attribute_dict['attributes']['type'] == "string") and (len (f_attribute_dict['value']) > 1) and (f_attribute_dict['value'][0:1] == "'")): self.local.query_parameters += ( f_attribute_dict['value'][1:-1], )
					else: self.local.query_parameters += ( f_attribute_dict['value'], )
				#
				elif (f_attribute_dict['attributes']['type'] == "string"): f_values.append ("''")
				else: f_values.append ("NULL")
			#

			f_return = "({0}) VALUES ({1})".format (",".join (f_keys),(",".join (f_values)))
		#

		return f_return
	#

	def query_exec (self,answer,query,query_params):
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
		query = direct_str (query)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.query_exec ({0},{1},query_params)- (#echo(__LINE__)#)".format (answer,query))

		f_return = False
		self.thread_local_check ()

		if (self.local.resource == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class.query_exec ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
		else:
		#
			try:
			#
				f_result_object = self.local.resource.execute (query,query_params)

				if (answer == "ar"): f_return = f_result_object.rowcount
				elif (answer == "co"): f_return = True
				elif (answer == "ma"):
				#
					f_return = [ ]
					f_row = f_result_object.fetchone ()

					while (f_row != None):
					#
						f_column = 0
						f_row_keys_list = f_row.keys ()

						f_filtered_row_dict = { }

						for f_column_data in f_row:
						#
							f_filtered_row_dict[f_row_keys_list[f_column]] = f_column_data
							f_column += 1
						#

						f_return.append (f_filtered_row_dict)
						f_row = f_result_object.fetchone ()
					#
				#
				elif (answer == "ms"):
				#
					f_return = [ ]
					f_row = f_result_object.fetchone ()

					while (f_row != None):
					#
						if (len (f_row) > 0):
						#
							f_row = ""

							for f_column_data in f_row:
							#
								if (len (f_row) > 0): f_row += "\n{0}".format (f_column_data)
								else: f_row = f_column_data
							#

							f_return.append (f_row)
						#

						f_row = f_result_object.fetchone ()
					#
				#
				elif (answer == "nr"):
				#
					f_row = f_result_object.fetchone ()
					f_return = f_row[0]
				#
				elif (answer == "sa"):
				#
					f_return = { }
					f_row = f_result_object.fetchone ()

					if (f_row != None):
					#
						f_column = 0
						f_row_keys_list = f_row.keys ()

						for f_column_data in f_row:
						#
							f_return[f_row_keys_list[f_column]] = f_column_data
							f_column += 1
						#
					#
				#
				elif (answer == "ss"):
				#
					f_return = ""
					f_row = f_result_object.fetchone ()

					if ((f_row != None) and (len (f_row) > 0)):
					#
						for f_column_data in f_row:
						#
							if (len (f_return) > 0): f_return += "\n{0}".format (f_column_data)
							else: f_return = f_column_data
						#
					#
				#
			#
			except Exception as f_handled_exception: self.trigger_error (("#echo(__FILEPATH__)# -db_class.query_exec ()- (#echo(__LINE__)#) reporting: {0!r}".format (f_handled_exception)),self.E_ERROR)
		#

		return f_return
	#

	def optimize (self,table):
	#
		"""
Optimizes a given table.

@param  table Name of the table
@return (bool) True on success
@since  v0.1.00
		"""

		table = direct_str (table)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.optimize ({0})- (#echo(__LINE__)#)".format (table))

		self.thread_local_check ()

		if (self.local.resource == None):
		#
			self.trigger_error ("#echo(__FILEPATH__)# -db_class.optimize ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
			return False
		#
		else: return True
	#

	def secure (self,data):
	#
		"""
Secures a given string to protect against SQL injections.

@param  data Input array or string
@return (mixed) Modified input or None on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.secure (data)- (#echo(__LINE__)#)")

		self.thread_local_check ()

		if (self.local.resource == None): return None
		else: return direct_str (data)
	#

	def set_trigger (self,py_function = None):
	#
		"""
Set a given function to be called for each exception or error.

@param py_function Python function to be called
@since v0.1.00
		"""

		self.error_callback = py_function
	#

	def thread_local_check (self):
	#
		"""
For thread safety some variables are defined per thread. This method makes
sure that these variables are defined.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.thread_local_check ()- (#echo(__LINE__)#)")

		if (not hasattr (self.local,"resource")):
		#
			self.local.query_cache = ""
			self.local.query_parameters = ( )
			self.local.resource = None
			self.local.transactions = 0
			self.connect ()
		#
	#

	def transaction_begin (self):
	#
		"""
Starts a transaction.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.transaction_begin ()- (#echo(__LINE__)#)")

		f_return = False
		self.thread_local_check ()

		if (self.local.resource == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class.transaction_begin ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
		else:
		#
			f_return = True
			if (self.local.transactions < 1): self.local.resource.isolation_level = "DEFERRED"
			self.local.transactions += 1
		#

		return f_return
	#

	def transaction_commit (self):
	#
		"""
Commits all transaction statements.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.transaction_commit ()- (#echo(__LINE__)#)")

		f_return = False
		self.thread_local_check ()

		if (self.local.resource == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class.transaction_commit ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
		else:
		#
			try:
			#
				if (self.local.transactions < 2):
				#
					self.local.resource.commit ()
					self.local.resource.isolation_level = None
				#

				f_return = True
				self.local.transactions -= 1
			#
			except Exception as f_handled_exception: self.trigger_error (("#echo(__FILEPATH__)# -db_class.transaction_commit ()- (#echo(__LINE__)#) reporting: {0!r}".format (f_handled_exception)),self.E_ERROR)
		#

		return f_return
	#

	def transaction_rollback (self):
	#
		"""
Calls the ROLLBACK statement.

@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class.transaction_rollback ()- (#echo(__LINE__)#)")

		f_return = False
		self.thread_local_check ()

		if (self.local.resource == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class.transaction_rollback ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
		else:
		#
			try:
			#
				if (self.local.transactions < 2):
				#
					self.local.resource.rollback ()
					self.local.resource.isolation_level = None
				#

				f_return = True
				self.local.transactions -= 1
			#
			except Exception as f_handled_exception: self.trigger_error (("#echo(__FILEPATH__)# -db_class.transaction_rollback- (#echo(__LINE__)#) reporting: {0!r}".format (f_handled_exception)),self.E_ERROR)
		#

		return f_return
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
#

##j## EOF
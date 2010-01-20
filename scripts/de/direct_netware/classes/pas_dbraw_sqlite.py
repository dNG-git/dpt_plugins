# -*- coding: utf-8 -*-
##j## BOF

"""n// NOTE
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
NOTE_END //n"""
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
@license    http://www.direct-netware.de/redirect.php?licenses;w3c
            W3C (R) Software License
"""

from de.direct_netware.classes.pas_debug import direct_debug
from de.direct_netware.classes.pas_settings import direct_settings
from de.direct_netware.classes.pas_xml_bridge import direct_xml_bridge
from threading import local
import re,sqlite3

class direct_dbraw_sqlite (object):
#
	"""
This class has been designed to be used with a SQLite database.

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
Constructor __init__ (direct_dbraw_sqlite)

@since v0.1.00
		"""

		self.debug = direct_debug.get ()
		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->__construct (direct_dbraw_sqlite)- (#echo(__LINE__)#)")
		self.local = local ()
	#

	def __del__ (self):
	#
		"""
Destructor __del__ (direct_dbraw_sqlite)

@since v0.1.00
		"""

		self.del_direct_dbraw_sqlite ()
	#

	def del_direct_dbraw_sqlite (self):
	#
		"""
Destructor del_direct_dbraw_sqlite (direct_dbraw_sqlite)

@since v0.1.00
		"""

		direct_debug.py_del ()
		self.disconnect ()
	#

	def connect (self):
	#
		"""
Opens the connection to a database server and selects a database.

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->connect ()- (#echo(__LINE__)#)")

		f_return = True
		f_settings = direct_settings.get ()
		self.thread_local_check ()

		if ("db_dbfile" in f_settings):
		#
			if (self.local.resource == None):
			#
				try:
				#
					self.local.resource = sqlite3.connect (f_settings['db_dbfile'],isolation_level = None,detect_types = sqlite3.PARSE_DECLTYPES)
					self.local.resource.row_factory = sqlite3.Row
				#
				except Exception,f_handled_exception:
				#
					f_return = False
					self.trigger_error ("#echo(__FILEPATH__)# -db_class->dispatch ()- (#echo(__LINE__)#) reporting: %s" % f_handled_exception,self.E_ERROR)
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

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->disconnect ()- (#echo(__LINE__)#)")

		self.thread_local_check ()

		if (self.local.resource != None):
		#
			self.local.resource.close ()
			return True
		#
		else: return False
	#

	def query_build (self,f_data):
	#
		"""
Builds a valid SQL query for SQLite and executes it.

@param  f_data Array containing query specific information.
@return (mixed) Result returned by the server in the specified format
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_build (+f_data)- (#echo(__LINE__)#)")
		f_return = False

		f_continue_check = True
		f_xml_object = direct_xml_bridge.get_xml_bridge ()
		self.thread_local_check ()

		self.local.query_parameters = ( )

		if (f_data['type'] == "delete"):
		#
			if (len (f_data['table']) < 1): f_continue_check = False
			self.local.query_cache = "DELETE FROM "
		#
		elif (f_data['type'] == "insert"):
		#
			if ((len (f_data['set_attributes']) < 1) and (len (f_data['values']) < 1)): f_continue_check = False
			if (len (f_data['table']) < 1): f_continue_check = False

			self.local.query_cache = "INSERT INTO "
		#
		elif (f_data['type'] == "replace"):
		#
			if (len (f_data['table']) < 1): f_continue_check = False
			if (len (f_data['values']) < 1): f_continue_check = False

			self.local.query_cache = "REPLACE INTO "
		#
		elif (f_data['type'] == "select"):
		#
			if (f_data['answer'] == "nr"): f_data['attributes'] = [ "count-rows(*)" ]
			elif (len (f_data['attributes']) < 1): f_continue_check = False

			if (len (f_data['table']) < 1): f_continue_check = False

			self.local.query_cache = "SELECT "
		#
		elif (f_data['type'] == "update"):
		#
			if ((len (f_data['set_attributes']) < 1) and (len (f_data['values']) < 1)): f_continue_check = False
			if (len (f_data['table']) < 1): f_continue_check = False

			self.local.query_cache = "UPDATE "
		#
		else: f_continue_check = False

		if (f_continue_check):
		#
			if ((f_data['type'] == "select") and (len (f_data['attributes']) > 0)): self.local.query_cache += "%s FROM " % self.query_build_attributes (f_data['attributes'])
			self.local.query_cache += f_data['table']

			if ((f_data['type'] == "select") and (len (f_data['joins']) > 0)):
			#
				for f_join_array in f_data['joins']:
				#
					if (f_join_array['type'] == "cross-join"): self.local.query_cache += " CROSS JOIN %s" % f_join_array['table']
					elif (f_join_array['type'] == "inner-join"): self.local.query_cache += " INNER JOIN %s ON " % f_join_array['table']
					elif (f_join_array['type'] == "left-outer-join"): self.local.query_cache += " LEFT OUTER JOIN %s ON " % f_join_array['table']
					elif (f_join_array['type'] == "natural-join"): self.local.query_cache += " NATURAL JOIN %s" % f_join_array['table']
					elif (f_join_array['type'] == "right-outer-join"): self.local.query_cache += " RIGHT OUTER JOIN %s ON " % f_join_array['table']

					if (len (f_join_array['requirements']) > 0):
					#
						f_xml_node_array = f_xml_object.xml2array (f_join_array['requirements'],f_strict_standard = False)
						if ("sqlconditions" in f_xml_node_array): self.local.query_cache += self.query_build_row_conditions_walker (f_xml_node_array['sqlconditions'])
					#
				#
			#

			if (((f_data['type'] == "insert") or (f_data['type'] == "replace") or (f_data['type'] == "update")) and (len (f_data['set_attributes']) > 0)):
			#
				f_xml_node_array = f_xml_object.xml2array (f_data['set_attributes'],f_strict_standard = False)

				if ("sqlvalues" in f_xml_node_array):
				#
					if (f_data['type'] == "update"): self.local.query_cache += " SET %s" % self.query_build_set_attributes (f_xml_node_array['sqlvalues'])
					else: self.local.query_cache += " %s" % self.query_build_values_keys (f_xml_node_array['sqlvalues'])
				#
			#

			if ((f_data['type'] == "delete") or (f_data['type'] == "select") or (f_data['type'] == "update")):
			#
				f_where_defined = False

				if (len (f_data['row_conditions']) > 0):
				#
					f_xml_node_array = f_xml_object.xml2array (f_data['row_conditions'],f_strict_standard = False)

					if ("sqlconditions" in f_xml_node_array):
					#
						f_where_defined = True
						self.local.query_cache += " WHERE %s" % self.query_build_row_conditions_walker (f_xml_node_array['sqlconditions'])
					#
				#

				if (f_data['type'] == "select"):
				#
					if (len (f_data['search_conditions']) > 0):
					#
						f_xml_node_array = f_xml_object.xml2array (f_data['search_conditions'],f_strict_standard = False)

						if ("sqlconditions" in f_xml_node_array):
						#
							if (f_where_defined): self.local.query_cache += " AND (%s)" % self.query_build_search_conditions (f_xml_node_array['sqlconditions'])
							else: self.local.query_cache += " WHERE %s" % self.query_build_search_conditions (f_xml_node_array['sqlconditions'])
						#
					#

					if (len (f_data['grouping']) > 0): self.local.query_cache += " GROUP BY %s" % ",".join (f_data['grouping'])
				#
			#

			if ((f_data['type'] == "select") and (len (f_data['ordering']) > 0)):
			#
				f_xml_node_array = f_xml_object.xml2array (f_data['ordering'],f_strict_standard = False)
				if ("sqlordering" in f_xml_node_array): self.local.query_cache += " ORDER BY %s" % self.query_build_ordering (f_xml_node_array['sqlordering'])
			#

			if ((f_data['type'] == "insert") or (f_data['type'] == "replace")):
			#
				if (f_data['values_keys']):
				#
					if (type (f_data['values_keys']) == list):
					#
						f_values_keys = ""

						for f_values_key in f_data['values_keys']:
						#
							if (len (f_values_keys) > 0): f_values_keys += ",?"
							else: f_values_keys += "?"

							self.local.query_parameters += ( f_values_key[(f_values_key.find (".") + 1):], )
						#

						self.local.query_cache += " (%s)" % f_values_keys
					#
				#

				if (len (f_data['values']) > 0):
				#
					f_xml_node_array = f_xml_object.xml2array (f_data['values'],f_strict_standard = False)
					if ("sqlvalues" in f_xml_node_array): self.local.query_cache += " VALUES %s" % self.query_build_values (f_xml_node_array['sqlvalues'])
				#
			#

			if (f_data['type'] == "select"):
			#
				if (f_data['limit']):
				#
					self.local.query_cache += " LIMIT ?"
					self.local.query_parameters += ( f_data['limit'], )
				#

				if (f_data['offset']):
				#
					self.local.query_cache += " OFFSET ?"
					self.local.query_parameters += ( f_data['offset'], )
				#
			#

			if (f_data['answer'] == "sql"): f_return = self.local.query_cache
			else: f_return = self.query_exec (f_data['answer'],self.local.query_cache,self.local.query_parameters)
		#
		else: self.trigger_error ("#echo(__FILEPATH__)# -db_class->query_build ()- (#echo(__LINE__)#) reporting: Required definition elements are missing",self.E_WARNING)

		return f_return
	#

	def query_build_attributes (self,f_attributes_array):
	#
		"""
Builds the SQL attributes list of a query.

@param  f_attributes_array Array of attributes
@return (string) Attributes list with translated function names
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_build_attributes (+f_attributes_array)- (#echo(__LINE__)#)")
		f_return = ""

		if ((type (f_attributes_array) == list) and (len (f_attributes_array) > 0)):
		#
			f_re_attribute = re.compile ("^(.*?)\\((.*?)\\)(.*?)$")

			for f_attribute in f_attributes_array:
			#
				if (len (f_return) > 0): f_return += ", "
				f_result_object = f_re_attribute.match (f_attribute)

				if (f_result_object == None): f_return += f_attribute
				else:
				#
					if (f_result_object.group (1) == "count-rows"): f_return += "COUNT(%s)%s" % ( f_result_object.group (2),f_result_object.group (3) )
					elif (f_result_object.group (1) == "sum-rows"): f_return += "SUM(%s)%s" % ( f_result_object.group (2),f_result_object.group (3) )
					else: f_return += "%s(%s)%s" % ( f_result_object.group (1),f_result_object.group (2),f_result_object.group (3) )
				#
			#
		#

		return f_return
	#

	def query_build_ordering (self,f_ordering_list):
	#
		"""
Builds the SQL ORDER BY part of a query.

@param  f_ordering_list ORDER BY list given as a XML array tree
@return (string) Valid SQL ORDER BY definition
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_build_ordering (+f_ordering_list)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (f_ordering_list) == dict):
		#
			if ("xml.item" in f_ordering_list): del (f_ordering_list['xml.item'])

			for f_ordering_key in f_ordering_list:
			#
				f_ordering_array = f_ordering_list[f_ordering_key]
				if (len (f_return) > 0): f_return += ", "

				if (f_ordering_array['attributes']['type'] == "desc"): f_return += "%s DESC" % f_ordering_array['attributes']['attribute']
				else: f_return += "%s ASC" % f_ordering_array['attributes']['attribute']
			#
		#

		return f_return
	#

	def query_build_row_conditions_walker (self,f_requirements_array):
	#
		"""
Creates a WHERE string including sublevel conditions.

@param  f_requirements_array WHERE definitions given as a XML array tree
@return (string) Valid SQL WHERE definition
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_build_row_conditions_walker (+f_requirements_array)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (f_requirements_array) == dict):
		#
			if ("xml.item" in f_requirements_array): del (f_requirements_array['xml.item'])

			for f_requirement_key in f_requirements_array:
			#
				f_requirement_array = f_requirements_array[f_requirement_key]

				if (type (f_requirement_array) == dict):
				#
					if ("xml.item" in f_requirement_array):
					#
						if (len (f_return) > 0):
						#
							if (("condition" in f_requirement_array['xml.item']['attributes']) and (f_requirement_array['xml.item']['attributes']['condition'] == "or")): f_return += " OR "
							else: f_return += " AND "
						#

						if (len (f_requirement_array) > 2): f_return += "(%s)" % self.query_build_row_conditions_walker (f_requirement_array)
						else: f_return += self.query_build_row_conditions_walker (f_requirement_array)
					#
					elif (f_requirement_array['value'] != "*"):
					#
						if (not "type" in f_requirement_array['attributes']): f_requirement_array['attributes']['type'] = "string"

						if (len (f_return) > 0):
						#
							if (("condition" in f_requirement_array['attributes']) and (f_requirement_array['attributes']['condition'] == "or")): f_return += " OR "
							else: f_return += " AND "
						#

						if (not "operator" in f_requirement_array['attributes']): f_requirement_array['attributes']['operator'] = ""
						if ((f_requirement_array['attributes']['operator'] != "!=") and (f_requirement_array['attributes']['operator'] != "<") and (f_requirement_array['attributes']['operator'] != "<=") and (f_requirement_array['attributes']['operator'] != ">") and (f_requirement_array['attributes']['operator'] != ">=")): f_requirement_array['attributes']['operator'] = "=="
						f_return += "%s" % f_requirement_array['attributes']['attribute']

						if ("null" in f_requirement_array['attributes']): f_return += " %s NULL" % f_requirement_array['attributes']['operator']
						elif (len (f_requirement_array['value']) > 0):
						#
							f_return += " %s ?" % f_requirement_array['attributes']['operator']

							if ((f_requirement_array['attributes']['type'] == "string") and (len (f_requirement_array['value']) > 1) and (f_requirement_array['value'][0:1] == "'")): self.local.query_parameters += ( f_requirement_array['value'][1:-1], )
							else: self.local.query_parameters += ( f_requirement_array['value'], )
						#
						elif (f_requirement_array['attributes']['type'] == "string"): f_return += " %s ''" % f_requirement_array['attributes']['operator']
						else: f_return += " %s NULL" % f_requirement_array['attributes']['operator']
					#
				#
			#
		#

		return f_return
	#

	def query_build_search_conditions (self,f_conditions_array):
	#
		"""
Creates search requests

@param  array $f_conditions_array WHERE definitions given as a XML array tree
@return (string) Valid SQL WHERE definition
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_build_search_conditions (+f_conditions_array)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (f_conditions_array) == dict):
		#
			f_attributes_array = [ ]
			f_search_term = ""

			if ("xml.item" in f_conditions_array): del (f_conditions_array['xml.item'])

			for f_condition_name in f_conditions_array:
			#
				f_condition_array = f_conditions_array[f_condition_name]

				if (type (f_condition_array) == dict): f_dict = True
				else: f_dict = False

				if ((f_dict) and ("xml.mtree" in f_condition_array)): f_mtree = True
				else: f_mtree = False

				if ((f_condition_name == "attribute") and (f_mtree)):
				#
					for f_condition_attribute_key in f_condition_array:
					#
						f_condition_attribute_array = f_condition_array[f_condition_attribute_key]
						if ("value" in f_condition_attribute_array): f_attributes_array.append (f_condition_attribute_array['value'])
					#
				#
				elif ((f_condition_name == "searchterm") and (f_mtree)):
				#
					for f_condition_searchterm_key in f_condition_array:
					#
						f_condition_searchterm_array = f_condition_array[f_condition_searchterm_key]
						if (("value" in f_condition_searchterm_array) and (len (f_condition_searchterm_array['value']) > 0)): f_search_term += f_condition_searchterm_array['value']
					#
				#
				elif ((f_dict) and ("tag" in f_condition_array)):
				#

					if (f_condition_array['tag'] == "attribute"): f_attributes_array.append (f_condition_array['value'])
					elif ((f_condition_array['tag'] == "searchterm") and (len (f_condition_array['value']) > 0)): f_search_term += f_condition_array['value']
				#
			#

			if ((len (f_attributes_array) > 0) and (len (f_search_term) > 0)):
			#
				"""
----------------------------------------------------------------------------
We will split on spaces to get valid LIKE expressions for each word.
"Test Test1 AND Test2 AND Test3 Test4 Test5 Test6 AND Test7" should be
Result is: [0] => %Test% [1] => %Test1 Test2 Test3% [2] => %Test4%
           [3] => %Test5% [4] => %Test6 Test7%
----------------------------------------------------------------------------
				"""

				f_search_term = re.compile("^\\*",re.M).sub ("%%",f_search_term)
				f_search_term = re.compile("(\\w)\\*").sub ("\\1%%",f_search_term)
				f_search_term = f_search_term.replace (" OR "," ")
				f_search_term = f_search_term.replace (" NOT "," ")
				f_search_term = f_search_term.replace ("HIGH ","")
				f_search_term = f_search_term.replace ("LOW ","")

				f_words = f_search_term.split (" ")
				f_and_check = False
				f_search_term_array = [ ]
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
							f_word_buffer = "%%%s%%" % f_word_buffer.strip ()
							f_search_term_array.append (f_word_buffer.replace ("%%%%","%%"))
							f_word_buffer = f_word
						#
						else:
						#
							if (len (f_word_buffer) > 0):
							#
								f_word_buffer = "%%%s%%" % f_word_buffer.strip ()
								f_search_term_array.append (f_word_buffer.replace ("%%%%","%%"))
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
					f_word_buffer = "%%%s%%" % f_word_buffer.strip ()
					f_search_term_array.append (f_word_buffer.replace ("%%%%","%%"))
				#

				for f_attribute in f_attributes_array:
				#
					for f_search_term in f_search_term_array:
					#
						if (len (f_return) > 0): f_return += " OR "
						f_return += "%s LIKE ?" % f_attribute
						self.local.query_parameters += ( f_search_term, )
					#
				#
			#
		#

		return f_return
	#

	def query_build_set_attributes (self,f_attributes_array):
	#
		"""
Builds the SQL attributes and values list for UPDATE.

@param  f_attributes_array Attributes given as a XML array tree
@return (string) Attributes list with translated function names
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_build_set_attributes (+f_attributes_array)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (f_attributes_array) == dict):
		#
			if ("xml.item" in f_attributes_array): del (f_attributes_array['xml.item'])

			for f_attribute_key in f_attributes_array:
			#
				f_attribute_array = f_attributes_array[f_attribute_key]

				if (len (f_return) > 0): f_return += ", %s=" % f_attribute_array['attributes']['attribute'][(f_attribute_array['attributes']['attribute'].find (".") + 1):]
				else: f_return += "%s=" % f_attribute_array['attributes']['attribute'][(f_attribute_array['attributes']['attribute'].find (".") + 1):]

				if ("null" in f_attribute_array['attributes']): f_return += "NULL"
				elif (len (f_attribute_array['value']) > 0):
				#
					f_return += "?"

					if ((f_attribute_array['attributes']['type'] == "string") and (len (f_attribute_array['value']) > 1) and (f_attribute_array['value'][0:1] == "'")): self.local.query_parameters += ( f_attribute_array['value'][1:-1], )
					else: self.local.query_parameters += ( f_attribute_array['value'], )
				#
				elif (f_attribute_array['attributes']['type'] == "string"): f_return += "''"
				else: f_return += "NULL"
			#
		#

		return f_return
	#

	def query_build_values (self,f_values_array):
	#
		"""
Builds the SQL VALUES part of a query.

@param  f_values_array WHERE definitions given as a XML array tree
@return (string) Valid SQL VALUES definition
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_build_values (+f_values_array)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (f_values_array) == dict):
		#
			if ("xml.item" in f_values_array): del (f_values_array['xml.item'])
			f_bracket_check = False

			for f_value_key in f_values_array:
			#
				f_value_array = f_values_array[f_value_key]

				if ("xml.item" in f_value_array):
				#
					if (len (f_return) > 0): f_return += ","
					f_return += self.query_build_values (f_value_array)
				#
				else:
				#
					f_bracket_check = True

					if (len (f_return) > 0): f_return += ","
					else: f_return += "("

					if ("null" in f_value_array['attributes']): f_return += "NULL"
					elif (len (f_value_array['value']) > 0):
					#
						f_return += "?"

						if ((f_value_array['attributes']['type'] == "string") and (len (f_value_array['value']) > 1) and (f_value_array['value'][0:1] == "'")): self.local.query_parameters += ( f_value_array['value'][1:-1], )
						else: self.local.query_parameters += ( f_value_array['value'], )
					#
					elif (f_value_array['attributes']['type'] == "string"): f_return += "''"
					else: f_return += "NULL"
				#
			#

			if (f_bracket_check): f_return += ")"
		#

		return f_return
	#

	def query_build_values_keys (self,f_attributes_array):
	#
		"""
Builds the SQL attributes and values list for INSERT.

@param  f_attributes_array Attributes given as a XML array tree
@return (string) Attributes list with translated function names
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_build_values_keys (+f_attributes_array)- (#echo(__LINE__)#)")
		f_return = ""

		if (type (f_attributes_array) == dict):
		#
			if ("xml.item" in f_attributes_array): del (f_attributes_array['xml.item'])
			f_keys = [ ]
			f_values = [ ]

			for f_attribute_key in f_attributes_array:
			#
				f_attribute_array = f_attributes_array[f_attribute_key]
				f_keys.append (f_attribute_array['attributes']['attribute'][(f_attribute_array['attributes']['attribute'].find (".") + 1):])

				if ("null" in f_attribute_array['attributes']): f_values.append ("NULL")
				elif (len (f_attribute_array['value']) > 0):
				#
					f_values.append ("?")

					if ((f_attribute_array['attributes']['type'] == "string") and (len (f_attribute_array['value']) > 1) and (f_attribute_array['value'][0:1] == "'")): self.local.query_parameters += ( f_attribute_array['value'][1:-1], )
					else: self.local.query_parameters += ( f_attribute_array['value'], )
				#
				elif (f_attribute_array['attributes']['type'] == "string"): f_values.append ("''")
				else: f_values.append ("NULL")
			#

			f_return = "(%s) VALUES (%s)" % ( (",".join (f_keys)),(",".join (f_values)) )
		#

		return f_return
	#

	def query_exec (self,f_answer,f_query,f_query_params):
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

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->query_exec (%s,%s,+f_query_params)- (#echo(__LINE__)#)" % ( f_answer,f_query ))

		f_return = False
		self.thread_local_check ()

		if (self.local.resource == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class->dispatch ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
		else:
		#
			try:
			#
				f_result_object = self.local.resource.execute (f_query,f_query_params)

				if (f_answer == "ar"): f_return = f_result_object.rowcount
				elif (f_answer == "co"): f_return = True
				elif (f_answer == "ma"):
				#
					f_return = [ ]
					f_row_array = f_result_object.fetchone ()

					while (f_row_array != None):
					#
						f_column = 0
						f_row_keys_array = f_row_array.keys ()

						f_filtered_row_array = { }

						for f_column_data in f_row_array:
						#
							f_filtered_row_array[f_row_keys_array[f_column]] = f_column_data
							f_column += 1
						#

						f_return.append (f_filtered_row_array)
						f_row_array = f_result_object.fetchone ()
					#
				#
				elif (f_answer == "ms"):
				#
					f_return = [ ]
					f_row_array = f_result_object.fetchone ()

					while (f_row_array != None):
					#
						if (len (f_row_array) > 0):
						#
							f_row = ""

							for f_column_data in f_row_array:
							#
								if (len (f_row) > 0): f_row += "\n%s" % f_column_data
								else: f_row = f_column_data
							#

							f_return.append (f_row)
						#

						f_row_array = f_result_object.fetchone ()
					#
				#
				elif (f_answer == "nr"):
				#
					f_row_array = f_result_object.fetchone ()
					f_return = f_row_array[0]
				#
				elif (f_answer == "sa"):
				#
					f_return = { }
					f_row_array = f_result_object.fetchone ()

					if (f_row_array != None):
					#
						f_column = 0
						f_row_keys_array = f_row_array.keys ()

						for f_column_data in f_row_array:
						#
							f_return[f_row_keys_array[f_column]] = f_column_data
							f_column += 1
						#
					#
				#
				elif (f_answer == "ss"):
				#
					f_return = ""
					f_row_array = f_result_object.fetchone ()

					if ((f_row_array != None) and (len (f_row_array) > 0)):
					#
						for f_column_data in f_row_array:
						#
							if (len (f_return) > 0): f_return += "\n%s" % f_column_data
							else: f_return = f_column_data
						#
					#
				#
			#
			except Exception,f_handled_exception: self.trigger_error ("#echo(__FILEPATH__)# -db_class->dispatch ()- (#echo(__LINE__)#) reporting: %s" % f_handled_exception,self.E_ERROR)
		#

		return f_return
	#

	def optimize (self,f_table):
	#
		"""
Optimizes a given table.

@param  f_table Name of the table
@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->optimize (%s)- (#echo(__LINE__)#)" % f_table)

		self.thread_local_check ()

		if (self.local.resource == None):
		#
			self.trigger_error ("#echo(__FILEPATH__)# -db_class->optimize ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
			return False
		#
		else: return True
	#

	def secure (self,f_data):
	#
		"""
Secures a given string to protect against SQL injections.

@param  f_data Input array or string; $f_data is NULL if there is no valid
        SQL resource. 
@return (mixed) Modified input or None on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->secure (+f_data)- (#echo(__LINE__)#)")

		self.thread_local_check ()

		if (self.local.resource == None): return None
		else: return f_data
	#

	def set_trigger (self,f_function = None):
	#
		"""
Set a given function to be called for each exception or error.

@param f_function Python function to be called
@since v0.1.00
		"""

		self.error_callback = f_function
	#

	def thread_local_check (self):
	#
		"""
Constructor __init__ (direct_dbraw_sqlite)

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->thread_local_check ()- (#echo(__LINE__)#)")

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

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->transaction_begin ()- (#echo(__LINE__)#)")

		f_return = False
		self.thread_local_check ()

		if (self.local.resource == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class->dispatch ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
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

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->transaction_commit ()- (#echo(__LINE__)#)")

		f_return = False
		self.thread_local_check ()

		if (self.local.resource == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class->dispatch ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
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
			except Exception,f_handled_exception: self.trigger_error ("#echo(__FILEPATH__)# -db_class->dispatch ()- (#echo(__LINE__)#) reporting: %s" % f_handled_exception,self.E_ERROR)
		#

		return f_return
	#

	def transaction_rollback (self):
	#
		"""
Calls the ROLLBACK statement.

@return (boolean) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -db_class->transaction_rollback ()- (#echo(__LINE__)#)")

		f_return = False
		self.thread_local_check ()

		if (self.local.resource == None): self.trigger_error ("#echo(__FILEPATH__)# -db_class->dispatch ()- (#echo(__LINE__)#) reporting: Database resource invalid",self.E_WARNING)
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
			except Exception,f_handled_exception: self.trigger_error ("#echo(__FILEPATH__)# -db_class->dispatch ()- (#echo(__LINE__)#) reporting: %s" % f_handled_exception,self.E_ERROR)
		#

		return f_return
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
#

##j## EOF
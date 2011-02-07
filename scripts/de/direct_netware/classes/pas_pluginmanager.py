# -*- coding: utf-8 -*-
##j## BOF

"""
Our main abstraction layer for plugins is the plugin manager. It registers
and identifies hooks.

@internal   We are using epydoc (JavaDoc style) to automate the
            documentation process for creating the Developer's Manual.
            Use the following line to ensure 76 character sizes:
----------------------------------------------------------------------------
@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    pas_basic
@subpackage plugins
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;w3c
            W3C (R) Software License
"""
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

from os import path
import imp,os

from .pas_globals import direct_globals
from .pas_logger import direct_logger
from .pas_pythonback import direct_str

_direct_pluginmanager = None
_direct_pluginmanager_base_dir = None
_direct_pluginmanager_counter = 0
_direct_pluginmanager_list = { }

class direct_plugin_hooks (object):
#
	"""
The direct_plugin_hooks class provides static helper functions.

@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    pas_basic
@subpackage plugins
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;w3c
            W3C (R) Software License
	"""

	def call (hook,**params):
	#
		"""
Call all functions registered for the hook with the specified parameters.

@param  hook Hook-ID
@param  params Keyword parameters
@return (mixed) Hook results on success; None if not defined
@since  v0.1.00
		"""

		global _direct_pluginmanager
		return _direct_pluginmanager.call_hook_handler (hook,params)
	#
	call = staticmethod (call)

	def register (hook,py_function,prepend = False,exclusive = False):
	#
		"""
Register a python function for the hook.

@param  hook Hook-ID
@param  py_function Python function to be registered
@param  prepend Add function at the beginning of the stack if true.
@param  exclusive Add the given function exclusively.
@since  v0.1.00
		"""

		global _direct_pluginmanager
		_direct_pluginmanager.register_hook (hook,py_function,prepend,exclusive)
	#
	register = staticmethod (register)
#

class direct_pluginmanager (object):
#
	"""
The direct_pluginmanager class provides hook-based Python plugins.

@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    pas_basic
@subpackage plugins
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;w3c
            W3C (R) Software License
	"""

	debug = None
	"""
Debug message container
	"""
	hooks = { }
	"""
Registered hook array
	"""
	pluginmanager = None
	"""
Registered plugin manager instance
	"""

	def __init__ (self,module_package,base_dir = ""):
	#
		"""
Constructor

@param module_package Module path to be scanned for *.py files
@param base_dir Base directory for plugin modules
@since v0.1.00
		"""

		global _direct_pluginmanager

		if (_direct_pluginmanager == None):
		#
			f_module_packages = [ "de.direct_netware.plugins" ]

			self.pluginmanager = self
			_direct_pluginmanager = self
			self.hooks = { }
		#
		else:
		#
			f_module_packages = [ ]
			self.pluginmanager = _direct_pluginmanager
		#

		self.debug = direct_globals['debug']
		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -pluginmanager.__init__ (direct_pluginmanager)- (#echo(__LINE__)#)")

		module_package = direct_str (module_package)
		f_type = type (module_package)

		if (f_type == list): f_module_packages += module_package
		elif (f_type == str): f_module_packages.append (module_package)

		if (len (base_dir) < 1): base_dir = direct_pluginmanager.plugins_base_dir_get ()
		if ((len (base_dir)) and (not base_dir.endswith ("/")) and (not base_dir.endswith ("\\"))): base_dir += path.sep

		for f_module_package in f_module_packages: self.load_module (f_module_package,base_dir)
	#

	def call_hook (self,hook,**params):
	#
		"""
Call the helper function to run all functions registered for the hook.

@param  hook Hook-ID
@return (mixed) Hook results on success; None if not defined
@since  v0.1.00
		"""

		return self.pluginmanager.call_hook_handler (hook,params)
	#

	def call_hook_handler (self,hook,params):
	#
		"""
Call all functions registered for the hook with the specified parameters.

@param  hook Hook-ID
@return (mixed) Data expected to be returned by the hook
@since  v0.1.00
		"""

		hook = direct_str (hook)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -pluginmanager.call_hook_handler ({0},params)- (#echo(__LINE__)#)".format (hook))
		f_return = None

		if (not "hook" in params): params['hook'] = hook

		if ((hook in self.pluginmanager.hooks) and (type (self.pluginmanager.hooks[hook]) == list)):
		#
			for f_function in self.pluginmanager.hooks[hook]:
			#
				try: f_return = f_function (params,last_return = f_return)
				except Exception as f_handled_exception:
				#
					direct_logger.critical (f_handled_exception)
					f_return = None
				#
			#
		#

		return f_return
	#

	def load_module (self,module_package,base_dir):
	#
		"""
Import the module and register all defined hooks.

@param module_package Module path to be scanned for *.py files
@param base_dir Base directory for plugin modules
@since  v0.1.00
		"""

		module_package = direct_str (module_package)
		base_dir = direct_str (base_dir)

		global _direct_pluginmanager_list
		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -pluginmanager.load_module ({0},{1})- (#echo(__LINE__)#)".format ( module_package,base_dir ))

		_direct_pluginmanager_list[module_package] = base_dir

		try:
		#
			( f_module_path,f_module_name ) = module_package.rsplit (".",1)
			f_path = f_module_path.replace (".",path.sep)

			imp.acquire_lock ()
			( f_file_object,f_file_path,f_pydescription ) = imp.find_module (f_module_name,[ base_dir + f_path ])
			imp.load_module (module_package,f_file_object,f_file_path,f_pydescription)
			if (f_file_object != None): f_file_object.close ()

			imp.release_lock ()
		#
		except Exception as f_handled_exception: direct_logger.critical (f_handled_exception)

		module_package += "."
		f_path = module_package.replace (".",path.sep)

		if (path.isdir (base_dir + f_path)):
		#
			f_dir_array = os.listdir (base_dir + f_path)

			for f_entry in f_dir_array:
			#
				if ((f_entry.endswith (".py")) and (f_entry != "__init__.py")):
				#
					f_file_object = None
					f_module_name = f_entry[:(len (f_entry) - 3)]

					imp.acquire_lock ()

					try:
					#
						( f_file_object,f_file_path,f_pydescription ) = imp.find_module (f_module_name,[ base_dir + f_path ])
						f_module = imp.load_module ((module_package + f_module_name),f_file_object,f_file_path,f_pydescription)
						if (f_file_object != None): f_file_object.close ()

						if (hasattr (f_module,"plugin_registration")): f_module.plugin_registration ()
					#
					except Exception as f_handled_exception: direct_logger.critical (f_handled_exception)

					imp.release_lock ()
				#
			#
		#
	#

	def register_hook (self,hook,py_function,prepend = False,exclusive = False):
	#
		"""
Register a python function for the hook.

@param  hook Hook-ID
@param  py_function Python function to be registered
@param  prepend Add function at the beginning of the stack if true.
@param  exclusive Add the given function exclusively.
@since  v0.1.00
		"""

		hook = direct_str (hook)

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -pluginmanager.register_hook ({0},py_function,prepend,exclusive)- (#echo(__LINE__)#)".format (hook))

		if (exclusive): self.pluginmanager.hooks[hook] = [ py_function ]
		else:
		#
			if (not hook in self.pluginmanager.hooks): self.pluginmanager.hooks[hook] = [ ]

			if (prepend): self.pluginmanager.hooks[hook].insert (0,py_function)
			else: self.pluginmanager.hooks[hook].append (py_function)
		#
	#

	def plugins_base_dir_get ():
	#
		"""
Get the default base directory where plugin modules will be searched in.

@return (str) Base directory for plugin modules
@since v0.1.00
		"""

		global _direct_pluginmanager_base_dir
		if (_direct_pluginmanager_base_dir == None): direct_pluginmanager.plugins_base_dir_set ("{0}/scripts".format (direct_globals['settings']['path_base']))
		return _direct_pluginmanager_base_dir
	#
	plugins_base_dir_get = staticmethod (plugins_base_dir_get)

	def plugins_base_dir_set (base_dir):
	#
		"""
Set a default base directory where plugin modules will be searched in.

@param base_dir Base directory for plugin modules
@since v0.1.00
		"""

		global _direct_pluginmanager_base_dir

		base_dir = direct_str (base_dir)
		if ((len (base_dir)) and (not base_dir.endswith ("/")) and (not base_dir.endswith ("\\"))): base_dir += path.sep
		_direct_pluginmanager_base_dir = base_dir
	#
	plugins_base_dir_set = staticmethod (plugins_base_dir_set)

	def py_del ():
	#
		"""
The last "py_del ()" call will activate the Python singleton destructor.

@since v0.1.00
		"""

		global _direct_pluginmanager,_direct_pluginmanager_counter

		_direct_pluginmanager_counter -= 1
		if (_direct_pluginmanager_counter == 0): _direct_pluginmanager = None
	#
	py_del = staticmethod (py_del)

	def py_get (count = False):
	#
		"""
Get the direct_pluginmanager singleton.

@param  count Count "get ()" request
@return (direct_pluginmanager) Object on success; None if not initialized
@since  v0.1.00
		"""

		global _direct_pluginmanager,_direct_pluginmanager_counter
		if (count): _direct_pluginmanager_counter += 1

		return _direct_pluginmanager
	#
	py_get = staticmethod (py_get)
#

##j## EOF
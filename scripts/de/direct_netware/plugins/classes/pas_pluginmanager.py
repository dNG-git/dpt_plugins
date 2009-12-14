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
de.direct_netware.plugins.classes.direct_pluginmanager

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

from de.direct_netware.classes.pas_debug import direct_debug
from de.direct_netware.classes.pas_settings import direct_settings
from os import path
import imp,os

_direct_pluginmanager = None
_direct_pluginmanager_base_dir = "%s/scripts" % direct_settings.get()['path_base']
_direct_pluginmanager_counter = 0

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

	@staticmethod
	def call (f_hook,**f_params):
	#
		"""
Call all functions registered for the hook with the specified parameters.

@param  f_hook Hook-ID
@return (mixed) Hook results on success; None if not defined
@since  v1.0.1
		"""

		global _direct_pluginmanager
		return _direct_pluginmanager.call_hook_handler (f_hook,f_params)
	#

	@staticmethod
	def register (f_hook,f_function,f_prepend = False,f_exclusive = False):
	#
		"""
Register a python function for the hook.

@param  f_hook Hook-ID
@param  f_function Python function to be registered
@param  f_prepend Add function at the beginning of the stack if true.
@param  f_exclusive Add the given function exclusively.
@since  v1.0.1
		"""

		global _direct_pluginmanager
		_direct_pluginmanager.register_hook (f_hook,f_function,f_prepend,f_exclusive)
	#
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

	def __init__ (self,f_module_package,f_base_dir = ""):
	#
		"""
Constructor

@param  f_module_package Module path to be scanned for *.py files.
@param  f_base_dir Base directory for plugin modules.
@since  v1.0.1
		"""

		global _direct_pluginmanager,_direct_pluginmanager_base_dir

		if (_direct_pluginmanager == None):
		#
			self.pluginmanager = self
			_direct_pluginmanager = self
			self.hooks = { }
		#
		else: self.pluginmanager = _direct_pluginmanager

		self.debug = direct_debug.get ()
		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -pluginmanager->__construct (direct_pluginmanager)- (#echo(__LINE__)#)")

		f_module_packages = [ ]
		f_type = type (f_module_package)

		if (f_type == list): f_module_packages = f_module_package
		elif ((f_type == str) or (f_type == unicode)): f_module_packages = [ f_module_package ]

		if (len (f_base_dir) < 1): f_base_dir = _direct_pluginmanager_base_dir
		if ((len (f_base_dir)) and (not f_base_dir.endswith ("/")) and (not f_base_dir.endswith ("\\"))): f_base_dir += path.sep

		imp.acquire_lock ()

		for f_module_package in f_module_packages:
		#
			f_module_package += "."
			f_path = f_module_package.replace (".",path.sep)

			if (path.isdir (f_base_dir + f_path)):
			#
				f_dir_array = os.listdir (f_base_dir + f_path)

				for f_entry in f_dir_array:
				#
					if ((f_entry.endswith (".py")) and (f_entry != "__init__.py")):
					#
						f_file_object = None
						f_module_name = f_entry[:(len (f_entry) - 3)]

						try:
						#
							(f_file_object,f_file_path,f_pydescription) = imp.find_module (f_module_name,[ f_base_dir + f_path ])
							f_module = imp.load_module ((f_module_package + f_module_name),f_file_object,f_file_path,f_pydescription)
							f_file_object.close ()

							f_module.plugin_registration ()
						#
						except Exception,f_unhandled_exception: pass
					#
				#
			#
		#

		imp.release_lock ()
	#

	def __del__ (self):
	#
		"""
Destructor __del__ (direct_pluginmanager)

@since v0.1.00
		"""

		self.del_direct_pluginmanager ()
	#

	def del_direct_pluginmanager (self):
	#
		"""
Destructor del_direct_pluginmanager (direct_pluginmanager)

@since v0.1.00
		"""

		direct_debug.py_del ()
	#

	def call_hook (self,f_hook,**f_params):
	#
		"""
Call the helper function to run all functions registered for the hook.

@param  f_hook Hook-ID
@return (mixed) Hook results on success; None if not defined
@since  v1.0.1
		"""

		return self.pluginmanager.call_hook_handler (f_hook,f_params)
	#

	def call_hook_handler (self,f_hook,f_params):
	#
		"""
Call all functions registered for the hook with the specified parameters.

@param  f_hook Hook-ID
@return (mixed) Data expected to be returned by the hook
@since  v1.0.1
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -pluginmanager->call_hook_handler (%s,+f_params)- (#echo(__LINE__)#)" % f_hook)
		f_return = None

		if (not "hook" in f_params): f_params['hook'] = f_hook

		if ((f_hook in self.pluginmanager.hooks) and (type (self.pluginmanager.hooks[f_hook]) == list)):
		#
			for f_function in self.pluginmanager.hooks[f_hook]: f_return = f_function (f_params,f_last_return = f_return)
		#

		return f_return
	#

	def register_hook (self,f_hook,f_function,f_prepend = False,f_exclusive = False):
	#
		"""
Register a python function for the hook.

@param  f_hook Hook-ID
@param  f_function Python function to be registered
@param  f_prepend Add function at the beginning of the stack if true.
@param  f_exclusive Add the given function f_exclusively.
@since  v1.0.1
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -pluginmanager->register_hook (%s,+f_function,+f_prepend,+f_exclusive)- (#echo(__LINE__)#)" % f_hook)

		if (f_exclusive): self.pluginmanager.hooks[f_hook] = [ f_function ]
		else:
		#
			if (not f_hook in self.pluginmanager.hooks): self.pluginmanager.hooks[f_hook] = [ ]

			if (f_prepend): self.pluginmanager.hooks[f_hook].insert (0,f_function)
			else: self.pluginmanager.hooks[f_hook].append (f_function)
		#
	#

	@staticmethod
	def get (f_count = False):
	#
		"""
Get the direct_pluginmanager singleton.

@param  bool Count "get ()" request
@return (direct_pluginmanager) Object on success; None if not initialized
@since  v1.0.0
		"""

		global _direct_pluginmanager,_direct_pluginmanager_counter
		if (f_count): _direct_pluginmanager_counter += 1

		return _direct_pluginmanager
	#

	@staticmethod
	def get_pluginmanager (f_count = False):
	#
		"""
Get the direct_pluginmanager singleton.

@param  bool Count "get ()" request
@return (direct_pluginmanager) Object on success; None if not initialized
@since  v1.0.0
		"""

		return direct_pluginmanager.get (f_count)
	#

	@staticmethod
	def py_del ():
	#
		"""
The last "py_del ()" call will activate the Python singleton destructor.

@since  v1.0.0
		"""

		global _direct_pluginmanager,_direct_pluginmanager_counter

		_direct_pluginmanager_counter -= 1
		if (_direct_pluginmanager_counter == 0): _direct_pluginmanager = None
	#

	@staticmethod
	def set_plugins_base_dir (f_base_dir):
	#
		"""
Set a default base directory where plugin modules will be searched in.

@param  f_base_dir Base directory for plugin modules.
@since  v1.0.1
		"""

		global _direct_pluginmanager_base_dir
		if ((len (f_base_dir)) and (not f_base_dir.endswith ("/")) and (not f_base_dir.endswith ("\\"))): f_base_dir += path.sep
		_direct_pluginmanager_base_dir= f_base_dir
	#
#

##j## EOF
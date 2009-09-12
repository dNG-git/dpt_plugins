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
NOTE_END //n*/"""
"""/**
* de.direct_netware.classes.plugins.direct_pluginmanager
*
* @internal   We are using JavaDoc to automate the documentation process for
*             creating the Developer's Manual. All sections including these
*             special comments will be removed from the release source code.
*             Use the following line to ensure 76 character sizes:
* ----------------------------------------------------------------------------
* @author     direct Netware Group
* @copyright  (C) direct Netware Group - All rights reserved
* @package    pas_basic
* @since      v0.1.00
* @license    http://www.direct-netware.de/redirect.php?licenses;w3c
*             W3C (R) Software License
*/"""

import imp,os

_direct_pluginmanager = None

class direct_plugin_hooks (object):
#
	"""/**
* The direct_plugin_hooks class provides static helper functions.
*
* @author    direct Netware Group
* @copyright (C) direct Netware Group - All rights reserved
* @since     v1.0.0
	*/"""

	@staticmethod
	def call (fHook,**fOptions):
	#
		global _direct_pluginmanager
		_direct_pluginmanager.hookCallHandler (fHook,fOptions)
	#

	@staticmethod
	def registration (fHook,fFunction):
	#
		global _direct_pluginmanager
		_direct_pluginmanager.hookRegistration (fHook,fFunction)
	#
#

class direct_pluginmanager (object):
#
	"""
The direct_pluginmanager class provides hook-based python plugins.

* @author    direct Netware Group
* @copyright (C) direct Netware Group - All rights reserved
* @since     v1.0.0
	"""

	hooks = { }
	"""
Registered hook array
	"""
	pluginmanager = { }
	"""
Registered plugin manager instance
	"""

	def __init__ (self,fModulePackage):
	#
		global _direct_pluginmanager

		if (_direct_pluginmanager == None):
		#
			self.pluginmanager = self
			_direct_pluginmanager = self
			self.hooks = { }
		#
		else: self.pluginmanager = _direct_pluginmanager

		fModulePackages = [ ]

		if (type (fModulePackage) == list): fModulePackages = fModulePackage
		elif (type (fModulePackage) == str): fModulePackages = [ fModulePackage ]

		imp.acquire_lock ()

		for fModulePackage in fModulePackages:
		#
			fModulePackage += "."
			fPath = fModulePackage.replace (".",os.sep)

			fDirArray = os.listdir (fPath)

			for fDir in fDirArray:
			#
				if ((fDir.endswith (".py")) and (fDir != "__init__.py")):
				#
					fFileObject = None
					fModuleName = fDir[:(len (fDir) - 3)]

					try:
					#
						fFilePath = fPath + fDir
						fFileObject = open (fFilePath,"r")

						fModule = imp.load_module ((fModulePackage + fModuleName),fFileObject,fFilePath,(".py","r",imp.PY_SOURCE))
						fModule.pluginRegistration ()
					#
					except Exception,f_unhandled_exception: pass

					if (fFileObject != None): fFileObject.close ()
				#
			#
		#

		imp.release_lock ()
	#

	def hookCall (self,fHook,**fOptions): self.pluginmanager.hookCallHandler (fHook,fOptions)

	def hookCallHandler (self,fHook,fOptions):
	#
		if ((self.pluginmanager.hooks.has_key (fHook)) and (type (self.pluginmanager.hooks[fHook]) == list)):
		#
			for fHookFunction in self.pluginmanager.hooks[fHook]: fHookFunction (fOptions)
		#
	#

	def hookRegistration (self,fHook,fFunction,fPrepend = False):
	#
		if (not self.pluginmanager.hooks.has_key (fHook)): self.pluginmanager.hooks[fHook] = [ ]

		if (fPrepend): self.pluginmanager.hooks[fHook].insert (0,fFunction)
		else: self.pluginmanager.hooks[fHook].append (fFunction)
	#

	@staticmethod
	def get ():
	#
		global _direct_pluginmanager
		return _direct_pluginmanager
	#
#

##j## EOF
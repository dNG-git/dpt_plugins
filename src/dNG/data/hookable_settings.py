# -*- coding: utf-8 -*-

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

from dNG.plugins.hook import Hook

from .settings import Settings

class HookableSettings(object):
    """
"HookableSettings" provide a hook based solution to set custom values for
requested settings in a given context and fall back to the default value
otherwise. Please note that None is not supported as a valid setting value.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: plugins
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self, hook, **kwargs):
        """
Constructor __init__(HookableSettings)

:since: v0.2.00
        """

        self.hook = hook
        """
Hook called to get custom values
        """
        self.params = kwargs
        """
Hook parameters used to provide context relevant information
        """
        self.settings = Settings.get_dict()
        """
Settings instance
        """
    #

    def is_defined(self, key):
        """
Checks if a given key is a defined setting.

:param key: Settings key

:return: (bool) True if defined
:since:  v0.2.00
        """

        _return = True
        if (Hook.call(self.hook, **self.params) is None): _return = (key in self.settings)

        return _return
    #

    def get(self, key = None, default = None):
        """
Returns the value with the specified key.

:param key: Settings key
:param default: Default value if not set

:return: (mixed) Value
:since:  v0.2.00
        """

        _return = Hook.call(self.hook, **self.params)
        if (_return is None): _return = self.settings.get(key)
        if (_return is None and default is not None): _return = default

        return _return
    #
#

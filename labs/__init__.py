# -*- coding: utf-8 -*-
"""
The base module for all modules within this folder. All modules implicitly inherit from __init__.py. This module also
initializes the labs package to allow other modules, such as unit tests, to import files from within this folder.

Project: Automation

Requirements:
- Python 2.7.5
"""
from abc import ABCMeta, abstractproperty, abstractmethod

__all__ = ["CiscoRouter"]


class CiscoRouter(object):
    """Abstract base class for all configuration scripts.

    Note - The "object" parameter is used in Python 2 to identify "new-style"
    type classes.

    .. seealso:: https://www.python.org/doc/newstyle/
    """

    # Force children to instantiate abstract methods from this class and any
    # super classes through the Abstract Base Class (ABC) module
    __metaclass__ = ABCMeta

    # Common class attributes
    # USE @abstractproperty INSTEAD OF @property FOR PYTHON < 3.3
    @abstractproperty
    def config_file_path(self):
        return None

    # USE @abstractproperty INSTEAD OF @property FOR PYTHON < 3.3
    @abstractproperty
    def device_ip_address(self):
        return None

    # USE @abstractproperty INSTEAD OF @property FOR PYTHON < 3.3
    @abstractproperty
    def subnet_mask(self):
        return None

    # Common class methods
    @abstractmethod
    def run(self, user_interface, **options):
        """This method must be implemented by all derived classes in
        mtk.mtk.script.

        :param user_interface: A reference to the Reporter object (a pop-up window)
            that is informing the user of the script's progress and status.
        :type user_interface: object
        :param options: A dictionary of additional keyword arguments for the
            method.
        :type options: dict

        :raises: NotImplementedError if the run method is not implemented in
            the child class.

        .. seealso:: mtk.gui.windows.py
        """
        raise NotImplementedError

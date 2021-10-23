"""
scriptlib.utils.exceptions

All scriptlib internal exceptions.
"""

class InitError(Exception):
    """
    Raised when an initialization error is encountered.
    """
    def __init__(self, message, traceback = True, log = True, error_state = True):
        super().__init__(message)

        self.message = message
        self.traceback = traceback
        self.log = log
        self.error_state = error_state

class CloseLoop(Exception):
    """
    Tells everything to shut down.
    """

class SubprocessError(Exception):
    """
    Raised on failed subprocess call.
    """

class InvalidData(Exception):
    """
    Exception used by the argument parser when
    data couldn't be parsed.
    """

class InvalidRule(Exception):
    """
    Used by the argument parser when a compilation
    error occurs.
    """

class InvalidFormat(Exception):
    """
    Shared exception for invalid formats for data
    passed to utility functions.
    """

class DevError(Exception):
    """
    When a general config/backend error happens
    due to you doing something wrong.
    """
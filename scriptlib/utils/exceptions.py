"""
scriptlib.utils.exceptions

All scriptlib internal exceptions.
"""

class InitError(Exception):
    """
    Raised when an initialization error is encountered.
    """

    pass

class CloseLoop(Exception):
    """
    Tells everything to shut down.
    """
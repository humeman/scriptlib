"""
scriptlib.classes.script

Contains the base script class, which does everything.
"""


from scriptlib.utils import (
    exceptions
)


class Script:
    """
    The base class for all scripts.
    
    Holds almost all data.
    """

    def __init__(
            self
        ) -> None:

        # We won't do anything for now - this should be done asynchronously.
        pass

    async def init(
            self,
            **kwargs
        ) -> None:
        """
        Asynchronous initialization function for Script class.
        
        Required kwargs:
            name: str
            version: str
        """

        required = {
            "name": [str],
            "version": [str]
        }

        for name, value in kwargs.items():
            setattr(self, name, value)

        for name, types in required.items():
            if not hasattr(self, name):
                raise exceptions.InitError(f"Script is missing required start value {name}.")

            if type(getattr(self, name)) not in types:
                raise exceptions.InitError(f"Script start value {name} is of wrong type.")

        # We'll figure this out later
        self.scripts = {}
"""
scriptlib.classes.subscript.Subscript
"""

from enum import Enum

from scriptlib.utils import (
    exceptions
)

class SubscriptTypes(Enum):
    NONE = 0


class Subscript:
    """
    Base class for a scriptlib subscript.
    Extend this class to make your own.
    
    Things you can mess with:
        async def run() - Called when the subscript is
            run
        self.name
        self.description
        self.type
        self.auto_run

        async self.run()
        etc.

    (Docs might come later. Look out for those.)
    (There will also be plenty of pre-created ones,
        likely in scriptlib.subscripts. Check there.)
    """

    def __init__(
            self,
            name: str = "A script",
            description: str = "If you see this, whoever made this script is lazy and didn't edit the description. SHAME!",
            script_type: SubscriptTypes = SubscriptTypes.NONE,
            run: bool = True
        ) -> None:
        """
        Initializes a Subscript class.
        
        If extending this class, make sure to insert
        this code somewhere in your __init__ function to 
        ensure this calls:
        
        super().__init__(*args, **kwargs)

        Arguments:
            name: str
            description: str
            script_type: scriptlib.classes.subscript.SubscriptTypes (Enum)
            run: bool
        """

        self.name = name
        self.description = description

        self.type = script_type

        self.auto_run = run

    async def start(
            self
        ) -> None:
        """
        Starts the script.
        """

        await self.run()

    async def run(
            self
        ) -> None:
        """
        Default run function.
        Raises an error, since whatever extends this should
        create this instead.
        """

        raise exceptions.DevError("If creating your own subscript class, you have to override the async def run() function.")
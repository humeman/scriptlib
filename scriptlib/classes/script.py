"""
scriptlib.classes.script

Contains the base script class, which does everything.
"""

import sys
import pytz

from scriptlib.utils import (
    exceptions,
    subprocess,
    errorhandler
)

from scriptlib.classes import (
    argparser,
    logger,
    config
)

import scriptlib

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
            scripts: list
        """

        # Most important :)
        self.logger = logger.Logger()

        required = {
            "name": [str],
            "version": [str],
            "scripts": [list]
        }

        for name, value in kwargs.items():
            setattr(self, name, value)

        for name, types in required.items():
            if not hasattr(self, name):
                raise exceptions.InitError(f"Script is missing required start value {name}.")

            if type(getattr(self, name)) not in types:
                raise exceptions.InitError(f"Script start value {name} is of wrong type.")

        # Load up config
        self.config = config.Config()

        # Register some classes
        self.args = argparser.ArgumentParser({})

        await self.debug()

        await self.config.init()

        # Set timezone
        self.timezone = pytz.timezone(self.config.timezone)

        await self.verify_start()
        self.logger.prep()

    async def debug(
            self
        ) -> None:
        """
        Testing routine for before I have a refined way to
        create start tasks.
        """

        # Try to parse a dict
        res = await self.args.parse(
            "dict",
            "th",
            {}
        )

        self.logger.log("debug", "debug", repr(res))


    async def verify_start(
            self
        ) -> None:
        """
        Verifies that the scriptlib is compatible with this
        system.
        """

        # Get python version
        version = sys.version_info

        if version[0] != 3 and version[1] < 6:
            raise exceptions.InitError(f"You're not running Python 3.6 or higher, which is required for this script. Run `python3 updater.py` (maybe) to install it.")

    async def run(
            self
        ) -> None:
        """
        Runs the script.
        """

        # Just tell each script to start
        for script in self.scripts:
            if script.auto_run:
                scriptlib.loop.create_task(errorhandler.wrap(script.start()))

        if len(self.scripts) == 0:
            self.logger.log("warn", "init", "No scripts are registered. Doing nothing.")
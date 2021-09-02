"""
scriptlib/funcs.py

Base functions, decorators, and etc. that make running things easier.
"""

import scriptlib

from scriptlib.utils import (
    errorhandler,
    exceptions
)

import traceback

def start(
        *args,
        **kwargs
    ) -> None:
    """
    A synchronous wrapper to scriptlib.run().
    
    Entrypoint to the script. Call this instead.

    Parameters:
        config: dict - kwargs passed to scriptlib.script.init().
    """
    try:
        errorhandler.wrap_sync(
            start_terminal
        )

        scriptlib.loop.run_until_complete(
            run(*args, **kwargs)
        )

        scriptlib.loop.run_forever()

    except (exceptions.InitError):
        cleanup()
        # TODO: Integrate into terminal
        print("Init error")

    except (exceptions.CloseLoop):
        cleanup()
        print("Done!")

    except:
        cleanup()
        print("An unexpected error was encountered, so the script is exiting.")
        traceback.print_exc()

async def run(
        config: dict
    ) -> None:
    """
    Fires off the async event loop, initializes the script, and runs everything.

    Parameters:
        config: dict - kwargs passed to scriptlib.script.init().
    """

    for task in [
            scriptlib.script.init(**config)
        ]:

        await errorhandler.wrap(
            task
        )

def cleanup() -> None:
    # Shuts down everything cleanly.
    # Event loop should not be running anymore.

    # Async tasks
    for task in [
            
        ]:

        scriptlib.loop.run_until_complete(
            errorhandler.wrap(
                task()
            )
        )

    # Sync tasks
    for task in [
            scriptlib.terminal.shutdown
        ]:

        errorhandler.wrap_sync(
            task()
        )

async def shutdown() -> None:
    """
    Exits the script and returns to the terminal.
    """
    raise exceptions.CloseLoop()

def start_terminal() -> None:
    """
    Boots the terminal.
    """


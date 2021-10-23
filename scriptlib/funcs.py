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

    scriptlib.loop.set_exception_handler(errorhandler.catch_asyncio)

    try:
        errorhandler.wrap_sync(
            start_terminal
        )

        scriptlib.loop.run_until_complete(
            errorhandler.wrap(
                run(*args, **kwargs)
            )
        )

        scriptlib.loop.run_forever()

    except KeyboardInterrupt as e:
        cleanup()

    except (exceptions.CloseLoop):
        cleanup()

    except:
        cleanup()
        print("An unexpected pre-initialization error was encountered, so the script is exiting.")
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
            scriptlib.script.init(**config),
            scriptlib.script.run()
        ]:

        await errorhandler.wrap(
            task
        )

def cleanup() -> None:
    # Shuts down everything cleanly.
    # Event loop should not be running anymore.

    scriptlib.t.disable_log = True

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


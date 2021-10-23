"""
scriptlib.utils.errorhandler

Built in error-handler, to ensure nothing explodes.
"""

import scriptlib

from scriptlib.utils import (
    exceptions,
    colors
)

import types
from typing import Callable
import traceback

async def wrap(
        coro: types.CoroutineType
    ) -> None:
    """
    Wraps async functions in an error handler
    and neatly logs errors to the console when they
    occur.
    
    Arguments:
        coro: Coroutine - Coroutine to await.
    """

    try:
        await coro

    except Exception as e:
        handle_errors(e)

def wrap_sync(
        func: Callable,
        args: list = [],
        kwargs: dict = {}
    ) -> None:
    """
    Wraps sync functions in an error handler
    and neatly logs errors to the console when they
    occur.
    
    Arguments:
        func: function - Function to call.
        args: list (opt) - Args to call func with.
        kwargs: dict (opt) - Kwargs to call func with.
    """

    try:
        func(*args, **kwargs)

    except Exception as e:
        handle_errors(e)


def handle_errors(
        exception: Exception
    ) -> None:
    """
    Handles exceptions from wrappers.
    
    Reraises them if they're essential. Otherwise,
    logs them.
    
    Arguments:
        exception: Exception - Exception to log
    """
    et = type(exception)

    if et == exceptions.InitError:
        if exception.error_state:
            # InitError is special -- enter error state, or not.

            if exception.traceback:
                log_exception(
                    exception,
                    "A fatal error has occurred!"
                )

            elif exception.log:
                scriptlib.script.logger.log(
                    "error",
                    "unhandlederror",
                    "A fatal error occurred!",
                    bold = True
                )

                scriptlib.script.logger.log_step(
                    "error",
                    "unhandlederror",
                    exception.message
                )

            scriptlib.t.error_state = True
            scriptlib.t.reprint(all = True)

        else:
            raise exceptions.CloseLoop()

    elif et in [exceptions.CloseLoop, KeyboardInterrupt]:
        raise et

    else:
        log_exception(exception)

def log_exception(
        exception: Exception,
        msg: str = "An internal exception occurred!"
    ) -> None:
    """
    Logs an exception to the terminal.
    
    Arguments:
        exception: Exception - Exception to log.
        msg: str (opt) - Title message to use.
    """

    # TODO: Use the logger
    scriptlib.t.log(f"{colors.TerminalColors.RED}{colors.TerminalColors.BOLD}{msg}")
    
    try:
        raise exception

    except:
        for line in traceback.format_exc().split("\n"):
            scriptlib.t.log(f" → {colors.TerminalColors.RED}{line}")

    scriptlib.t.reprint(logs = True)


def catch_asyncio(loop, context):
    if "exception" not in context:
        scriptlib.script.logger.log("warn", "unhandlederror", "An asyncio exception was thrown, but no exception was passed.")
        return

    exc = context["exception"]
    et = type(exc)

    if et in [SystemExit, KeyboardInterrupt]:
        raise

    elif et in exceptions.CloseLoop:
        raise

    scriptlib.script.logger.log("warn", "unhandlederror", "An asyncio exception wasn't handled!")

    scriptlib.script.logger.log_long("warn", "unhandlederror", "\n".join(traceback.format_tb(tb = exc.__traceback__) + [f"{et.__name__}: {repr(exc)}"]).strip())    
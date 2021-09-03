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

    if et in [exceptions.CloseLoop, exceptions.InitError, KeyboardInterrupt]:
        raise et

    else:
        log_exception(exception)

def log_exception(
        exception: Exception
    ) -> None:
    """
    Logs an exception to the terminal.
    
    Arguments:
        exception: Exception - Exception to log.
    """

    # TODO: Use the logger
    scriptlib.t.log(f"{colors.TerminalColors.RED}{colors.TerminalColors.BOLD}An internal exception occurred!")
    
    try:
        raise exception

    except:
        for line in traceback.format_exc().split("\n"):
            scriptlib.t.log(f" → {colors.TerminalColors.RED}{line}")

    scriptlib.t.reprint(logs = True)

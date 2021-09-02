"""
scriptlib.utils.errorhandler

Built in error-handler, to ensure nothing explodes.
"""

from scriptlib.utils import (
    exceptions
)

import types
from typing import Callable
import traceback # TODO

async def wrap(
        coro: types.CoroutineType
    ) -> None:

    try:
        await coro

    except Exception as e:
        handle_errors(e)

def wrap_sync(
        func: Callable,
        args: list = [],
        kwargs: dict = {}
    ) -> None:
    try:
        func(*args, **kwargs)

    except Exception as e:
        handle_errors(e)


def handle_errors(
        exception: Exception
    ) -> None:
    et = type(exception)

    if et in [exceptions.CloseLoop, exceptions.InitError]:
        raise et

    else:
        # TODO
        traceback.print_exc()
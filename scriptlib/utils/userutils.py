"""
scriptlib.utils.userutils

Manages the users on this computer.
"""

from . import (
    exceptions,
    subprocess
)

import scriptlib

from typing import Optional


async def get_user() -> str:
    """
    Gets the active user.
    """

    return " ".join((await subprocess.run("whoami")).data).strip()
"""
scriptlib.utils.timeutils

Contains various utility functions for dealing with
dates and times.
"""

import datetime
import re
import pytz

from . import (
    exceptions
)

import scriptlib

from typing import Optional

specs = {
    "second": "%Y-%m-%d %H:%M-%S",
    "minute": "%Y-%m-%d %H:%M",
    "hour": "%Y-%m-%d %H",
    "day": "%Y-%m-%d",
    "week": "%Y-%U",
    "month": "%Y-%m",
    "year": "%Y"
}

aliases = {
    "second": ["secondly"],
    "minute": ["minutely"],
    "hour": ["hourly"],
    "day": ["daily"],
    "week": ["weekly"],
    "month": ["monthly"],
    "year": ["yearly"]
}

def get_datetime(
        specificity: str, 
        timedelta: Optional[dict] = None,
        format_override: str = None
    ) -> str:
    """
    Gets the current date/time as a string, down
    to a specified specificity.
    
    Arguments:
        specificity: str - Specificity to use.
            second, minute, hour, day, etc.
        timedelta: dict - Timedelta to add to current
            time
        format_override: str - Strftime format to
            override builtin.
    
    Returns:
        datetime: str
    """
    time_format = None

    if specificity in specs:
        time_format = specs[specificity]

    else:
        for change_to, names in aliases.items():
            if specificity in names:
                time_format = specs[change_to]

    if (not time_format) and format_override:
        time_format = format_override

    if not time_format:
        raise exceptions.InvalidFormat(f"Specificity {specificity} does not exist")

    if timedelta is None:
        current = datetime.datetime.utcnow()

    else:
        current = datetime.datetime.utcnow() + datetime.timedelta(**timedelta)


    if hasattr(scriptlib, "script"):
        return pytz.utc.localize(current).astimezone(scriptlib.script.timezone).strftime(time_format)

    else:
        return datetime.datetime.now().strftime(time_format)

times = {
    "year": 31556952,
    "month": 2629800,
    "day": 86400,
    "hour": 3600,
    "minute": 60,
    "second": 0
}

friendly_names = {
    "year": "y",
    "month": "mo",
    "day": "d",
    "hour": "h",
    "minute": "m",
    "second": "s"
}
    
def get_duration(
        seconds: int,
        short: bool = True
    ) -> str:
    """
    Gets a formatted duration from a time in seconds.
    
    Arguments:
        seconds: int - Duration to format
        short: bool = True - Shortened value
    
    Returns:
        duration: str
    """
    seconds = int(seconds)

    comp = {}

    while seconds > 0:
        for name, bound in times.items():
            if seconds > bound:
                # Find number
                if name == "second":
                    comp[name] = seconds
                    seconds = 0

                else:
                    comp[name] = seconds // bound
                    seconds = seconds % bound

    if len(comp) == 0:
        comp["second"] = 0

    # Compile into string
    comp_str = []
    for name, value in comp.items():
        if value == 0 and (name != "second" and len(comp_str) > 0):
            continue

        if short:
            comp_str.append(f"{value}{friendly_names[name]}")

        else:
            comp_str.append(f"{value} {name}s")

    return ", ".join(comp_str)

def parse_duration(
        duration: str
    ) -> str:
    """
    Parses a duration in string format into a
    duration in seconds.
    
    Arguments:
        duration: str
        
    Returns:
        seconds: int
    """

    comp = {}

    for name, value in friendly_names.items():
        comp[name] = 0
        # Find every instance
        for value in re.findall(f"(\d+){name}", duration) + re.findall(f"(\d+){value}", duration):
            try:
                comp[name] += float(value)

            except:
                raise exceptions.InvalidDate(f"{value} is not a number")

    # Compile into seconds
    total = 0
    for unit, value in comp.items():
        if unit == "second":
            total += value

        else:
            total += times[unit] * value

    return total

def get_timestamp(
        seconds: int
    ) -> str:
    """
    Gets the time, down to the second, as a string,
    from epoch time.
    
    Arguments:
        seconds: int
        
    Returns:
        time: str
    """
    return f"{datetime.datetime.fromtimestamp(seconds).strftime('%b %d, %Y at %H:%M %Z')}"

int_times = [
    1,
    60,
    3600,
    86400,
    604800,
    2628000,
    31540000
]

def timestamp_to_seconds(
        seconds: str
    ) -> int:
    """
    Parses a timestamp into seconds.
    
    Arguments:
        timestamp: str
        
    Returns:
        seconds: int
    """
    seconds = seconds.split(":")

    i = len(seconds) - 1
    total = 0
    for duration in seconds:
        duration = int(duration)

        total += duration * int_times[i]

        i -= 1

    return total
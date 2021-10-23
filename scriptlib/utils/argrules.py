"""
scriptlib.utils.argrules

Contains all the argument parsing rules for scriptlib.script.args.
It's a mess. Ported from my old Humecord library, and I don't want
to beautify it. It works.
"""

from typing import OrderedDict
from ..utils.exceptions import InvalidData as IE

import re

import scriptlib

class ParseStr:
    async def main(
            inp
        ):

        try:
            inp = str(inp)

        except:
            raise IE(f"Unable to convert to string")

        return inp

    async def len(
            inp,
            args
        ):
        l = len(inp)

        if l < args[0] or l > args[1]:
            raise IE(f"Value's length isn't within bounds: {args[0]} to {args[1]}")

    async def includes(
            inp,
            args
        ):

        inp = inp.lower()

        for arg in args:
            arg = arg.lower()

            if arg in inp:
                return

        raise IE(f"Value doesn't include any of required words: {', '.join(args)}")

    async def alnum(
            inp,
            args
        ):

        if not inp.replace("-", "").replace("_", "").isalnum():
            raise IE("Value isn't alphanumeric")

    async def in_(
            inp,
            args
        ):

        args = [x.lower() for x in args]

        if inp.lower() not in args:
            raise IE(f"Value isn't one of required phrases: {', '.join(args)}")
    
    async def regex(
            inp,
            args
        ):

        for arg in args:
            if not re.match(arg, inp):
                raise IE(f"Value failed regex check: {arg}")

    async def format(
            inp
        ):

        return str(inp)

class ParseInt:
    async def main(
            inp
        ):

        try:
            inp = int(inp)

        except:
            raise IE(f"Unable to convert to int")

        return inp

    async def between(
            inp,
            args
        ):

        if inp < args[0] or inp > args[1]:
            raise IE(f"Value is outside of bounds: {args[0]} to {args[1]}")

    async def less(
            inp,
            args
        ):

        if inp >= args[0]:
            return IE(f"Value isn't less than {args[0]}")

    async def greater(
            inp,
            args
        ):

        if inp <= args[0]:
            return IE(f"Value isn't greater than {args[0]}")

    async def format(
            inp
        ):

        return str(inp)

class ParseBool:
    async def main(
            inp
        ):

        inp = inp.lower()

        if inp in ["yes", "y", "true", "t", "enable", "on"]:
            return True

        elif inp in ["no", "n", "false", "f", "disable", "off"]:
            return False

        else:
            raise IE("Unable to convert into bool")

    async def format(
            inp
        ):

        return "Yes" if inp else "No"

whitespace_regex = re.compile(r'(\s|\u180B|\u200B|\u200C|\u200D|\u2060|\uFEFF)+') # Removes whitepsace
class ParseURL:
    async def main(
            inp: str
        ):

        inp = inp.strip()

        # Make sure there aren't spaces
        if whitespace_regex.sub("", inp) != inp:
            raise IE(f"URL cannot have whitespace in it - is it properly encoded?")

        # Check for protocol
        if "://" not in inp:
            raise IE(f"Missing protocol (http:// or https://)")

        # Get protocol
        protocol, rest = inp.split("://", 1)

        if protocol not in ["http", "https"]:
            raise IE(f"Invalid protocol (must be http or https)")

        # Check domain
        domain = rest.split("/")[0]

        if "." not in domain:
            raise IE(f"Invalid domain")

        # Good
        return inp

    async def format(
            inp
        ):

        return str(inp)

class ParseDict:
    async def main(
        inp: str
    ):
        # Game plan:
        # -> Find every '==' key
        #   Must be in the middle/end of a word
        #   Must have content after it

        current = inp
        comp = {}
        last_key = None
        ind = current.find("==")

        while ind != -1:
            # Everything before = last key's value + new key, everything after = current

            # So, find the first space before '=='
            start = current.rfind(" ", 0, ind - 1)
            if start != -1:
                # Something found. Add everything before to previous key.
                if last_key is None:
                    raise IE(f"Initial value has no key.")
                
                comp[last_key] = current[:start] # Old value is everything up to this space

            # Set current to everything after '=='
            key = current[start + 1:ind]
            current = current[ind + 2:]

            # Set last_key
            last_key = key

            # Find the next ==
            ind = current.find("==")

        if last_key == None:
            # This isn't a dict.
            raise IE(f"Value contains no separators ('==').")

        # Set the rest of current to the last key
        comp[last_key] = current

        return comp

    async def key(
            inp,
            args
        ):
        # Check if every key matches the specified rule.
        rules = ",".join(args) # Janky workaround to nested rules being wack

        comp = {} # New parsed dict

        for key, value in inp.items():
            if type(value) == str:
                valid, res = await scriptlib.script.args.parse(
                    rules,
                    key,
                    {}
                )

            else:
                valid, res = await scriptlib.script.args.parse_typed(
                    rules,
                    key,
                    {}
                )

            if not valid:
                raise IE(f"Validation failed key name {key}: {', '.join(res)}")

            else:
                comp[res] = value # Overwrite with new value

        return comp

    async def value(
            inp,
            args
        ):
        # Basically the same as key().
        rules = ",".join(args) # Janky workaround to nested rules being wack

        comp = {} # New parsed dict

        for key, value in inp.items():
            if type(value) == str:
                valid, res = await scriptlib.script.args.parse(
                    rules,
                    value,
                    {}
                )

            else:
                valid, res = await scriptlib.script.args.parse_typed(
                    rules,
                    value,
                    {}
                )

            if not valid:
                raise IE(f"Validation failed for value of {key}: {', '.join(res)}")

            else:
                comp[key] = res # Overwrite with new value

        return comp








# Argument rules
# Imported by the argument parser on init.
rules = {
    "str": {
        "main": ParseStr.main,
        "functions": {
            "len": {
                "function": ParseStr.len,
                "args": [[int], [int]],
                "str": "between %0 and %1 characters"
            },
            "includes": {
                "function": ParseStr.includes,
                "arg_types": [str],
                "str": "includes one of %all"
            },
            "alnum": {
                "function": ParseStr.alnum,
                "str": "alphanumeric"
            },
            "in": {
                "function": ParseStr.in_,
                "arg_types": [str],
                "str": "one of %all"
            },
            "regex": {
                "function": ParseStr.regex,
                "arg_types": [str],
                "str": "matches regex %all"
            }
        },
        "str": "a string",
        "data": {},
        "format": {
            "data": {},
            "function": ParseStr.format
        },
        "valid_types": [str]
    },
    "bool": {
        "main": ParseBool.main,
        "functions": {},
        "data": {},
        "str": "a boolean",
        "format": {
            "data": {},
            "function": ParseBool.format
        },
        "valid_types": [bool]
    },
    "int": {
        "main": ParseInt.main,
        "str": "an integer",
        "functions": {
            "between": {
                "function": ParseInt.between,
                "args": [[int], [int]],
                "str": "between %0 and %1"
            },
            "less": {
                "function": ParseInt.less,
                "args": [[int]],
                "str": "below %0"
            },
            "greater": {
                "function": ParseInt.greater,
                "args": [[int]],
                "str": "above %0"
            }
        },
        "data": {},
        "format": {
            "data": {},
            "function": ParseInt.format
        },
        "valid_types": [int]
    },
    "url": {
        "main": ParseURL.main,
        "str": "a url",
        "functions": {},
        "data": {},
        "format": {
            "data": {},
            "function": ParseURL.format
        },
        "valid_types": [str]
    },
    "dict": {
        "main": ParseDict.main,
        "str": "a dict",
        "functions": {
            "key": {
                "function": ParseDict.key,
                "arg_types": [str],
                "str": "with keys matching rule %all"
            },
            "value": {
                "function": ParseDict.value,
                "arg_types": [str],
                "str": "with values matching rule %all"
            }
        },
        "data": {},
        "format": {
            "data": {},
            "function": None #ParseDict.format
        },
        "valid_types": [dict, OrderedDict]
    }
}
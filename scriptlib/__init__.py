"""
scriptlib 0.0a

A simple asynchronous Python scripting library, designed to combine all
the tools you need to create effective shell scripts into one easy package.

https://github.com/humeman/scriptlib
"""
version = "0.0a"

# IMPORTANT NOTE TO SELF: DON'T PUT F-STRINGS IN THIS FILE
# SEE CODE DIRECTLY BELOW THIS FOR REASON WHY

# Validate version
import sys

version = sys.version_info

if version[0] != 3 or version[1] < 6:
    print("ERROR: Can't run. You need Python 3.6 or higher - you're running Python {}.{}. Install via PPA (linux) or python.org (windows).".format(version[0], version[1]))
    
    if version[0] == 2:
        print("Side note: You're on Python 2, which is unsupported. Try running using 'python3' instead of 'python'.")
        
    sys.exit(1)

# Set up asyncio stuff
import asyncio
loop = asyncio.new_event_loop()

# Import base classes
from .classes.script import Script
from .classes.terminal import Terminal

# Create Terminal class
terminal = Terminal()
# Create aliases
term = terminal
t = terminal
terminal.init()



# Create Script class
script = Script()
scr = script
s = script

# Import everything else
from .funcs import *
from . import subscripts
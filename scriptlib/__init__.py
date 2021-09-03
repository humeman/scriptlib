"""
scriptlib 0.0a

A simple asynchronous Python scripting library, designed to combine all
the tools you need to create effective shell scripts into one easy package.

https://github.com/humeman/scriptlib
"""
version = "0.0a"

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
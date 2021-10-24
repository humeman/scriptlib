"""
scriptlib.classes.console

Contains classes and functions required to manage
input and commands from the integrated terminal.
"""

import curses
from threading import Thread
import re
import asyncio
import traceback
from enum import Enum
from typing import Callable

from .terminal import ConsoleModes
from ..utils import (
    colors,
    errorhandler
)

import scriptlib

# Will be skipped by ctrl + backspace.
chars = "abcdefghijklmnopqrstuvwxyz0123456789"

class Console:
    """
    Class that handles input and commands from the
    integrated terminal.
    """

    def __init__(
            self
        ) -> None:
        self.term = scriptlib.terminal

        self.current = {
            ConsoleModes.REGULAR: "",
            ConsoleModes.ASK: "",
            ConsoleModes.MENU: None
        }

        self.history = []
        self.hist_current = None

        self.mode = ConsoleModes.REGULAR

        self.error_state = False
        self.char = None

        self.location = 0

        self.shutdown = False

        self.sequences = {
            343: Actions.execute, # Enter # Good
            263: Actions.backspace, # Backspace
            330: Actions.delete, # Delete
            337: lambda *args: Actions.history(*args, -1), #lambda *args: Actions.scroll(*args, -1), # Shift arrow up
            336: lambda *args: Actions.history(*args, 1), #lambda *args: Actions.scroll(*args, 1), # Shift arrow down
            339: lambda *args: Actions.scroll(*args, -1 * (self.term.term.height - 8)), # Page up
            338: lambda *args: Actions.scroll(*args, self.term.term.height - 8), # Page down
            259: lambda *args: Actions.scroll(*args, -1), # Arrow up
            258: lambda *args: Actions.scroll(*args, 1), # Arrow down
            361: Actions.activate_esc,
            #385: Actions.shutdown,
            #360: Actions.shutdown,
            260: lambda *args: Actions.scroll_console(*args, -1), # Scroll left
            261: lambda *args: Actions.scroll_console(*args, 1), # Scroll right
            #331: Actions.reload, # Insert
            262: Actions.home # you'd never believe it
        }

        self.chars = {
            "\x17": Actions.backspace,
            #"\x04": Actions.shutdown
        }

        self.escapes = {
            "[1;5D": lambda *args: Actions.scroll_far(*args, -1), # Ctrl arrow left
            "[1;5C": lambda *args: Actions.scroll_far(*args, 1), # Ctrl arrow right
            "[1;5A": lambda *args: Actions.history(*args, -1), # Ctrl arrow up
            "[1;5B": lambda *args: Actions.history(*args, 1) # Ctrl arrow down
        }

        self.escape = False
        self.escape_mem = ""

        self.start()

    def start(
            self
        ) -> None:
        """
        Starts the console listener in another thread.
        """

        self.thread = Thread(target = self.wait_for_key)
        self.thread.start()

    def wait_for_key(
            self
        ) -> None:
        """
        Infinite loop that listens for keyboard keypresses.
        """

        while not self.shutdown:
            try: # TODO: Hook into normal error handler, when that works
                char = self.term.getch(timeout = 0.02)

                if not char:
                    # Check for escape chars
                    if self.escape:
                        self.escape = False
                        self.set_current("")
                        self.location = 0
                        self.term.reprint(console = True)

                    continue

                self.got_input(char)

            except Exception as e:
                errorhandler.log_exception(e)

    def got_input(
            self,
            char
        ) -> None:
        """
        Fired when a character is received.
        """

        # Check for sequence characters
        if char.is_sequence:
            code = char.code

            try:
                if code in self.sequences:
                    self.sequences[code](self, char)

                else:
                    self.term.log(f"Unknown sequence: {code}", True)

            except Exception as e:
                errorhandler.log_exception(e)

        else:
            # Check for string chars
            code = str(char)

            run = False
            try:
                if code in self.chars:
                    self.chars[code](self, char)
                    run = True

            except Exception as e:
                errorhandler.log_exception(e)

            # Collect escape chars
            if self.escape:
                self.escape_mem += char.__str__()
                run = True

                if len(self.escape_mem) == 5: # Escape sequence complete
                    if self.escape_mem in self.escapes:
                        try:
                            self.escapes[self.escape_mem](self, char)

                        except Exception as e:
                            errorhandler.log_exception(e)

                    else:
                        # Not an escape char (shouldn't be humanly possible, but whatever)
                        # Treat it like clear and append escape mem & run
                        self.set_current(self.escape_mem)

                        self.location = 5
                        run = False

                    self.escape = False
                    self.escape_mem = ""

            # Append to current if not a command
            if not run:
                self.insert_current(self.location, char.__str__())

                self.location += 1

        self.term.reprint(logs = True, console = True)

    def set_current(
            self,
            new: str
        ) -> None:
        """
        Replaces the current register based on
        whatever mode is active.
        
        Arguments:
            new: str - String to replace with
        """

        self.current[self.mode] = new

    def insert_current(
            self,
            index: int,
            new: str
        ) -> str:
        """
        Inserts 'new' at the specified 'index' and returns
        the new current string.
        
        Arguments:
            index: int - Index to insert before
            new: str - String to insert at that location
        
        Returns:
            current: str - New current string
        """

        current = self.current[self.mode]

        self.current[self.mode] = f"{current[:self.location]}{new}{current[self.location:]}"

        return self.current[self.mode]

    def get_current(
            self
        ) -> str:
        """
        Returns the current console string.
        """

        return self.current[self.mode]



console_headers = {
    ConsoleModes.REGULAR: ("console", "$"),
    ConsoleModes.ASK: ("ask", ">"),
    ConsoleModes.MENU: ("menu", "@")
}

class Actions:
    def execute(
            self,
            char: str
        ) -> None:
        """
        Executes a command.
        """

        if self.mode == ConsoleModes.ASK:
            scriptlib.terminal.ask_mode["complete"] = True

        current = self.get_current()
        self.history.append(current)

        mode, char = console_headers[self.mode]
        self.term.log(f"{self.term.color[mode]}{colors.TerminalColors.BOLD}{char} {colors.TerminalColors.RESET}{self.term.color[mode]}{current}", True)

        if self.mode == ConsoleModes.REGULAR:
            self.set_current("")

        self.location = 0
        self.hist_current = None

    def backspace(
            self,
            char: str
        ) -> None:
        """
        Handles backspace and ctrl + backspace.
        """

        inp = self.get_current()

        if char == "\x7f":
            # Backspace
            index = self.location - 1

            if index >= 0:
                self.set_current(f"{inp[:index]}{inp[index + 1:]}")
                self.location = index

        elif char in ["\x08", "\x17"]:
            # Ctrl backspace
            # Start at index, remove until first char not in "abcd...."
            low_index = Actions.find_next( # TODO: Move to utils
                lambda char: char.lower() not in chars,
                lambda i: i == self.location - 1,
                reversed(list(enumerate(inp[:self.location]))),
                0
            )

            if low_index != 0:
                low_index += 1

            # Remove everything in between
            self.set_current(f"{inp[:low_index]}{inp[self.location:]}")
            self.location = low_index

    def delete(
            self,
            char: str
        ) -> None:
        """
        Handles del.
        """
        index = self.location
        current = self.get_current()

        if index < len(current):
            self.set_current(f"{current[:index]}{current[index + 1:]}")

    def scroll(
            self,
            char: str,
            diff: int
        ) -> None:
        """
        Handles scrolling.

        Arguments:
            diff: int - Lines to scroll by
        """

        self.term.scroll(diff)

    def activate_esc(
            self,
            char: str
        ) -> None:
        """
        Starts searching for escape sequences.
        """

        self.escape = True
        self.escape_mem = ""

    def scroll_far(
            self,
            char: str,
            direction: int
        ) -> None:
        """
        Handles long scrolling (ctrl + arrow) in the console.
        """

        current = self.get_current()

        if direction > 0:
            # Find first non-alpha char after location.
            scroll_to = Actions.find_next(
                lambda char: char.lower() not in chars,
                lambda i: i == self.location + 1,
                [(i + self.location + 1, x) for i, x in enumerate(current[self.location + 1:])],
                len(current)
            )

        else:
            scroll_to = Actions.find_next(
                lambda char: char.lower() not in chars,
                lambda i: i == self.location - 1,
                reversed(list(enumerate(current[:self.location]))),
                0
            )

        self.location = scroll_to

    def find_next(
            charset: Callable,
            trigger: Callable,
            chars,
            default: int = 0
        ) -> int:
        """
        Returns the next instance of the specified charset.
        
        Arguments:
            charset: Callable - If condition to satisfy.
                ex: lambda char: char.lower() not in chars
            trigger: Callable - Skip condition to meet.
                ex: lambda i: i == self.location - 1
            chars: List[Tuple(int, str)] - String to search
            default: int - Location to return if nothing found

        Returns:
            location: int - Location found.
        """
        skip = False
        scroll_to = default

        for i, char in chars:
            if charset(char):
                if trigger(i):
                    skip = True
                    continue

                if skip:
                    continue

                scroll_to = i
                break

            elif skip:
                scroll_to = i
                break

        return scroll_to

    def scroll_console(
            self,
            char: str,
            diff: int
        ) -> None:
        """
        Scrolls the console.
        
        Arguments:
            diff: int - Chars to scroll by.
        """
        current = self.get_current()

        self.location += diff

        if diff > 0:
            if self.location > len(current):
                self.location = len(current)

        elif diff < 0:
            if self.location < 0:
                self.location = 0

    def history(
            self,
            char: str,
            new: str
        ) -> None:
        """
        Scrolls in the history register.
        """

        current = self.get_current()

        if self.hist_current is None:
            # We need to first append current, if it's not None,
            # so it's not lost

            if current != "":
                self.history.append(current)

            self.hist_current = len(self.history)

        self.hist_current += new

        if self.hist_current < 0:
            self.hist_current = 0

        if self.hist_current >= len(self.history):
            self.hist_current = None

        if self.hist_current is None:
            self.set_current("")
            self.location = 0

        else:
            # Set to hist index
            self.set_current(str(self.history[self.hist_current]))
            self.location = len(self.get_current())

    def home(
            self,
            char: str
        ) -> None:
        """
        Returns to the most recent line when the home
        key is pressed.
        """

        self.term.manual_scroll = False
        self.term.location = len(self.term.lines) - self.term.log_count

        if self.term.location < 0:
            self.term.location = 0

        


            

                
